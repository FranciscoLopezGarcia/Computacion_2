import socket

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 9999))
        print("Conectado al servidor.\n")

        while True:
            data = sock.recv(4096).decode()
            if not data:
                break
            print(data, end='')

            if "¿Querés que valga 1 u 11?" in data or "Tu eleccion (H/S):" in data or "Elegí solo 1 o 11" in data:
                user_input = input()
                sock.sendall(user_input.encode())

if __name__ == "__main__":
    main()
