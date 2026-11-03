import cv2
import numpy as np
import config

# umbral = config.UMBRAL
porcentaje_error = config.PORCENTAJE_ERROR

# areas de las letras
area_min = config.AREA_MIN
area_max = config.AREA_MAX
margen = config.MARGEN #  pixeles que se ignoran

# tam de hoja enderezada
ancho_hoja = config.ANCHO_HOJA
alto_hoja = config.ALTO_HOJA
dest = np.array([[0, 0], [ancho_hoja, 0], [ancho_hoja, alto_hoja], [0, alto_hoja]], dtype=np.float32)

fuente = cv2.FONT_HERSHEY_SIMPLEX
color = (255, 0, 0)
color_texto = (0, 0, 255)
grosor = 1
escala = 1
texto = ""

def detectar_hoja(frame):
    frame_byn = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_blur = cv2.GaussianBlur(frame_byn, (5, 5), 0)
    _, frame_bin = cv2.threshold(frame_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contornos, _ = cv2.findContours(frame_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # si no hay contornos encontrados hace return
    if len(contornos) == 0:
        return None

    # coge el mayor contorno encontrado
    contorno = max(contornos, key = cv2.contourArea)

    # si la hoja ocupa muy poco hace return
    # if cv2.contourArea(contorno) < 0.1 * frame.shape[0] * frame.shape[1]:
    #     return None

    margen_error = porcentaje_error * cv2.arcLength(contorno, True)
    contorno_aprox = cv2.approxPolyDP(contorno, margen_error, True)

    # cv2.drawContours(frame, [contorno_aprox], 0, color, grosor)

    # la hoja debe tener 4 vertices
    if len(contorno_aprox) != 4:
        return None 

    cv2.drawContours(frame, [contorno_aprox], 0, color, grosor)

    # esquinas ordenadas
    # suma x+y min -> arriba izq
    # suma x+y max -> abajo der
    # resta x-y min -> arriba der
    # resta x-y max -> abajo izq
    puntos = contorno_aprox.reshape(4, 2).astype(np.float32)
    suma = puntos.sum(axis=1)
    resta = np.diff(puntos, axis=1).ravel()
    esquinas = np.array([puntos[np.argmin(suma)], puntos[np.argmin(resta)], puntos[np.argmax(suma)], puntos[np.argmax(resta)]], dtype = np.float32)
    
    return esquinas

def enderezarHoja(frame, esquinas):
    matriz = cv2.getPerspectiveTransform(esquinas, dest)
    return cv2.warpPerspective(frame, matriz, (ancho_hoja, alto_hoja))


def encontrarCortorno(frame, frame_filtrada):
    # _, frame_umbral = cv2.threshold(frame_filtrada, umbral, 255, cv2.THRESH_BINARY_INV)
    # contornos, _ = cv2.findContours(frame_umbral, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    frame_umbral = frame_filtrada.copy()

    # se quita el margen para que no cuente como letra poniendo 0s
    frame_umbral[:margen, :] = 0
    frame_umbral[-margen:, :] = 0
    frame_umbral[:, :margen] = 0
    frame_umbral[:, -margen:] = 0

    contornos, _ = cv2.findContours(frame_umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cajas = []
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area >= area_min and area < area_max:
            cajas.append(cv2.boundingRect(contorno))
    
    return cajas
