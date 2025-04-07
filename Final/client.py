# client.py
import socket

HOST, PORT = "localhost", 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    while True:
        try:
            data = sock.recv(1024).decode()
        except Exception:
            break
        if not data:
            break
        print(data)
        # Si se solicita el valor de un As:
        if "Has recibido un As" in data:
            valor = input("Valor para el As (1 o 11): ").strip()
            sock.sendall(valor.encode())
        # Si se solicita acción del jugador:
        elif "Ingresa acción:" in data or "Es tu turno" in data:
            accion = input("Ingresa acción ([H]it, [S]tand, [E]xit): ").strip().upper()
            sock.sendall(accion.encode())
