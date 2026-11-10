# Escáner multiusos

Programa que permite escanear texto y fotos.

## Ejecución principal
```
carpeta raiz
python3 -m main
```
En la interfaz desplegada se elige el modo a ejecutar o si se quiere salir, una vez seleccionado el modo se espera un poco y este se ejecutará, si se quiere finalizar el modo de ejecución con pulsar la `q` se vuelve al menú de selección.

## Escáner de fotos

El escáner de fotos permite separar, digitalizar y mejorar las fotos de un álbum, su funcionamiento es el siguiente: 

Ejecución individual:
```
cd separadorFotos
python3 -m main
```

Para escanear una página se deben subir las fotos a la carpeta imgs y ejecutar, para modificar, en caso de error, la detección de imágenes pulsar `e` y con el click izquierdo añades zonas de recorte, y con el click derecho las eliminar, después pulsas `Enter` para confirmar los cambios.

## Escáner de texto

El escáner de texto permite identificar texto escrito, su funcionamiento es el siguiente:

Ejecución individual:
```
cd transcriptorTexto
python3 -m main
```

Para escanear una hoja se debe pulsar `Espacio`. Para re-escanearla `R` y para transcribir el texto `T`.

Una vez se ha escaneado la hoja se pueden ajustar los bordes de las letras con dos _thresholds_ para intentar que cuadren mejor.

Es necesario modificar el método de conexión pues está puesto un dispositivo móvil por IP.

### Limitaciones

Este proyecto cuenta con algunas limitaciones:

#### TEXTO:
- Algunos caracteres no se leen. Con el uso de `matchTemplate` se comparan las letras con una plantilla definida de letras mayúsculas. A veces esta comparación falla.
- Funciona mejor con texto escrito por máquina, pero la letra 'O' es normalmente confundida con una 'D'.

#### FOTOS:
- Si las fotos estan solapadas tiende a "encontrar" fotos de más.
- Si no hay una distinción clara con el fondo del album es posible que confunda parte del fondo con la foto o viceversa.
- Es posible que detecte incorrectamente fotos en blanco y negro o sepia en caso de tener mucha variación de color.
