import pygame


class ObjectManager:
    def __init__(self, game):
        self.current_objects = []
        self.game = game
        self.interaction = True
        self.up = 0
        pygame.time.set_timer(pygame.USEREVENT, 500)
        self.hover = False
        self.position = 0

    def set_current_objects(self):
        self.current_objects.clear()
        for obj in self.game.world_manager.current_room.objects:
            self.current_objects.append(obj)
        if self.game.world_manager.next_room:
            for obj in self.game.world_manager.next_room.objects:
                self.current_objects.append(obj)

    def delete_items(self):
        for obj in self.game.world_manager.current_room.objects:
            obj.remove_object()

    def first_weapon(self):
        if (
                self.game.world_manager.current_room.type == 'starting_room'
                and self.game.world_manager.level == 1
                and self.game.player.weapon
        ):
            self.delete_items()

    def update(self):
        self.set_current_objects()
        for o in self.current_objects:
            if self.interaction:
                o.detect_collision()
            o.update()
        self.hover = False
        self.first_weapon()

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
