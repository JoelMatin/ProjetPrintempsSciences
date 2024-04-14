# Constantes
length_between_motors = 18.5  # in cm   #Longueur entre le moteur et le feutre
port = "COM6"  # Numéro du port d'entrée
curve_steps = 40  # Nombre d'étape pour une courbe de Bézier
baudrate = 74880  # Vitesse de la transmission d'information
radius = 0.9  # rayon de l'enrouleur en cm


def recup_in_config(file):
    variables = []
    for ligne in open(file, "r"):
        if ligne != '\n':
            variables.append(float(ligne))
    return variables

# Variables modifiables


class Configuration:
    def cm_into_multi(self, request_height_in_cm):
        multi = request_height_in_cm / max(self.height, self.length) * 100
        return multi

    def __init__(self, file_name):
        parameters = recup_in_config(file_name)
        # in cm                 # Premier chiffre = Dimension du support
        self.height = parameters[0]  # Hauteur du tableau
        self.length = parameters[1]  # Largeur du tableau
        self.rope_left = parameters[2]
        self.rope_right = parameters[3]
        self.center_x = parameters[4]
        self.center_y = parameters[5]
        self.size = parameters[6]  # Taille en centimètre
        self.multi = self.cm_into_multi(self.size)
        # marge entre le support et le début potentiel du dessin (en x)
        self.margin_x = 0
        # marge entre le support et le début potentiel du dessin (en y)
        self.margin_y = 0
        self.treshold = 0.1   # Distance entre les déplacements
