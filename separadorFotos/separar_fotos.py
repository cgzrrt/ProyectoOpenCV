import cv2
import numpy as np
import config
import utiles

# ------------------------------------------------------------
#  PASO 2: separar las fotos de una pagina
#
#  1. Color de fondo del album: el gris mas frecuente (histograma, P30)
#  2. Mapa de distancia: cuanto se parece cada pixel al fondo (restas, P26)
#  3. Deteccion gruesa: umbral (P32) + rellenar huecos + apertura grande
#     (erosion y dilatacion, P36/P37) -> contornos (P41) -> boundingRect (P45)
#  4. Ajuste fino de cada lado: se recorre desde el centro hacia fuera
#     hasta llegar al fondo, y se pega al borde con más contraste (Sobel, P35)
#  5. Recorte por slicing (P57)
#
# ------------------------------------------------------------


# ------------------------------------------------------------
#  1 y 2, Fondo y mapa de distancia
# ------------------------------------------------------------
def color_fondo(pagina):
    """Color (B, G, R) más frecuente de la página: el fondo del álbum."""
    if config.COLOR_FONDO is not None:
        return list(config.COLOR_FONDO)

    suave = cv2.blur(pagina, (31, 31))                   # borra el estampado del fondo
    gris = cv2.cvtColor(suave, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gris], [0], None, [256], [0, 256])
    hist = np.float32(hist).reshape(256, 1)              # mismo formato en todas las versiones
    hist = cv2.blur(hist, (1, 9))                        # suaviza el histograma
    _, _, _, pico = cv2.minMaxLoc(hist)
    valor = pico[1]                                      # gris es lo mas frecuente

    cerca = cv2.inRange(gris, max(valor - 12, 0), min(valor + 12, 255))
    return [int(v) for v in np.mean(suave[cerca > 0], axis=0)]


def mapa_distancia(pagina, fondo):
    """Imagen de 0 a 255: cuanto más clara, más se diferencia ese píxel del fondo."""
    k = max(5, int(0.012 * min(pagina.shape[:2])) | 1)
    suave = cv2.blur(pagina, (k, k))
    suma = None
    for canal, valor in zip(cv2.split(suave), fondo):
        plano = np.ones(canal.shape, np.uint8) * valor
        dif = cv2.add(cv2.subtract(canal, plano), cv2.subtract(plano, canal))
        suma = dif if suma is None else cv2.add(suma, dif)
    return suma


# ------------------------------------------------------------
#  3) Deteccion gruesa
# ------------------------------------------------------------
def deteccion_gruesa(distancia, umbral):
    """Imagen binaria con una mancha blanca por foto (o grupo de fotos pegadas)."""
    _, mascara = cv2.threshold(distancia, umbral, 255, cv2.THRESH_BINARY)

    # Se ignora el borde exterior de la pagina
    m = int(config.MARGEN_PAGINA * min(mascara.shape))
    mascara[:m, :] = 0
    mascara[-m:, :] = 0
    mascara[:, :m] = 0
    mascara[:, -m:] = 0

    # Rellenar huecos: se dibujan los contornos exteriores rellenos
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rellena = np.zeros(mascara.shape, np.uint8)
    cv2.drawContours(rellena, contornos, -1, 255, -1)

    # Apertura grande: elimina todo lo que sea mas fino que una foto
    # (franjas de mesa, tapa del álbum, bordes de páginas vecinas)
    k = max(5, int(config.APERTURA * min(mascara.shape)))
    kernel = np.ones((k, k), np.uint8)
    rellena = cv2.erode(rellena, kernel)
    return cv2.dilate(rellena, kernel)


def dividir_contorno(contorno, forma, area_pagina):
    """Si un contorno son varias fotos pegadas, erosiona hasta que se rompa
    el puente que las une y luego dilata cada parte de vuelta."""
    mancha = np.zeros(forma, np.uint8)
    cv2.drawContours(mancha, [contorno], -1, 255, -1)
    kernel = np.ones((3, 3), np.uint8)
    area_minima = 0.3 * config.AREA_MIN_FOTO * area_pagina
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
    if max(ancho, alto) / min(ancho, alto) > 8:
        return None

    relleno_min = config.RELLENO_MIN * (0.8 if es_parte else 1.0)
    if area / (ancho * alto) < relleno_min or area > config.AREA_MAX_FOTO * area_pagina:
        return None if es_parte else 'dividir'
    return (x, y, ancho, alto)


# ------------------------------------------------------------
#  4) Ajuste fino de los lados
# ------------------------------------------------------------
def ajustar_lados(distancia, rect, umbral):
    """Desde el centro, avanza hacia fuera mientras la franja central siga
    siendo 'foto' (distancia media al fondo alta). Para al llegar al fondo."""
    x, y, ancho, alto = rect
    H, W = distancia.shape
    T = umbral

    for _ in range(2):
        holgura = int(0.12 * ancho)
        columnas = np.mean(distancia[y + int(0.2 * alto):y + int(0.8 * alto), :], axis=0)
        i = j = x + ancho // 2
        while i > max(x - holgura, 1) and columnas[i - 1] > T:
            i -= 1
        while j < min(x + ancho + holgura, W - 2) and columnas[j + 1] > T:
            j += 1
        x, ancho = i, j - i + 1

        holgura = int(0.12 * alto)
        filas = np.mean(distancia[:, x + int(0.2 * ancho):x + int(0.8 * ancho)], axis=1)
        i = j = y + alto // 2
        while i > max(y - holgura, 1) and filas[i - 1] > T:
            i -= 1
        while j < min(y + alto + holgura, H - 2) and filas[j + 1] > T:
            j += 1
        y, alto = i, j - i + 1
    return (x, y, ancho, alto)


def pegar_a_bordes(gx, gy, rect):
    """Mueve cada lado hasta la línea de mayor contraste dentro de una ventana
    cercana (quita restos de tapa, funda o mesa que hayan quedado dentro)."""
    x, y, ancho, alto = rect
    f = config.VENTANA_BORDE

    def mejor(perfil):
        i = int(np.argmax(perfil))
        return i if perfil[i] > 1.5 * np.mean(perfil) else None

    vx, vy = int(f * ancho), int(f * alto)
    y0, y1 = y + int(0.2 * alto), y + int(0.8 * alto)
    x0, x1 = x + int(0.2 * ancho), x + int(0.8 * ancho)

    izq = mejor(np.mean(gx[y0:y1, x:x + vx], axis=0)) if vx > 2 else None
    der = mejor(np.mean(gx[y0:y1, x + ancho - vx:x + ancho], axis=0)) if vx > 2 else None
    sup = mejor(np.mean(gy[y:y + vy, x0:x1], axis=1)) if vy > 2 else None
    inf = mejor(np.mean(gy[y + alto - vy:y + alto, x0:x1], axis=1)) if vy > 2 else None

    nx0 = x + izq if izq is not None else x
    nx1 = (x + ancho - vx + der + 1) if der is not None else x + ancho
    ny0 = y + sup if sup is not None else y
    ny1 = (y + alto - vy + inf + 1) if inf is not None else y + alto
    return (nx0, ny0, nx1 - nx0, ny1 - ny0)


def quitar_solapados(rects):
    """Si dos rectangulos se pisan mucho (misma foto detectada dos veces), se queda el mayor."""
    rects = sorted(rects, key=lambda r: r[2] * r[3], reverse=True)
    finales = []
    for r in rects:
        repetido = False
        for f in finales:
            ancho_i = min(r[0] + r[2], f[0] + f[2]) - max(r[0], f[0])
            alto_i = min(r[1] + r[3], f[1] + f[3]) - max(r[1], f[1])
            if ancho_i > 0 and alto_i > 0 and ancho_i * alto_i > 0.5 * r[2] * r[3]:
                repetido = True
        if not repetido:
            finales.append(r)
    return finales


# ------------------------------------------------------------
#  Busqueda con un umbral concreto
# ------------------------------------------------------------
def buscar_rects(distancia, gx, gy, umbral):
    """Rectangulos (x, y, ancho, alto) de las fotos encontradas con ese umbral."""
    alto_p, ancho_p = distancia.shape
    area_pagina = alto_p * ancho_p
    gruesa = deteccion_gruesa(distancia, umbral)

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

    ajustados = []
    for r in rects:
        r = ajustar_lados(distancia, r, umbral)
        if config.AJUSTAR_A_BORDES:
            r = pegar_a_bordes(gx, gy, r)
        if r[2] * r[3] >= config.AREA_MIN_FOTO * area_pagina:
            ajustados.append(r)
    return quitar_solapados(ajustados)


def elegir_umbral(distancia, gx, gy):
    """Si UMBRAL_FONDO es un número, se usa. Si es None, se prueban varios y se
    elige el que encuentra más fotos (a igualdad, el que cubre más superficie):
    con umbral bajo las fotos se pegan entre sí y con umbral alto se fragmentan."""
    if config.UMBRAL_FONDO is not None:
        return config.UMBRAL_FONDO, buscar_rects(distancia, gx, gy, config.UMBRAL_FONDO)

    mejor = None
    for umbral in config.UMBRALES_AUTOMATICOS:
        rects = buscar_rects(distancia, gx, gy, umbral)
        superficie = sum(r[2] * r[3] for r in rects)
        puntuacion = (len(rects), superficie)
        if mejor is None or puntuacion > mejor[0]:
            mejor = (puntuacion, umbral, rects)
    return mejor[1], mejor[2]


# ------------------------------------------------------------
#  Funcion principal del módulo
# ------------------------------------------------------------
def separar(pagina):
    """Devuelve (lista de fotos recortadas, imagen de depuración).
    Se analiza una copia reducida, pero se recorta de la página original."""
    pequena, factor = utiles.reducir_ancho(pagina, config.ANCHO_ANALISIS)
    alto_p, ancho_p = pequena.shape[:2]

    fondo = color_fondo(pequena)
    distancia = mapa_distancia(pequena, fondo)
    gris = cv2.cvtColor(cv2.blur(pequena, (5, 5)), cv2.COLOR_BGR2GRAY)
    gx = cv2.convertScaleAbs(cv2.Sobel(gris, cv2.CV_64F, 1, 0, ksize=3))
    gy = cv2.convertScaleAbs(cv2.Sobel(gris, cv2.CV_64F, 0, 1, ksize=3))

    umbral, rects = elegir_umbral(distancia, gx, gy)

    # Orden de lectura: filas de arriba a abajo, en cada fila, de izquierda a derecha
    rects.sort(key=lambda r: (round(r[1] / (0.15 * alto_p)), r[0]))

    depuracion = pequena.copy()
    cv2.putText(depuracion, 'umbral %d' % umbral, (10, alto_p - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    fotos = []
    for i, (x, y, ancho, alto) in enumerate(rects, 1):
        cv2.rectangle(depuracion, (x, y), (x + ancho, y + alto), (0, 0, 255), 3)
        cv2.putText(depuracion, str(i), (x + 10, y + 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 0, 255), 3)
        xo, yo = int(x * factor), int(y * factor)           # a tamaño original
        wo, ho = int(ancho * factor), int(alto * factor)
        m = int(config.RECORTE_BORDE * min(wo, ho))
        fotos.append(pagina[yo + m:yo + ho - m, xo + m:xo + wo - m].copy())
    return fotos, depuracion