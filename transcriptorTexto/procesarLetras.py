import cv2
import numpy as np 
import string

def crearPlantillas(ancho=32, alto=32):
    plantillas = {}
    caracteres = string.ascii_uppercase + string.ascii_lowercase + string.digits
    fuente = cv2.FONT_HERSHEY_SIMPLEX

    for car in caracteres:
        img_char = np.zeros((60, 60), dtype=np.uint8)
        (an, al), _ = cv2.getTextSize(car, fuente, 1.5, 2)
        cv2.putText(img_char, car, ((60 - an) // 2, (60 + al) // 2), fuente, 1.5, 255, 2)

        plantillas[car] = cv2.resize(img_char, (ancho, alto))
    return plantillas

def clasificarLetras(letraRecortada, plantillas):
    resizedRecortado = cv2.resize(letraRecortada, (32, 32))
    letra = "?"
    maximo = -1.0

    for car, plantilla in plantillas.items():
        res = cv2.matchTemplate(resizedRecortado, plantilla, cv2.TM_CCOEFF_NORMED)
        _, valorMax, _, _ = cv2.minMaxLoc(res)

        if valorMax > maximo:
            maximo = valorMax
            letra = car 

    return letra if maximo > 0.45 else "?"

# falta