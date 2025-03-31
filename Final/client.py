import socket

HOST, PORT = "localhost", 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print(sock.recv(1024).decode())  # Cartas iniciales
    
    while True:
        accion = input("[P]edir carta o [Q]uit? ").strip().upper()
        sock.sendall(accion.encode())
        if accion == "P":
            print(sock.recv(1024).decode())  # Nueva carta
        elif accion == "Q":
            print("Te has plantado.")
            break


        ##oiewnfoie