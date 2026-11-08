import os
import subprocess
import sys
import tkinter as tk

# ============================================================
#  LANZADOR DE PROYECTOS OPENCV
#
#  Abre una ventana pequeña donde eliges qué programa ejecutar.
#  Cada programa se ejecuta como un proceso aparte, desde su propia carpeta.
#  Así no se mezclan sus 'config.py' y 'main.py' (se llaman igual en los dos),
#  y las rutas relativas de cada uno (como 'Salida') siguen funcionando igual
#  que cuando los ejecutas por separado.
# ============================================================

RAIZ = os.path.dirname(os.path.abspath(__file__))

# (texto del boton, carpeta del proyecto)
PROGRAMAS = [
    ("Separador de fotos de álbum", "separadorFotos"),
    ("Transcriptor de texto", "transcriptorTexto"),
]

COLOR_FONDO = "#f2f2f2"


class Lanzador:
    def __init__(self, ventana):
        self.ventana = ventana
        self.proceso = None
        self.botones = []

        ventana.title("Proyectos OpenCV")
        ventana.geometry("380x290")
        ventana.resizable(False, False)
        ventana.configure(bg=COLOR_FONDO, padx=20, pady=15)

        tk.Label(ventana, text="¿Que quieres ejecutar?", bg=COLOR_FONDO,
                 font=("Segoe UI", 13, "bold")).pack(pady=(0, 12))

        for texto, carpeta in PROGRAMAS:
            boton = tk.Button(ventana, text=texto, font=("Segoe UI", 11), height=2,
                              command=lambda c=carpeta, t=texto: self.ejecutar(t, c))
            boton.pack(fill="x", pady=4)
            self.botones.append(boton)

        self.estado = tk.Label(ventana, text="", bg=COLOR_FONDO, fg="#444444",
                               font=("Segoe UI", 9), wraplength=340, justify="center")
        self.estado.pack(pady=(10, 4))

        tk.Button(ventana, text="Salir", width=10, command=self.salir).pack(pady=(4, 0))
        ventana.protocol("WM_DELETE_WINDOW", self.salir)

    def ejecutar(self, texto, carpeta):
        """Lanza el main.py de la carpeta elegida."""
        ruta_carpeta = os.path.join(RAIZ, carpeta)
        ruta_main = os.path.join(ruta_carpeta, "main.py")
        if not os.path.isfile(ruta_main):
            self.estado.config(text="No se encuentra:\n" + ruta_main, fg="#b00020")
            return

        # sys.executable = el mismo Python (y entorno virtual) que ha abierto esta ventana
        self.proceso = subprocess.Popen([sys.executable, ruta_main], cwd=ruta_carpeta)
        self.nombre = texto
        self.bloquear(True)
        self.estado.config(text="Ejecutando: %s\n(cuando termine, volveras aqui)" % texto,
                           fg="#444444")
        self.vigilar()

    def vigilar(self):
        """Comprueba cada medio segundo si el programa lanzado ya ha terminado"""
        codigo = self.proceso.poll()
        if codigo is None:
            self.ventana.after(500, self.vigilar)
            return
        self.proceso = None
        self.bloquear(False)
        if codigo == 0:
            self.estado.config(text="%s: terminado." % self.nombre, fg="#2e7d32")
        else:
            self.estado.config(
                text="%s termino con un error (código %d).\nMira el mensaje en la terminal"
                     % (self.nombre, codigo), fg="#b00020")

    def bloquear(self, bloqueado):
        """Desactiva los botones mientras hay un programa en marcha."""
        for boton in self.botones:
            boton.config(state="disabled" if bloqueado else "normal")

    def salir(self):
        if self.proceso is not None and self.proceso.poll() is None:
            self.proceso.terminate()          # cierra tambien el programa lanzado
        self.ventana.destroy()


if __name__ == "__main__":
    ventana = tk.Tk()
    Lanzador(ventana)
    ventana.mainloop()