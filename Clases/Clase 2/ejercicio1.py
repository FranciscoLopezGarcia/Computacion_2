#Ejercicio 1:#
#Escribir un programa en Python que acepte un numero de argumento entero positivo n y
#genere una lista de los n primeros numero impares.
#El programa debe imprimir la lista resultante en la salida estandar.

#PYTHON NORMAL#
def main_impar(n):
    impar = []
    i = 1
    while len(impar) < n:
        if i % 2 != 0:
            impar.append(i)
        i += 1
    return impar
n = int(input("Ingrese un número entero positivo: "))
nmr_impar = main_impar(n)
print("Los primeros", n, "números impares son:", nmr_impar)


#BAJO NIVEL#
import argparse

parser = argparse.ArgumentParser(description='Genera una lista de los n primeros números impares')
parser.add_argument('n', type=int, help='Cantidad de impares a generar')
args = parser.parse_args()
impares = []
i = 1
while len(impares) < args.n:
    if i % 2 != 0:
        impares.append(i)
    i += 1
print(impares)