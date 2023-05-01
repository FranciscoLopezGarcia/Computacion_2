import os
import sys
import argparse
from multiprocessing import Process, Pipe

def invertir_linea(linea):
    return linea[::-1]

def proceso_hijo(pipe_hijo, linea):
    pipe_hijo.send(invertir_linea(linea))
    pipe_hijo.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Archivo de texto', required=True)
    args = parser.parse_args()

    try:
        args = parser.parse_args()
    except:
        sys.stderr.write("Error: Argumentos invalidos\n")
        sys.exit(1)

    try:
        with open(args.file, 'r') as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        sys.stderr.write(f"Error: Archivo {args.file} no encontrado\n")
        sys.exit(1)

    pipes = []
    procesos = []

    for linea in lineas:
        padre_conn, hijo_conn = Pipe()
        proceso = Process(target=proceso_hijo, args=(hijo_conn, linea.strip()))
        proceso.start()

        pipes.append(padre_conn)
        procesos.append(proceso)

    for pipe in pipes:
        print(pipe.recv())

    for proceso in procesos:
        proceso.join()

if __name__ == "__main__":
    main()

