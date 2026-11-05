import cv2
import numpy as np
import utiles
import config

# ==========================
# Colorear a mano con el ratón
# 
#   clic izq -> pintar la region que rodea el punto
#   barra tolerancia -> lo que varía el gris en la región
#   z -> deshacer   Enter -> aceptar    Esc/q -> cancelar
# 
# solo se tocan los canales a y b de lab, la luminosidad no cambia
# ==========================

estado = {'click': None}

def raton(evento, x, y, flags, param):
    if evento == cv2.EVENT_LBUTTONDOWN:
        estado['click'] = (x, y)

def nada(valor):
    pass

def regionClick(gris_suave, semilla, tolerancia):
    """Máscara con los píxeles conectados a semilla cuyo gris se parece"""
    alto, ancho = gris_suave.shape
    mascara = np.zeros((alto+2, ancho+2), np.uint8)
    flags = 4 | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8)
    cv2.floodFill(gris_suave.copy(), mascara, semilla, 0, tolerancia, tolerancia, flags)
    mascara = mascara[1:-1, 1:-1]
    return cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

def colorAB(matiz, saturacion):
    """Pasa un color HSV a sus canales a y b de Lab"""
    hsv = np.uint8([[[matiz, saturacion, 200]]])
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[0, 0]
    return float(lab[1]), float(lab[2])

def componer(L, a, b):
    lab = cv2.merge([L, np.clip(a, 0, 255).astype(np.uint8), np.clip(b, 0, 255).astype(np.uint8)])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def pintar(img):
    """Abre el editor sobre img y devuelve la imagen pintada"""
    L, a, b = [c.astype(np.float32) if i else c for i, c in enumerate(cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2LAB)))]
    suave = cv2.blur(L, (7, 7))
    escala = config.ALTO_VENTANA / img.shape[0]
    historial = []

    cv2.namedWindow('pintar')
    cv2.createTrackbar('matiz', 'pintar', 105, 179, nada)
    cv2.createTrackbar('saturacion', 'pintar', 120, 255, nada)
    cv2.createTrackbar('tolerancia', 'pintar', 12, 40, nada)
    cv2.setMouseCallback('pintar', raton)
    estado['click'] = None 

    resultado = img 

    while True:
        if estado['click'] is not None:
            x, y = estado['click']
            estado['click'] = None 
            semilla = (int(x/escala), int(y/escala))
            tolerancia = max(1, cv2.getTrackbarPos('tolerancia', 'pintar'))
            mascara = regionClick(suave, semilla, tolerancia)
            peso = cv2.GaussianBlur(mascara, (7, 7), 0).astype(np.float32) / 255
            ca, cb = colorAB(cv2.getTrackbarPos('matiz', 'pintar'), cv2.getTrackbarPos('saturacion', 'pintar'))
            historial.append((a.copy(), b.copy()))
            a = a * (1-peso) + ca * peso
            b = b * (1-peso) + cb * peso

        vista = utiles.redimensionar_alto(componer(L, a, b), config.ALTO_VENTANA)
        cv2.rectangle(vista, (0, 0), (vista.shape[1], 26), (0, 0, 0), -1)
        cv2.imshow('pintar', vista)

        tecla = cv2.waitKey(20) & 0xFF
        if tecla in (13, 10, 32):
            resultado = componer(L, a, b)
            break
        if tecla in (27, ord('q')):
            break 
        if tecla == ord('z') and historial:
            a, b = historial.pop()

    cv2.destroyWindow('pintar')
    return resultado