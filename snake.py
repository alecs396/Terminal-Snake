"""The snake module contains the classes for playing the Snake action game. 

Author(s):      [Alec Swainston]
Email(s):       [swa15008@byui.edu]
"""
import curses
import curses.ascii
import random
import sys

MAX_X = 60
MAX_Y = 20
SEGMENTS = 10

class Game:
    """A game to play. 
    
    The responsibility of Game is to use the other classes in the system to 
    control the sequence of play.

    Stereotype:
        Controller
    """
    def __init__(self, input_service, output_service):
        self._snake = Snake()
        self._food = Food() 
        self._score = Score()
        self._input_service = input_service
        self._output_service = output_service
        self._keep_playing = True
        
    def play(self):
        while self._keep_playing:
            self._get_inputs()
            self._update_snake()
            self._update_score()
            self._do_outputs()
            
    def _get_inputs(self):
        direction = self._input_service.get_direction()
        self._snake.move_next(direction)
    
    def _do_outputs(self):
        actors = [self._food, self._score]
        actors.append(self._snake.get_head())
        actors.extend(self._snake.get_body())
        self._output_service.draw_actors(actors)
    
    def _update_score(self):
        head = self._snake.get_head()
        if head.same_position_as(self._food.get_position()):
            self._snake.grow_head()
            self._score.add_points(1)
            self._food.move_random()

    def _update_snake(self):
        head = self._snake.get_head()
        for segment in self._snake.get_body():
            if head.same_position_as(segment.get_position()):
                self._keep_playing = False
                break
        

# ------------------------------------------------------------------------------
# Domain Classes
# ------------------------------------------------------------------------------
class Actor:
    """A visible, moveable thing that participates in the game.
    
    The responsibility of Actor is to keep track of its appearance, position 
    and velocity in 2d space.

    Stereotype:
        Information Holder
    """
    def __init__(self):
        self._text = ""
        self._position = (0, 0)
        self._velocity = (0, 0)
        
    def get_position(self):
        return self._position
    
    def get_text(self):
        return self._text

    def get_velocity(self):
        return self._velocity
    
    def move_next(self):
        x = 1 + (self._position[0] + self._velocity[0] - 1) % (MAX_X - 2)
        y = 1 + (self._position[1] + self._velocity[1] - 1) % (MAX_Y - 2)
        self._position = (x, y)
    
    def set_position(self, position):
        self._position = position
    
    def set_text(self, text):
        self._text = text

    def set_velocity(self, velocity):
       self._velocity = velocity


# ------------------------------------------------------------------------------
# Application Classes
# ------------------------------------------------------------------------------

# TODO: Define your Food class here. Use Score and Segment as your example.
class Food(Actor):
    def __init__(self):
        super().__init__()
        self.set_text("@")
        self.move_random()

    def move_random(self):
        x = random.randint(1, MAX_X -2)
        y = random.randint(1, MAX_Y -2)
        self.set_position( (x,y) )        

class Score(Actor):
    """A record of player points.
    
    The responsibility of Score is to keep track of the player's points.

    Stereotype:
        Information Holder
    """
    def __init__(self):
        super().__init__()
        self._points = 0
        self.set_position( (1, 0) )
        self.add_points(0)

    def add_points(self, points):
        self._points += points
        self.set_text(f"Score: {self._points}")


class Segment(Actor):
    """Part of a snake.
    
    The responsibility of Segment is to keep track of its appearance, location, and velocity. Segment can also tell if it occupies a specific position.

    Stereotype:
        Information Holder
    """
    def __init__(self):
        super().__init__()
    
    def same_position_as(self, position):
        return self.get_position() == position


class Snake:
    """A limbless reptile.
    
    The responsibility of Snake is keep track of its segments. It contains methods for moving and growing among others.

    Stereotype:
        Structurer, Information Holder
    """
    def __init__(self):
        super().__init__()
        self._body = []
        x = int(MAX_X / 2)
        y = int(MAX_Y / 2)
        head = Segment()
        head.set_text("8")
        head.set_position( (x, y) )
        head.set_velocity( (1, 0) )
        self._body.append(head)
        for _ in range(SEGMENTS):
            self.grow_head()
            
    def get_body(self):
        return self._body[1:]

    def get_head(self):
        return self._body[0]

    def move_next(self, direction):
        self.get_head().set_velocity(direction)
        self.grow_head()
        self.trim_tail()  

    def grow_head(self):
        head = self.get_head()
        position = head.get_position()
        head.move_next()
        segment = Segment()
        segment.set_text("#")
        segment.set_position(position)
        self._body.insert(1, segment)

    def trim_tail(self):
        self._body.pop()
       
# ------------------------------------------------------------------------------
# Infrastructure Classes
# ------------------------------------------------------------------------------
class InputService:
    """Detects player input.

    An InputService is responsible for detecting input from the keyboard and 
    providing the direction that was selected.

    Stereotype: 
        Service Provider
    """
    def __init__(self, window):
        self._window = window
        self._directions = {}
        self._directions[curses.KEY_UP] = (0, -1)
        self._directions[curses.KEY_RIGHT] = (1, 0)
        self._directions[curses.KEY_DOWN] = (0, 1)
        self._directions[curses.KEY_LEFT] = (-1, 0)
        self._current = (1, 0)
        
    def get_direction(self):
        key = self._window.getch()
        if key == curses.ascii.ESC: 
            sys.exit()
        self._current = self._directions.get(key, self._current)
        return self._current


class OutputService:
    """Outputs the game state.

    An OutputService is responsible for drawing the game state on the terminal. 
    
    Stereotype: 
        Service Provider
    """
    def __init__(self, window):
        self._window = window
    
    def draw_actors(self, actors):
        self._window.clear()
        self._window.border(0)
        for actor in actors:
            column, row = actor.get_position()
            text = actor.get_text()
            self._window.addstr(row, column, text)
        self._window.refresh()


# ------------------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    curses.initscr()
    curses.curs_set(0)

    window = curses.newwin(MAX_Y, MAX_X, 0, 0)
    window.timeout(80)
    window.keypad(1)

    input_service = InputService(window)
    output_service = OutputService(window)
    game = Game(input_service, output_service)
    game.play()

    curses.endwin()