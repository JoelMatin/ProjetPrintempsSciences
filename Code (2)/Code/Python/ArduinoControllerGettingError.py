import Config
import serial
import time
import math
import turtle as t
from os.path import exists

config = Config.Configuration("params.txt")

# VARIABLES

# longueurs initiales des cordes sur le tableau
l_1_i = config.rope_left
l_2_i = config.rope_right

arduinoUp = True

arduino_nano = serial.Serial(
    port=Config.port, baudrate=Config.baudrate, timeout=.1)  # Désignation du port utilisé

num = 0
while exists("Data_from_arduino" + str(num) + ".txt"):
    num += 1

def read_arduino_data():
    """Fonction permettant de recevoir des informations de l'arduino"""
    return arduino_nano.readline().decode('utf-8').rstrip()


def send_arduino_data(data):
    """Fonction permettant d'envoyer des informations à l'arduino"""
    print("Send : ")
    print(data)
    arduino_nano.write(bytes(str(data), 'utf-8'))


def initialise():
    """Fonction permettant de laisser du temps a serial pour s'initialiser"""
    time.sleep(0.09)
    time.sleep(2)


def distance(a, b):
    """Fonction qui calcule la longueur de la corde avec Pythagore"""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def up():
    """Fonction qui dit à l'arduino de lever le bic"""
    global arduinoUp
    if not arduinoUp:
        arduinoUp = True
        time.sleep(2)
        print("Asking the arduino to up the pen")
        send_arduino_data('U')
        wait_for_answer('D')
        print("done")


def down():
    """Fonction qui dit à l'arduino de descendre le bic"""
    global arduinoUp
    if arduinoUp:
        arduinoUp = False
        time.sleep(2)
        print("Asking the arduino to down the pen")
        send_arduino_data('D')
        wait_for_answer('D')
        print("done")


def rope_lengths_from_coo(coo):
    """ Fonction qui donne la longueur de chaque corde pour une coordonnée coo (du point en haut du traceur)"""
    wanted_motor1_pos = (
        coo[0] - Config.length_between_motors / 2, coo[1])  # origine au centre du tableau
    wanted_motor2_pos = (
        coo[0] + Config.length_between_motors / 2,  coo[1])
    # Le coin supérieur gauche est à la moitié de la largeur vers la gauche et la moitié de la hauteur vers le haut
    length_1 = distance(wanted_motor1_pos, (-config.length/2, config.height/2))
    length_2 = distance(wanted_motor2_pos, (config.length/2, config.height/2))
    return length_1, length_2


def rope_between_points(l_1_i, l_2_i, l_1_f, l_2_f):
    """Retourne le déplacement de chaque cordes ==> delta(l)"""
    return (l_1_i-l_1_f, l_2_i-l_2_f)


def from_delta_turn(delta, perimeter):
    """Fonction calculant l'angle (en°) a enrouler/dérouler selon la longueur de corde à dérouler """
    angle_1 = delta[0]/perimeter * 360
    angle_2 = delta[1]/perimeter * 360
    if angle_1 > 0:
        angle_1 += 1
    else:
        angle_1 -= 1
    if angle_2 > 0:
        angle_2 += 1
    else:
        angle_2 -= 1
    return (angle_1, angle_2)


def wait_for_answer(answer):
    """Fonction bloquant le code tant que l'Arduino n'a pas répondu"""
    data = read_arduino_data()
    print("waiting")
    while answer not in data:
        data += read_arduino_data()
        print(data)
        print("data : ")
    f = open("Data_from_arduino" + str(num) + ".txt", 'a')
    f.write(str(data).replace(answer, ""))
    f.write("\n")
    f.close()


def get_u(rotation, relative_board_pos):
    u_go_down_bottom = -25
    u_go_down_top = -15

    u_go_up_bottom = 70
    u_go_up_top = 90

    if rotation > 0:
        u = u_go_up_bottom + \
            (u_go_up_top - u_go_up_bottom) * relative_board_pos
    else:
        u = u_go_down_bottom + \
            (u_go_down_top - u_go_down_bottom) * relative_board_pos

    return int(u)


def send_coordinates(coo):
    """Fonction qui calcule la longueur de corde à enrouler/dérouler pour aller du point 1 au point 2 et envoyant les angles correspondants à l'Arduino"""
    global l_1_i, l_2_i
    coo = (coo[0], coo[1])
    lenghts = rope_lengths_from_coo(coo)
    delta_l = rope_between_points(l_1_i, l_2_i, lenghts[0], lenghts[1])
    circumference = 2*math.pi*Config.radius
    (rotation_1, rotation_2) = from_delta_turn(delta_l, circumference)

    relative_board_pos = (coo[1] + config.height / 2) / config.height
    print("T" + str(rotation_1)[0:7] + ':' + str(rotation_2)[0:7] + ':' +
          str(get_u(rotation_1, relative_board_pos)) + ':' + str(get_u(rotation_2, relative_board_pos)))
    send_arduino_data("T" + str(rotation_1)[0:7] + ':' + str(rotation_2)[0:7] + ':' +
                      str(get_u(rotation_1, relative_board_pos)) + ':' + str(get_u(rotation_2, relative_board_pos)))
    print("Waiting for answer")
    wait_for_answer("D")
    print("Answer received")
    l_1_i = lenghts[0]
    l_2_i = lenghts[1]


initialise()
if __name__ == "__main__":
    time.sleep(2)
    send_arduino_data("T55:5:0:0")
    wait_for_answer("D")
