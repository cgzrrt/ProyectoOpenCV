import cv2
import numpy as np
import config

# ------------------------------------------------------------
#  PASO 3: mejorar una foto
#  1. Balance de blancos   
#  2. Quitar ruido (blur, P34)
#  3. Estirar contraste (HSV + histograma, P28-P30)
#  4. Enfocar: original - pasa baja (P35)
# ------------------------------------------------------------


def balance_gris(img):
    """Iguala la media de los tres canales (corrige dominantes de color)."""
    b, g, r = cv2.split(img)
    medias = [max(float(np.mean(c)), 1.0) for c in (b, g, r)]
    gris = sum(medias) / 3
    canales = []
    for canal, media in zip((b, g, r), medias):
        factor = min(max(gris / media, 0.8), 1.25)     # limite para no pasarse
        canales.append(cv2.convertScaleAbs(canal, alpha=factor))
    return cv2.merge(canales)


def percentil(hist, porcentaje):
    """Valor de gris (0-255) por debajo del cual esta ese porcentaje de pixeles."""
    hist = hist.ravel()
    total = float(hist.sum())
    acumulado = 0.0
    for valor in range(256):
        acumulado += float(hist[valor])
        if acumulado >= total * porcentaje / 100:
            return valor
    return 255


def estirar_contraste(img):
    """Reparte la luminosidad (V) entre 0 y 255, ignorando el 1 % mas extremo."""
    h, s, v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
    hist = cv2.calcHist([v], [0], None, [256], [0, 256])
    bajo = percentil(hist, 1)
    alto = percentil(hist, 99)
    if alto - bajo < 30:
        return img
    alfa = min(255.0 / (alto - bajo), 2.0)
    beta = -bajo * alfa
    v = cv2.convertScaleAbs(v, alpha=alfa, beta=beta)
    s = cv2.convertScaleAbs(s, alpha=1.1)           # un poco mas de color
    return cv2.cvtColor(cv2.merge((h, s, v)), cv2.COLOR_HSV2BGR)


def enfocar(img):
    pasa_baja = cv2.blur(img, (5, 5))
    k = config.FACTOR_ENFOQUE
    return cv2.addWeighted(img, 1 + k, pasa_baja, -k, 0)


def mejorar_foto(img):
    if config.BALANCE_BLANCOS:
        img = balance_gris(img)
    if config.QUITAR_RUIDO:
        img = cv2.blur(img, (3, 3))
    if config.ESTIRAR_CONTRASTE:
        img = estirar_contraste(img)
    if config.ENFOCAR:
        img = enfocar(img)
    return img