import networkx as nx
import matplotlib.pyplot as plt

from math import sqrt
from random import random
from typing import List, Dict, Tuple

def lecture(fichier:str) -> Tuple[nx.Graph,Dict, List]:
    '''
    fonction qui lis les donnees d'un fichier et qui retourne le graphe, les positions et les alignements
    Args:
        fichier (str): emplacement fichier entree
    Returns:
        Tuple[nx.Graph,dict, list]
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
            positions[point[0]] = (int(point[2]), int(point[4]))

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
    g.add_edges_from(edges)

    return (g,positions,alignements)

def longueur_arete(Graph:nx.Graph,postion_sommet:Dict[str,Tuple[str,str]]) -> nx.Graph :
    '''Cette fonction prend en entré un graph et la postion de ces sommets
    et retourne un graphe avec pour chaque arête la longeur de celle si.
        
    Args:
        Graphe (nx.Graph): Graphe des couloir
        postion_sommet (Dict[str:Tuple[str,str]): Le mot de passe pour la connexion.
        alignements (List[List[str,str]]): Liste contenant les alignement des points.

    Returns:
        nx.Graph: Graph avec les longeur des arete.
        
    '''
    #On cree une liste d'arrete initialement vide
    liste_arrete=[]

    #Parcour de toute les aretes du Graph
    for arete in Graph.edges():
        #Recuperation des coordonnees X Y de chacune des extremite des aretes
        pos_a=postion_sommet[arete[0]]
        pos_b=postion_sommet[arete[1]]
        #Calcule de la longueur
        longueur=sqrt((pos_b[0]-pos_a[0])**2+(pos_b[1]-pos_a[1])**2)
        #Ajout tu tuple (sommet_debut,sommet_fin,{'longeur':valeur_longeur}) dans la liste des aretes
        liste_arrete.append((arete[0],arete[1],{'longeur':longueur}))
    
    #Création d'un graph vide
    Graphe_final:nx.Graph=nx.Graph()
    #Ajout des aretes et renvoie
    Graphe_final.add_edges_from(liste_arrete)
    return Graphe_final

G,positions,alignements = lecture("graphe.txt")
G=longueur_arete(G,positions)
