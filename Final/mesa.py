# mesa.py
import random

class Mesa:
    def __init__(self):
        self.mazo = self.crear_mazo()

    def crear_mazo(self):
        palos = ['Corazones', 'Diamantes', 'Tréboles', 'Picas']
        numeros = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return [(p, n) for p in palos for n in numeros]

    def repartir_carta(self):
        if not self.mazo:
            raise ValueError("No hay cartas en el mazo")
        indice = random.randint(0, len(self.mazo)-1)
        return self.mazo.pop(indice)
