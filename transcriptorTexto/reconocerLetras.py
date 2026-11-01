import cv2

# contornos de aproximacion?

umbral = 200
porcentaje_error = 0.13

fuente = cv2.FONT_HERSHEY_SIMPLEX
color = (255, 0, 0)
grosor = 1
escala = 1
texto = ""

def encontrarCortorno(frame, frame_filtrada):
    _, frame_umbral = cv2.threshold(frame_filtrada, umbral, 255, cv2.THRESH_BINARY_INV)
    contornos, _ = cv2.findContours(frame_umbral, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    for contorno in contornos:
        x, y, ancho, alto = cv2.boundingRect(contorno)
        margen_error = porcentaje_error * cv2.arcLength(contorno, True)
        contorno_aprox = cv2.approxPolyDP(contorno, margen_error, True)

        cv2.drawContours(frame, [contorno_aprox], 0, color, grosor)