import random

class Mesa:
    def __init__(self):
        self.mazo = self.crear_mazo()

    def crear_mazo(self):
        palos = ['Corazones', 'Diamantes', 'Tréboles', 'Picas']
        nmr = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        mazo = [(p, n) for p in palos for n in nmr]
        return mazo

    def repartir_carta(self):
        if not self.mazo:
            raise ValueError("No hay cartas en el mazo")
        return self.mazo.pop(random.randint(0, len(self.mazo)-1))
