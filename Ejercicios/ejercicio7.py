# Memoria Compartida

# Etapa 1
# Escribir un programa que reciba por argumento la opción -f acompañada de un path_file

# El programa deberá crear un segmento de memoria compartida y generar dos hijos H1 y H2.

# H1 deberá leer desde sdtin lo que ingrese el usuario, línea por línea, enviando una señal USR1 al padre en cada línea leida.

# Una vez ingresada una línea, el proceso padre leerá la memoria compartida y mostrará la línea leida por pantalla y enviará una señal USR1 a H2.

# Al recibir la señal USR1, H2 leerá la línea desde la memoria compartida y la escribirá en mayúsculas en el archivo recibido como argumento.

# Etapa 2
# Cuando el usuario introduzca "bye" en la terminal, H1 enviará al padre la señal USR2 y terminará.

# Al recibir la señal USR2, el padre, la enviará a H2 que también terminará.

# El padre esperará a ambos hijos y terminará también.
