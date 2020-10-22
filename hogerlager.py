import os
import pyglet
import random
from pyglet.gl import *

font_data = {'font_name': 'Times New Roman', 'font_size': 32, 'color': (0, 0, 0, 255), 'anchor_x': 'center', 'anchor_y': 'center'}
suits = ("Clubs", "Diamonds", "Hearths", "Spades")

def get_scaling(image_width, image_height, width, height):
    ''' Set scaling of X/Y as proportion of measurements if avail, if not use scaling of other measurements. '''
    scale_x = width / image_width if not width is None else height / image_height
    scale_y = height / image_height if not height is None else width / image_width 
    return scale_x, scale_y

def higher(x, y):
    return x > y

def lower(x, y):
    return x < y

def relative_path(*args):
    return os.path.join(os.getcwd(), *args)

def get_card_image_path(suit_nr, card_nr):
    return relative_path('resources', f'cards_{suit_nr+1}x{card_nr+1}.png')

def sprite_from_path(path):
    return pyglet.sprite.Sprite(pyglet.image.load(path))

class Button(pyglet.sprite.Sprite):
    def __init__(self, path, root, connect):
        super().__init__(pyglet.image.load(relative_path(*path)))
        self.root = root
        self.connected_function = None
        if connect:
            self.connect(connect)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y

    @property
    def top(self):
        return self.y + self.height
    
    def connect(self, function):
        self.connected_function = function
        self.root.push_handlers(self.on_mouse_press)

    def on_mouse_press(self, mouse_x, mouse_y, button, modifiers):
        if self.left <= mouse_x <= self.right and self.bottom <= mouse_y <= self.top:
            self.connected_function()

class Card:
    def __init__(self, suit, suit_nr, number):
        self.suit = suit
        self.number = number
        self.image = sprite_from_path(get_card_image_path(suit_nr, number))

    def __lt__(self, other):
        if self.number < other.number:
            return True
        return False
    
    def __lte__(self, other):
        if self.number <= other.number:
            return True
        return False
    
    def __gt__(self, other):
        if self.number > other.number:
            return True
        return False
    
    def __gte__(self, other):
        if self.number > other.number:
            return True
        return False

class Deck:
    def __init__(self):
        self._cards = [Card(suit, suit_nr, card_nr) for card_nr in range(13) for suit_nr, suit in enumerate(suits)]

    def shuffle(self):
        random.shuffle(self._cards)
    
    def update_sprites(self, **kwargs):
        for card in self._cards:
            card.image.update(**kwargs)

class HogerLager(Deck):
    def __init__(self, root, x, y, width=None, height=None):
        super().__init__()
        self.root = root
        self.root.push_handlers(self.on_mouse_press)
        self.finished = False
        self.show_score = False
        self.x = x
        self.y = y

        base_image_width = self._cards[0].image.width
        base_image_height = self._cards[0].image.height
        scale_x, scale_y = get_scaling(base_image_width, base_image_height, width, height)
        scaled_image_width = base_image_width*scale_x
        scaled_image_height = base_image_height*scale_y

        self.up = Button(root=self.root, path=('resources', 'up.png'), connect=self.press_up)
        self.down = Button(root=self.root, path=('resources', 'down.png'), connect=self.press_down)
        self.up.update(x=x, y=y-self.up.image.height*2-10, scale_x=scale_x*2, scale_y=scale_y*2)
        self.down.update(x=x+scaled_image_width-self.down.image.width*2-10, y=y-self.down.image.height*2-10, scale_x=scale_x*2, scale_y=scale_y*2)

        self.update_sprites(x=x, y=y, scale_x=scale_x, scale_y=scale_y)

        self.score_label = pyglet.text.Label('0', x=self.x+scaled_image_width//2, y=self.y-self.up.height//2, **font_data)
        self.finished_label = pyglet.text.Label(' ', x=self.x+scaled_image_width//2, y=self.y-3*self.up.height//2, **font_data)

        self.start()

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self.score_label.text = f'{self.score}'

    def start(self):
        self.shuffle()
        self.index = 0
        self.score = 0
        self.finished = False

    def draw(self):
        if not self.finished:
            self.up.draw()
            self.down.draw()
            self._cards[self.index].image.draw()
            self.score_label.draw()
        else:
            self.finished_label.draw()

    def on_mouse_press(self, mouse_x, mouse_y, button, modifiers):
        if self.finished and self.show_score: 
            self.show_score = False
        elif self.finished and not self.show_score:
            self.start()
    
    def press_up(self):
        self.next_card(lower)
    
    def press_down(self):
        self.next_card(higher)
    
    def next_card(self, comparison):
        cur_value = self._cards[self.index]
        self.index += 1
        next_value = self._cards[self.index]

        if comparison(cur_value, next_value):
            self.score += 1

        if self.index == len(self._cards)-1:
            self.finished_label.text = f'Je hebt {self.score} punten. Klik om te herstarten.'
            self.finished = True
            self.show_score = True

class Screen(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        glClearColor(1, 1, 1, 1)
        self.deck = HogerLager(self, self.width//5*2, self.height//2, self.width//4)

    def on_draw(self):
        self.clear()
        self.deck.draw()

    def set_2d(self):
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

def main():
    screen = Screen(width=800, height=640)
    pyglet.app.run()

main()
