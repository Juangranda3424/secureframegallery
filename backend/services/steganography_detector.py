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
    is_suspicious = lsb_analysis["anomaly_score"] > 0.7 or entropy > 7.8 or eof_suspicious

    return {
        "is_suspicious": is_suspicious,
        "confidence": max(lsb_analysis["anomaly_score"], entropy / 8),
        "details": {
            "lsb_anomaly": lsb_analysis["anomaly_score"],
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
#la entreopia se trata de una imagen normal, la entropia suele ser alta, mientras que una imagen con esteganografia puede tener una entropia mas baja debido a patrones repetitivos en los bits menos significativos.
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
