# Escribir un programa que reciba un mensaje desde otro proceso usando fifo (pipes con nombre).
# El proceso receptor deberá lanzar tantos hilos como líneas tenga el mensaje y deberá enviar cada línea a los hilos secundarios.
# Cada hilo secundario deberá calcular la cantidad de caracteres de su línea y COMPROBAR la cuenta de la línea anterior.