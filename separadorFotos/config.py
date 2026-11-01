import os

# ============================================================
#  CONFIGURACIÓN GENERAL
# ============================================================

# Que hay en la carpeta de entrada (imgs/Albumes/Fotos):
#   'album'          -> fotos de caras de un album (varias fotos por imagen)
#   'fotos_sueltas'  -> fotos individuales (solo se mejoran)
TIPO_ENTRADA = 'album'

# True  = antes de separar, busca la pagina dentro de la imagen (si hay mesa alrededor)
# False = la imagen ya es solo la pagina (recortada o escaneada)
BUSCAR_PAGINA = True

# True = enseña cada imagen procesada (cualquier tecla = siguiente, q = salir)
MOSTRAR_VENTANAS = True

# ---------- Carpetas ----------
# CARPETA_CODIGO = donde estan main.py y config.py  (ProyectoOpenCV/separadorFotos)
# RAIZ           = carpeta del proyecto, un nivel por encima (ProyectoOpenCV)
CARPETA_CODIGO = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(CARPETA_CODIGO)

# Entrada:  ProyectoOpenCV/imgs/Albumes/Fotos
CARPETA_ENTRADA = os.path.join(RAIZ, 'imgs', 'Albumes', 'Fotos')

# Salida:   ProyectoOpenCV/Salida/...
CARPETA_SALIDA = os.path.join(RAIZ, 'Salida')
CARPETA_FOTOS_SALIDA = os.path.join(CARPETA_SALIDA, 'fotos_Salida')            # fotos definitivas (mejoradas)
CARPETA_SIN_MEJORAR = os.path.join(CARPETA_SALIDA, 'fotos_sin_mejorar')        # recortes sin mejorar
CARPETA_PAGINAS = os.path.join(CARPETA_SALIDA, 'paginas')                      # paginas recortadas
CARPETA_DEPURACION = os.path.join(CARPETA_SALIDA, 'depuracion')                # recuadros detectados

EXTENSIONES = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tif', '.tiff')

# Las imagenes grandes se analizan en una copia reducida a este ancho (mas rapido);
# los recortes se hacen siempre sobre la imagen original.
ANCHO_ANALISIS = 1000

# ---------- Paso 1: encontrar la pagina dentro de la imagen ----------
SENSIBILIDAD_CANNY = 30    # umbral de Canny; si no encuentra la pagina, probar 20 o 15
AREA_MIN_PAGINA = 0.5      # la pagina ocupa al menos el 50 % de la imagen
AREA_MAX_PAGINA = 0.97     # ...y no es la imagen entera (si lo es, no hace falta recortar)
MARGEN_RECORTE_PAGINA = 0.015   # se recorta un 1,5 % por dentro para no guardar mesa

# ---------- Paso 2: separar las fotos ----------
COLOR_FONDO = None         # None = automatico (color mas frecuente); o (B, G, R) a mano
UMBRAL_FONDO = None        # None = automatico; o un número (0-255): distancia al fondo para ser "foto"
UMBRALES_AUTOMATICOS = (30, 40, 50, 60, 70, 80, 100)   # los que se prueban en modo automatico
MARGEN_PAGINA = 0.015      # se ignora el 1,5 % exterior de la pagina
APERTURA = 0.05            # tamaño minimo de una foto (fracción de la pagina); quita franjas finas
AREA_MIN_FOTO = 0.02       # una foto ocupa al menos el 2 % de la pagina
AREA_MAX_FOTO = 0.90
RELLENO_MIN = 0.75         # area del contorno / area de su rectángulo
AJUSTAR_A_BORDES = True    # pega cada lado a la linea de mas contraste cercana
VENTANA_BORDE = 0.15       # hasta qué distancia (fraccion del tamaño) busca ese borde
RECORTE_BORDE = 0.02       # se recorta un 2 % por dentro de cada foto

# ---------- Paso 3: mejorar las fotos ----------
BALANCE_BLANCOS = True
QUITAR_RUIDO = True
ESTIRAR_CONTRASTE = True
ENFOCAR = True
FACTOR_ENFOQUE = 0.5       # 0 = sin enfoque