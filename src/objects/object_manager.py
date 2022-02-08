import pygame


class ObjectManager:
    def __init__(self, game):
        self.current_objects = []
        self.game = game
        self.interaction = True
        self.up = 0
        pygame.time.set_timer(pygame.USEREVENT, 500)
        self.hover = False

    def set_current_objects(self):
        self.current_objects.clear()
        for obj in self.game.world_manager.current_room.objects:
            self.current_objects.append(obj)
        if self.game.world_manager.next_room:
            for obj in self.game.world_manager.next_room.objects:
                self.current_objects.append(obj)

    def hover_event(self):
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                self.up += 1
                self.hover = True

    def update(self):
        self.hover_event()
        self.set_current_objects()
        for o in self.current_objects:
            if self.interaction:
                o.detect_collision()
            o.update()

    def draw(self):
        for o in self.current_objects:
            if o.name == 'next_level':
                o.draw()
        for o in self.current_objects:
            if o.name != 'next_level':
                o.draw()

    def interact(self):
        for o in self.current_objects:
            if o.interaction:
                if not o.for_sale:
                    o.interact()
                else:
                    o.buy()
