## EJERCICIO ##

# Escribir un programa que implemente un socket pasivo que gestione de forma serializada distintas conecciones entrantes.

# Debe atender nuevas conexiones de forma indefinida.

# NOTA: cuando decimos serializado decimo que atiende una conexión y recibe una nueva conección una vez que esa conexión se cerró

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("localhost", 7000))
s.listen(1)
s.settimeout(20)

try:
    while True:
        try:
            conn, addr = s.accept()
            print("New connection from: ", addr)

            while True:
                data = conn.recv(1024)
                if not data:
                    print("Connection closed")
                    break
                print("Received data: ", data)
                conn.sendall(data)
            conn.close()

        except socket.timeout:
            print("Socket timeout")
            break
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            break

except KeyboardInterrupt:
    print("Keyboard interrupt: server closed by user")

finally:
    s.close()

