import os

# ============================================================
#  CONFIGURACIÓN GENERAL
# ============================================================

# Qué hay en la carpeta de entrada (imgs/Albumes/Fotos):
#   'album'          -> fotos de caras de un álbum (varias fotos por imagen)
#   'fotos_sueltas'  -> fotos individuales (solo se mejoran)
TIPO_ENTRADA = 'album'

# True  = antes de separar, busca la página dentro de la imagen (si hay mesa alrededor)
# False = la imagen ya es solo la página (recortada o escaneada)
BUSCAR_PAGINA = True

# True = enseña cada imagen procesada (cualquier tecla = siguiente, q = salir)
MOSTRAR_VENTANAS = True

# ---------- Carpetas ----------
CARPETA_CODIGO = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(CARPETA_CODIGO)
CARPETA_ENTRADA = os.path.join(RAIZ, 'imgs', 'Albumes', 'Fotos')
CARPETA_SALIDA = os.path.join(RAIZ, 'Salida')
CARPETA_FOTOS_SALIDA = os.path.join(CARPETA_SALIDA, 'fotos_Salida')
CARPETA_SIN_MEJORAR = os.path.join(CARPETA_SALIDA, 'fotos_sin_mejorar')
CARPETA_PAGINAS = os.path.join(CARPETA_SALIDA, 'paginas')
CARPETA_DEPURACION = os.path.join(CARPETA_SALIDA, 'depuracion')

EXTENSIONES = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff')

ANCHO_ANALISIS = 1000

# ---------- Paso 1: encontrar la página dentro de la imagen ----------
SENSIBILIDAD_CANNY = 30
AREA_MIN_PAGINA = 0.5
AREA_MAX_PAGINA = 0.97
MARGEN_RECORTE_PAGINA = 0.015

# ---------- Paso 2: separar las fotos ----------
# Color del papel: None = se calcula solo (a partir de las rayas del papel o, si no
# hay rayas, el color más frecuente). O un color fijo (B, G, R).
COLOR_FONDO = None
MARGEN_PAGINA = 0.01          # borde de la página que se ignora
AREA_MIN_FOTO = 0.006         # fracción mínima de la página (así entran las fotos de carnet)
AREA_MAX_FOTO = 0.85          # una "foto" mayor que esto es la página entera, no una foto
LADO_MIN_FOTO = 0.08          # lado mínimo (fracción del ancho): descarta anillas y tiras
RELLENO_MIN = 0.75

# Fondo rayado (papel de álbum con rayas horizontales). Las fotos no tienen rayas,
# así que sirven para saber qué es fondo sin depender del color.
RAYAS_EY_MIN = 2.5            # contraste mínimo vertical para considerar "raya"
RAYAS_RATIO = 2.0             # cuánto más fuerte vertical que horizontal
RAYAS_MIN_FRACCION = 0.10     # si hay menos rayas que esto en la imagen, se ignoran
UMBRAL_DISTANCIA = 45         # distancia al color del papel para considerar "foto"

# Se hacen varias pasadas con distintos ajustes y se junta lo mejor de cada una.
# (usar_color, usar_rayas, difuminado, apertura, umbral de 0 a 1)
PASADAS = (
    (1, 1, 5, 0.03, 0.5),
    (1, 1, 5, 0.02, 0.6),
    (1, 1, 3, 0.03, 0.7),
    (1, 1, 7, 0.04, 0.5),
    (0, 1, 3, 0.03, 0.5),
    (0, 1, 5, 0.02, 0.5),
)

# Validación: una foto tiene un borde nítido y recto en sus cuatro lados
APOYO_MIN = 0.38
VENTANA_PASO = 0.015
PASO_MIN = 60
HOLGURA_APOYO = 0.10

# Recorte final: margen interior para no dejar restos del papel
RECORTE_BORDE = 0.02

# ---------- Paso 3: mejorar las fotos ----------
BALANCE_BLANCOS = True
QUITAR_RUIDO = True
ESTIRAR_CONTRASTE = True
ENFOCAR = True
FACTOR_ENFOQUE = 0.5

# ---------- Paso 4: colorear las fotos ----------
COLOREAR = True
COLOREAR_A_MANO = True
RUTA_HAAR = "../haarcascades/haarcascade_frontalface_default.xml"
SATURACION_MAX_BIN = 35
TINTE_FONDO = (1, 6)
PIEL_A = 13
PIEL_B = 20
PALIDEZ_MAX = 0.55

ALTO_VENTANA = 800