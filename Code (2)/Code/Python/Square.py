import math
import Config
import turtle as t
import time

communicate_with_arduino = True  # True pour communiquer

if communicate_with_arduino:
    import ArduinoController
    ArduinoController.up()

    
config = Config.Configuration("params.txt")

stepsPerSide = 400
turtle_size = 4
sideSize = min((config.height - 2 * config.margin_y),
               (config.length - 2 * config.margin_x)) * config.multi / 100
multi_y = 0.9


def trace_board(width, height):
    """Fonction tracant un rectangle en vert des dimensions appelées"""
    t.color("green")
    t.tracer(0)
    t.up()
    t.goto(-width / 2 * turtle_size, -height / 2 * turtle_size)
    t.down()
    t.goto(-width / 2 * turtle_size, height / 2 * turtle_size)
    t.goto(width / 2 * turtle_size, height / 2 * turtle_size)
    t.goto(width / 2 * turtle_size, -height / 2 * turtle_size)
    t.goto(-width / 2 * turtle_size, -height / 2 * turtle_size)
    t.color("black")


trace_board(config.length, config.height)  # Tracer les contours du tableau

t.up()
t.speed(1)
t.tracer(1)


# Traçage du carré grâce aux équations paramétriques
for i in range(stepsPerSide):
    x = sideSize / 2
    y = sideSize / 2 * (1 - i / stepsPerSide * 2)
    t.goto(x * turtle_size, y * turtle_size)
    if communicate_with_arduino:
        ArduinoController.send_coordinates((x, y*multi_y))
        ArduinoController.down()
    t.down()

time.sleep(4)


for i in range(stepsPerSide):
    x = sideSize / 2 * (1 - i / stepsPerSide * 2)
    y = -sideSize / 2
    if communicate_with_arduino:
        ArduinoController.send_coordinates((x, y*multi_y))
    t.goto(x * turtle_size, y * turtle_size)

time.sleep(4)

for i in range(stepsPerSide):
    x = -sideSize / 2
    y = sideSize / 2 * (-1 + i / (stepsPerSide) * 2)
    if communicate_with_arduino:
        ArduinoController.send_coordinates((x, y*multi_y))
    t.goto(x * turtle_size, y * turtle_size)

time.sleep(4)

for i in range(stepsPerSide + 1):
    x = sideSize / 2 * (-1 + i / stepsPerSide * 2)
    y = sideSize / 2
    if communicate_with_arduino:
        ArduinoController.send_coordinates((x, y*multi_y))
    t.goto(x * turtle_size, y * turtle_size)

time.sleep(4)

t.mainloop()
