import pygame


class ObjectManager:
    def __init__(self, game):
        self.current_objects = None
        self.game = game

    def update(self):
        self.current_objects = self.game.world_manager.current_room.objects
        for o in self.current_objects:
            o.detect_collision()
            o.update()

    def draw(self):
        for o in self.current_objects:
            o.draw()

    def interact(self):
        for o in self.current_objects:
            if o.interaction:
                o.interact()

    def move_objects(self):
        for o in self.current_objects:
            pass



