# region Imports
import os
import turtle as t
from flask import Flask, render_template, request
import Config
import SvgDrawer

app = Flask(__name__)


def isnotempty(var, default):
    if var == "":
        var = default
    return float(var)


def print_text(text, center_abs, size_drawing):
    for i in str(text):
        # cherche si le svg de la lettre majuscule
        if i in "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890,.?-':;+=()":
            if i in "abcdefghijklmopqrstuvwxyz":
                SvgDrawer.draw("SvgFiles/Lettres/"+i+"_min.svg")
            elif i == "?":
                SvgDrawer.draw("SvgFiles/Lettres/pointinterrogation.svg")
            else:
                SvgDrawer.draw("SvgFiles/Lettres/"+i+".svg")
            print(i + " is written!")
        Config.center_x += float(size_drawing) * 3/2


def print_art(art):
    print("Je suis arrivé jusqu'au dessin")
    SvgDrawer.draw("SvgFiles/"+art+".svg")
    print(art + " has been drawn!")


@app.route("/launch_drawing", methods=["POST"])
def launch():
    # Art est dans le fichier index.html et désigne l'input dans le form à remplir
    art = request.form.get("Art")
    text = request.form.get("Text")
    board_l = request.form.get("Length")
    board_h = request.form.get("Height")
    l_r = request.form.get("Left_Rope")
    r_r = request.form.get("Right_Rope")
    center_abs = request.form.get("Center_x")
    center_ord = request.form.get("Center_y")
    size_drawing = request.form.get("Size")

    l_r = isnotempty(l_r, 50)
    r_r = isnotempty(r_r, 50)
    # assigne une valeur par défaut aux variables si elles ne sont pas rentrées
    size_drawing = isnotempty(size_drawing, 20)
    center_abs = isnotempty(center_abs, 0)
    center_ord = isnotempty(center_ord, 0)
    board_h = isnotempty(board_h, 125)
    board_l = isnotempty(board_l, 112)
    # multi à mettre
    modify_python_file("params.txt", board_h, board_l, l_r,
                       r_r, center_abs, center_ord, size_drawing)
    if str(art) != "":
        print_art(art)
    elif str(text) != "":
        print("Je suis arrivé jusqu'au texte")
        print_text(text, center_abs, size_drawing)
    else:
        print("error")
    t.mainloop()
    return render_template("index.html")


def modify_python_file(input_file, board_h, board_l, l_r, r_r, center_abs, center_ord, size_drawing):
    donnee = [str(board_h)+"\n", str(board_l)+"\n", str(l_r)+"\n", str(r_r) +
              "\n", str(center_abs)+"\n", str(center_ord)+"\n", str(size_drawing)+"\n"]
    with open(input_file, "r+") as f:
        f.writelines(donnee)


print(str(Config.multi))


@app.route("/")
def index():
    return render_template("/index.html")


if __name__ == "__main__":
    app.run()
