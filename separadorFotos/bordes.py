import cv2
import numpy as np
import config

# ============================================================
#  Validación de un rectángulo: ¿tiene un borde nítido y recto en los 4 lados?
#  Se compara el color medio de una ventana a cada lado de la línea (restas, P26).
#  Una foto cumple en sus cuatro lados; un trozo de marco o de fondo, no.
# ============================================================


def preparar(img):
    """Mapas de 'salto de color' en horizontal y en vertical."""
    s = max(5, int(config.VENTANA_PASO * min(img.shape[:2])))
    suave = cv2.blur(img, (3, 3))
    bx = cv2.blur(suave, (s, 1)).astype(np.int16)
    by = cv2.blur(suave, (1, s)).astype(np.int16)
    paso_x = np.abs(bx[:, s:] - bx[:, :-s]).sum(axis=2)
    paso_y = np.abs(by[s:, :] - by[:-s, :]).sum(axis=2)
    return paso_x, paso_y, s


def apoyo(pasos, rect):
    """Devuelve de 0 a 1 el apoyo del lado más débil del rectángulo."""
    paso_x, paso_y, s = pasos
    x, y, ancho, alto = rect
    alto_img, ancho_img = paso_x.shape[0], paso_y.shape[1]
    if ancho < 10 or alto < 10 or x < 0 or y < 0:
        return 0.0                                        # rectángulo inválido
    cerca = int(0.025 * min(alto_img, ancho_img))     # un lado pegado al borde de la imagen
                                                      # no se puede comprobar: se da por bueno
    dx, dy = int(config.HOLGURA_APOYO * ancho), int(config.HOLGURA_APOYO * alto)
    filas = slice(max(y + int(0.15 * alto), 0), y + int(0.85 * alto))
    columnas = slice(max(x + int(0.15 * ancho), 0), x + int(0.85 * ancho))

    valores = []
    for xb in (x, x + ancho):                                 # lados verticales
        if xb <= cerca or xb >= ancho_img - cerca:
            valores.append(1.0)
            continue
        a, b = max(xb - dx - s // 2, 0), min(xb + dx - s // 2 + 1, paso_x.shape[1])
        if b <= a:
            return 0.0
        if paso_x[filas, a:b].size == 0:
            return 0.0
        fuerza = np.max(paso_x[filas, a:b], axis=1)
        valores.append(float(np.mean(fuerza > config.PASO_MIN)))
    for yb in (y, y + alto):                                  # lados horizontales
        if yb <= cerca or yb >= alto_img - cerca:
            valores.append(1.0)
            continue
        a, b = max(yb - dy - s // 2, 0), min(yb + dy - s // 2 + 1, paso_y.shape[0])
        if b <= a:
            return 0.0
        if paso_y[a:b, columnas].size == 0:
            return 0.0
        fuerza = np.max(paso_y[a:b, columnas], axis=0)
        valores.append(float(np.mean(fuerza > config.PASO_MIN)))
    return min(valores)