from distutils.command.config import config
from re import X

from numpy import size
import SvgDrawer
import time
import math
import Config
import turtle as t
from tkinter import *
from tkinter import ttk

start_time = time.time()  # chronomètre utilisé lors des simulations


def draw_svg(file_name):
    """Fonction appelant la fonction principale draw pour dessiner depuis un fichier SVG"""
    SvgDrawer.draw(file_name)


def how_to_print():
    x = float(
        input("Where do you want it to be placed (on the x axis)? \nx = "))
    y = float(
        input("Where do you want it to be placed (on the y axis)? \ny = "))
    while abs(x) > Config.length or abs(y) > Config.height:
        print("Your dimensions are going off the board, try again: for your information, here are the board dimensions: " +
              str(Config.length) + " X " + str(Config.height))
        x = float(
            input("Where do you want it to be placed (on the x axis)? \nx = "))
        y = float(
            input("Where do you want it to be placed (on the y axis)? \ny = "))
    Config.center_x = x
    Config.center_y = y


def size_to_print():
    hauteur = float(input(
        "How tall do you want your drawing to be? \nHeight in cm = "))
    return hauteur


def assemble_text(text):
    letters = "aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ1234567890:;,?.!'-_"
    size_letters = size_to_print()
    multi = SvgDrawer.cm_into_multi(size_letters)
    Config.multi = multi
    for i in text:
        if i in letters:
            SvgDrawer.draw("Svgfiles/Lettres/"+i+".svg")
            Config.center_x += size_letters
            print(i + " is written")
        else:
            """C'est le cas d'un espace """
            SvgDrawer.draw("")


def print_text():
    text = str(input("What text do you want to write? \nYour text: "))
    how_to_print()
    assemble_text(text)


def print_image():
    dessin = str(input("What do you want to draw? \nName of your drawing: "))
    how_to_print()
    Config.multi = float(SvgDrawer.cm_into_multi(size_to_print()))
    draw_svg("Svgfiles/"+dessin+".svg")


def init_table():
    request = str(
        input("Do you want to modify your table's data? y/n?   "))
    while request not in "yn":
        request = str(
            input("Do you want to modify your table's data? y/n?   "))
    if request == "y":
        Config.height = float(input("Table's height: "))
        Config.length = float(input("Table's width: "))
    print("\n")


def init_rope():
    print("What are the dimensions of the rope between the edge pf the board and Simon?")
    left = float(input("Length of the left rope: "))
    right = float(input("Lenght of the right rope: "))
    while (not isinstance(left, (float, int)) or not isinstance(right, (float, int))) or (right < 1 or right > 150) or (left < 1 or left > 150):
        print("Your command was not in the right format, try to write a number between 1 and 150")
        left = float(input("Length of the left rope: "))
        right = float(input("Lenght of the right rope: "))
    Config.rope_left = left
    Config.rope_right = right


def interface():
    print("What do you want Simon to draw? \n1: Write\n2: Draw\n3: Nothing")
    commande = input("I want to do: ")
    while commande not in "123":
        print("We did not understand your command, try again.")
        commande = input("I want to do: ")
    if commande == "1":
        init_table()
        # init_rope()
        print_text()
    elif commande == "2":
        init_table()
        # init_rope()
        print_image()
    elif commande == "3":
        print("No problem, come back when you want!")
    SvgDrawer.move_turtle(50, -50, False)


def keep_going():
    var = input("Do you want to draw something else? (y/n)    ")
    while var not in "yn":
        print(str(var) + " is not a correct command. Try again.")
        var = input("Do you want to draw something else? (y/n)    ")
    if var == "y":
        interface()
        keep_going()
    elif var == "n":
        print("No problem, we hope you enjoyed your experience!")

"""
print("Hello, welcome in Simon's interface!")
interface()
keep_going()
print("See you later!")

end_time = time.time()
print("Took: " + str(end_time - start_time))
t.mainloop()


print(end_time - start_time)  #Affiche la durée  du programme
"""