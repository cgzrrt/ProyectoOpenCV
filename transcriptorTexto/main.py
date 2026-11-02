import os
import cv2
import config
import filtrado as f
import procesarHoja as ph
import procesarLetras as pl

umbral = 120

carpeta = config.CARPETA_SALIDA
archivo = carpeta + '/hoja.jpg'

# Cámara del móvil
# poner tu propia IP
camara = cv2.VideoCapture('http://192.168.1.129:8080/video')

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

while True:
    ret, frame = camara.read()
    if not ret:
        print("No es posible obtener la imagen")
        break

    if hoja is None:
        frame = redimensionar_alto(frame, 800) 
        copia = frame.copy()
        esquinas = ph.detectar_hoja(frame)

        cv2.imshow('imagen original', frame)
        cv2.imshow('imagen filtrada', f.filtrado(copia))
    else:
        frame_umbral = f.filtrado(hoja)

        hoja_copia = hoja.copy()
        ph.encontrarCortorno(hoja_copia, frame_umbral)

        cv2.imshow('imagen original', hoja_copia)
        cv2.imshow('imagen filtrada', frame_umbral)

    tecla = cv2.waitKey(1)

    if tecla == ord(' ') and hoja is None and esquinas is not None:
        hoja = ph.enderezarHoja(frame, esquinas)
        cv2.imwrite(archivo, hoja)

        print("Hoja guardada en: ", archivo)
    
    if tecla == ord('r'):
        hoja = None
        cv2.destroyWindow('imagen filtrada')
    
    if tecla == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()