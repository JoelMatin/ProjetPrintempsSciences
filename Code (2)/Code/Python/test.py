from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *

fenetre = Tk()


def recupere():
    print(entree.get())


value = StringVar()
value.set("Valeur")
entree = Entry(fenetre, textvariable=value, width=30)
entree.pack()

bouton = Button(fenetre, text="Valider", command=recupere)
bouton.pack()


fenetre.mainloop()
