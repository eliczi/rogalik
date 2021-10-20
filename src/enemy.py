import random
import pygame
import math
import os


def draw_health_bar(surf, pos, size, border_c, back_c, health_c, progress):
    """

    :param surf:
    :type surf:
    :param pos:
    :type pos:
    :param size:
    :type size:
    :param border_c:
    :type border_c:
    :param back_c:
    :type back_c:
    :param health_c:
    :type health_c:
    :param progress:
    :type progress:
    :return:
    :rtype:
    """
    pygame.draw.rect(surf, back_c, (*pos, *size))
    pygame.draw.rect(surf, border_c, (*pos, *size), 1)
    inner_pos = (pos[0] + 1, pos[1] + 1)
    inner_size = ((size[0] - 2) * progress, size[1] - 2)
    rect = (round(inner_pos[0]), round(inner_pos[1]), round(inner_size[0]), round(inner_size[1]))
    pygame.draw.rect(surf, health_c, rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, speed, max_hp, name, *groups):
        super().__init__(*groups)
        self.name = name
        self.animation_database = {"IDLE_LEFT": [],
                                   "IDLE_RIGHT": [],
                                   "WALK_LEFT": [],
                                   "WALK_RIGHT": [],
                                   "HURT_LEFT": [],
                                   "HURT_RIGHT": []}

        self.player_index = 0
        self.game = game
        self.max_hp = max_hp
        self.hp = self.max_hp
        enemy_side = int(self.set_side())
        self.image_size = (15 * enemy_side, 15 * enemy_side)
        self.image = pygame.image.load("../assets/goblin/idle/right_idle0.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, self.image_size)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.mask.get_rect()
        self.rect_mask = None  # Get rect of some size as 'image'.
        self.spawn()
        self.speed = speed
        self.velocity = [0, 0]
        self.old_velocity = [0, 0]
        self.priority = 100
        self.step = 400
        self.direction = "UP"
        self.load_animation('../assets/goblin/')
        self.hitbox = None
        self.hurt = False
        self.counter = 0

    def getMaskRect(self, surf, top: int = 0, left: int = 0) -> None:
        """

        :param surf:
        :type surf:
        :param top:
        :type top:
        :param left:
        :type left:
        :return:
        :rtype:
        """
        surf_mask = pygame.mask.from_surface(surf)
        rect_list = surf_mask.get_bounding_rects()
        surf_mask_rect = rect_list[0].unionall(rect_list)
        surf_mask_rect.move_ip(top, left)
        return surf_mask_rect

    def load_animation(self, path):
        """

        :param path:
        :type path:
        :return:
        :rtype:
        """
        animation_states = os.listdir(path)
        for state in animation_states:
            substates = os.listdir(path + state)
            for ss in substates:
                image_loc = ss
                elements = image_loc.split('_')
                key = state.upper() + '_' + elements[0].upper()  # key to dictionary
                animation_image = pygame.image.load(path + state + '/' + image_loc).convert()
                animation_image = pygame.transform.scale(animation_image, self.image_size)
                self.animation_database[key].append(animation_image)

    def moving(self):
        """

        :return:
        :rtype:
        """
        if self.old_velocity != self.velocity:
            return True
        else:
            return False

    def check_direction(self):
        '''old rect.x - rect.x > '''

    def animation(self):
        """

        :return:
        :rtype:
        """
        if self.counter >= 4:
            self.hurt = False
            self.counter = 0
        if self.hurt and self.counter <= 4:  # if hurt
            if self.player_index >= 4:
                self.player_index = 0
            self.image = self.animation_database["HURT_RIGHT"][2]  # just the red animation
            #self.player_index += 0.035
            self.counter += 0.2

        elif self.moving():  # if moving
            self.player_index += 0.035  # how fast animation changes
            if self.player_index >= 4:
                self.player_index = 0
            if self.direction == 'LEFT':
                self.image = self.animation_database["WALK_LEFT"][int(self.player_index)]
            elif self.direction == 'UP':
                self.image = self.animation_database["WALK_RIGHT"][int(self.player_index)]
            elif self.direction == "RIGHT":
                self.image = self.animation_database["WALK_RIGHT"][int(self.player_index)]
            elif self.direction == "DOWN":
                self.image = self.animation_database["WALK_RIGHT"][int(self.player_index)]
        else:  # if idle
            self.player_index += 0.035  # how fast animation changes
            if self.player_index >= 4:
                self.player_index = 0
            if self.direction == 'LEFT':
                self.image = self.animation_database["IDLE_LEFT"][int(self.player_index)]
            elif self.direction == 'RIGHT':
                self.image = self.animation_database["IDLE_RIGHT"][int(self.player_index)]
            elif self.direction == "UP":
                self.image = self.animation_database["IDLE_RIGHT"][int(self.player_index)]
            elif self.direction == "DOWN":
                self.image = self.animation_database["IDLE_RIGHT"][int(self.player_index)]

    def set_side(self):
        """

        :return:
        :rtype:
        """
        enemy_side = self.max_hp / 10
        return enemy_side

    def spawn(self):
        self.rect.x = 250
        self.rect.y = 100
        self.rect_mask = self.getMaskRect(self.image, *self.rect.topleft)
        self.hitbox = self.rect_mask
        # """
        #
        # :return:
        # :rtype:
        # """
        # spawned = False
        # while not spawned:
        #     spawn_point = self.game.map.spawn_points[random.randint(0, len(self.game.map.spawn_points) - 1)]
        #     if spawn_point[1]:
        #         spawn_point_y = spawn_point[0]
        #         spawn_point_x = spawn_point[1][random.randint(0, len(spawn_point[1]) - 1)]
        #         self.rect.x = spawn_point_x
        #         self.rect.y = spawn_point_y
        #
        #         self.rect_mask = self.getMaskRect(self.image, *self.rect.topleft)
        #         self.hitbox = self.rect_mask
        #         spawned = True

    def update(self):
        """

        :return:
        :rtype:
        """

        self.animation()
        self.hitbox = pygame.Rect(self.rect.x + 19, self.rect.y + 26, 37, 52)


    def move(self, dtick):
        """

        :param dtick:
        :type dtick:
        :return:
        :rtype:
        """
        threshold = random.randrange(1, 20)
        if self.step >= threshold:
            self.old_velocity = self.velocity

            # self.velocity[0] = random.randint(-self.speed, self.speed) * dtick
            # self.velocity[1] = random.randint(-self.speed, self.speed) * dtick
            self.move_towards_player(self.game.player, dtick)  # zmiana
            self.step = 0
            # self.find_target(dtick, self.game.player)
        self.step += 1

    def move_towards_player(self, player, dtick):
        """

        :param player:
        :type player:
        :param dtick:
        :type dtick:
        :return:
        :rtype:
        """
        # Find direction vector (dx, dy) between enemy and player.
        dirvect = pygame.math.Vector2(player.rect.x - self.rect.x,
                                      player.rect.y - self.rect.y)
        if dirvect.length_squared() > 0:
            dirvect.normalize()
            # Move along this normalized vector towards the player at current speed.
            dirvect.scale_to_length(self.speed * 3 * dtick)
        self.rect.move_ip(dirvect)
        self.rect_mask.move_ip(dirvect)

    def find_target(self, dtick, target):
        """

        :param dtick:
        :type dtick:
        :param target:
        :type target:
        :return:
        :rtype:
        """
        dist_to_target_x = target.rect.x - self.rect.x
        dist_to_target_y = target.rect.x - self.rect.y

        self.velocity[0] = dist_to_target_x / self.speed * dtick * 10
        self.velocity[1] = dist_to_target_y / self.speed * dtick * 10

    def collision(self, collided):
        """

        :param collided:
        :type collided:
        :return:
        :rtype:
        """
        pass

    def draw_health(self, surf):
        """

        :param surf:
        :type surf:
        :return:
        :rtype:
        """
        if self.hp < self.max_hp:
            health_rect = pygame.Rect(0, 0, 20, 5)
            health_rect.midbottom = self.rect.centerx, self.rect.top
            draw_health_bar(surf, health_rect.topleft, health_rect.size,
                            (0, 0, 0), (255, 0, 0), (0, 255, 0), self.hp / self.max_hp)


class EnemySlow(Enemy):
    def __init__(self, game, speed, max_hp , name, *groups):
        super().__init__(game, speed, max_hp, name, *groups)

    def move(self, dtick):
        """

        :param dtick:
        :type dtick:
        :return:
        :rtype:
        """
        self.old_velocity = self.velocity
        self.velocity[0] = random.randint(-(self.max_hp - self.hp), (self.max_hp - self.hp)) / 200
        self.velocity[1] = random.randint(-(self.max_hp - self.hp), (self.max_hp - self.hp)) / 200

    def set_side(self):
        """

        :return:
        :rtype:
        """
        enemy_side = int(self.hp / 10)
        return enemy_side

    def update_size(self):
        """

        :return:
        :rtype:
        """
        pos_x = self.rect.x
        pos_y = self.rect.y
        self.image = pygame.transform.smoothscale(self.image, (self.set_side(), self.set_side()))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self):
        """

        :return:
        :rtype:
        """
        self.update_size()
        self.rect.move_ip(*self.velocity)
