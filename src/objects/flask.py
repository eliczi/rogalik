from .object import Object


class Flask(Object):
    def __init__(self, game, name, size, room, position):
        Object.__init__(self, game, name, size, room, position)

    def interact(self):
        if not self.game.player.weapon:
            self.game.player.weapon = self
        self.game.player.items.append(self)
        if self.room == self.game.room:
            self.room.objects.remove(self)
        self.interaction = False
        self.show_name.reset_line_length()

    def update(self):
        if self in self.game.player.items:
            self.rect.bottomright= self.game.player.hitbox.topleft
            self.image = self.original_image