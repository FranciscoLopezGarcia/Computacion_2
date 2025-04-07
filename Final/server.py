import socketserver
import threading
import random
import time

lock = threading.Lock()
clients = []
turn_index = 0
dealer_hand = []

# Baraja y valores
suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [(rank, suit) for suit in suits for rank in ranks]
random.shuffle(deck)

# Función para calcular los puntos
def calcular_puntos(mano, ases_valores):
    total = 0
    for i, (carta, _) in enumerate(mano):
        if carta in ['J', 'Q', 'K']:
            total += 10
        elif carta == 'A':
            total += ases_valores[i]
        else:
            total += int(carta)
    return total

class PlayerData:
    def __init__(self, conn, name):
        self.conn = conn
        self.name = name
        self.hand = []
        self.ases_valores = []

class BlackjackHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global turn_index, dealer_hand

        with lock:
            player = PlayerData(self.request, f"Jugador-{self.client_address[1]}")
            clients.append(player)
            print(f"{player.name} conectado desde {self.client_address}")
        
        player.conn.sendall(f"Bienvenido {player.name}.\nEsperando a que todos se conecten...\n".encode())

        # Esperar que se conecten 2 jugadores
        while True:
            with lock:
                if len(clients) == 2:
                    break
            time.sleep(1)

        # Esperar hasta que sea el turno de este jugador
        while True:
            with lock:
                if clients[turn_index] == player:
                    break
            time.sleep(0.5)

        # Repartir 2 cartas
        with lock:
            for _ in range(2):
                carta = deck.pop()
                player.hand.append(carta)
                if carta[0] == 'A':
                    player.conn.sendall(f"Recibiste un As ({carta[0]} de {carta[1]}). ¿Querés que valga 1 u 11? ".encode())
                    while True:
                        valor = player.conn.recv(1024).decode().strip()
                        if valor in ['1', '11']:
                            player.ases_valores.append(int(valor))
                            break
                        else:
                            player.conn.sendall("Elegí solo 1 o 11: ".encode())
                else:
                    player.ases_valores.append(0)

        # Turno del jugador
        while True:
            puntos = calcular_puntos(player.hand, player.ases_valores)
            mano_str = ', '.join(f"{c[0]} de {c[1]}" for c in player.hand)
            player.conn.sendall(f"Tu mano: {mano_str} (Puntos: {puntos})\n".encode())

            if puntos > 21:
                player.conn.sendall("Te pasaste de 21. Fin de tu turno.\n".encode())
                break

            player.conn.sendall("Escribe 'H' para Pedir Carta o 'S' para Plantarte:\nTu eleccion (H/S): ".encode())
            respuesta = player.conn.recv(1024).decode().strip().upper()

            if respuesta == 'H':
                carta = deck.pop()
                player.hand.append(carta)
                if carta[0] == 'A':
                    player.conn.sendall(f"Recibiste un As ({carta[0]} de {carta[1]}). ¿Querés que valga 1 u 11? ".encode())
                    while True:
                        valor = player.conn.recv(1024).decode().strip()
                        if valor in ['1', '11']:
                            player.ases_valores.append(int(valor))
                            break
                        else:
                            player.conn.sendall("Elegí solo 1 o 11: ".encode())
                else:
                    player.ases_valores.append(0)
            elif respuesta == 'S':
                player.conn.sendall("Te has plantado. Fin de tu turno.\n".encode())
                break

        with lock:
            turn_index += 1

        # Esperar a que todos terminen
        while True:
            with lock:
                if turn_index >= len(clients):
                    break
            time.sleep(1)

        # Crupier juega solo una vez
        if self.client_address == clients[0].conn.getpeername():
            dealer_hand = [deck.pop(), deck.pop()]
            while calcular_puntos(dealer_hand, [11 if c[0] == 'A' else 10 if c[0] in ['J','Q','K'] else int(c[0]) for c in dealer_hand]) < 17:
                dealer_hand.append(deck.pop())

        # Espera a que crupier termine
        while not dealer_hand:
            time.sleep(0.5)

        # Mostrar resultado
        puntos_dealer = calcular_puntos(dealer_hand, [11 if c[0] == 'A' else 10 if c[0] in ['J','Q','K'] else int(c[0]) for c in dealer_hand])
        dealer_str = ', '.join(f"{c[0]} de {c[1]}" for c in dealer_hand)
        puntos_jugador = calcular_puntos(player.hand, player.ases_valores)

        if puntos_jugador > 21:
            resultado = "Perdiste"
        elif puntos_dealer > 21 or puntos_jugador > puntos_dealer:
            resultado = "Ganaste"
        elif puntos_jugador < puntos_dealer:
            resultado = "Perdiste"
        else:
            resultado = "Empate"

        player.conn.sendall(f"\n--- Crupier: {dealer_str} (Puntos: {puntos_dealer}) ---\nResultado: {resultado}\n".encode())
        player.conn.close()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    print(f"Servidor Blackjack iniciado en {HOST}:{PORT}")
    with socketserver.ThreadingTCPServer((HOST, PORT), BlackjackHandler) as server:
        server.serve_forever()
