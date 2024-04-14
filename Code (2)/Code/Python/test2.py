# region Imports
from audioop import add
import os
import turtle as t
from flask import Flask, render_template, request
import Config
import SvgDrawer

app = Flask(__name__)
l = []


config = Config.Configuration("params.txt")


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
    return SvgDrawer.get_rectangle(content)


def modify_python_file(input_file, board_h, board_l, l_r, r_r, center_abs, center_ord, size_drawing):
    donnee = [str(board_h)+"\n", str(board_l)+"\n", str(l_r)+"\n", str(r_r) +
              "\n", str(center_abs)+"\n", str(center_ord)+"\n", str(size_drawing)+"\n"]
    with open(input_file, "r+") as f:
        f.writelines(donnee)


def get_space(fichiersvg):
    b_r, b_l, t_l, t_r = get_rectangle_from_svg(fichiersvg)
    svg_size = SvgDrawer.delta_coo(b_l, t_r)
    size = config.multi * \
        SvgDrawer.adjustement_table(svg_size[0], svg_size[1]) / 100
    return svg_size[0]*size


def get_letter_path(letter):
    path = ""
    if letter in "abcdefghijklmopqrstuvwxyz":
        path = "SvgFiles/Lettres/" + letter + "_min.svg"
    elif letter == "?":
        path = "SvgFiles/Lettres/pointinterrogation.svg"
    else:
        path = "SvgFiles/Lettres/" + letter + ".svg"
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
    SvgDrawer.config = config
    SvgDrawer.draw(get_letter_path(letter))
    config.multi /= size_multiplier
    print(letter + " is written!")
    config.center_x += (float(space) / 1.8 + config.multi * min(config.height, config.length) / 100 / 4 - offset[0]) \
        * size_multiplier
    config.center_y -= offset[1] * size_multiplier

    if SvgDrawer.communicate_with_arduino:
        config.rope_left = SvgDrawer.ArduinoController.l_1_i
        config.rope_right = SvgDrawer.ArduinoController.l_2_i


def print_text(text):
    global config
    config = Config.Configuration("params.txt")
    start_center_x = config.center_x
    SvgDrawer.turtle_size = 1 / max(config.height, config.length) * 700
    text_in_words = from_sentence_into_words(str(text))
    print(text_in_words)
    for i in text_in_words:
        print(i)
        mot_en_entier(i, start_center_x)
        for j in i:
            if j in "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890,.?-':;+=()":
                write_one_letter(j)
        config.center_x += config.multi * \
            min(config.height, config.length) / 100 / 1.2


def from_sentence_into_words(sentence):
    rest_of_sentence = ""
    word = ""
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
    SvgDrawer.config = config
    SvgDrawer.draw("SvgFiles/"+art+".svg")
    print(art + " has been drawn!")


@app.route("/launch_drawing", methods=["POST"])
def launch():
    t.reset()
    # Art est dans le fichier index.html et désigne l'input dans le form à remplir
    SvgDrawer.follow_fixed_cm_size = True
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
    board_l = isnotempty(board_l, 135)
    # multi à mettre
    modify_python_file("params.txt", board_h, board_l, l_r,
                       r_r, center_abs, center_ord, size_drawing)
    # print(Config.parameters)
    import Config
    if str(art) != "":
        print_art(art)
    elif str(text) != "":
        print("Je suis arrivé jusqu'au texte")
        print_text(text)
    else:
        print("error")
    t.mainloop()
    return render_template("index.html")


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


if __name__ == "__main__":
    app.run()
