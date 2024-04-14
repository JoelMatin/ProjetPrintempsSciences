import math
import Config
import turtle as t
import time


# Activer la communication avec l'Arduino
communicate_with_arduino = True  # True pour communiquer
print("Starting")
dessin = "circle"

if communicate_with_arduino:
    import ArduinoControllerGettingError

# VARIABLES
size = 1

translation = 0, 0
last_pos_treshold = 0, 0
global turtle_size
turtle_size = 4
config = Config.Configuration("params.txt")
center = [config.center_x, config.center_y]
follow_fixed_cm_size = False


def get_rectangle(coo):
    """Fonction trouvant les plus grands et plus bas x et y pour connaître la taille du dessin"""
    global size, translation
    size = 1
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
    # if communicate_with_arduino:
    #     ArduinoController.down()
    if down != "undefined":
        if down:
            t.down()
            if communicate_with_arduino:
                ArduinoControllerGettingError.down()
        else:
            t.up()
            if communicate_with_arduino:
                ArduinoControllerGettingError.up()
    if distance((x, y), last_pos_treshold) > config.treshold:
        if communicate_with_arduino:
            ArduinoControllerGettingError.send_coordinates((x, y))
            # time.sleep(1)
        t.goto(x * turtle_size, y * turtle_size)
        last_pos_treshold = (x, y)


def get_coo(i, txt):
    """Fonction qui récupére les coordonées dans le fichier SVG"""
    coo = ""

    if i + 3 > len(txt):
        return False, i + 3
    i += 1
    if txt[i] == ' ':
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
    return (x * size + translation[0] + config.center_x, -y * size + translation[1] + config.center_y), i


def moveto(i, txt, last_move_pos):
    """Fonction qui permet le déplacement du turtle jusqu'au prochain point de départ"""
    t.up()
    n = 10
    if communicate_with_arduino:
        ArduinoControllerGettingError.up()
    coo, i = get_x_y(i, txt)
    #move_turtle(coo[0], coo[1], False)
    if last_move_pos != False:
        vector_0 = coo[0] - last_move_pos[0]
        vector_1 = coo[1] - last_move_pos[1]
        for j in range(n+1):
            addable_0 = last_move_pos[0] + vector_0*(j / n)
            addable_1 = last_move_pos[1] + vector_1*(j / n)
            move_turtle(addable_0, addable_1, False)
    else:
        move_turtle(coo[0], coo[1], False)
    #move_turtle(coo[0], coo[1], False)
    # print("t1")
    move_turtle(coo[0], coo[1], True)
    # print("t2")
    i += 1
    return i, coo


def line(i, txt):
    """Fonction qui lit et trouve les coordonnées avec get_coo par ligne"""
    #i += 1
    """pt1, i = get_x_y(i, txt)
    pt2, i = get_x_y(i, txt)
    if pt2 == (False, False):
        move_turtle(pt1[0], pt1[1], "undefined")
        return i, pt1
    move_turtle(pt1[0], pt1[1], "undefined")
    move_turtle(pt2[0], pt2[1], True)
    return i, pt2"""
    pt, i = get_x_y(i, txt)
    move_turtle(pt[0], pt[1], "undefined")
    move_turtle(pt[0], pt[1], True)
    new_i = i
    new_pt = pt
    while new_pt != (False, False):
        last_pt = pt
        pt = new_pt
        i = new_i
        vector = (new_pt[0] - last_pt[0], new_pt[1] - last_pt[1])
        num_of_steps = 30
        for j in range(1, num_of_steps + 1):
            move_turtle(last_pt[0] + j / num_of_steps * vector[0],
                        last_pt[1] + j / num_of_steps * vector[1], True)
        i -= 1
        new_pt, new_i = get_x_y(i, txt)
    return i, pt


def bezier_pos_old(x1, y1, x2, y2, x3, y3, ti):
    """Fonction qui calcule la courbe de Bézier"""
    return x2 + (1 - ti) ** 2 * (x1 - x2) + ti ** 2 * (x3 - x2), y2 + (1 - ti) ** 2 * (y1 - y2) + ti ** 2 * (y3 - y2)


def bezier_pos(x0, y0, x1, y1, x2, y2, x3, y3, ti):
    """Fonction qui calcule la courbe de Bézier"""
    return x0 * (1 - ti) ** 3 + x1 * 3 * (1 - ti) ** 2 * ti + x2 * 3 * (1 - ti) * ti ** 2 + x3 * ti ** 3, \
        y0 * (1 - ti) ** 3 + y1 * 3 * (1 - ti) ** 2 * ti + \
        y2 * 3 * (1 - ti) * ti ** 2 + y3 * ti ** 3


def curve(i, txt, lp):
    """Fonction qui renvoie les coordonnées à la fonction bezierPos"""
    i += 1
    pt1, i = get_x_y(i, txt)
    pt2, i = get_x_y(i, txt)
    pt3, i = get_x_y(i, txt)

    origin = bezier_pos(lp[0], lp[1],  pt1[0], pt1[1],
                        pt2[0], pt2[1], pt3[0], pt3[1], 0)
    move_turtle(origin[0], origin[1], "undefined")
    for j in range(0, Config.curve_steps):
        ti = j / (Config.curve_steps - 1)
        xi, yi = bezier_pos(lp[0], lp[1],  pt1[0], pt1[1],
                            pt2[0], pt2[1], pt3[0], pt3[1], ti)
        move_turtle(xi, yi, True)
    return i, (bezier_pos(lp[0], lp[1],  pt1[0], pt1[1], pt2[0], pt2[1], pt3[0], pt3[1], 1)[0],
               bezier_pos(lp[0], lp[1],  pt1[0], pt1[1], pt2[0], pt2[1], pt3[0], pt3[1], 1)[1])


def adjustement_table(width_drawing, height_drawing):
    # Fonction qui calcule le multiplicateur pour que le dessin aie la taille  maximale
    width_drawing = max(width_drawing, 1)
    multi_x = (config.length - 2 * config.margin_x) / width_drawing
    multi_y = (config.height - 2 * config.margin_y) / height_drawing
    if follow_fixed_cm_size:

        multi_x = (config.length - 2 * config.margin_x) / \
            max(width_drawing, height_drawing)
        multi_y = (config.height - 2 * config.margin_y) / \
            max(width_drawing, height_drawing)

        multi_x = (config.length - 2 * config.margin_x) / \
            max(width_drawing, height_drawing)
        multi_y = (config.height - 2 * config.margin_y) / \
            max(width_drawing, height_drawing)

    return min(multi_x, multi_y)


def delta_coo(bot_left, top_right):
    # Retourne la longueur et hauteur du dessin svg
    return (abs(top_right[0] - bot_left[0]), abs(top_right[1] - bot_left[1]))


def center_and_resize(svg_file):
    # Fonction qui recentre le dessin et applique le multiplicateur sur le dessin
    global translation, size
    bottom_right, bottom_left, top_left, top_right = get_rectangle(svg_file)
    svg_size = delta_coo(bottom_left, top_right)
    print(config.multi)
    size = config.multi * adjustement_table(svg_size[0], svg_size[1]) / 100
    translation = -size * (bottom_right[0] + bottom_left[0]) / \
        2, -size * (top_right[1] + bottom_left[1]) / 2
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


wasM = False


def instructions_from_svg(svg_file):
    global wasM
    last_i = -1
    i = 0
    instructions = "MLCZ"
    t.tracer(1)
    last_move_pos = False
    while i < len(svg_file):
        if i == len(svg_file) - 1:
            break
        while svg_file[i] not in instructions and i < len(svg_file) - 1:
            i += 1
        # Mettre un switch ici :
        if i < len(svg_file):  # Instruction varie en fonction de la lettre
            print("   ")
            print(svg_file[i:i+15])
            # time.sleep(15)
            if svg_file[i] == 'M':  # M=move
                i, lp = moveto(i, svg_file, last_move_pos)
                last_move_pos = lp
                wasM = True
                continue
            if svg_file[i] == 'L':  # L=line
                i, lp = line(i, svg_file)
                last_move_pos = lp
                continue
            if svg_file[i] == 'C':  # C=curve
                i, lp = curve(i, svg_file, last_move_pos)
                last_move_pos = lp
                wasM = False
                continue
            if svg_file[i] == 'Z':  # revenir au début du chemin
                i = len(svg_file)
                print("Found a Z!")
        if last_i == i:
            i += 1
        last_i = i
    t.tracer(1)


def draw(file_name):  # fonction principale
    # print(config.center_x)
    if communicate_with_arduino:
        ArduinoControllerGettingError.config = config
        ArduinoControllerGettingError.l_1_i = config.rope_left
        ArduinoControllerGettingError.l_2_i = config.rope_right
    f = open(file_name, "r")
    svg_file = f.read()
    t.pensize(2)
    t.tracer(1)
    t.up()
    print("Getting coordonates ! ")
    t.tracer(1)
    global size, translation
    size = 1
    translation = (0, 0)
    trace_board(config.length, config.height)
    center_and_resize(svg_file)
    t.tracer(1)
    print("Started drawing ! ")
    instructions_from_svg(svg_file)
    print("Finished")
    t.up()
    t.goto(0, 0)
    f.close()


if __name__ == "__main__":
    if communicate_with_arduino:
        ArduinoControllerGettingError.wait_for_answer("D")
        time.sleep(1)
    draw("SvgFiles/" + dessin + ".svg")
    t.mainloop()
