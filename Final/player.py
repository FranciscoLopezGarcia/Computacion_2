class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mano = []
        self.puntaje = 0
    
    def agregar_carta(self, carta):
        self.mano.append(carta)

##tcrear puntos