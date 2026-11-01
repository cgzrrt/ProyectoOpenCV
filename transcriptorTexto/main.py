import cv2
import filtrado as f

umbral = 120

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


bloque = 3 # vecino
constante = 0 


cv2.namedWindow('imagen original')
cv2.createTrackbar('bloque', 'imagen original', bloque, 100, f.actualizar_bloque)
cv2.createTrackbar('constante', 'imagen original', constante, 100, f.actualizar_constante)

while True:
    ret, frame = camara.read()
    if not ret:
        print("No es posible obtener la imagen")
        break

    frame = redimensionar_alto(frame, 800)  

    frame_umbral = f.filtrado(frame)

    cv2.imshow('imagen original', frame)
    cv2.imshow('imagen filtrada', frame_umbral)

    if cv2.waitKey(1) == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()