import cv2
import numpy as np
import config
import utiles
import fondo
import bordes

# ============================================================
#  PASO 2: separar las fotos de una página
#
#  1) Mapas de fondo (fondo.py): distancia al color del papel + rayas del papel.
#  2) VARIAS PASADAS con distintos difuminados, aperturas y umbrales. En cada una:
#     umbral (P32) + rellenar huecos + apertura grande (erosión y dilatación,
#     P36/P37) -> contornos (P41) -> boundingRect (P45). Si varias fotos están
#     pegadas se separan por erosión (P37).
#  3) Se juntan los rectángulos de todas las pasadas y se puntúa cada uno por el
#     'apoyo' de sus bordes (bordes.py): una foto tiene borde nítido y recto en los
#     cuatro lados; la mesa, las anillas o las franjas, no.
#  4) Selección: se descarta lo que no tiene apoyo o tamaño razonable, se quitan los
#     bloques que son varias fotos fusionadas (si dentro caben 2 o más candidatas
#     más pequeñas) y los duplicados. Recorte por slicing (P57).
#
#  NOTA: con boundingRect una foto girada conserva pequeñas esquinas de fondo.
# ============================================================


# ------------------------------------------------------------
#  Detección gruesa
# ------------------------------------------------------------
def deteccion_gruesa(mapa, umbral, apertura):
    """Imagen binaria con una mancha blanca por foto (o grupo de fotos pegadas)."""
    _, mascara = cv2.threshold(mapa, umbral, 255, cv2.THRESH_BINARY)

    # Se ignora el borde exterior de la página
    m = int(config.MARGEN_PAGINA * min(mascara.shape))
    mascara[:m, :] = 0
    mascara[-m:, :] = 0
    mascara[:, :m] = 0
    mascara[:, -m:] = 0

    # Rellenar huecos: se dibujan los contornos exteriores rellenos
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rellena = np.zeros(mascara.shape, np.uint8)
    cv2.drawContours(rellena, contornos, -1, 255, -1)

    # Apertura grande: elimina todo lo que sea más fino que una foto
    k = max(5, int(apertura * min(mascara.shape)))
    kernel = np.ones((k, k), np.uint8)
    rellena = cv2.erode(rellena, kernel)
    return cv2.dilate(rellena, kernel)


def dividir_contorno(contorno, forma, area_pagina):
    """Si un contorno son varias fotos pegadas, erosiona hasta que se rompa
    el puente que las une y luego dilata cada parte de vuelta."""
    mancha = np.zeros(forma, np.uint8)
    cv2.drawContours(mancha, [contorno], -1, 255, -1)
    kernel = np.ones((3, 3), np.uint8)
    area_minima = 0.003 * area_pagina        # trozos más pequeños que esto se ignoran
    erosionada = mancha.copy()

    for n in range(1, 60):
        erosionada = cv2.erode(erosionada, kernel)
        partes, _ = cv2.findContours(erosionada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        partes = [p for p in partes if cv2.contourArea(p) > area_minima]
        if not partes:
            break
        if len(partes) >= 2:
            resultado = []
            for parte in partes:
                mascara_parte = np.zeros(forma, np.uint8)
                cv2.drawContours(mascara_parte, [parte], -1, 255, -1)
                mascara_parte = cv2.dilate(mascara_parte, kernel, iterations=n)
                mascara_parte = cv2.bitwise_and(mascara_parte, mancha)
                c, _ = cv2.findContours(mascara_parte, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                resultado.append(max(c, key=cv2.contourArea))
            return resultado
    return [contorno]


def evaluar_contorno(contorno, area_pagina, es_parte=False):
    """Devuelve (x, y, ancho, alto) si parece una foto, 'dividir' si parecen
    varias fotos unidas, o None si se descarta.
    Las partes que ya salen de una división se aceptan con un filtro más permisivo."""
    area = cv2.contourArea(contorno)
    if area < config.AREA_MIN_FOTO * area_pagina:
        return None
    x, y, ancho, alto = cv2.boundingRect(contorno)
    if ancho == 0 or alto == 0 or max(ancho, alto) / min(ancho, alto) > 8:
        return None

    relleno_min = config.RELLENO_MIN * (0.8 if es_parte else 1.0)
    if area / (ancho * alto) < relleno_min or area > config.AREA_MAX_FOTO * area_pagina:
        return None if es_parte else 'dividir'
    return (x, y, ancho, alto)


def buscar_rects(mapa, umbral, apertura):
    """Rectángulos (x, y, ancho, alto) que salen de una pasada concreta."""
    alto_p, ancho_p = mapa.shape
    area_pagina = alto_p * ancho_p
    gruesa = deteccion_gruesa(mapa, umbral, apertura)

    contornos, _ = cv2.findContours(gruesa, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for contorno in contornos:
        resultado = evaluar_contorno(contorno, area_pagina)
        if resultado == 'dividir':
            for parte in dividir_contorno(contorno, gruesa.shape, area_pagina):
                r = evaluar_contorno(parte, area_pagina, es_parte=True)
                if r is not None:
                    rects.append(r)
        elif resultado is not None:
            rects.append(resultado)
    return rects


# ------------------------------------------------------------
#  Selección de los mejores rectángulos
# ------------------------------------------------------------
def interseccion(a, b):
    """Área común de dos rectángulos (x, y, ancho, alto)."""
    ancho = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    alto = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return max(ancho, 0) * max(alto, 0)


def es_fusion(r, candidatos):
    """True si 'r' contiene 2 o más candidatos distintos y claramente más pequeños:
    entonces r es un bloque de varias fotos pegadas, no una foto."""
    dentro = []
    for q in candidatos:
        area_q = q[2] * q[3]
        if q == r or not (0.2 * r[2] * r[3] <= area_q <= 0.65 * r[2] * r[3]):
            continue
        if interseccion(q, r) < 0.85 * area_q:
            continue
        if all(interseccion(q, p) < 0.3 * min(area_q, p[2] * p[3]) for p in dentro):
            dentro.append(q)
    return len(dentro) >= 2


def seleccionar(candidatos, ancho, alto):
    """candidatos = [(rectángulo, apoyo)]. Devuelve los rectángulos elegidos."""
    area_pagina = ancho * alto
    validos = []
    for r, apoyo in candidatos:
        lado_menor, lado_mayor = min(r[2], r[3]), max(r[2], r[3])
        if apoyo < config.APOYO_MIN:
            continue
        if lado_menor < config.LADO_MIN_FOTO * ancho or lado_mayor / lado_menor > 4:
            continue
        if r[2] * r[3] > config.AREA_MAX_FOTO * area_pagina:
            continue
        validos.append((r, apoyo))

    rects = [r for r, _ in validos]
    validos = [(r, a) for r, a in validos if not es_fusion(r, rects)]

    # Primero los de mejor apoyo (agrupado de 0.1 en 0.1) y, a igualdad, los mayores
    validos.sort(key=lambda t: (round(t[1] / 0.1), t[0][2] * t[0][3]), reverse=True)
    elegidos = []
    for r, _ in validos:
        area_r = r[2] * r[3]
        if all(interseccion(r, e) < 0.3 * min(area_r, e[2] * e[3]) for e in elegidos):
            elegidos.append(r)
    return elegidos


def quitar_solapados(rects):
    """Si dos rectángulos se pisan mucho (misma foto detectada dos veces), se queda el mayor."""
    rects = sorted(rects, key=lambda r: r[2] * r[3], reverse=True)
    finales = []
    for r in rects:
        repetido = False
        for f in finales:
            if interseccion(r, f) > 0.5 * r[2] * r[3]:
                repetido = True
        if not repetido:
            finales.append(r)
    return finales


def analizar(img):
    """Busca fotos en 'img' con todas las pasadas de config.PASADAS y devuelve
    la lista de rectángulos elegidos."""
    pasos = bordes.preparar(img)
    a, b, hay_rayas = fondo.preparar_mapas(img)

    candidatos = []
    for usar_color, usar_rayas, difuminado, apertura, umbral in config.PASADAS:
        if not hay_rayas and not (usar_color and usar_rayas):
            continue                       # sin rayas todas las pasadas serían iguales
        mapa = fondo.combinar(a, b, hay_rayas, usar_color, usar_rayas, difuminado)
        for r in buscar_rects(mapa, int(umbral * 255), apertura):
            candidatos.append((r, bordes.apoyo(pasos, r)))
    return seleccionar(candidatos, img.shape[1], img.shape[0])


# ------------------------------------------------------------
#  Función principal del módulo
# ------------------------------------------------------------
def detectar(pagina):
    """Devuelve (rectángulos en la página reducida, página reducida, factor de escala)."""
    pequena, factor = utiles.reducir_ancho(pagina, config.ANCHO_ANALISIS)
    rects = analizar(pequena)
    return ordenar(rects, pequena.shape[0]), pequena, factor


def ordenar(rects, alto):
    """Orden de lectura: filas de arriba a abajo; en cada fila, de izquierda a derecha."""
    return sorted(rects, key=lambda r: (round(r[1] / (0.15 * alto)), r[0]))


def a_originales(rects, factor):
    """Pasa rectángulos de la página reducida a la página original."""
    return [(int(x * factor), int(y * factor), int(w * factor), int(h * factor))
            for (x, y, w, h) in rects]


def recortar(pagina, rects):
    """Recorta cada rectángulo (con un pequeño margen interior) sin salirse de la imagen.
    Los rectángulos inválidos (vacíos o fuera de la página) se ignoran: antes producían
    recortes vacíos y cv2.imwrite fallaba."""
    alto_img, ancho_img = pagina.shape[:2]
    fotos = []
    for (x, y, ancho, alto) in rects:
        m = int(config.RECORTE_BORDE * min(ancho, alto))
        x0, y0 = max(x + m, 0), max(y + m, 0)
        x1, y1 = min(x + ancho - m, ancho_img), min(y + alto - m, alto_img)
        if x1 - x0 < 10 or y1 - y0 < 10:
            continue
        fotos.append(pagina[y0:y1, x0:x1].copy())
    return fotos


def dibujar(pequena, rects):
    """Imagen de depuración con los recuadros numerados."""
    imagen = pequena.copy()
    for i, (x, y, ancho, alto) in enumerate(rects, 1):
        cv2.rectangle(imagen, (x, y), (x + ancho, y + alto), (0, 0, 255), 3)
        cv2.putText(imagen, str(i), (x + 10, y + 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 0, 255), 3)
    return imagen
