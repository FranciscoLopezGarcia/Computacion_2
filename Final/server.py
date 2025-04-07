import socketserver
import threading
import time
from mesa import Mesa
from player import Jugador

class BlackjackHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # Solo se permite la conexión si el juego aún no ha iniciado.
        with self.server.lock:
            if self.server.game_started:
                self.request.sendall("Juego en progreso, intenta más tarde.\n".encode())
                self.request.close()
                return
            jugador = Jugador(f"Jugador-{self.client_address[1]}")
            self.server.players.append((self.request, jugador))
            self.request.sendall("Te has unido a la mesa. Espera a que comience el juego.\n".encode())
        
        # Espera a que comience el juego.
        self.server.game_start_event.wait()
        
        # Ahora, en el ciclo de turno, el jugador actúa solo cuando es su turno.
        while not self.server.game_ended:
            with self.server.turn_cond:
                # Espera hasta que sea su turno o que el juego finalice.
                while (self.server.current_player_socket() != self.request) and (not self.server.game_ended):
                    self.server.turn_cond.wait()
            if self.server.game_ended:
                break

            # Es el turno de este jugador.
            self.request.sendall("Es tu turno. Elige: [H]it, [S]tand, [E]xit: ".encode())
            try:
                accion = self.request.recv(1024).decode().strip().upper()
            except:
                accion = "E"
            if accion == "H":
                self.server.deal_card_to_player(self.request)
            elif accion == "S":
                self.server.set_player_stand(self.request)
            elif accion == "E":
                self.server.set_player_exit(self.request)
            else:
                self.request.sendall("Acción inválida.\n".encode())
                continue
            # Finaliza el turno y notifica para avanzar.
            with self.server.turn_cond:
                self.server.advance_turn()
                self.server.turn_cond.notify_all()
        
        # Una vez finalizada la partida, se envían los resultados finales al jugador.
        dealer_hand = self.server.dealer_hand_str(final=True)
        resultado = self.server.calculate_results(self.request)
        self.request.sendall(f"Mano del crupier: {dealer_hand}\n{resultado}\n".encode())
        self.request.close()

class BlackjackServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesa = Mesa()
        self.players = []          # Lista de (socket, Jugador)
        self.game_started = False  # Indica si la partida inició (se aceptan conexiones solo antes)
        self.game_ended = False
        self.game_start_event = threading.Event()  # Se activa cuando inicia la partida
        self.turn_cond = threading.Condition()       # Para coordinar el turno de jugadores
        self.current_turn_index = 0                  # Índice del jugador activo
        self.lock = threading.Lock()
        self.dealer = None                           # Instancia de Jugador para el crupier

    def current_player_socket(self):
        if self.players and self.current_turn_index < len(self.players):
            return self.players[self.current_turn_index][0]
        return None

    def deal_initial_cards(self):
        # Reparte dos cartas a cada jugador.
        for sock, jugador in self.players:
            for _ in range(2):
                self.deal_card_to_player(sock)
        # Reparte cartas al crupier.
        self.dealer = Jugador("Dealer")
        for i in range(2):
            carta = self.mesa.repartir_carta()
            palo, valor = carta
            if valor == 'A':
                valor = 11  # Para el dealer se fija en 11
            elif valor in ['J', 'Q', 'K']:
                valor = 10
            else:
                valor = int(valor)
            self.dealer.agregar_carta((palo, valor))

    def deal_card_to_player(self, sock):
        # Busca el jugador asociado al socket y le reparte una carta.
        for s, jugador in self.players:
            if s == sock:
                carta = self.mesa.repartir_carta()
                palo, valor = carta
                if valor == 'A':
                    s.sendall("Has recibido un As. ¿Quieres que valga 1 u 11? ".encode())
                    while True:
                        resp = s.recv(1024).decode().strip()
                        if resp in ['1', '11']:
                            valor = int(resp)
                            break
                        else:
                            s.sendall("Por favor ingresa 1 o 11: ".encode())
                elif valor in ['J', 'Q', 'K']:
                    valor = 10
                else:
                    valor = int(valor)
                jugador.agregar_carta((palo, valor))
                self.broadcast(self.player_hand_str(jugador))
                break

    def set_player_stand(self, sock):
        for s, jugador in self.players:
            if s == sock:
                jugador.stand = True
                break
        self.broadcast(f"{self.player_name(sock)} se planta.")

    def set_player_exit(self, sock):
        for s, jugador in self.players:
            if s == sock:
                jugador.stand = True
                jugador.exit = True
                break
        self.broadcast(f"{self.player_name(sock)} se retira.")

    def player_name(self, sock):
        for s, jugador in self.players:
            if s == sock:
                return jugador.nombre
        return "Desconocido"

    def player_hand_str(self, jugador):
        cartas = ', '.join([f"{palo} de {valor}" for palo, valor in jugador.mano])
        return f"{jugador.nombre}: {cartas} (Puntos: {jugador.calcular_puntos()})"

    def broadcast(self, mensaje):
        for s, _ in self.players:
            try:
                s.sendall((mensaje + "\n").encode())
            except:
                pass

    def advance_turn(self):
        self.current_turn_index += 1
        if self.current_turn_index >= len(self.players):
            # Si ya jugaron todos los jugadores, se ejecuta el turno del crupier.
            self.dealer_play()

    def dealer_hand_str(self, final=False):
        # Si la partida aún no terminó, se muestra la primera carta y una X para la oculta.
        if self.dealer and self.dealer.mano:
            primer = self.dealer.mano[0]
            if final or len(self.dealer.mano) == 1:
                # Se muestran todas las cartas si la partida terminó o solo hay una.
                return ', '.join([f"{p} de {v}" for p, v in self.dealer.mano])
            else:
                return f"{primer[0]} de {primer[1]}, X"
        return ""

    def dealer_play(self):
        self.broadcast("Turno del crupier.")
        # Se revela la mano completa del crupier.
        dealer_full = ', '.join([f"{palo} de {valor}" for palo, valor in self.dealer.mano])
        self.broadcast(f"Mano del crupier: {dealer_full}")
        while self.dealer.calcular_puntos() < 17:
            carta = self.mesa.repartir_carta()
            palo, valor = carta
            if valor == 'A':
                valor = 11 if self.dealer.calcular_puntos() + 11 <= 21 else 1
            elif valor in ['J', 'Q', 'K']:
                valor = 10
            else:
                valor = int(valor)
            self.dealer.agregar_carta((palo, valor))
            self.broadcast(f"El crupier pide: {palo} de {valor}")
            dealer_full = ', '.join([f"{p} de {v}" for p, v in self.dealer.mano])
            self.broadcast(f"Mano del crupier: {dealer_full}")
        self.broadcast(f"Puntos del crupier: {self.dealer.calcular_puntos()}")
        self.game_ended = True
        with self.turn_cond:
            self.turn_cond.notify_all()

    def calculate_results(self, sock):
        for s, jugador in self.players:
            if s == sock:
                player_points = jugador.calcular_puntos()
                dealer_points = self.dealer.calcular_puntos()
                if player_points > 21:
                    return "Perdiste, te pasaste de 21."
                elif dealer_points > 21 or player_points > dealer_points:
                    return "¡Ganaste contra el crupier!"
                elif player_points == dealer_points:
                    return "Empate con el crupier."
                else:
                    return "Perdiste, el crupier gana."
        return ""

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    with BlackjackServer((HOST, PORT), BlackjackHandler) as server:
        print("Esperando jugadores para iniciar la partida (se aceptan conexiones durante 30 segundos)...")
        # Se espera 10 segundos para que se conecten jugadores.
        time.sleep(30)
        with server.lock:
            server.game_started = True
            server.game_start_event.set()
        # Se reparten las cartas iniciales a todos los jugadores y al crupier.
        server.deal_initial_cards()
        server.broadcast("Se han repartido las cartas iniciales.")
        # Se muestra la mano de cada jugador.
        for s, jugador in server.players:
            try:
                s.sendall((server.player_hand_str(jugador) + "\n").encode())
            except:
                pass
        # Se muestra la mano inicial del crupier (con la segunda carta oculta).
        server.broadcast("Mano del crupier: " + server.dealer_hand_str())
        # Notifica para comenzar el turno del primer jugador.
        with server.turn_cond:
            server.turn_cond.notify_all()
        server.serve_forever()
