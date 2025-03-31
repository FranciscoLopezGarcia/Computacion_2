import socketserver
from mesa import Mesa
from player import Jugador

class BlackjackHandler(socketserver.BaseRequestHandler):
    def handle(self):
        jugador = Jugador(f"Jugador-{self.client_address[1]}")
        mesa = self.server.mesa
        
        # Repartir 2 cartas iniciales
        for _ in range(2):
            jugador.agregar_carta(mesa.repartir_carta())
        
        # Enviar estado inicial al cliente
        self.request.sendall(f"Tus cartas: {', '.join([f'{carta[0]} de {carta[1]}' for carta in jugador.mano])}\n".encode())        
        # Lógica de turnos (simplificada)
        while True:
            accion = self.request.recv(1024).decode().strip().upper()
            if accion == "P":
                jugador.agregar_carta(mesa.repartir_carta())
                self.request.sendall(f"Nueva carta: {jugador.mano[-1]}\n".encode())
            elif accion == "Q":
                break

class BlackjackServer(socketserver.ThreadingTCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesa = Mesa()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    with BlackjackServer((HOST, PORT), BlackjackHandler) as server:
        print(f"Servidor Blackjack en {HOST}:{PORT}")
        server.serve_forever()


        ##agregar