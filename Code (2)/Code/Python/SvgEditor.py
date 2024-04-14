import math
import Config2 as Config
import turtle as t
import time

file_to_draw = "SvgFiles/WorldMapV3.svg"


# VARIABLES
size = 1

t.pensize(2)
t.tracer(1)
translation = 0, 0
last_pos_treshold = 0, 0
global turtle_size
turtle_size = 4
center = [Config.center_x, Config.center_y]


def cm_into_multi(request_height_in_cm):
    multi = request_height_in_cm / Config.height*100
    return multi


# Config.multi = cm_into_multi(Config.size)


def get_rectangle(coo):
    """Fonction trouvant les plus grands et plus bas x et y pour connaître la taille du dessin"""
    instructions = "MLCZ"
    largest_x = False
    largest_y = False
    smallest_x = False
    smallest_y = False
    i = 0
    while coo[i] not in instructions and i < len(coo) - 1:
        i += 1
    while i < len(coo) - 1:
        while i < len(coo) - 1 and coo[i] not in "0123456789.-":
            if coo[i] == '(':
                while i < len(coo) - 1 and coo[i] != ')':
                    i += 1
            if coo[i] == '#':
                i = len(coo) - 1
                break
            i += 1
        if i < len(coo) - 1:
            point, i = get_x_y(i - 1, coo)
            if largest_x == False or (point[0] > largest_x and point[0] != False):
                largest_x = point[0]
            if smallest_x == False or (point[0] < smallest_x and point[0] != False):
                smallest_x = point[0]
            if largest_y == False or (point[1] > largest_y and point[1] != False):
                largest_y = point[1]
            if smallest_y == False or (point[1] < smallest_y and point[1] != False):
                smallest_y = point[1]
    bottom_right = (largest_x, largest_y)
    bottom_left = (smallest_x, largest_y)
    top_left = (smallest_x, smallest_y)
    top_right = (largest_x, smallest_y)
    return bottom_right, bottom_left, top_left, top_right


def distance(pt1, pt2):
    """Fonction calculant la distance entre 2 points à l'aide de Pythagore"""
    return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5


def move_turtle(x, y, down):
    """Fonction faisant bouger le turtle, en prenant en compte si le stylo doit être déposé ou pas.
        Fait aussi bouger l'arduino et lever le bic"""
    global last_pos_treshold
    if down != "undefined":
        if down:
            t.down()
        else:
            t.up()
    if distance((x, y), last_pos_treshold) > Config.treshold:
        t.goto(x * turtle_size, y * turtle_size)
        last_pos_treshold = (x, y)


def get_coo(i, txt):
    """Fonction qui récupére les coordonées dans le fichier SVG"""
    coo = ""
    i += 1
    # Soit un chiffre, une virgule ou un tiret(signe négatif)
    while txt[i].isnumeric() or txt[i] == '.' or txt[i] == '-':
        coo += txt[i]  # Ajouter sur la "chaîne"
        i += 1
    if coo == '' or coo == '-':
        coo = False
    else:
        coo = float(coo)  # Transformation string en float
    return coo, i


def get_x_y(i, txt):
    x, i = get_coo(i, txt)
    if not x:
        return (False, False), i
    y, i = get_coo(i, txt)
    return (x * size + translation[0] + Config.center_x, -y * size + translation[1] + Config.center_y), i


def moveto(i, txt, last_move_pos):
    """Fonction qui permet le déplacement du turtle jusqu'au prochain point de départ"""
    t.up()
    i += 1
    i = get_x_y(i, txt)[1]
    i += 1
    return i, last_move_pos


def line(i, txt):
    """Fonction qui lit et trouve les coordonnées avec get_coo par ligne"""
    i += 1
    pt1, i = get_x_y(i, txt)
    pt2, i = get_x_y(i, txt)
    if pt2 == (False, False):
        return i, pt1
    move_turtle(pt1[0], pt1[1], "undefined")
    move_turtle(pt2[0], pt2[1], True)
    return i, pt1


def bezier_pos(x1, y1, x2, y2, x3, y3, ti):
    """Fonction qui calcule la courbe de Bézier"""
    return x2 + (1 - ti) ** 2 * (x1 - x2) + ti ** 2 * (x3 - x2), y2 + (1 - ti) ** 2 * (y1 - y2) + ti ** 2 * (y3 - y2)


def curve(i, txt):
    """Fonction qui renvoie les coordonnées à la fonction bezierPos"""
    i += 1
    pt1, i = get_x_y(i, txt)
    pt2, i = get_x_y(i, txt)
    pt3, i = get_x_y(i, txt)
    move_turtle(pt1[0], pt1[1], "undefined")
    for j in range(Config.curve_steps):
        ti = j / (Config.curve_steps - 1)
        xi, yi = bezier_pos(pt1[0], pt1[1], pt2[0], pt2[1], pt3[0], pt3[1], ti)
        move_turtle(xi, yi, True)
    return i, (bezier_pos(pt1[0], pt1[1], pt2[0], pt2[1], pt3[0], pt3[1], 0)[0],
               bezier_pos(pt1[0], pt1[1], pt2[0], pt2[1], pt3[0], pt3[1], 0)[1])


def adjustement_table(width_drawing, height_drawing):
    # Fonction qui calcule le multiplicateur pour que le dessin aie la taille  maximale
    multi_x = (Config.length - 2 * Config.margin_x) / width_drawing
    multi_y = (Config.height - 2 * Config.margin_y) / height_drawing
    return min(multi_x, multi_y)


def delta_coo(bot_left, top_right):
    # Retourne la longueur et hauteur du dessin svg
    return (abs(top_right[0] - bot_left[0]), abs(top_right[1] - bot_left[1]))


def center_and_resize(svg_file):
    # Fonction qui recentre le dessin et applique le multiplicateur sur le dessin
    global translation, size
    bottom_right, bottom_left, top_left, top_right = get_rectangle(svg_file)
    svg_size = delta_coo(bottom_left, top_right)
    print("adjustement_table" +
          str(adjustement_table(svg_size[0], svg_size[1])))
    print(bottom_right)
    size = Config.multi * adjustement_table(svg_size[0], svg_size[1]) / 100
    translation = -size * (bottom_right[0] + bottom_left[0]) / \
        2, -size * (top_right[1] + bottom_left[1]) / 2
    t.tracer(0)
    t.color("red")
    t.penup()
    # t.goto((bottom_right[0] * size + translation[0]) * turtle_size,
    #        (bottom_right[1] * size + translation[1]) * turtle_size)
    # t.pendown()
    # t.goto((bottom_left[0] * size + translation[0]) * turtle_size,
    #        (bottom_left[1] * size + translation[1]) * turtle_size)
    # t.goto((top_left[0] * size + translation[0]) * turtle_size,
    #        (top_left[1] * size + translation[1]) * turtle_size)
    # t.goto((top_right[0] * size + translation[0]) * turtle_size,
    #        (top_right[1] * size + translation[1]) * turtle_size)
    # t.goto((bottom_right[0] * size + translation[0]) * turtle_size,
    #        (bottom_right[1] * size + translation[1]) * turtle_size)
    t.color("black")
    t.tracer(1)


def trace_board(width, height):
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


def instructions_from_svg(svg_file):
    last_i = -1
    i = 0
    instructions = "MLCZ"
    t.tracer(1)
    last_move_pos = False
    last_instruct = False
    while i < len(svg_file):
        if i == len(svg_file) - 1:
            break
        while svg_file[i] not in instructions and i < len(svg_file) - 1:
            i += 1
        # Mettre un switch ici :
        print(i)
        if i > 0:
            input("About to execute : " +
                  str(svg_file[i:i+30]) + "\n press enter to continue")
        if i < len(svg_file):  # Instruction varie en fonction de la lettre
            if svg_file[i] == 'M':  # M=move
                i, lp = moveto(i, svg_file, last_move_pos)
                last_instruct = 'M'
                last_move_pos = False
            if svg_file[i] == 'L':  # L=line
                i, lp = line(i, svg_file)
                if last_instruct == 'M':
                    last_move_pos = lp
                    last_instruct = 'L'
            if svg_file[i] == 'C':  # C=curve
                i, lp = curve(i, svg_file)
                if last_instruct == 'M':
                    last_move_pos = lp
                    last_instruct = 'C'
            if svg_file[i] == 'Z':  # revenir au début du chemin
                i = len(svg_file)
                print("Found a Z!")
    if last_i == i:
        i += 1
    last_i = i
    t.tracer(1)


def draw(file_name):
    f = open(file_name, "r")
    svg_file = f.read()
    t.tracer(1)
    global size, translation
    size = 1
    translation = (0, 0)
    trace_board(Config.length, Config.height)
    center_and_resize(svg_file)
    t.tracer(1)
    print("Started drawing ! ")
    instructions_from_svg(svg_file)
    print("Finished")
    t.up()
    t.goto(0, 0)
    f.close()


draw(file_to_draw)
