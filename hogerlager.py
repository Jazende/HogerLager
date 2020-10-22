import os
import pyglet
import random
from pyglet.gl import *

font_data = {'font_name': 'Times New Roman', 'font_size': 32, 'color': (0, 0, 0, 255), 'anchor_x': 'center', 'anchor_y': 'center'}

def get_scaling(image_width, image_height, width, height):
    if width is None:
        scale_y = height / image_height
        scale_x = scale_y
    elif height is None:
        scale_x = width / image_width
        scale_y = scale_x
    else:
        scale_y = height / image_height
        scale_x = width / image_width
    return scale_x, scale_y

def higher(x, y):
    if not isinstance(x, Card):
        raise TypeError
    if not isinstance(y, Card):
        raise TypeError
    return x.number > y.number

def lower(x, y):
    if not isinstance(x, Card):
        raise TypeError
    if not isinstance(y, Card):
        raise TypeError
    return x.number < y.number

def get_card_image_path(suit_nr, card_nr):
    return os.path.join(os.getcwd(), 'resources', f'cards_{suit_nr+1}x{card_nr+1}.png')

def sprite_from_path(path):
    return pyglet.sprite.Sprite(pyglet.image.load(path))

class Card:
    def __init__(self, suit, suit_nr, number):
        self.suit = suit
        self.number = number
        self.image = sprite_from_path(get_card_image_path(suit_nr, number))

class Deck:
    def __init__(self):
        self._cards = [Card(suit, suit_nr, card_nr) for card_nr in range(13) for suit_nr, suit in enumerate(["Clubs", "Diamonds", "Hearths", "Spades"])]

    def shuffle(self):
        random.shuffle(self._cards)

class HogerLager(Deck):
    def __init__(self, x, y, width=None, height=None):
        super().__init__()
        self.finished = False
        self.x = x
        self.y = y

        base_image_width = self._cards[0].image.width
        base_image_height = self._cards[0].image.height
        scale_x, scale_y = get_scaling(base_image_width, base_image_height, width, height)
        scaled_image_width = base_image_width*scale_x
        scaled_image_height = base_image_height*scale_y

        self.up = sprite_from_path(os.path.join(os.getcwd(), 'resources', 'up.png'))
        self.down = sprite_from_path(os.path.join(os.getcwd(), 'resources', 'down.png'))
        self.up.update(x=x, y=y-self.up.image.height*2-10, scale_x=scale_x*2, scale_y=scale_y*2)
        self.down.update(x=x+scaled_image_width-self.down.image.width*2-10, y=y-self.down.image.height*2-10, scale_x=scale_x*2, scale_y=scale_y*2)

        for card in self._cards:
            card.image.update(x=x, y=y, scale_x=scale_x, scale_y=scale_y)

        self.score_label = pyglet.text.Label('0', x=self.x+scaled_image_width//2, y=self.y-self.up.height//2, **font_data)
        self.finished_label = pyglet.text.Label(' ', x=self.x+scaled_image_width//2, y=self.y-3*self.up.height//2, **font_data)

        self.start()

    def start(self):
        self.shuffle()
        self.index = 0
        self.score = 0
        self.finished = False
        self.update_score()

    def update_score(self):
        self.score_label.text = f'{self.score}'
        self.finished_label.text = f'Je hebt {self.score} punten. Klik om te herstarten.'

    def draw(self):
        if not self.finished:
            self.up.draw()
            self.down.draw()
            self._cards[self.index].image.draw()
            self.score_label.draw()
        else:
            self.finished_label.draw()
    
    def on_mouse_press(self, mouse_x, mouse_y, button, modifiers):
        if self.finished: 
            self.start()
        else:
            if self.up.x <= mouse_x  <= self.up.x + self.up.width and \
                self.up.y <= mouse_y <= self.up.y + self.up.height:
                self.press_up()
            elif self.down.x <= mouse_x  <= self.down.x + self.down.width and \
                self.down.y <= mouse_y <= self.down.y + self.down.height:
                self.press_down()
    
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
            self.update_score()

        if self.index == len(self._cards)-1:
            self.finished = True

class Screen(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._events_passthrough = {'on_mouse_press': []}
        glClearColor(1, 1, 1, 1)
        self.deck = HogerLager(self.width//5*2, self.height//2, self.width//4)
        self._events_passthrough['on_mouse_press'].append(self.deck)

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

    def on_mouse_press(self, mouse_x, mouse_y, button, modifiers):
        if 'on_mouse_press' in self._events_passthrough:
            for passthrough in self._events_passthrough['on_mouse_press']:
                passthrough.on_mouse_press(mouse_x, mouse_y, button, modifiers)

def main():
    screen = Screen(width=800, height=640)
    pyglet.app.run()

main()
