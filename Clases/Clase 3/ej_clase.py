# import os

# print('SOY EL PADRE (PID: %d)' % os.getpid())
# print('------------------------------------')

# #Error al crear el proceso hijo
# try:
#     ret = os.fork()
# except OSError:
#     print('Error al crear el proceso hijo')
    
# #Proceso padre
# ret = os.fork()

# if ret > 0:
#     print('Soy el padre (PID: %d)' % os.getpid())

# elif ret == 0:
#     print('Soy el hijo (PID: %d)' % (os.getpid(), os.getppid()))


# import os
# import sys
# import time

# print('SOY EL PADRE (PID: %d)' % os.getpid())
# print('------------------------------------')

# ret = os.fork()

# for i in range(10):
#     if ret > 0 :
#         print('Soy el padre (PID: %d)' % os.getpid())

#     elif ret == 0:
#         print('Soy el hijo (PID: %d)' % (os.getpid(), os.getppid()))

#     time.sleep(1)
#     print()

# print(os.wait())

# import os
# import sys
# import time

# def main():
#     fd = open ('archivo.txt', 'w+')

#     pid = os.fork()

#     if (pid): #Este es el proceso padre
#         print('PADRE (PID: %d)' % os.getpid())
#         fd.seek(0) #Posiciona el puntero al inicio del archivo, lo q tiene q leer
#         print (fd.read())

#     else: #Este es el proceso hijo
#         print('HIJO (PID: %d)' % os.getpid())
#         fd.write('Esto es una linea del proceso hijo')
#         fd.flush() #Fuerza a escribir lo q hay en el write, no hay q esperar
#         time.sleep(1) #El hijo escriba antes de q el padre lea 
#         sys.exit(0)

#         #time.sleep(60)

# if __name__ == '__main__':
#     main()


# import os
# import sys
# import time

# def main():
#     var = 100
#     print('PADRE: Soy el proceso padre y mi pid es: %d' % os.getpid())

#     pid = os.fork()

#     for i in range(10):
#         if (pid): #Padre
#             var += 1
#             print('PADRE: var = %d ---%d' % (var, id(var)))
#             time.sleep(1)

#         else: #Hijo
#             var -= 1
#             print('HIJO: var = %d ---%d' % (var, id(var)))
#             time.sleep(1)

# if __name__ == '__main__':
#     main()



import os
import sys
import time

print('Soy el PADRE (PID: %d)' % os.getpid())
print('------------------------------------')

ret = os.fork()

if ret > 8:
    print('Soy el padre (PID: %d)' % os.getpid())
    #Cuando bash ejecuta algo como este programa, se queda esperando el exit del hijo
    ret = os.wait() #Si no se pone el wait, el padre termina antes q el hijo y el hijo queda como zombie
    print(ret)
    print('Fin del padre')

elif ret == 0:
    print('Soy el hijo (PID: %d)' % (os.getpid(), os.getppid()))
    
    time.sleep(2)
    os.execlp('python3', 'python3', './hijo.py')

    print('Da igual lo que se ejecute, porque exec modifica el binario actual')