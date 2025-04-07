# player.py
class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mano = []  # Cada elemento es una tupla (palo, valor) con valor numérico fijo.
        self.stand = False  # Se planta
        self.exit = False   # Se retira

    def agregar_carta(self, carta):
        self.mano.append(carta)

    def calcular_puntos(self):
        return sum(valor for _, valor in self.mano)

    def estado_final(self):
        puntos = self.calcular_puntos()
        if puntos > 21:
            return "Perdiste, te pasaste de 21."
        elif puntos == 21:
            return "¡Ganaste! Tienes 21."
        return ""
