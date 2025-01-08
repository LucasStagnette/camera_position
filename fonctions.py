import networkx as nx

from math import sqrt
from random import random
from typing import List, Dict, Tuple

def lecture(fichier:str) -> Tuple[nx.DiGraph,Dict, List]:
    '''
    fonction qui lis les donnees d'un fichier et qui retourne le graphe, les positions et les alignements
    Args:
        fichier (str): emplacement fichier entree
    Returns:
        Tuple[nx.DiGraph,dict, list]
    '''

    g = nx.Graph()
    positions ={}
    alignements = []

    with open(fichier, "r") as file:
        # lecture du fichier et separation de la partie position et alignement dans 2 variables
        a = file.read().split("!")
        b = a[0].split("\n")[0:-1]
        c = a[1]

        # placement des positions avec leur sommet dans un dico
        for point in b:
            positions[point[0]] = (point[2], point[4])

        # placement des sommets alignes
        for ligne in c.split("\n")[1:]:
            temp = []
            for carac in ligne:
                # on verifie si c'est un nombre et qu'il n'a pas deja ete ajoute
                if carac not in temp and carac in ["0","1","2","3","4","5","6","7","8","9"]:
                    temp.append(carac)
            alignements.append(temp)

    aretes = [i.split(";") for i in c.split("\n")[1:]]
    aretes = [item for sublist in aretes for item in sublist]
    edges = [(i[0], i[2]) for i in aretes]
    g:nx.DiGraph=nx.DiGraph()

    return (g.add_edges_from(edges),positions,alignements)


Graph,positions,alignements = lecture("graphe.txt")