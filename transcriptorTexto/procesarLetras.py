import cv2
import numpy as np 
import string
import config

tamano = config.TAM
umbral_confianza = config.UMBRAL_CONF

def normalizarLetra(frame):
    puntos = cv2.findNonZero(frame)
    if puntos is None:
        return
    
    x, y, ancho, alto = cv2.boundingRect(puntos)
    recorte = frame[y:y+alto, x:x+ancho]

    borde = 3
    escala = (tamano - 2*borde) / max(ancho, alto)
    nuevo_ancho = max(1, int(round(ancho * escala)))
    nuevo_alto = max(1, int(round(alto * escala)))
    recorte = cv2.resize(recorte, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)

    lienzo = np.zeros((tamano, tamano), dtype=np.uint8)
    x0 = (tamano - nuevo_ancho) // 2
    y0 = (tamano - nuevo_alto) // 2
    lienzo[y0:y0+nuevo_alto, x0:x0+nuevo_ancho] = recorte

    return cv2.GaussianBlur(lienzo, (3, 3), 0)


def crearPlantillas(ancho=32, alto=32):
    plantillas = {}
    caracteres = string.ascii_uppercase # + string.ascii_lowercase + string.digits
    fuente = cv2.FONT_HERSHEY_SIMPLEX

    for car in caracteres:
        img_char = np.zeros((80, 80), dtype=np.uint8)
        (an, al), _ = cv2.getTextSize(car, fuente, 2, 3)
        cv2.putText(img_char, car, ((80 - an) // 2, (80 + al) // 2), fuente, 2, 255, 3)

        plantillas[car] = normalizarLetra(img_char)
    return plantillas

def clasificarLetras(letraRecortada, plantillas):
    letraN = normalizarLetra(letraRecortada)
    if letraN is None:
        return "?"

    letra = "?"
    maximo = -1.0

    for car, plantilla in plantillas.items():
        res = cv2.matchTemplate(letraN, plantilla, cv2.TM_CCOEFF_NORMED)
        valor = res[0][0]

        if valor > maximo:
            maximo = valor
            letra = car 

    return letra if maximo > 0.45 else "?"

def transcribir(hoja_umbral, lineas, plantillas):
    alturas = []
    for linea in lineas:
        for caja in linea:
            alturas.append(caja[3])

    if len(alturas) == 0:
        return "", []
    
    alto_medio = np.median(alturas)
    
    texto = ""
    resultados = []

    for linea in lineas:
        anterior = None

        for caja in linea:
            x, y, ancho, alto = caja

            if anterior is not None and x - (anterior[0] + anterior[2]) > 0.5 * alto_medio:
                texto += " "
            
            letra = clasificarLetras(hoja_umbral[y:y+alto, x:x+ancho], plantillas)
            texto += letra 
            anterior = caja
        
        texto += "\n"

    return texto, resultados

def centroVertical(caja):
    return caja[1] + caja[3] / 2

def posicionX(caja):
    return caja[0]

def ordenarCajas(cajas):
    if len(cajas) == 0:
        return []
    
    alturas = []
    for caja in cajas:
        alturas.append(caja[3])
    alto_medio = np.median(alturas)

    cajas = sorted(cajas, key=centroVertical)

    lineas = []
    linea = [cajas[0]]
    centros = [centroVertical(cajas[0])]

    for caja in cajas[1:]:
        if abs(centroVertical(caja) - np.mean(centros)) < 0.6 * alto_medio:
            linea.append(caja)
            centros.append(centroVertical(caja))
        else:
            lineas.append(sorted(linea, key=posicionX))
            linea = [caja]
            centros = [centroVertical(caja)]
        
    lineas.append(sorted(linea, key=posicionX))
    return lineas
