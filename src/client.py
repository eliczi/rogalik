import socket
import pygame as pg

c = socket.socket()  # arguementss (IPV4, TCP)
HOST1 = '192.168.1.25'  # IPV4 address of the server
PORT = 7070
c.connect((HOST1, PORT))  # connects client to an address
msg = c.recv(64)  # recieves a packet of 64 bytes from server
print(msg.decode('utf-8'))  # decodes bytes into string

name = input()
c.send(bytes(name, 'utf-8'))  # encodes name string to bytes and sends to server

pg.init()  # initiates pygame window

screen = pg.display.set_mode((200, 200), pg.RESIZABLE)  # all operations must be performed on pg screen
done = False
pg.joystick.init()
if pg.joystick.get_count() != 0:  # checks whether a joystick is connected
    joystick = pg.joystick.Joystick(0)
    print(joystick)
    joystick.init()

while not done:
    button = "No Button is Pressed"  # deafult msg
    if pg.joystick.get_count() != 0:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
        axis1 = joystick.get_axis(1)  # gets front and back value from left stick of joystick
        axis1 = int(-100 * axis1)  # converts 8 point float value to 0-100 range
        axis0 = joystick.get_axis(0)  # gets left/ back value from left stick
        axis0 = int(100 * axis0)
        axis2 = joystick.get_axis(2)  # gets left and right trigger values
        axis2 = int(100 * axis2)
        A = joystick.get_button(0)  # following buttons return bool value if (not) pressed
        B = joystick.get_button(1)
        Y = joystick.get_button(3)
        X = joystick.get_button(2)
        LB = joystick.get_button(4)
        RB = joystick.get_button(5)
        START = joystick.get_button(7)
        keys = pg.key.get_pressed()
        if A == 1:
            button = "A is pressed"  # button is the message to be sent
        if B == 1:
            button = "B is pressed"
        if Y == 1:
            button = "Y is pressed"  # button takes values accordingly
        if X == 1:
            button = "X is pressed"
        if LB == 1:
            button = "LB is pressed"
        if RB == 1:
            button = "RB is pressed"
        if START == 1:  # press START button on joystick to QUIT
            done = True
        if axis1 < -25:  # ignoring small values
            button = ("BACK by: " + str(-axis1 / 100))  # we must keep button completely a string to encode into bytes
        if axis1 > 25:
            button = ("FORWARD by: " + str(axis1 / 100))
        if axis0 < -25:
            button = ("LEFT by: " + str(-axis0 / 100))
        if axis0 > 25:
            button = ("RIGHT by: " + str(axis0 / 100))
        if axis2 > 10:
            button = ("LT is pressed: " + str(axis2 / 100))
        if axis2 < -10:
            button = ("RT is pressed: " + str(-axis2 / 100))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT]:  # arrow keys on keyboard upon pressing
        button = "KEY LEFT"
    elif keys[pg.K_RIGHT]:
        button = "KEY RIGHT"
    elif keys[pg.K_UP]:
        button = "KEY UP"
    elif keys[pg.K_DOWN]:
        button = "KEY DOWN"
    elif keys[pg.K_ESCAPE]:  # press ESC to QUIT
        done = True

    HEADER = chr(len(button))  # chr() returns the character whose ASCII value is passed to it
    # HEADER stores the character whose ASCII value is length of button
    c.send(bytes(HEADER, 'utf-8'))  # first we send HEADER so the server knows the length of button to recieve
    c.send(bytes(button, 'utf-8'))  # sending button to server

pg.quit()  # quit pygame window
