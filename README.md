# Escáner multiusos

Programa que permite escanear texto y fotos.

## Escáner de fotos

## Escáner de texto

El escáner de texto permite identificar texto escrito, su funcionamiento es el siguiente:

```
cd transcriptorTexto
python3 -m main
```

Para escanear una hoja se debe pulsar `Espacio`. Para re-escanearla `R` y para transcribir el texto `T`.

Una vez se ha escaneado la hoja se pueden ajustar los bordes de las letras con dos _thresholds_ para intentar que cuadren mejor.

### Limitaciones

Este proyecto cuenta con algunas limitaciones:

- Algunos caracteres no se leen. Con el uso de `matchTemplate` se comparan las letras con una plantilla definida de letras mayúsculas. A veces esta comparación falla.
- Funciona mejor con texto escrito por máquina, pero la letra 'O' es normalmente confundida con una 'D'.
