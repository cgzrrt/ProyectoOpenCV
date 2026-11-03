import cv2
import config
import numpy as np

bloque = config.BLOQUE
constante = config.CONSTANTE

def actualizar_bloque(blq):
    global bloque
    bloque = blq 

def actualizar_constante(cte):
    global constante
    constante = cte 

def aplicar_filtros(frame):
    blanconegro = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    suavizado = cv2.GaussianBlur(blanconegro, (5, 5), 0)
    
    return suavizado

def calcular_bloque_valido():
    bloque_valido = max(3, bloque)
    if bloque_valido % 2 == 0:
        bloque_valido += 1
    
    return bloque_valido

def filtrado(frame):
    frame_filtrada = aplicar_filtros(frame)
    bloq = calcular_bloque_valido()

    # INV para que quede tinta blanca sobre fondo negro
    frame_umbral = cv2.adaptiveThreshold(frame_filtrada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, bloq, constante)

    # limpieza de ruido
    kernel = np.ones((2, 2), np.uint8)
    frame_limpio = cv2.erode(frame_umbral, kernel)
    frame_limpio = cv2.dilate(frame_limpio, kernel)

    return frame_limpio

    