import cv2
import numpy as np
import config

# ============================================================
#  Fondo de la página: color del papel y mapas de "esto es foto"
#
#  Dos señales que fallan en sitios distintos, por eso se combinan:
#    A) distancia al color del papel (restas, P26)
#    B) rayas del papel: el fondo tiene rayas horizontales (fuerte contraste
#       vertical, casi nada horizontal) y las fotos no (Sobel, P35)
#  El color del papel se toma de los píxeles que seguro son rayas; así no se
#  confunde con el color de las fotos cuando éstas ocupan más que el papel.
# ============================================================


def color_frecuente(img):
    """Color (B, G, R) más frecuente: sirve cuando el fondo ocupa la mayor parte."""
    suave = cv2.blur(img, (31, 31))                      # borra el estampado del fondo
    gris = cv2.cvtColor(suave, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gris], [0], None, [256], [0, 256])
    hist = np.float32(hist).reshape(256, 1)              # mismo formato en todas las versiones
    hist = cv2.blur(hist, (1, 9))                        # suaviza el histograma
    _, _, _, pico = cv2.minMaxLoc(hist)
    valor = pico[1]
    cerca = cv2.inRange(gris, max(valor - 12, 0), min(valor + 12, 255))
    return [int(v) for v in np.mean(suave[cerca > 0], axis=0)]


def mascara_rayas(img):
    """Imagen binaria: 255 donde hay rayas horizontales (papel), 0 en el resto."""
    gris = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 1.0)
    gy = np.abs(cv2.Sobel(gris, cv2.CV_32F, 0, 1, ksize=3))
    gx = np.abs(cv2.Sobel(gris, cv2.CV_32F, 1, 0, ksize=3))
    ancho = img.shape[1]
    kx = max(5, int(0.025 * ancho) | 1)                  # ventana ancha...
    ky = max(3, int(0.009 * ancho) | 1)                  # ...y baja
    ey = cv2.blur(gy, (kx, ky))
    ex = cv2.blur(gx, (kx, ky))
    raya = ((ey > config.RAYAS_EY_MIN) & (ey / (ex + 2) > config.RAYAS_RATIO)).astype(np.uint8) * 255
    return cv2.morphologyEx(raya, cv2.MORPH_CLOSE, np.ones((ky, kx), np.uint8))


def color_de_fondo(img, raya=None):
    """Color del papel: el indicado en config; si no, el de los píxeles con rayas seguras;
    si no hay rayas, el color más frecuente."""
    if config.COLOR_FONDO is not None:
        return list(config.COLOR_FONDO)
    if raya is not None:
        seguras = cv2.erode(raya, np.ones((15, 15), np.uint8))
        if np.count_nonzero(seguras) > 500:
            suave = cv2.blur(img, (15, 15))
            return [int(v) for v in np.median(suave[seguras > 0], axis=0)]
    return color_frecuente(img)


def mapa_distancia(img, fondo):
    """Imagen de 0 a 255: cuanto más clara, más se diferencia ese píxel del fondo."""
    k = max(5, int(0.012 * min(img.shape[:2])) | 1)
    suave = cv2.blur(img, (k, k))
    suma = None
    for canal, valor in zip(cv2.split(suave), fondo):
        plano = np.ones(canal.shape, np.uint8) * valor
        dif = cv2.add(cv2.subtract(canal, plano), cv2.subtract(plano, canal))
        suma = dif if suma is None else cv2.add(suma, dif)
    return suma


def preparar_mapas(img):
    """Devuelve (A, B, hay_rayas):
       A = 1 donde el color se aparta del papel, B = 1 donde NO hay rayas.
       Si la imagen no tiene rayas (mesa lisa, marco...), solo vale A."""
    raya = mascara_rayas(img)
    hay_rayas = np.count_nonzero(raya) / raya.size > config.RAYAS_MIN_FRACCION
    color = color_de_fondo(img, raya if hay_rayas else None)
    distancia = mapa_distancia(img, color)
    a = (distancia > config.UMBRAL_DISTANCIA).astype(np.float32)
    b = (255 - raya).astype(np.float32) / 255
    return a, b, hay_rayas


def combinar(a, b, hay_rayas, usar_color, usar_rayas, difuminado):
    """Mapa de 0 a 255 que mezcla las señales según la pasada."""
    if not hay_rayas or (usar_color and not usar_rayas):
        s = a
    elif usar_color and usar_rayas:
        s = 0.5 * a + 0.5 * b
    else:
        s = b
    if difuminado > 1:
        s = cv2.blur(s, (difuminado, difuminado))
    return (np.clip(s, 0, 1) * 255).astype(np.uint8)
