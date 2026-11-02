import cv2
import numpy as np

umbral = 200
porcentaje_error = 0.01

area_min = 10000
area_max = 50000

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
        print("sin contornos")
        return None

    # coge el mayor contorno encontrado
    contorno = max(contornos, key = cv2.contourArea)

    # si la hoja ocupa muy poco hace return
    if cv2.contourArea(contorno) < 0.1 * frame.shape[0] * frame.shape[1]:
        print("hoja demasiado pequeña")
        return None

    margen_error = porcentaje_error * cv2.arcLength(contorno, True)
    contorno_aprox = cv2.approxPolyDP(contorno, margen_error, True)
    print("vertices:", len(contorno_aprox))

    cv2.drawContours(frame, [contorno_aprox], 0, color, grosor)

    # la hoja debe tener 4 vertices
    if len(contorno_aprox) != 4:
        return None 

    cv2.drawContours(frame, [contorno_aprox], 0, color, grosor)
    
    return contorno_aprox


def encontrarCortorno(frame, frame_filtrada):
    _, frame_umbral = cv2.threshold(frame_filtrada, umbral, 255, cv2.THRESH_BINARY_INV)
    contornos, _ = cv2.findContours(frame_umbral, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    esquinas = detectar_hoja(frame)

    if esquinas is None:
        print("no se han encontrado esquinas")
        return None, None

    for contorno in contornos:
        x, y, ancho, alto = cv2.boundingRect(contorno)
        margen_error = porcentaje_error * cv2.arcLength(contorno, True)
        contorno_aprox = cv2.approxPolyDP(contorno, margen_error, True)

        area = abs(cv2.contourArea(contorno_aprox, True))

        cv2.drawContours(frame, [contorno_aprox], 0, color_texto, grosor)

        # if area >= area_min and area < area_max:        