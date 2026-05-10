import numpy as np
from PIL import Image
from io import BytesIO
import string
import zlib

MAX_LSB_SCAN_BYTES = 4096
MIN_PRINTABLE_PAYLOAD = 8
MIN_NULL_TERMINATED_PAYLOAD = 2
MIN_STRUCTURED_PAYLOAD = 8
MAX_HEADER_SCAN_OFFSET = 16
LSB_TAIL_START_BITS = 2048
LSB_NORMALIZED_TAIL_ZERO_RATIO = 0.995
LSB_BIT_DEPTHS = (1, 2, 4)
KNOWN_PAYLOAD_SIGNATURES = {
    b"ENC::": "PixelVault encrypted text",
    b"SPW1": "StegVault/PixelVault",
    b"Salted__": "OpenSSL encrypted payload",
    b"PK\x03\x04": "ZIP payload",
    b"\x1f\x8b": "GZIP payload",
}
KNOWN_SAFE_PNG_CHUNKS = {
    b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"cHRM", b"gAMA", b"iCCP",
    b"sBIT", b"sRGB", b"bKGD", b"hIST", b"pHYs", b"sPLT", b"tIME",
}

def detect_steganography(image_bytes: bytes) -> dict:
    """Detecta posible esteganografia analizando LSB y ruido"""
    img = Image.open(BytesIO(image_bytes))
    arr = np.array(img.convert("RGB"))
    full_arr = np.array(img.convert("RGBA"))

    #Analisis LSB (Least Significant Bit)
    # esto lo que hace es tomar el bit menos significativo de cada canal de color y ver si hay patrones inusuales
    lsb_analysis = analyze_lsb_pattern(arr)

    #Analisis de entropia
    entropy = float(calculate_entropy(arr))

    eof_suspicious = has_trailing_data(image_bytes)
    lsb_balance_score = lsb_analysis["anomaly_score"]
    embedded_text_findings = find_lsb_text_payloads(full_arr)
    null_terminated_findings = find_lsb_null_terminated_payloads(full_arr)
    embedded_payload_findings = find_lsb_structured_payloads(full_arr)
    lsb_normalization_findings = find_lsb_normalized_tail(arr)
    png_chunk_findings = find_suspicious_png_chunks(image_bytes)
    suspicious_reasons = []

    if eof_suspicious:
        suspicious_reasons.append("Datos extra detectados despues del final del archivo")

    if embedded_text_findings:
        channels = ", ".join(sorted({finding["source"] for finding in embedded_text_findings}))
        suspicious_reasons.append(f"Texto legible detectado en bits LSB ({channels})")

    if null_terminated_findings:
        channels = ", ".join(sorted({finding["source"] for finding in null_terminated_findings}))
        suspicious_reasons.append(f"Mensaje terminado en NULL detectado en bits LSB ({channels})")

    if embedded_payload_findings:
        channels = ", ".join(sorted({finding["source"] for finding in embedded_payload_findings}))
        suspicious_reasons.append(f"Payload estructurado detectado en bits LSB ({channels})")

    if lsb_normalization_findings:
        channels = ", ".join(sorted({finding["source"] for finding in lsb_normalization_findings}))
        suspicious_reasons.append(f"Patron de normalizacion LSB detectado ({channels})")

    if png_chunk_findings:
        chunk_names = ", ".join(sorted({finding["chunk"] for finding in png_chunk_findings}))
        suspicious_reasons.append(f"Datos sospechosos en chunks PNG ({chunk_names})")

    # La entropia alta por si sola no prueba esteganografia: muchas fotos normales,
    # imagenes con ruido o JPEG/WebP comprimidos pueden acercarse a 8 bits.
    # Solo la usamos como senal fuerte cuando ademas los LSB estan casi perfectamente balanceados.
    if entropy > 7.95 and lsb_balance_score < 0.03:
        suspicious_reasons.append("Entropia muy alta con LSB casi perfectamente balanceado")

    is_suspicious = len(suspicious_reasons) > 0

    return {
        "is_suspicious": is_suspicious,
        "confidence": float(max(lsb_balance_score, entropy / 8) if is_suspicious else min(max(lsb_balance_score, entropy / 8), 0.49)),
        "reasons": suspicious_reasons,
        "details": {
            "lsb_balance_score": float(lsb_balance_score),
            "entropy": float(entropy),
            "eof_suspicious": eof_suspicious,
            "embedded_text_findings": embedded_text_findings,
            "null_terminated_findings": null_terminated_findings,
            "embedded_payload_findings": embedded_payload_findings,
            "lsb_normalization_findings": lsb_normalization_findings,
            "png_chunk_findings": png_chunk_findings
        }
    }


def analyze_lsb_pattern(arr):
    """Analiza patrones en bits menos significativos"""
    # Extraemos el bit menos significativo de cada canal
    lsb = arr & 1

    # calculamos distribucion de 0s y 1s en los LSB, 
    #debe ser 50/50 si una imagen es normal
    zeros = np.sum(lsb == 0)
    ones = np.sum(lsb == 1)
    total = zeros + ones

    if total == 0:
        return {"anomaly_score": 0}

    ratio = abs(zeros - ones) / total
    return {"anomaly_score": float(ratio)}

#esta funcion calcula la entropia de una imagen, que es una medida de su aleatoriedad.
#la entropia alta puede aparecer en imagenes normales comprimidas o con mucho detalle; no debe usarse sola para enviar a cuarentena.
def calculate_entropy(arr):
    """Calcula entropia de la imagen"""
    flat = arr.flatten()
    hist, _ = np.histogram(flat, bins=256, range=(0, 256))
    hist = hist[hist > 0]
    probs = hist / hist.sum()
    entropy = -np.sum(probs * np.log2(probs))
    return entropy

def find_lsb_text_payloads(arr):
    """Busca texto UTF-8/ASCII escondido en los bits bajos de canales RGB/RGBA."""
    findings = []

    for source, bits in iter_lsb_sources(arr, bit_depths=(1,)):
        payload = extract_lsb_text(bits)
        if payload:
            findings.append({
                "source": source,
                "length": len(payload),
                "preview": payload[:80]
            })

    return findings

def extract_lsb_text(bits):
    byte_streams = [
        bits_to_bytes(bits[:MAX_LSB_SCAN_BYTES * 8], bit_order="big"),
        bits_to_bytes(bits[:MAX_LSB_SCAN_BYTES * 8], bit_order="little"),
    ]

    for byte_stream in byte_streams:
        for candidate in payload_candidates(byte_stream):
            text = decode_printable_payload(candidate)
            if text:
                return text

    return ""

def find_lsb_null_terminated_payloads(arr):
    """Detecta mensajes escritos desde el primer pixel y terminados con byte NUL."""
    findings = []

    for source, bits in iter_lsb_sources(arr, bit_depths=(1,)):
        for bit_order in ("big", "little"):
            byte_stream = bits_to_bytes(bits[:MAX_LSB_SCAN_BYTES * 8], bit_order=bit_order)
            finding = detect_null_terminated_payload(byte_stream, source, bit_order)
            if finding:
                findings.append(finding)
                break

    return findings

def detect_null_terminated_payload(byte_stream, source, bit_order):
    nul_index = byte_stream.find(b"\x00")
    if not MIN_NULL_TERMINATED_PAYLOAD <= nul_index <= MAX_LSB_SCAN_BYTES:
        return None

    payload = byte_stream[:nul_index]
    text = decode_short_printable_payload(payload)
    if not text:
        return None

    return {
        "source": source,
        "bit_order": bit_order,
        "length": len(text),
        "preview": text[:80],
    }

def decode_short_printable_payload(payload):
    payload = payload.strip(b"\r\n\t ")
    if len(payload) < MIN_NULL_TERMINATED_PAYLOAD:
        return ""

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return ""

    if any(ch not in string.printable for ch in text):
        return ""

    letters = sum(ch.isalpha() for ch in text)
    digits = sum(ch.isdigit() for ch in text)
    spaces = sum(ch.isspace() for ch in text)
    punctuation = len(text) - letters - digits - spaces

    if text.startswith("ENC::") and len(text) >= 10:
        return text

    if letters >= 1 and punctuation <= max(1, len(text) * 0.25):
        return text

    return ""

def payload_candidates(byte_stream):
    candidates = []

    # Herramientas comunes guardan 4 bytes iniciales con la longitud del mensaje.
    if len(byte_stream) >= 4:
        for byte_order in ("big", "little"):
            length = int.from_bytes(byte_stream[:4], byte_order)
            if MIN_PRINTABLE_PAYLOAD <= length <= min(len(byte_stream) - 4, MAX_LSB_SCAN_BYTES):
                candidates.append(byte_stream[4:4 + length])

    # Otras herramientas escriben el texto desde el primer pixel y terminan con NUL.
    nul_index = byte_stream.find(b"\x00")
    if nul_index >= MIN_PRINTABLE_PAYLOAD:
        candidates.append(byte_stream[:nul_index])

    candidates.extend(find_printable_runs(byte_stream))
    return candidates

def bits_to_bytes(bits, bit_order="big"):
    if len(bits) < 8:
        return b""

    usable_bits = bits[:len(bits) - (len(bits) % 8)]
    packed_bits = usable_bits.reshape(-1, 8)
    values = np.packbits(packed_bits, axis=1, bitorder=bit_order).reshape(-1)
    return values.tobytes()

def find_lsb_structured_payloads(arr):
    """Detecta payloads en bits bajos aunque el contenido no sea texto plano."""
    findings = []

    for source, bits in iter_lsb_sources(arr):
        capacity_bytes = len(bits) // 8
        scan_bits = bits[:MAX_LSB_SCAN_BYTES * 8]

        for bit_order in ("big", "little"):
            byte_stream = bits_to_bytes(scan_bits, bit_order=bit_order)
            signature = detect_payload_signature(byte_stream, source, bit_order)
            if signature:
                findings.append(signature)
                break

            finding = detect_length_prefixed_payload(
                byte_stream,
                capacity_bytes,
                source,
                bit_order,
            )
            if finding:
                findings.append(finding)
                break

    return findings

def iter_lsb_sources(arr, bit_depths=LSB_BIT_DEPTHS):
    source_arrays = {
        "RGB": arr[:, :, :3].reshape(-1),
        "R": arr[:, :, 0].reshape(-1),
        "G": arr[:, :, 1].reshape(-1),
        "B": arr[:, :, 2].reshape(-1),
    }

    if arr.shape[2] == 4:
        source_arrays["RGBA"] = arr.reshape(-1)
        source_arrays["A"] = arr[:, :, 3].reshape(-1)

    for bit_depth in bit_depths:
        for source, values in source_arrays.items():
            yield f"{source}/{bit_depth}lsb", values_to_low_bit_stream(values, bit_depth)

def values_to_low_bit_stream(values, bit_depth):
    values = values.astype(np.uint8, copy=False)
    if bit_depth == 1:
        return (values & 1).reshape(-1)

    low_values = values & ((1 << bit_depth) - 1)
    bit_planes = [((low_values >> shift) & 1) for shift in range(bit_depth - 1, -1, -1)]
    return np.stack(bit_planes, axis=1).reshape(-1)

def detect_payload_signature(byte_stream, source, bit_order):
    scan_window = byte_stream[:64]
    for signature, name in KNOWN_PAYLOAD_SIGNATURES.items():
        offset = scan_window.find(signature)
        if offset != -1:
            return {
                "source": source,
                "bit_order": bit_order,
                "signature": name,
                "offset": offset,
            }

    return None

def detect_length_prefixed_payload(byte_stream, capacity_bytes, source, bit_order):
    max_offset = min(MAX_HEADER_SCAN_OFFSET, max(len(byte_stream) - 4, 0))

    for offset in range(max_offset + 1):
        header_end = offset + 4
        for byte_order in ("big", "little"):
            payload_length = int.from_bytes(byte_stream[offset:header_end], byte_order)
            available_capacity = capacity_bytes - header_end

            if not MIN_STRUCTURED_PAYLOAD <= payload_length <= available_capacity:
                continue

            available_sample = byte_stream[header_end:header_end + min(payload_length, len(byte_stream) - header_end)]
            if len(available_sample) < MIN_STRUCTURED_PAYLOAD:
                continue

            sample_entropy = float(calculate_byte_entropy(available_sample))
            printable_ratio = float(calculate_printable_ratio(available_sample))
            if sample_entropy < 2.5:
                continue

            return {
                "source": source,
                "bit_order": bit_order,
                "byte_order": byte_order,
                "offset": offset,
                "length": int(payload_length),
                "sample_entropy": sample_entropy,
                "printable_ratio": printable_ratio
            }

    return None

def calculate_byte_entropy(byte_stream):
    if not byte_stream:
        return 0

    values = np.frombuffer(byte_stream, dtype=np.uint8)
    hist, _ = np.histogram(values, bins=256, range=(0, 256))
    hist = hist[hist > 0]
    probs = hist / hist.sum()
    return -np.sum(probs * np.log2(probs))

def calculate_printable_ratio(byte_stream):
    if not byte_stream:
        return 0

    printable = sum(is_printable_byte(value) for value in byte_stream)
    return printable / len(byte_stream)

def find_lsb_normalized_tail(arr):
    """Detecta herramientas que ponen casi todos los LSB en cero y escriben solo al inicio."""
    findings = []
    sources = {
        "RGB": (arr & 1).reshape(-1),
        "R": (arr[:, :, 0] & 1).reshape(-1),
        "G": (arr[:, :, 1] & 1).reshape(-1),
        "B": (arr[:, :, 2] & 1).reshape(-1),
    }

    for source, bits in sources.items():
        if len(bits) <= LSB_TAIL_START_BITS * 2:
            continue

        prefix = bits[:LSB_TAIL_START_BITS]
        tail = bits[LSB_TAIL_START_BITS:]
        tail_zero_ratio = float(np.mean(tail == 0))
        overall_zero_ratio = float(np.mean(bits == 0))
        prefix_ones = int(np.sum(prefix == 1))

        if (
            prefix_ones > 0
            and tail_zero_ratio >= LSB_NORMALIZED_TAIL_ZERO_RATIO
            and overall_zero_ratio >= 0.90
        ):
            findings.append({
                "source": source,
                "tail_zero_ratio": tail_zero_ratio,
                "overall_zero_ratio": overall_zero_ratio,
                "prefix_ones": prefix_ones,
            })

    return findings

def find_printable_runs(byte_stream):
    runs = []
    start = None

    for index, value in enumerate(byte_stream):
        if is_printable_byte(value):
            if start is None:
                start = index
        else:
            if start is not None and index - start >= MIN_PRINTABLE_PAYLOAD:
                runs.append(byte_stream[start:index])
            start = None

    if start is not None and len(byte_stream) - start >= MIN_PRINTABLE_PAYLOAD:
        runs.append(byte_stream[start:])

    return runs

def decode_printable_payload(payload):
    payload = payload.strip(b"\x00\r\n\t ")
    if len(payload) < MIN_PRINTABLE_PAYLOAD:
        return ""

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = payload.decode("latin-1")
        except UnicodeDecodeError:
            return ""

    cleaned = "".join(ch for ch in text if ch in string.printable).strip()
    if len(cleaned) < MIN_PRINTABLE_PAYLOAD:
        return ""

    letters = sum(ch.isalpha() for ch in cleaned)
    digits = sum(ch.isdigit() for ch in cleaned)
    spaces = sum(ch.isspace() for ch in cleaned)
    printable_ratio = sum(ch in string.printable for ch in cleaned) / len(cleaned)
    unique_ratio = len(set(cleaned)) / len(cleaned)
    most_common_ratio = max(cleaned.count(ch) for ch in set(cleaned)) / len(cleaned)
    punctuation = len(cleaned) - letters - digits - spaces

    if (
        printable_ratio >= 0.90
        and letters >= 4
        and (letters + digits + spaces) >= len(cleaned) * 0.70
        and punctuation <= len(cleaned) * 0.25
        and unique_ratio >= 0.15
        and most_common_ratio <= 0.45
    ):
        return cleaned

    return ""

def is_printable_byte(value):
    return value in b"\n\r\t" or 32 <= value <= 126

def find_suspicious_png_chunks(image_bytes):
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return []

    findings = []
    offset = 8

    while offset + 8 <= len(image_bytes):
        length = int.from_bytes(image_bytes[offset:offset + 4], "big")
        chunk_type = image_bytes[offset + 4:offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        crc_end = data_end + 4

        if crc_end > len(image_bytes):
            findings.append({"chunk": "PNG", "length": length, "reason": "chunk truncado o malformado"})
            break

        chunk_data = image_bytes[data_start:data_end]
        chunk_name = chunk_type.decode("latin-1", errors="replace")

        if chunk_type in (b"tEXt", b"iTXt", b"zTXt"):
            text = extract_png_text_chunk(chunk_type, chunk_data)
            if decode_printable_payload(text.encode("latin-1", errors="ignore") if isinstance(text, str) else text):
                findings.append({"chunk": chunk_name, "length": length, "reason": "texto embebido"})
        elif chunk_type not in KNOWN_SAFE_PNG_CHUNKS and length >= 32:
            findings.append({"chunk": chunk_name, "length": length, "reason": "chunk no estandar con datos"})

        offset = crc_end
        if chunk_type == b"IEND":
            break

    return findings

def extract_png_text_chunk(chunk_type, chunk_data):
    if chunk_type == b"tEXt":
        return chunk_data

    if chunk_type == b"zTXt":
        parts = chunk_data.split(b"\x00", 1)
        if len(parts) != 2 or len(parts[1]) < 2:
            return b""

        try:
            return zlib.decompress(parts[1][1:])
        except zlib.error:
            return b""

    if chunk_type == b"iTXt":
        parts = chunk_data.split(b"\x00", 5)
        if len(parts) < 6:
            return b""

        compression_flag = parts[1]
        text = parts[5]
        if compression_flag == b"\x01":
            try:
                return zlib.decompress(text)
            except zlib.error:
                return b""
        return text

    return b""

def has_trailing_data(image_bytes: bytes) -> bool:
    if image_bytes.startswith(b"\xff\xd8"):
        jpg_end = image_bytes.rfind(b"\xff\xd9")
        if jpg_end != -1:
            return len(image_bytes[jpg_end + 2:].strip()) > 0

    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        png_end = image_bytes.rfind(b"IEND")
        if png_end != -1:
            return len(image_bytes[png_end + 8:].strip()) > 0

    if image_bytes.startswith((b"GIF87a", b"GIF89a")):
        gif_end = image_bytes.rfind(b"\x3b")
        if gif_end != -1:
            return len(image_bytes[gif_end + 1:].strip()) > 0

    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        declared_size = int.from_bytes(image_bytes[4:8], "little") + 8
        return len(image_bytes[declared_size:].strip()) > 0

    return False
