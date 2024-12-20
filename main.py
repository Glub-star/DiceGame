import pygame, random

#region Blueprints
class Player():
    def __init__(self, health, name="Player"):
        self.health = health
        self.name = name
    
    def Take_Damage(self, damage):
        self.health -= damage
#endregion


#region Dice Player
class Dice():
    def __init__(self):
        self.values = list(range(1,7))

    def roll(self):
        return random.choice(self.values)

class DicePlayer(Player):
    def __init__(self, health, name="Player"):
        super().__init__(health, name)
        self.dice = [Dice() for _ in range(3)]
    
#endregion


