import os
import cv2
import config
import filtrado as f
import procesarHoja as ph
import procesarLetras as pl

carpeta = config.CARPETA_SALIDA
archivo = carpeta + '/hoja.jpg'
archivo_texto = carpeta + '/texto.txt'

# Cámara del móvil
# poner tu propia IP
camara = cv2.VideoCapture('http://10.121.167.40:8080/video')

if not camara.isOpened():
    print("No es posible abrir la cámara")
    exit()

# Redimensionar la ventana para poder controlar el threshold
# Si se sale de la resolucion de la pantalla no se puede mover porque queda abajo
def redimensionar_alto(imagen, alto_deseado=400):
    alto, ancho = imagen.shape[:2]
    factor = alto_deseado / alto
    ancho_nuevo = int(ancho * factor)
    return cv2.resize(imagen, (ancho_nuevo, alto_deseado), interpolation=cv2.INTER_AREA)

# crea la carpeta si no existe
os.makedirs(carpeta, exist_ok=True)

cv2.namedWindow('imagen original')
cv2.createTrackbar('bloque', 'imagen original', f.bloque, 100, f.actualizar_bloque)
cv2.createTrackbar('constante', 'imagen original', f.constante, 100, f.actualizar_constante)

hoja = None
plantillas = pl.crearPlantillas()
texto = ""
esquinas = None

while True:
    ret, frame = camara.read()
    if not ret:
        print("No es posible obtener la imagen")
        break

    # si no hay hoja procesada, detecta las esquinas del papel
    # las esquinas que detecta son las del área de mayor tamano
    if hoja is None:
        frame = redimensionar_alto(frame, 800) 
        copia = frame.copy()
        esquinas = ph.detectar_hoja(frame)

        cv2.imshow('imagen original', frame)
        cv2.imshow('imagen filtrada', f.filtrado(copia))
    else:
        # cuando se ha seleccionado una hoja, se filtra
        frame_umbral = f.filtrado(hoja)
        hoja_copia = hoja.copy() # se trabaja sobre una copia

        cajas = ph.encontrarCortorno(hoja_copia, frame_umbral)
        lineas = pl.ordenarCajas(cajas)
        texto, resultados = pl.transcribir(frame_umbral, lineas, plantillas)

        
        for (x, y, ancho, alto), letra in resultados:
            cv2.rectangle(hoja_copia, (x, y), (x+ancho, y+alto), config.COLOR_RECT, config.GROSOR)
            cv2.putText(hoja_copia, letra, (x, y-3), config.FUENTE, 0.5, config.COLOR_TEXTO, 1)

        for (x, y, ancho, alto), letra in resultados:
            cv2.putText(hoja_copia, letra, (x, y-3), ph.fuente, 0.5, ph.color, 1)

        cv2.imshow('imagen original', hoja_copia)
        cv2.imshow('imagen filtrada', frame_umbral)

    tecla = cv2.waitKey(1)

    if tecla == ord(' ') and hoja is None and esquinas is not None:
        hoja = ph.enderezarHoja(copia, esquinas)
        cv2.imwrite(archivo, hoja)

        print("Hoja guardada en: ", archivo)
    
    if tecla == ord('r'):
        hoja = None
        cv2.destroyWindow('imagen filtrada')

    if tecla == ord('t') and hoja is not None:
        print(texto)
        with open(archivo_texto, 'w', encoding='utf-8') as fichero:
            fichero.write(texto)
        print("texto guardado en: ", archivo_texto)
    
    if tecla == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()