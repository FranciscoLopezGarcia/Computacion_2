# server.py
import socketserver
import threading
import time
from mesa import Mesa
from player import Jugador

TIEMPO_ESPERA = 30  # Tiempo en segundos para acumular jugadores

class BlackjackHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(None)
        self.server.log(f"Nuevo cliente conectado: {self.client_address}")
        # Agregar cliente a la sala de espera.
        with self.server.lock:
            self.server.waiting_clients.append(self.request)
        self.send("Te has conectado al servidor de Blackjack.\nEsperá el inicio de la partida.\n")
        
        # Espera hasta que se inicie una partida y su socket se incluya en game_clients.
        while True:
            with self.server.lock:
                if self.request in self.server.game_clients:
                    break
            time.sleep(0.5)
        
        # Se obtiene el objeto Jugador asignado a este socket.
        jugador = self.server.get_jugador(self.request)
        self.send(f"Bienvenido a la partida, {jugador.nombre}.\n")
        
        # Bucle de turno: el jugador juega hasta plantarse, retirarse, alcanzar 21 o pasarse.
        while not self.server.game_over:
            # Solo el jugador cuyo socket coincide con current_turn juega.
            with self.server.turn_cond:
                while self.server.current_player_socket() != self.request and not self.server.game_over:
                    self.server.turn_cond.wait()
            if self.server.game_over:
                break
            # Es el turno de este jugador. Se le envía siempre su mano actualizada.
            self.send(f"Tus cartas: {self.server.player_hand_str(jugador)}\n")
            self.send("Es tu turno. Ingresa acción: [H]it, [S]tand, [E]xit: ")
            try:
                accion = self.request.recv(1024).decode().strip().upper()
            except Exception:
                accion = "E"
            if accion == "H":
                self.server.player_hit(self.request)
                # Verificamos si el jugador alcanzó o superó 21:
                if jugador.calcular_puntos() >= 21:
                    self.send(f"Tu puntaje es {jugador.calcular_puntos()}.\n")
                    break  # Finaliza turno automáticamente.
            elif accion == "S":
                self.server.player_stand(self.request)
                break  # Se planta: termina su turno.
            elif accion == "E":
                self.server.player_exit(self.request)
                break
            else:
                self.send("Acción inválida.\n")
                continue
            # Si no terminó el turno, se repite la opción.
        # Final del turno de este jugador: notifica que terminó su turno y avanza.
        with self.server.turn_cond:
            self.server.advance_turn(advance_only_current=True)
            self.server.turn_cond.notify_all()
        # Si el juego ya terminó, se espera el turno del crupier y el resumen final.
        while not self.server.game_over:
            time.sleep(0.5)
        # Enviar resumen final individual.
        final_msg = self.server.get_final_message(self.request)
        self.send(final_msg)
        self.request.close()

    def send(self, mensaje):
        try:
            self.request.sendall(mensaje.encode())
        except Exception:
            pass

class BlackjackServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.turn_cond = threading.Condition(self.lock)
        # Clientes en sala de espera (socket)
        self.waiting_clients = []
        # Sockets incluidos en la partida actual.
        self.game_clients = []
        # Lista de tuplas (socket, Jugador) de la partida actual.
        self.players = []
        # Variables del juego.
        self.game_over = False
        self.current_turn_index = 0
        self.dealer = None
        self.mesa = None
        self.game_in_progress = False

    def log(self, msg):
        print(msg)

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
        # Actualiza a todos con la mano de ese jugador.
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

    def advance_turn(self, advance_only_current=False):
        # Si se usa advance_only_current, solo se finaliza el turno actual sin pasar al siguiente.
        if not advance_only_current:
            self.current_turn_index += 1
        # Si ya pasaron todos los jugadores, se inicia el turno del crupier.
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
            if not self.waiting_clients:
                return
            # Toma todos los sockets en espera y forma la partida actual.
            self.game_clients = self.waiting_clients.copy()
            self.waiting_clients.clear()
            self.players = []
            for sock in self.game_clients:
                jugador = Jugador(f"Jugador-{sock.getpeername()[1]}")
                self.players.append((sock, jugador))
            # Inicializa variables de la partida.
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
            # Envia a cada jugador su mano inicial.
            for sock, jugador in self.players:
                try:
                    sock.sendall((f"Tus cartas: {self.player_hand_str(jugador)}\n").encode())
                except:
                    pass
            # Muestra la mano del crupier (solo la primera carta y “X” para la oculta).
            dealer_first = f"{self.dealer.mano[0][0]} de {self.dealer.mano[0][1]}, X"
            self.broadcast("Mano del crupier: " + dealer_first)
            self.game_in_progress = True
            # Notifica a los jugadores que comience el turno del primero.
            with self.turn_cond:
                self.turn_cond.notify_all()

def game_loop(server):
    while True:
        server.log(f"Esperando {TIEMPO_ESPERA} segundos para nuevos jugadores...")
        time.sleep(TIEMPO_ESPERA)
        server.log("Iniciando partida...")
        server.start_game()
        # Espera a que la partida finalice.
        while not server.game_over:
            time.sleep(1)
        server.log("Partida finalizada.")
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
