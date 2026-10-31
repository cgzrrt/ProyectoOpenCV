import cv2

#Cámara del móvil
# poner tu propia IP
camara = cv2.VideoCapture('')

if not camara.isOpened():
    print("No es posible abrir la cámara")
    exit()


def redimensionar_alto(imagen, alto_deseado=400):
    alto, ancho = imagen.shape[:2]
    factor = alto_deseado / alto
    ancho_nuevo = int(ancho * factor)
    return cv2.resize(imagen, (ancho_nuevo, alto_deseado), interpolation=cv2.INTER_AREA)

bloque = 3 #vecindario
constante = 0 #ajusta el umbral local calculado

#Si es mayor, reduce el umbral local; si es menor, lo aumenta.
def actualizar_bloque(blq):
    global bloque
    bloque = blq
    
    if bloque < 3 : bloque = 3
    elif bloque%2 == 0 : bloque += 1
    
    img_umbral = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,bloque,constante)
    #ADAPTIVE_THRESH_MEAN_C::
    cv2.imshow('Imagen filtrada', img_umbral)

def actualizar_constante (cte): #Ajusta el umbral calculado
    global constante
    constante = cte
    # img_umbral = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,bloque,constante)
    # cv2.imshow('Imagen filtrada', img_umbral)

cv2.namedWindow('imagen original')
cv2.createTrackbar('bloque', 'imagen original', bloque, 500, actualizar_bloque)
cv2.createTrackbar('constante', 'imagen original', constante, 500, actualizar_constante)

while True:
    ret, frame = camara.read()
    if not ret:
        print("No es posible obtener la imagen")
        break

    img = redimensionar_alto(frame, 800)
    img_gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    

    bloque_valido = max(3, bloque)
    if bloque_valido % 2 == 0:
        bloque_valido += 1

    
    img_umbral = cv2.adaptiveThreshold(img_gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, bloque_valido, constante)

    cv2.imshow('imagen original', img)
    cv2.imshow('imagen filtrada', img_umbral)

    if cv2.waitKey(1) == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()