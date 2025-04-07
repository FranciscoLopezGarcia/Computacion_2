class Player:
    def __init__(self, name, is_dealer=False):
        self.name = name
        self.hand = []
        self.stand = False
        self.is_dealer = is_dealer

    def add_card(self, card):
        self.hand.append(card)

    def point_calc(self):
        total = sum(card.puntos for card in self.hand)
        aces = sum(1 for card in self.hand if card.valor == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def status(self):
        points = self.point_calc()
        if points == 21 and len(self.hand) == 2:
            return "Blackjack"
        elif points > 21:
            return "Bust"
        else:
            return "Active"

    def show_hand(self):
        return ', '.join(str(card) for card in self.hand)


