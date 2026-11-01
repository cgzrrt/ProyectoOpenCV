import cv2

# ------------------------------------------------------------
#  Funciones auxiliares de tamaño
# ------------------------------------------------------------

def reducir_ancho(img, ancho_max):
    """Devuelve (imagen reducida, factor). factor = ancho original / ancho nuevo.
    Si la imagen ya es pequeña se devuelve igual con factor 1."""
    alto, ancho = img.shape[:2]
    if ancho <= ancho_max:
        return img, 1.0
    factor = ancho / ancho_max
    nueva = cv2.resize(img, (ancho_max, int(alto / factor)), interpolation=cv2.INTER_AREA)
    return nueva, factor


def redimensionar_alto(imagen, alto_deseado=700):
    """Para enseñar imagenes grandes en pantalla (igual que en el main de texto)."""
    alto, ancho = imagen.shape[:2]
    factor = alto_deseado / alto
    return cv2.resize(imagen, (int(ancho * factor), alto_deseado), interpolation=cv2.INTER_AREA)