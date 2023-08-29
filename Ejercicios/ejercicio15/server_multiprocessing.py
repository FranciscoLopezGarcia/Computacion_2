# 2 - Realizar dos versiones de un servidor de mayúsculas que atienda múltiples clientes de forma concurrente
# utilizando multiprocessing y threading utilizando sockets TCP.

# El hilo/proceso hijo debe responder con mayúsculas hasta que el cliente envíe la palabra exit. 
# En caso de exit el cliente debe administrar correctamente el cierre de la conexión y del proceso/hilo.

import socket, os
import multiprocessing
import signal

signal.signal(signal.SIGCHLD, signal.SIG_IGN)
serversocekt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocekt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = ""
port = 50002
serversocekt.bind((host, port))

serversocekt.listen(5)

def activo():
    while True:
        try:
            msg = clientsocket.recv(1024)
            print("message received : %s" % msg.decode().upper())
            if msg.decode() == "exit":
                print("closing connection with client")
                break
            clientsocket.send(msg.decode().upper().encode())
        except KeyboardInterrupt:
            break
    socket.close()

try:
    while True:
        print("waiting for connection")
        clientsocket, addr = serversocekt.accept()
        print("connected from: %s" % str(addr))
        msg = "Welcome to the server"

        p = multiprocessing.Process(target=activo, args=())
        print("starting connection")
        clientsocket.send(msg.encode('ascii'))
        p.start()

except KeyboardInterrupt:
    print("closing server, manually interrupted")
    p.join()
    serversocekt.close()
    clientsocket.close()


finally:
    print("closing server")
    p.join()
    serversocekt.close()
