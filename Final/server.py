# server.py
import socketserver
import threading
import time
from mesa import Mesa
from player import Jugador

# Tiempo de espera (en segundos) para acumular jugadores en la sala de espera.
TIEMPO_ESPERA = 30

class BlackjackHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(None)
        self.server.log(f"Nuevo cliente conectado: {self.client_address}")
        # Al conectarse se agrega a la sala de espera.
        with self.server.lock:
            self.server.waiting_players.append(self.request)
        self.send("Te has conectado al servidor de Blackjack.\nEsperá a que comience la partida.\n")
        
        # Espera hasta que el juego se inicie y su socket esté incluido en la partida actual.
        while True:
            with self.server.lock:
                if self.request in self.server.game_clients:
                    break
            time.sleep(0.5)
        
        # Una vez iniciado el juego, se obtiene el Jugador asignado.
        jugador = self.server.get_jugador(self.request)
        self.send(f"Bienvenido a la partida, {jugador.nombre}.\n")
        
        # Ciclo de turnos: el cliente actúa solo cuando le corresponde.
        while not self.server.game_over:
            with self.server.turn_cond:
                while self.server.current_player_socket() != self.request and not self.server.game_over:
                    self.server.turn_cond.wait()
            if self.server.game_over:
                break
            # Es su turno
            self.send("Es tu turno. Ingresa acción: [H]it, [S]tand, [E]xit: ")
            try:
                accion = self.request.recv(1024).decode().strip().upper()
            except:
                accion = "E"
            if accion == "H":
                self.server.player_hit(self.request)
            elif accion == "S":
                self.server.player_stand(self.request)
            elif accion == "E":
                self.server.player_exit(self.request)
            else:
                self.send("Acción inválida.\n")
                continue
            with self.server.turn_cond:
                self.server.advance_turn()
                self.server.turn_cond.notify_all()
        
        # Final de partida: se envía el mensaje final al cliente.
        final_msg = self.server.get_final_message(self.request)
        self.send(final_msg)
        self.request.close()

    def send(self, mensaje):
        try:
            self.request.sendall(mensaje.encode())
        except:
            pass

class BlackjackServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.turn_cond = threading.Condition(self.lock)
        # Sala de espera: sockets que esperan para la próxima partida.
        self.waiting_players = []
        # Sockets que participan en la partida actual.
        self.game_clients = []
        # Lista de tuplas (socket, Jugador) para la partida actual.
        self.players = []
        self.game_over = False
        self.current_turn_index = 0
        self.dealer = None
        self.mesa = None
        self.game_in_progress = False

    def log(self, mensaje):
        print(mensaje)

    def get_jugador(self, sock):
        for s, jugador in self.players:
            if s == sock:
                return jugador
        return None

    def current_player_socket(self):
        if self.players and self.current_turn_index < len(self.players):
            return self.players[self.current_turn_index][0]
        return None

    def broadcast(self, mensaje):
        for s, _ in self.players:
            try:
                s.sendall((mensaje+"\n").encode())
            except:
                pass

    def player_hand_str(self, jugador):
        cartas = ', '.join([f"{p} de {v}" for p, v in jugador.mano])
        return f"{jugador.nombre}: {cartas} - Puntos: {jugador.calcular_puntos()}"

    def deal_card(self, sock, jugador):
        carta = self.mesa.repartir_carta()
        p, v = carta
        # Si es As, se pregunta al cliente.
        if v == 'A':
            try:
                sock.sendall("Has recibido un As. ¿Quieres que valga 1 u 11? ".encode())
                resp = sock.recv(1024).decode().strip()
                if resp in ['1', '11']:
                    v = int(resp)
                else:
                    v = 11
            except:
                v = 11
        elif v in ['J', 'Q', 'K']:
            v = 10
        else:
            v = int(v)
        jugador.agregar_carta((p, v))
        self.broadcast(self.player_hand_str(jugador))

    def player_hit(self, sock):
        for s, jugador in self.players:
            if s == sock:
                self.deal_card(sock, jugador)
                break

    def player_stand(self, sock):
        for s, jugador in self.players:
            if s == sock:
                jugador.stand = True
                self.broadcast(f"{jugador.nombre} se planta.")
                break

    def player_exit(self, sock):
        for s, jugador in self.players:
            if s == sock:
                jugador.exit = True
                self.broadcast(f"{jugador.nombre} se retira.")
                break

    def advance_turn(self):
        self.current_turn_index += 1
        if self.current_turn_index >= len(self.players):
            self.dealer_turn()
            self.game_over = True
            self.broadcast("La partida ha finalizado.")

    def dealer_turn(self):
        self.broadcast("Turno del crupier.")
        # Revela la mano completa del crupier.
        dealer_full = ', '.join([f"{p} de {v}" for p, v in self.dealer.mano])
        self.broadcast("Mano del crupier: " + dealer_full)
        while self.dealer.calcular_puntos() < 17:
            carta = self.mesa.repartir_carta()
            p, v = carta
            if v == 'A':
                v = 11 if self.dealer.calcular_puntos() + 11 <= 21 else 1
            elif v in ['J', 'Q', 'K']:
                v = 10
            else:
                v = int(v)
            self.dealer.agregar_carta((p, v))
            self.broadcast(f"El crupier pide: {p} de {v}")
            dealer_full = ', '.join([f"{p} de {v}" for p, v in self.dealer.mano])
            self.broadcast("Mano del crupier: " + dealer_full)
        self.broadcast(f"Puntos del crupier: {self.dealer.calcular_puntos()}")

    def get_final_message(self, sock):
        jugador = self.get_jugador(sock)
        if not jugador:
            return ""
        player_points = jugador.calcular_puntos()
        dealer_points = self.dealer.calcular_puntos()
        if player_points > 21:
            res = "Perdiste, te pasaste de 21."
        elif dealer_points > 21 or player_points > dealer_points:
            res = "¡Ganaste contra el crupier!"
        elif player_points == dealer_points:
            res = "Empate con el crupier."
        else:
            res = "Perdiste, el crupier gana."
        final = (
            f"Tus cartas: {', '.join([f'{p} de {v}' for p, v in jugador.mano])} - Puntos: {player_points}\n"
            f"Mano del crupier: {', '.join([f'{p} de {v}' for p, v in self.dealer.mano])} - Puntos: {dealer_points}\n"
            f"Resultado: {res}"
        )
        return final

    def start_game(self):
        with self.lock:
            if not self.waiting_players:
                return
            # Se toman todos los sockets en espera para formar la partida actual.
            self.game_clients = self.waiting_players.copy()
            self.waiting_players.clear()
            self.players = []
            for sock in self.game_clients:
                jugador = Jugador(f"Jugador-{sock.getpeername()[1]}")
                self.players.append((sock, jugador))
            self.mesa = Mesa()
            self.game_over = False
            self.current_turn_index = 0
            # Reparte 2 cartas a cada jugador.
            for sock, jugador in self.players:
                for _ in range(2):
                    self.deal_card(sock, jugador)
            # Reparte 2 cartas al crupier.
            self.dealer = Jugador("Dealer")
            for _ in range(2):
                carta = self.mesa.repartir_carta()
                p, v = carta
                if v == 'A':
                    v = 11
                elif v in ['J', 'Q', 'K']:
                    v = 10
                else:
                    v = int(v)
                self.dealer.agregar_carta((p, v))
            # Envía a cada jugador su mano y muestra la carta visible del crupier.
            for sock, jugador in self.players:
                try:
                    sock.sendall((f"Tus cartas: {', '.join([f'{p} de {v}' for p,v in jugador.mano])} - "
                                  f"Puntos: {jugador.calcular_puntos()}\n").encode())
                except:
                    pass
            dealer_first = f"{self.dealer.mano[0][0]} de {self.dealer.mano[0][1]}, X"
            self.broadcast("Mano del crupier: " + dealer_first)
            self.game_in_progress = True
            with self.turn_cond:
                self.turn_cond.notify_all()

def game_loop(server):
    while True:
        server.log(f"Esperando {TIEMPO_ESPERA} segundos para nuevos jugadores...")
        time.sleep(TIEMPO_ESPERA)
        server.log("Iniciando partida...")
        server.start_game()
        # Espera a que finalice la partida.
        while not server.game_over:
            time.sleep(1)
        server.log("Partida finalizada. Esperando nuevos jugadores para la siguiente partida...")
        with server.lock:
            server.game_clients.clear()
            server.players.clear()
            server.game_in_progress = False

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    with BlackjackServer((HOST, PORT), BlackjackHandler) as server:
        threading.Thread(target=game_loop, args=(server,), daemon=True).start()
        server.log("Servidor Blackjack iniciado.")
        server.serve_forever()
