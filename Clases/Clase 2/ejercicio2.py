#Ejercicio 2:#
#Escribir un programa en Python que acepte dos argumentos de linea de comando: una cadena de texto, un numero entero.
#El programa debe imprimir una repeticion de la cadena de texto tantas veces como el numero entero

#PYTHON NORMAL#
# def main_cadena():
#     cadena = input("Ingrese una cadena de texto: ")
#     n = int(input("Ingrese un número entero: "))
#     for i in range(n):
#         print(cadena)


# #BAJO NIVEL#
import argparse

parser = argparse.ArgumentParser(description='Repite el texto n veces')
parser.add_argument('cadena', type=str, help='Cadena de texto a repetir')
parser.add_argument('n', type=int, help='Cantidad de veces que se repite la cadena')
args = parser.parse_args()
cadena = args.cadena
n = args.n
resultado = cadena * n
print(resultado)
