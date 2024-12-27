import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Main Menu")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
grey = (200, 200, 200)
light_grey = (170, 170, 170)
blue = (0, 0, 255)
red = (255, 0, 0)

# Fonts
font = pygame.font.SysFont("Arial", 40)

# Blueprints
class Player:
    def __init__(self, health, name="Player"):
        self.health = health
        self.name = name

    def take_damage(self, damage):
        damage_taken = max(0, damage - self.block)
        self.health -= damage_taken

class Enemy:
    def __init__(self, name="Enemy", health=20, damage=5, block=0, sprite=pygame.image.load("./assets/MissingTexture.png")):
        self.name = name
        self.health = health
        self.damage = damage
        self.block = block
        self.sprite = sprite

    def take_damage(self, damage):
        damage_taken = max(0, damage - self.block)
        self.health -= damage_taken

    def turn(self, player: Player):
        player.take_damage(self.damage)

class Dice:
    def __init__(self):
        self.values = list(range(1, 7))

    def roll(self):
        return random.choice(self.values)

class DicePlayer(Player):
    def __init__(self, health, name="Player"):
        super().__init__(health, name)
        self.dice = [Dice() for _ in range(3)]

class Button:
    def __init__(self, text, x, y, width, height, inactive_color=grey, active_color=light_grey, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = self.active_color
        else:
            color = self.inactive_color
        pygame.draw.rect(screen, color, self.rect)
        
        text_surface = font.render(self.text, True, white)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

def main_menu():
    def start_game():
        print("Start Game")
        character_selected = None
        character_selection(character_selected)
        game_map = Map()
        game_map.map_loop()

    def quit_game():
        pygame.quit()
        sys.exit()

    start_button = Button("Start Game", 300, 200, 200, 50, grey, light_grey, start_game)
    quit_button = Button("Quit", 300, 300, 200, 50, grey, light_grey, quit_game)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            start_button.is_clicked(event)
            quit_button.is_clicked(event)
        
        screen.fill(black)
        start_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()

def character_selection(character_selected):
    running = True

    def character_button(character):
        nonlocal character_selected
        nonlocal running
        if character == "Dice":
            character_selected = "Dice"
            running = False
        elif character == "Locked":
            print("Player not available")
        else:
            print("Unexpected player type")

    dice_button = Button("Dice", 100, 200, 200, 50, action=lambda: character_button("Dice"))
    locked_button = Button("Locked", 100, 300, 200, 50, action=lambda: character_button("Locked"))

    while running:
        screen.fill(white)
        dice_button.draw(screen)
        locked_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            dice_button.is_clicked(event)
            locked_button.is_clicked(event)

        pygame.display.flip()

class Node:
    def __init__(self, x, y, level=0):
        self.x = x
        self.y = y
        self.level = level
        self.connections = []
        self.radius = 10
        self.color = (255, 255, 255)

    def connect(self, other_node):
        if other_node not in self.connections:
            self.connections.append(other_node)
            other_node.connections.append(self)

    def draw(self, screen, camera_offset):
        pygame.draw.circle(screen, self.color, (self.x - camera_offset[0], self.y - camera_offset[1]), self.radius)
        for node in self.connections:
            pygame.draw.line(screen, (255, 255, 255), 
                             (self.x - camera_offset[0], self.y - camera_offset[1]), 
                             (node.x - camera_offset[0], node.y - camera_offset[1]))

    def is_hovered(self, pos):
        return (self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2 < self.radius ** 2

    def is_connected(self, other_node):
        return other_node in self.connections

class Map:
    def __init__(self):
        start_node = Node(screen_width // 2, screen_height // 7)
        first_node = Node(screen_width // 2, screen_height // 5)
        start_node.connect(first_node)
        self.nodes = [start_node, first_node]
        self.current_node = start_node
        self.current_node.color = (0, 255, 0)
        self.visited_nodes = {start_node}
        self.camera_offset = [0, 0]
        self.target_camera_offset = [0, 0]

    def lerp(self, start, end, t):
        return start + t * (end - start)

    def map_loop(self):
        running = True
        clock = pygame.time.Clock()  # Initialize the clock

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for node in self.nodes:
                        if (node.is_hovered((mouse_pos[0] + self.camera_offset[0], mouse_pos[1] + self.camera_offset[1])) and
                                self.current_node.is_connected(node) and
                                node not in self.visited_nodes):
                            self.current_node.color = (255, 255, 255)
                            self.current_node = node
                            self.current_node.color = (0, 255, 0)
                            self.visited_nodes.add(self.current_node)
                            new_nodes = create_nodes(self.current_node)
                            self.nodes.extend(new_nodes)
                            self.update_camera()

            mouse_pos = pygame.mouse.get_pos()
            screen.fill(black)  # Fill the screen with black

            for node in self.nodes:
                if node.is_hovered((mouse_pos[0] + self.camera_offset[0], mouse_pos[1] + self.camera_offset[1])) and self.current_node.is_connected(node) and node not in self.visited_nodes:
                    node.color = (255, 0, 0)
                elif node == self.current_node:
                    node.color = (0, 255, 0)
                else:
                    node.color = (255, 255, 255)
                node.draw(screen, self.camera_offset)

            pygame.display.flip()

            self.camera_offset[0] = self.lerp(self.camera_offset[0], self.target_camera_offset[0], 0.1)
            self.camera_offset[1] = self.lerp(self.camera_offset[1], self.target_camera_offset[1], 0.1)

            clock.tick(60)  # Maintain 60 FPS

    def update_camera(self):
        self.target_camera_offset[0] = self.current_node.x - screen_width // 2
        self.target_camera_offset[1] = self.current_node.y - screen_height // 2

def create_nodes(current_node, max_nodes=3):
    level = current_node.level + 1
    new_nodes = []
    num_new_nodes = random.randint(1, max_nodes)  # 1 to 3 new nodes

    for _ in range(num_new_nodes):
        x_offset = random.randint(-100, 100)
        y = screen_height // 6 + level * screen_height // 6
        x = current_node.x + x_offset
        x = max(min(x, screen_width - 50), 50)
        new_node = Node(x, y, level)
        current_node.connect(new_node)
        new_nodes.append(new_node)

    return new_nodes

class Slime(Enemy):
    def __init__(self, name="Slime", health=20, damage=5, block=0):
        super().__init__(name, health, damage, block)

if __name__ == "__main__":
    main_menu()
