from PIL import Image
from io import BytesIO
import piexif

def strip_exif(image_bytes: bytes) -> bytes:
    """Eliminar metadatos EXIF de imagen"""
    img = Image.open(BytesIO(image_bytes))

    # Aqui creamos la imagen sin los datos EXIF
    data = list(img.getdata())
    image_without_exif = Image.new(img.mode, img.size)
    image_without_exif.putdata(data)

    #guardamos en el buffer
    output = BytesIO()
    image_without_exif.save(output, format=img.format)
    return output.getvalue()

