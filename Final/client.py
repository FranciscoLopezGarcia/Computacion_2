import socket

HOST, PORT = "localhost", 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    while True:
        data = sock.recv(1024).decode()
        if not data:
            break
        print(data)
        # Si se solicita asignar valor a un As:
        if "Has recibido un As" in data:
            valor = input("Valor para el As (1 o 11): ").strip()
            sock.sendall(valor.encode())
        # Si es el turno (se muestran las opciones):
        elif "Es tu turno" in data or "Elige:" in data:
            accion = input("Ingresa tu acción ([H]it, [S]tand, [E]xit): ").strip().upper()
            sock.sendall(accion.encode())
