# Ejercicios

# 1 - Escribir un programa que genere dos hilos utilizando threading.
# Uno de los hilos debera leer desde stdin el texto ingresado por el usuario y deberá escribirlo en una cola de mensajes (queue).
# El segundo hilo deberá leer desde la queue el contenido y encriptará dicho texto utilizando el algoritmo ROT13 y lo almacenará en una cola de mensajes (queue).
# El primer hilo deberá leer dicho mensaje de la cola y lo mostrará por pantalla.

# ROT13

# A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
# N O P Q R S T U V W X Y Z A B C D E F G H I J K L M

# gato (claro)->(rot13) tngb

# 2 - Analizar el comportamiento de el programa queue0.py y explicarlo. Usar Queue.join(), Thead.join(). Ejecutar el hilo deamon=True y deamon=False.