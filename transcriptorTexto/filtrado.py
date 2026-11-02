import cv2

bloque = 3
constante = 0

def actualizar_bloque(blq):
    global bloque
    bloque = blq 

def actualizar_constante(cte):
    global constante
    constante = cte 

def aplicar_filtros(frame):
    blanconegro = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('imagen en grises', blanconegro)

    # se puede intentar aplicando el filtro de Canny, con lo que no haría falta
    # barra deslizante (?)
    # edges = cv2.Canny(frame, 150, 250)
    
    return blanconegro

def calcular_bloque_valido():
    bloque_valido = max(3, bloque)
    if bloque_valido % 2 == 0:
        bloque_valido += 1
    
    return bloque_valido

def filtrado(frame):
    frame_filtrada = aplicar_filtros(frame)
    bloq = calcular_bloque_valido()

    frame_umbral = cv2.adaptiveThreshold(frame_filtrada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, bloq, constante)

    return frame_umbral

    