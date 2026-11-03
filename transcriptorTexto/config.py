import cv2 

# ---- rutas
CARPETA_SALIDA = 'Salida'

# --- VISUAL ----
COLOR_TEXTO = (0, 255, 0)
COLOR_RECT = (0, 0, 255)
GROSOR = 1
FUENTE = cv2.FONT_HERSHEY_SIMPLEX

# ---- filtrado ----
BLOQUE = 31
CONSTANTE = 15

# ---- procesado de hoja ----
PORCENTAJE_ERROR = 0.02

# tam letra
AREA_MIN = 40
AREA_MAX = 8000
MARGEN = 20

# tam A4
ANCHO_HOJA = 595
ALTO_HOJA = 842

# ---- procesar letras ----
TAM = 32
UMBRAL_CONF = 0.45