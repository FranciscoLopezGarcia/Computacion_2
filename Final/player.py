# player.py
class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mano = []  # Lista de tuplas: (palo, valor) (valor ya numérico)
        self.stand = False  # Indica si el jugador se plantó
        self.exit = False   # Indica si el jugador se retiró

    def agregar_carta(self, carta):
        self.mano.append(carta)

    def calcular_puntos(self):
        return sum(valor for _, valor in self.mano)

    def winner_winner_chicken_dinner(self):
        puntos = self.calcular_puntos()
        if puntos > 21:
            return "Perdiste, te pasaste de 21."
        elif puntos == 21:
            return "¡Ganaste! Tienes 21."
        return None
