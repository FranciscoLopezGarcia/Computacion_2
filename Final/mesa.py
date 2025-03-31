import random


class Mesa:
    def __init__(self):
        self.mazo = self.crear_mazo()
        # self.baraja()

    def crear_mazo(self):
        palos = ['Corazones', 'Diamantes', 'Tréboles', 'Picas']
        nmr = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        mazo = []
        for p in palos:
            for n in nmr:
                mazo.append((p, n))

        return mazo
    
    def repartir_carta(self):
        if len(self.mazo) == 0:
            raise ValueError("No hay cartas en el mazo")
        return self.mazo.pop(random.randint(0, len(self.mazo) - 1))

mesa = Mesa()
# print(mesa.mazo)