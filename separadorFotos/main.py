import cv2
import config
import archivos
import utiles
import pagina
import separar_fotos
import mejora

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
#  Todos los ajustes están en config.py
# ============================================================


def procesar_album(img, nombre):
    """Una imagen con una cara de álbum -> varias fotos mejoradas."""
    img_pagina, rect = pagina.extraer_pagina(img)
    archivos.guardar(config.CARPETA_PAGINAS, nombre + '.png', img_pagina)

    fotos, depuracion = separar_fotos.separar(img_pagina)
    archivos.guardar(config.CARPETA_DEPURACION, nombre + '_detecciones.jpg', depuracion)

    if len(fotos) == 0:
        print("  %s: no se ha encontrado ninguna foto (revisa 'depuracion' y UMBRAL_FONDO)" % nombre)
    else:
        print("  %s: %d fotos encontradas" % (nombre, len(fotos)))

    for i, foto in enumerate(fotos, 1):
        nombre_foto = '%s_foto_%02d' % (nombre, i)
        archivos.guardar(config.CARPETA_SIN_MEJORAR, nombre_foto + '.png', foto)
        archivos.guardar(config.CARPETA_FOTOS_SALIDA, nombre_foto + '.jpg', mejora.mejorar_foto(foto))

    if config.MOSTRAR_VENTANAS:
        cv2.imshow('Fotos detectadas', utiles.redimensionar_alto(depuracion, 700))


def procesar_foto_suelta(img, nombre):
    """Una foto individual -> copia sin mejorar + foto mejorada."""
    mejorada = mejora.mejorar_foto(img)
    archivos.guardar(config.CARPETA_SIN_MEJORAR, nombre + '.png', img)
    archivos.guardar(config.CARPETA_FOTOS_SALIDA, nombre + '.jpg', mejorada)
    print("  %s: mejorada" % nombre)

    if config.MOSTRAR_VENTANAS:
        cv2.imshow('Original', utiles.redimensionar_alto(img, 600))
        cv2.imshow('Mejorada', utiles.redimensionar_alto(mejorada, 600))


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
        procesar_foto_suelta(img, nombre)
    else:
        procesar_album(img, nombre)

    if config.MOSTRAR_VENTANAS:
        if cv2.waitKey(0) == ord('q'):
            break

cv2.destroyAllWindows()
print("Terminado. Resultados en:", config.CARPETA_FOTOS_SALIDA)