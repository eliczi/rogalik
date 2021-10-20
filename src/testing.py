import random


# random map layout generator
def generator():
    w, h = 4, 4  # world size
    world = [[0 for x in range(w)] for y in range(h)]
    start_x, start_y = random.randint(0, w - 1), random.randint(0, h - 1)
    world[start_x][start_y] = 1  # starting position
    i = 0
    num_of_rooms = 3
    current_room_x = start_x
    current_room_y = start_y

    my_dict = {"left": False,
               "right": False,
               "up": False,
               "down": False}
    map_info = []
    while i != num_of_rooms:
        c = random.choice(["up", 'down', 'left', 'right'])
        if c == 'up' and current_room_x - 1 > 0:
            if world[current_room_x - 1][current_room_y] != 1:
                world[current_room_x - 1][current_room_y] = 1
                current_room_x -= 1
                i += 1
                room_dict = my_dict.copy()
                room_dict['up'] = True
                map_info.append([i, room_dict])
        elif c == 'down' and current_room_x + 1 < 3:
            if world[current_room_x + 1][current_room_y] != 1:
                world[current_room_x + 1][current_room_y] = 1
                current_room_x += 1
                i += 1
                room_dict = my_dict.copy()
                room_dict['down'] = True
                map_info.append([i, room_dict])
        elif c == 'right' and current_room_y + 1 < 3:
            if world[current_room_x][current_room_y + 1] != 1:
                world[current_room_x][current_room_y + 1] = 1
                current_room_y += 1
                i += 1
                room_dict = my_dict.copy()
                room_dict['right'] = True
                map_info.append([i, room_dict])
        elif c == 'left' and current_room_y - 1 > 0:
            if world[current_room_x][current_room_y - 1] != 1:
                world[current_room_x][current_room_y - 1] = 1
                current_room_y -= 1
                i += 1
                room_dict = my_dict.copy()
                room_dict['left'] = True
                map_info.append([i, room_dict])

    for row in world:
        print(row)
    return map_info



my_map = generator()
for row in my_map:
    print(row)