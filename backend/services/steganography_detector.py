import numpy as np
from PIL import Image
from io import BytesIO

def detect_steganography(image_bytes: bytes) -> dict:
    """Detecta posible esteganografia analizando LSB y ruido"""
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img)

    #Analisis LSB (Least Significant Bit)
    # esto lo que hace es tomar el bit menos significativo de cada canal de color y ver si hay patrones inusuales
    lsb_analysis = analyze_lsb_pattern(arr)

    #Analisis de entropia
    entropy = calculate_entropy(arr)

    eof_suspicious = has_trailing_data(image_bytes)
    lsb_balance_score = lsb_analysis["anomaly_score"]
    suspicious_reasons = []

    if eof_suspicious:
        suspicious_reasons.append("Datos extra detectados despues del final del archivo")

    # La entropia alta por si sola no prueba esteganografia: muchas fotos normales,
    # imagenes con ruido o JPEG/WebP comprimidos pueden acercarse a 8 bits.
    # Solo la usamos como senal fuerte cuando ademas los LSB estan casi perfectamente balanceados.
    if entropy > 7.95 and lsb_balance_score < 0.03:
        suspicious_reasons.append("Entropia muy alta con LSB casi perfectamente balanceado")

    is_suspicious = len(suspicious_reasons) > 0

    return {
        "is_suspicious": is_suspicious,
        "confidence": max(lsb_balance_score, entropy / 8) if is_suspicious else min(max(lsb_balance_score, entropy / 8), 0.49),
        "reasons": suspicious_reasons,
        "details": {
            "lsb_balance_score": lsb_balance_score,
            "entropy": entropy,
            "eof_suspicious": eof_suspicious
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

def has_trailing_data(image_bytes: bytes) -> bool:
    jpg_end = image_bytes.rfind(b"\xff\xd9")
    if jpg_end != -1:
        return len(image_bytes[jpg_end + 2:].strip()) > 0
    return False
