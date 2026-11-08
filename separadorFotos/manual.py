import cv2
import numpy as np
import utiles

# ============================================================
#  Corrección a mano con el ratón
#
#    Arrastrar con el botón izquierdo  -> añade una foto
#    Clic derecho sobre un recuadro    -> lo borra
#    r -> borra todos       Enter -> aceptar       Esc / q -> cancelar
# ============================================================

ALTO_VENTANA = 800

rects_pantalla = []      # recuadros en coordenadas de la ventana
inicio = None            # esquina donde se pulsó el botón
actual = None            # posición actual del ratón mientras se arrastra
tam_ventana = (1, 1)     # (ancho, alto) de la imagen mostrada, para no salirse de ella


def raton(evento, x, y, flags, param):
    global inicio, actual
    # El ratón puede salir de la ventana: se limita a la imagen (si no, salen
    # recuadros con coordenadas negativas y los recortes salen vacíos)
    x = min(max(x, 0), tam_ventana[0] - 1)
    y = min(max(y, 0), tam_ventana[1] - 1)
    if evento == cv2.EVENT_LBUTTONDOWN:
        inicio = (x, y)
        actual = (x, y)
    elif evento == cv2.EVENT_MOUSEMOVE and inicio is not None:
        actual = (x, y)
    elif evento == cv2.EVENT_LBUTTONUP and inicio is not None:
        x0, y0 = inicio
        inicio = None
        actual = None
        if abs(x - x0) > 15 and abs(y - y0) > 15:            # ignora clics sueltos
            rects_pantalla.append((min(x0, x), min(y0, y), abs(x - x0), abs(y - y0)))
    elif evento == cv2.EVENT_RBUTTONDOWN:
        for i in range(len(rects_pantalla) - 1, -1, -1):     # borra el recuadro pulsado
            rx, ry, rw, rh = rects_pantalla[i]
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                del rects_pantalla[i]
                break


def dibujar_editor(base):
    """Ventana con los recuadros actuales, el que se está arrastrando y las instrucciones."""
    vista = base.copy()
    for i, (x, y, ancho, alto) in enumerate(rects_pantalla, 1):
        cv2.rectangle(vista, (x, y), (x + ancho, y + alto), (0, 0, 255), 2)
        cv2.putText(vista, str(i), (x + 8, y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    if inicio is not None and actual is not None:
        cv2.rectangle(vista, inicio, actual, (0, 255, 255), 2)
    texto = 'Arrastrar: anadir | Clic dcho: borrar | r: borrar todo | Enter: aceptar | Esc: cancelar'
    cv2.rectangle(vista, (0, 0), (vista.shape[1], 30), (0, 0, 0), -1)
    cv2.putText(vista, texto, (10, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    return vista


def editar(pequena, rects):
    """Abre el editor. Devuelve los rectángulos (en coordenadas de 'pequena');
    si se cancela, devuelve los que había."""
    global inicio, actual, tam_ventana
    base = utiles.redimensionar_alto(pequena, ALTO_VENTANA)
    tam_ventana = (base.shape[1], base.shape[0])
    escala = base.shape[0] / pequena.shape[0]
    rects_pantalla.clear()
    rects_pantalla.extend([(int(x * escala), int(y * escala), int(w * escala), int(h * escala))
                           for (x, y, w, h) in rects])
    inicio = None
    actual = None

    cv2.namedWindow('Editar fotos')
    cv2.setMouseCallback('Editar fotos', raton)
    resultado = rects
    while True:
        cv2.imshow('Editar fotos', dibujar_editor(base))
        tecla = cv2.waitKey(20) & 0xFF
        if tecla in (13, 10, 32):                            # Enter o espacio
            resultado = [(int(x / escala), int(y / escala), int(w / escala), int(h / escala))
                         for (x, y, w, h) in rects_pantalla]
            break
        if tecla in (27, ord('q')):                          # Esc o q
            break
        if tecla == ord('r'):
            rects_pantalla.clear()
    cv2.destroyAllWindows()
    return resultado