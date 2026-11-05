import cv2
import numpy as np
import config

# -------------------------------------
# PASO 4: colorear foto en blanco y negro
# -------------------------------------

clasificador = cv2.CascadeClassifier(config.RUTA_HAAR)

def esBlancoNegro(img):
    """True si la foto tiene saturación media-baja en hsv"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return float(np.mean(hsv[:, :, 1])) < config.SATURACION_MAX_BIN

def detectarCaras(gris):
    """Rectángulos (x, y, ancho, alto) de las caras.
    Se ecualiza para fotos con poco contraste"""
    ecualizar = cv2.equalizeHist(gris)
    caras = clasificador.detectMultiScale(ecualizar, 1.1, 5, minSize=(40, 40))
    return [tuple(int(v) for v in c) for c in caras]

def mascCara(forma, cara):
    """Elipse suavizada sin esquinas del rectángulo"""
    x, y, ancho, alto = cara
    mascara = np.zeros(forma, np.uint8)
    centro = (x + ancho // 2, y + int(0.55 * alto))
    ejes = (int(0.42 * ancho), int(0.50* alto))
    cv2.ellipse(mascara, centro, ejes, 0, 0, 360, 255, -1)
    k = max(3, int(0.15 * ancho) | 1)
    return cv2.GaussianBlur(mascara, (k, k), 0).astype(np.float32) / 255

def colorearFoto(img):
    """Devuelve la foto coloreada si es blanco y negro"""
    if not esBlancoNegro(img):
        return img
    
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(cv2.cvtColor(gris, cv2.COLOR_GRAY2RGB), cv2.COLOR_BGR2LAB)
    L = lab[:, :, 0]
    a = np.full(gris.shape, 128 + config.TINTE_FONDO[0], np.float32)
    b = np.full(gris.shape, 128 + config.TINTE_FONDO[1], np.float32)

    for cara in detectarCaras(gris):
        x, y, ancho, alto = cara
        centro = L[y+alto // 4:y+3*alto // 4, x+ancho // 4:x+3*ancho // 4]
        media = max(float(np.mean(centro)), 1.0)

        relativa = L.astype(np.float32) / media
        claridad = np.clip((relativa - 0.7) / 0.8, 0, 1)
        croma = 1.0 - config.PALIDEZ_MAX * claridad

        peso = mascCara(gris.shape, cara) * np.clip(L / 70.0, 0, 1)

        a = a*(1-peso)+(128+config.PIEL_A*croma)*peso
        b = b*(1-peso)+(128+config.PIEL_B*croma)*peso
    
    lab = cv2.merge([L, np.clip(a, 0, 255).astype(np.uint8), np.clip(b, 0, 255).astype(np.uint8)])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)