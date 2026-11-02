import os
import cv2
import config

# ------------------------------------------------------------
#  Guardar y listar archivos
# -------------------------------------------------------------

def guardar(carpeta, nombre, img):
    """Guarda la imagen; la extension del nombre decide el formato (.png / .jpg).
    Si la imagen esta vacia no se guarda (cv2.imwrite daria error)."""
    if img is None or img.size == 0:
        print("  AVISO: imagen vacia, no se guarda:", nombre)
        return False
    os.makedirs(carpeta, exist_ok=True)
    return cv2.imwrite(os.path.join(carpeta, nombre), img)


def listar_entrada():
    """Rutas de las imágenes de la carpeta de entrada, ordenadas por nombre."""
    if not os.path.isdir(config.CARPETA_ENTRADA):
        return []
    nombres = sorted(os.listdir(config.CARPETA_ENTRADA))
    return [os.path.join(config.CARPETA_ENTRADA, n) for n in nombres
            if n.lower().endswith(config.EXTENSIONES)]


def nombre_sin_extension(ruta):
    return os.path.splitext(os.path.basename(ruta))[0]


def explicar_entrada_vacia():
    """Mensaje que dice por que no se ha encontrado ninguna imagen."""
    carpeta = config.CARPETA_ENTRADA
    if not os.path.isdir(carpeta):
        return "La carpeta no existe: " + carpeta
    contenido = os.listdir(carpeta)
    if len(contenido) == 0:
        return "La carpeta esta vacia: " + carpeta
    return ("La carpeta existe pero no tiene imagenes compatibles %s.\n"
            "Archivos que hay: %s" % (str(config.EXTENSIONES), ', '.join(contenido[:10])))