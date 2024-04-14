# RUN pour avoir l'interface sur internet (cliquer sur le lien)

import time
from audioop import add
import os
import turtle as t
from flask import Flask, render_template, request
import Config

app = Flask(__name__)
l = []


config = Config.Configuration("params.txt")
# -------------------------------------------------------------------------------------------------------------------


# Activer la communication avec l'Arduino
communicate_with_arduino = False  # True pour communiquer
dessin = "commu"

if communicate_with_arduino:
    import ArduinoController

# VARIABLES
size = 1


translation = 0, 0
last_pos_treshold = 0, 0
global turtle_size
turtle_size = 4
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
    if down != "undefined":
        if down:
            t.down()
            if communicate_with_arduino:
                ArduinoController.down()
        else:
            t.up()
            if communicate_with_arduino:
                ArduinoController.up()
    print("move_turtle 1")
    if distance((x, y), last_pos_treshold) > config.treshold:
        print("move_turtle 2")
        if communicate_with_arduino:
            ArduinoController.send_coordinates((x, y))

        t.goto(x * turtle_size, y * turtle_size)
        print("move_turtle 3")

        last_pos_treshold = (x, y)
        print("move_turtle 4")


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
        ArduinoController.up()
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
    move_turtle(coo[0], coo[1], True)
    i += 1
    return i, coo


def line(i, txt):
    """Fonction qui lit et trouve les coordonnées avec get_coo par ligne"""
    pt, i = get_x_y(i, txt)
    print("Moveturtle 1")
    move_turtle(pt[0], pt[1], "undefined")
    print("Moveturtle 2")
    move_turtle(pt[0], pt[1], True)
    print("Moveturtle 3")
    new_i = i
    new_pt = pt
    while new_pt != (False, False):
        print("Moveturtle 4")
        last_pt = pt
        pt = new_pt
        i = new_i
        vector = (new_pt[0] - last_pt[0], new_pt[1] - last_pt[1])
        num_of_steps = 100
        for j in range(1, num_of_steps + 1):
            print("Moveturtle 4a")
            move_turtle(last_pt[0] + j / num_of_steps * vector[0],
                        last_pt[1] + j / num_of_steps * vector[1], True)
            print("Moveturtle 4b")
        i -= 1
        print("Moveturtle 5")
        new_pt, new_i = get_x_y(i, txt)
        print("Moveturtle 6")
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
                print("M")
                i, lp = moveto(i, svg_file, last_move_pos)
                last_move_pos = lp
                wasM = True
                continue
            if svg_file[i] == 'L':  # L=line
                print("L")
                i, lp = line(i, svg_file)
                print("L2")
                last_move_pos = lp
                continue
            if svg_file[i] == 'C':  # C=curve
                print("C")
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
    print("DRAW 1")
    if communicate_with_arduino:
        ArduinoController.config = config
        ArduinoController.l_1_i = config.rope_left
        ArduinoController.l_2_i = config.rope_right
    f = open(file_name, "r")
    print("DRAW 2")
    svg_file = f.read()
    print("DRAW 3")
    t.pensize(2)
    print("DRAW 4")
    t.tracer(1)
    t.up()
    print("Getting coordonates ! ")
    t.tracer(1)
    global size, translation
    size = 1
    translation = (0, 0)
    print("DRAW 5")
    trace_board(config.length, config.height)
    print("DRAW 6")
    center_and_resize(svg_file)
    print("DRAW 7")
    t.tracer(1)
    print("Started drawing ! ")
    instructions_from_svg(svg_file)
    print("Finished")
    t.up()
    t.goto(0, 0)
    print("DRAW 8")
    f.close()


# ---------------------------------------------------------------------------------------------------------------------
def isnotempty(var, default):
    if var == "":
        var = default
    return float(var)


def get_rectangle_from_svg(name):
    content = ""
    f = open(name, "r", encoding='utf-8')
    for i in f.read():
        content += i
    f.close()
    return get_rectangle(content)


def modify_python_file(input_file, board_h, board_l, l_r, r_r, center_abs, center_ord, size_drawing):
    donnee = [str(board_h)+"\n", str(board_l)+"\n", str(l_r)+"\n", str(r_r) +
              "\n", str(center_abs)+"\n", str(center_ord)+"\n", str(size_drawing)+"\n"]
    with open(input_file, "r+") as f:
        f.writelines(donnee)


def get_space(fichiersvg):
    b_r, b_l, t_l, t_r = get_rectangle_from_svg(fichiersvg)
    svg_size = delta_coo(b_l, t_r)
    size = config.multi * \
        adjustement_table(svg_size[0], svg_size[1]) / 100
    return svg_size[0]*size


def get_letter_path(letter):
    path = ""
    if letter in "abcdefghijklmopqrstuvwxyz":
        path = "SvgFiles/Lettres/" + letter + "_min.svg"
    elif letter == "coucou":
        path = "SvgFiles/Lettres/..svg"
    elif letter == "?":
        path = "SvgFiles/Lettres_V2/point_interrogation.svg"
        # path = "SvgFiles/Lettres/" + letter + ".svg"
    else:
        # path = "SvgFiles/Lettres/" + letter + ".svg"
        path = "SvgFiles/Lettres_V2/" + letter + ".svg"
    return path


def get_letter_parameters(letter):
    path = get_letter_path(letter)
    path = path.replace(".svg", "_parameters.txt")
    size_multiplier = 1
    offset = [0, 0]
    letter_size = config.multi * min(config.height, config.length) / 100
    if os.path.exists(path):
        with open(path, 'r') as f:
            read_file = f.read().split('\n')
            print(read_file)
            size_multiplier = float(read_file[0])
            offset[0] = float(read_file[1]) * letter_size
            offset[1] = float(read_file[2]) * letter_size
    else:
        print("No parameter file found for : " + path)
    return size_multiplier, offset


def write_one_letter(letter):
    size_multiplier, offset = get_letter_parameters(letter)
    space = get_space(get_letter_path(letter))
    config.center_x += (float(space) / 1.8 + offset[0]) * size_multiplier
    config.center_y += offset[1] * size_multiplier
    config.multi *= size_multiplier
    draw_on_screen(get_letter_path(letter))
    config.multi /= size_multiplier
    print(letter + " is written!")
    config.center_x += (float(space) / 1.8 + config.multi * min(config.height, config.length) / 100 / 4 - offset[0]) \
        * size_multiplier
    config.center_y -= offset[1] * size_multiplier
    if communicate_with_arduino:
        config.rope_left = ArduinoController.l_1_i
        config.rope_right = ArduinoController.l_2_i


def start_good(text):
    draw_on_screen(get_letter_path(text))
    if communicate_with_arduino:
        config.rope_left = ArduinoController.l_1_i
        config.rope_right = ArduinoController.l_2_i


def print_text(text):
    global config
    print("LA 1")
    config = Config.Configuration("params.txt")
    print("Texte à imprimer = " + text)
    start_center_x = config.center_x
    turtle_size = 1 / max(config.height, config.length) * 700
    print("LA 3")
    text_in_words = from_sentence_into_words(str(text))
    print("Texte en mots = ", text_in_words)
    print("LA 4")
    for i in text_in_words:
        print(i)
        print("LA 5")
        mot_en_entier(i, start_center_x)
        for j in i:
            if j in "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890,.?-':;+=()!":
                print("LA 6")
                write_one_letter(j)
                print("LA 7")
        config.center_x += config.multi * \
            min(config.height, config.length) / 100 / 1.2
        print("LA 8")


def from_sentence_into_words(sentence):
    rest_of_sentence = ""
    word = ""
    l = []
    for j in sentence:
        if j != " ":
            word += j
        else:
            break
    l.append(word)
    n = len(word)
    f = 0
    for i in sentence:
        if f > n:
            rest_of_sentence += i
        f += 1
    if len(rest_of_sentence) != 0:
        from_sentence_into_words(rest_of_sentence)
    return l


def mot_en_entier(word, start):
    n = len(word)
    if config.center_x + n*config.multi * min(config.height, config.length) / 100 * 1.1 > config.length / 2:
        config.center_x = start
        config.center_y -= config.multi * \
            min(config.height, config.length) / 100 * 1.7


def print_art(art):
    print("Je suis arrivé jusqu'au dessin")
    config = Config.Configuration("params.txt")
    config = config
    draw_on_screen("SvgFiles/"+art)
    print(art + " has been drawn!")


def draw_on_screen(file):
    print("DRAW_ON_SCREEN 1")
    screen = t.Screen()
    draw(file)
    print("DRAW_ON_SCREEN 2")
    screen.bye()
    #screen.exitonclick()
    print("DRAW_ON_SCREEN 3")
    """try:
        t.mainloop()
    except t.Terminator:
        pass"""
    print("DRAW_ON_SCREEN 4")


@app.route("/launch_drawing", methods=["POST"])
def launch():
    t.reset()
    print("Requete de dessin reçue --> dessinons ensemble :)")
    # Art est dans le fichier index.html et désigne l'input dans le form à remplir
    art = ""
    text = ""
    follow_fixed_cm_size = True
    art = request.form.get("Art")
    text = request.form.get("Text")
    board_l = request.form.get("Length")
    board_h = request.form.get("Height")
    l_r = request.form.get("Left_Rope")
    r_r = request.form.get("Right_Rope")
    center_abs = request.form.get("Center_x")
    center_ord = request.form.get("Center_y")
    size_drawing = request.form.get("Size")
    # assigne une valeur par défaut aux variables si elles ne sont pas rentrées
    l_r = isnotempty(l_r, 50)
    r_r = isnotempty(r_r, 50)
    size_drawing = isnotempty(size_drawing, 20)
    center_abs = isnotempty(center_abs, 0)
    center_ord = isnotempty(center_ord, 0)
    board_h = isnotempty(board_h, 125)
    board_l = isnotempty(board_l, 140)
    # multi à mettre
    modify_python_file("params.txt", board_h, board_l, l_r,
                       r_r, center_abs, center_ord, size_drawing)
    # print(Config.parameters)
    if str(art) != "":
        print("ici 1")
        print_art(art)
    elif str(text) != "":
        print("ici 2")
        print("Je suis arrivé jusqu'au texte")
        print_text(text)
        print("ici 3")
    else:
        print("Error")
    print("ici 4")
    return render_template("/index.html")


@app.route("/")
def index():
    return render_template("/index.html")


@app.route("/", methods=["POST"])
def reset():
    val = request.form.get("Reset")
    if val == "True":
        return render_template('/')
    else:
        return render_template('/index.html')


@app.route("/quit", methods=["POST"])
def quit():
    return render_template("/index.html")


if __name__ == "__main__":
    app.run()
