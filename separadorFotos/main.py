import cv2
import config
import archivos
import utiles
import pagina
import separar_fotos
import manual
import mejora
import colorear
import pintar

# ============================================================
#  PROCESADO DE FOTOS DE ÁLBUM (sin vídeo)
#
#  Entrada:  ../imgs/Albumes/Fotos   (junto a la carpeta de este código)
#  Salida:   ../Salida/fotos_Salida  (fotos definitivas, mejoradas)
#
#  TIPO_ENTRADA = 'album':
#      imagen -> página (Salida/paginas) -> fotos sin mejorar (Salida/fotos_sin_mejorar)
#             -> fotos mejoradas (Salida/fotos_Salida)
#  TIPO_ENTRADA = 'fotos_sueltas':
#      imagen -> copia sin mejorar -> mejorada (Salida/fotos_Salida)
#
#  Con MOSTRAR_VENTANAS = True se enseña lo detectado en cada imagen:
#      e = corregir a mano con el ratón     q = salir     otra tecla = continuar
#  Todos los ajustes están en config.py
# ============================================================


def procesar_album(img, nombre):
    """Una imagen con una cara de álbum -> varias fotos mejoradas.
    Devuelve False si el usuario pide salir."""
    img_pagina, rect = pagina.extraer_pagina(img)
    archivos.guardar(config.CARPETA_PAGINAS, nombre + '.png', img_pagina)

    rects, pequena, factor = separar_fotos.detectar(img_pagina)

    if config.MOSTRAR_VENTANAS:
        cv2.imshow('Fotos detectadas', utiles.redimensionar_alto(separar_fotos.dibujar(pequena, rects), 700))
        print("  %s: %d fotos detectadas  (e = corregir a mano, q = salir, otra tecla = continuar)"
              % (nombre, len(rects)))
        tecla = cv2.waitKey(0)
        if tecla == ord('q'):
            return False
        if tecla == ord('e'):
            rects = separar_fotos.ordenar(manual.editar(pequena, rects), pequena.shape[0])

    # Depuración y recortes
    depuracion = separar_fotos.dibujar(pequena, rects)
    archivos.guardar(config.CARPETA_DEPURACION, nombre + '_detecciones.jpg', depuracion)
    fotos = separar_fotos.recortar(img_pagina, separar_fotos.a_originales(rects, factor))

    if len(fotos) == 0:
        print("  %s: no se ha encontrado ninguna foto (revisa 'depuracion'; con MOSTRAR_VENTANAS puedes marcarlas a mano)" % nombre)
    else:
        print("  %s: %d fotos guardadas" % (nombre, len(fotos)))

    for i, foto in enumerate(fotos, 1):
        nombre_foto = '%s_foto_%02d' % (nombre, i)
        archivos.guardar(config.CARPETA_SIN_MEJORAR, nombre_foto + '.png', foto)
        # archivos.guardar(config.CARPETA_FOTOS_SALIDA, nombre_foto + '.jpg', mejora.mejorar_foto(foto))
        mejorada = mejora.mejorar_foto(foto)
        if config.COLOREAR:
            mejorada = colorear.colorearFoto(mejorada)
            archivos.guardar(config.CARPETA_FOTOS_SALIDA, nombre_foto + 'AUTO.jpg', mejorada)
            if config.COLOREAR_A_MANO and config.MOSTRAR_VENTANAS:
                mejoradaMano = pintar.pintar(mejorada)
                archivos.guardar(config.CARPETA_FOTOS_SALIDA, nombre_foto + 'MANO.jpg', mejoradaMano)
        
    return True


def procesar_foto_suelta(img, nombre):
    """Una foto individual -> copia sin mejorar + foto mejorada.
    Devuelve False si el usuario pide salir."""
    mejorada = mejora.mejorar_foto(img)
    archivos.guardar(config.CARPETA_SIN_MEJORAR, nombre + '.png', img)
    archivos.guardar(config.CARPETA_FOTOS_SALIDA, nombre + '.jpg', mejorada)
    print("  %s: mejorada" % nombre)

    if config.MOSTRAR_VENTANAS:
        cv2.imshow('Original', utiles.redimensionar_alto(img, 600))
        cv2.imshow('Mejorada', utiles.redimensionar_alto(mejorada, 600))
        if cv2.waitKey(0) == ord('q'):
            return False
    return True


rutas = archivos.listar_entrada()
if len(rutas) == 0:
    print(archivos.explicar_entrada_vacia())

for ruta in rutas:
    img = cv2.imread(ruta)
    if img is None:
        print("No se puede leer", ruta)
        continue

    nombre = archivos.nombre_sin_extension(ruta)
    if config.TIPO_ENTRADA == 'fotos_sueltas':
        seguir = procesar_foto_suelta(img, nombre)
    else:
        seguir = procesar_album(img, nombre)
    if not seguir:
        break

cv2.destroyAllWindows()
print("Terminado. Resultados en:", config.CARPETA_FOTOS_SALIDA)