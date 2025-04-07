import random

class Card:
    def __init__(self, palo, valor):
        self.palo = palo
        self.valor = valor

    def __str__(self):
        return f"{self.valor} de {self.palo}"

    @property
    def puntos(self):
        if self.valor in ['J', 'Q', 'K']:
            return 10
        elif self.valor == 'A':
            return 11
        else:
            return int(self.valor)

class Deck:
    def __init__(self):
        self.deck = self.create_deck()
        self.shuffle_deck()

    def create_deck(self):
        palos = ['♥', '♦', '♣', '♠']
        valores = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return [Card(p, v) for p in palos for v in valores]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def give_card(self):
        if len(self.deck) == 0:
            self.deck = self.create_deck()
            self.shuffle_deck()
        return self.deck.pop()
