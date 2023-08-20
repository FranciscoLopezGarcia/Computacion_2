import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 7000))

print("Connected to server")
while True:
    data = input("Enter data to send: ")
    if not data:
        break
    s.sendall(data.encode())

    if data == "exit":
        break

s.close()