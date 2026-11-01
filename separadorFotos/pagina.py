import cv2
import numpy as np
import config
import utiles

# ------------------------------------------------------------
#  PASO 1: encontrar la pagina del album dentro de la imagen
#  (Canny + dilatar/erosionar + contornos + boundingRect: P38, P41, P45, P46)
# ------------------------------------------------------------

kernel = np.ones((5, 5), np.uint8)


def detectar_pagina(img):
    """Devuelve (x, y, ancho, alto) de la pagina en 'img' o None si no la encuentra."""
    byn = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    suavizado = cv2.blur(byn, (7, 7))
    s = config.SENSIBILIDAD_CANNY
    bordes = cv2.Canny(suavizado, s, s * 2)
    bordes = cv2.dilate(bordes, kernel, iterations=4)   # cierra huecos en el borde
    bordes = cv2.erode(bordes, kernel, iterations=4)    # y vuelve al grosor original

    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Se elige el contorno cuyo rectangulo envolvente sea el mayor dentro de los límites
    area_imagen = img.shape[0] * img.shape[1]
    mejor = None
    area_mejor = 0
    for contorno in contornos:
        x, y, ancho, alto = cv2.boundingRect(contorno)
        area = ancho * alto
        if config.AREA_MIN_PAGINA * area_imagen <= area <= config.AREA_MAX_PAGINA * area_imagen:
            if area > area_mejor:
                mejor = (x, y, ancho, alto)
                area_mejor = area
    return mejor


def extraer_pagina(img):
    """Devuelve (pagina recortada, rectangulo en la imagen original o None).
    Si no hay que buscarla o no se encuentra, la pagina es la imagen entera."""
    if not config.BUSCAR_PAGINA:
        return img, None

    pequena, factor = utiles.reducir_ancho(img, config.ANCHO_ANALISIS)
    rect = detectar_pagina(pequena)
    if rect is None:
        return img, None

    x, y, ancho, alto = [int(v * factor) for v in rect]      # a tamaño original
    m = int(config.MARGEN_RECORTE_PAGINA * min(ancho, alto))
    pagina = img[y + m:y + alto - m, x + m:x + ancho - m].copy()   # slicing, como P57
    return pagina, (x, y, ancho, alto)