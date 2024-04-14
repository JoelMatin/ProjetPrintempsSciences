import math
import Config
import turtle as t
import math
import time


config = Config.Configuration("params.txt")
# Activer la communication avec l'Arduino
communicate_with_arduino = True  # True pour communiquer
generate_arduino_code = False

if communicate_with_arduino:
    import ArduinoController
    ArduinoController.up()

# VARIABLES
steps = 360  # Nombre d'étapes
turtle_size = 4  # Taille de la tortue
t.shape("turtle")
sideSquare = min((config.height - 2 * config.margin_y),
                 (config.length - 2 * config.margin_x)) * config.multi / 100
radius = sideSquare / 2
multi_y = 0.85


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


trace_board(config.length, config.height)  # Tracer le contour du tableau

t.up()
t.speed(10)
t.tracer(1)


# Traçage du cercle grâce aux équations paramétriques
for i in range(steps):
    x = radius * (math.cos(2 * math.pi * i / (steps - 1)))
    y = radius * (math.sin(2 * math.pi * i / (steps - 1)))
    t.goto(x * turtle_size, y * turtle_size*multi_y)
    if communicate_with_arduino:
        ArduinoController.send_coordinates((x, y*multi_y))
        ArduinoController.down()
    # if generate_arduino_code:
    #     ArduinoCodeGenerator.print_instruction((x, y*multi_y))
    t.down()


# if generate_arduino_code:
#     file = open("monfichier.txt", "w")
#     file.write(str(ArduinoCodeGenerator.liste_motor_1))
#     file.write("\n")
#     file.write(str(ArduinoCodeGenerator.liste_motor_2))
#     file.close()
#     print(len(ArduinoCodeGenerator.liste_motor_1))


t.mainloop()
