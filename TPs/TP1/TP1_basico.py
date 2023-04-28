import os
import sys
import argparse


##Devuleve la linea invertida
def invertir_linea(linea):
    return linea[::-1]

def proceso_hijo(pipe_hijo, linea):
    #Cierra la lectura en el hijo
    os.close(pipe_hijo[0])
    os.write(pipe_hijo[1], invertir_linea(linea).encode())
    #CIerra la escritura en el hijo
    os.close(pipe_hijo[1])
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Archivo de texto', required=True)
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        sys.stderr.write(f"Error: Archivo {args.file} no encontrado\n")
        sys.exit(1)

    pipes = []
    pids = []

    for linea in lineas:
        pipe_padre, pipe_hijo = os.pipe()
        pid = os.fork()

        if pid == 0:  
            proceso_hijo((pipe_padre, pipe_hijo), linea.strip())
        else:
            #Cierra la escritura en el padre
            os.close(pipe_hijo)
            pipes.append(pipe_padre)
            pids.append(pid)

    for pipe in pipes:
        print(os.read(pipe, 1024).decode().strip())

    for pid in pids:
        os.waitpid(pid, 0)

if __name__ == "__main__":
    main()
