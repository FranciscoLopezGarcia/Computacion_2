# 2 - Realizar dos versiones de un servidor de mayúsculas que atienda múltiples clientes de forma concurrente
# utilizando multiprocessing y threading utilizando sockets TCP.

# El hilo/proceso hijo debe responder con mayúsculas hasta que el cliente envíe la palabra exit. 
# En caso de exit el cliente debe administrar correctamente el cierre de la conexión y del proceso/hilo.

import socket, os
import threading
import signal

signal.signal(signal.SIGCHLD, signal.SIG_IGN)
serversocekt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocekt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = "localhost"
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
                clientsocket.close()
                break
            clientsocket.send(msg.encode("utf-8"))
        except KeyboardInterrupt:
            break
    
try:
    while True:
        print("waiting for connection \n", serversocekt)
        clientsocket, addr = serversocekt.accept()
        print("connected from: %s" % str(addr))
        msg = "Welcome to the server"

        t = threading.Thread(target=activo, args=())
        print("starting connection")
        clientsocket.send(msg.encode('ascii'))
        t.start()

except KeyboardInterrupt:
    print("closing server, manually interrupted")
    t.join()
    serversocekt.close()
    clientsocket.close()

finally:
    print("closing server")
    t.join()
    serversocekt.close()