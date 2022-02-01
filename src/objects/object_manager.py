import pygame


class ObjectManager:
    def __init__(self, game):
        self.current_objects = []
        self.game = game
        self.interaction = True

    def set_current_objects(self):
        self.current_objects.clear()
        for obj in self.game.world_manager.current_room.objects:
            self.current_objects.append(obj)
        if self.game.world_manager.next_room:
            for obj in self.game.world_manager.next_room.objects:
                self.current_objects.append(obj)

    def update(self):
        self.set_current_objects()
        for o in self.current_objects:
            if self.interaction:
                o.detect_collision()
            o.update()

    def draw(self):
        for o in self.current_objects:
            o.draw()

    def interact(self):
        for o in self.current_objects:
            if o.interaction:
                if not o.for_sale:
                    o.interact()
                else:
                    o.buy()
