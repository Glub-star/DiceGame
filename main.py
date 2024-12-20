import pygame, random, sys

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Main Menu")

#region colours
white = (255, 255, 255)
black = (0, 0, 0)
grey = (200, 200, 200)
light_grey = (170, 170, 170)
blue = (0, 0, 255)
red = (255, 0, 0)
#endregion

#region fonts
font = pygame.font.SysFont("Arial", 40)
#endregion

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

#region UI classes and methods
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

#endregion

#region game screens
def main_menu():
    def start_game():
        print("Start Game")

    def quit_game():
        pygame.quit()
        sys.exit()

    # Create buttons
    start_button = Button("Start Game", 300, 200, 200, 50, grey, light_grey, start_game)
    quit_button = Button("Quit", 300, 300, 200, 50, grey, light_grey, quit_game)

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            start_button.is_clicked(event)
            quit_button.is_clicked(event)
        
        # Fill the screen with black
        screen.fill(black)
        
        # Draw buttons
        start_button.draw(screen)
        quit_button.draw(screen)
        
        # Update the display
        pygame.display.flip()

def character_selection():

    def character_button(character):
        match character:
            case "Dice":
                print("Dice player selected")
            case "Locked":
                print("Player not available")
            case _:
                print("Unexpected player type")

    dice_button = Button("Dice", 100, 200, 200, 50, action=lambda: character_button("Dice"))
    locked_button = Button("Locked", 100, 300, 200, 50,action= lambda: character_button("Locked"))

    running = True
    
    while running:
        screen.fill((255, 255, 255))

        dice_button.draw(screen)
        locked_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            dice_button.is_clicked(event)
            locked_button.is_clicked(event)

        pygame.display.flip()  # Update the screen

    pygame.quit()

    pygame.quit()

def map_screen():
    map = Map()
    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear the screen
        map.draw(screen)  # Draw the map
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if map.get_current_node().rect.collidepoint(event.pos):
                    map.move_to_next()  # Move to the next room

        pygame.display.flip()  # Update the screen

    pygame.quit()


#endregion

#region map sht

NODE_RADIUS = 30
LINE_WIDTH = 4

class Node:
    def __init__(self, x, y, room_type):
        self.x = x
        self.y = y
        self.room_type = room_type  # Event, Fight, Treasure, etc.
        self.rect = pygame.Rect(x - NODE_RADIUS, y - NODE_RADIUS, NODE_RADIUS * 2, NODE_RADIUS * 2)

    def draw(self, screen, is_selected=False):
        # Draw room node (circle)
        color = blue if not is_selected else red
        pygame.draw.circle(screen, color, (self.x, self.y), NODE_RADIUS)
        
        # Display the room type as text
        font = pygame.font.SysFont(None, 24)
        text = font.render(self.room_type, True, white)
        screen.blit(text, (self.x - text.get_width() // 2, self.y - text.get_height() // 2))

class Map:
    def __init__(self):
        self.layers = []
        self.create_layers()
        self.current_layer_index = 0
        self.current_node_index = 0

    def create_layers(self):
        # Create multiple layers, each with random numbers of nodes
        num_layers = 5
        for i in range(num_layers):
            num_nodes = random.randint(2, 5)  # Each layer has 2 to 5 nodes
            layer = []
            for j in range(num_nodes):
                room_type = random.choice(['Event', 'Fight', 'Treasure'])  # Random room types
                x = screen_height // 2 + random.randint(-100, 100)  # Random horizontal offset
                y = (i + 1) * (screen_height // (num_layers + 1))  # Position layers vertically
                layer.append(Node(x, y, room_type))
            self.layers.append(layer)

        def draw(self, screen):
            for i, layer in enumerate(self.layers):
                for j, node in enumerate(layer):
                    is_selected = i == self.current_layer_index and j == self.current_node_index
                    node.draw(screen, is_selected)
                    
                    # Draw lines connecting nodes within the same layer horizontally
                    if j < len(layer) - 1:
                        pygame.draw.line(screen, w, (layer[j].x, layer[j].y), 
                                        (layer[j + 1].x, layer[j + 1].y), LINE_WIDTH)
                    
                    # Draw lines connecting nodes vertically between layers
                    if i < len(self.layers) - 1:
                        # Make sure there's a corresponding node in the next layer (same index j)
                        if j < len(self.layers[i + 1]):  # Ensure the j-th node exists in the next layer
                            pygame.draw.line(screen, white, (layer[j].x, layer[j].y), 
                                            (self.layers[i + 1][j].x, self.layers[i + 1][j].y), LINE_WIDTH)

    def move_to_next_layer(self):
        if self.current_layer_index < len(self.layers) - 1:
            self.current_layer_index += 1
            self.current_node_index = 0  # Reset to the first node of the next layer
            print(f"Moving to Layer {self.current_layer_index + 1}, Node {self.current_node_index + 1}: {self.layers[self.current_layer_index][self.current_node_index].room_type}")

    def move_to_next_node(self):
        # Move to the next node in the current layer
        if self.current_node_index < len(self.layers[self.current_layer_index]) - 1:
            self.current_node_index += 1
            print(f"Moved to Node {self.current_node_index + 1}: {self.layers[self.current_layer_index][self.current_node_index].room_type}")

    def get_current_node(self):
        return self.layers[self.current_layer_index][self.current_node_index]

#endregion


map_screen()