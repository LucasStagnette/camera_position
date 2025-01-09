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

def longueur_arete(Graph:nx.Graph,position_sommet:Dict[str,Tuple[str,str]]) -> nx.Graph :
    '''Cette fonction prends en entree un graphe et la position de ses sommets
    et retourne un graphe avec pour chaque arete la longeur de celle ci.
        
    Args:
        Graphe (nx.Graph): Graphe des couloirs
        position_sommet (Dict[str:Tuple[str,str]): Le mot de passe pour la connexion.
        alignements (List[List[str,str]]): Liste contenant les alignements des points.

    Returns:
        nx.Graph: Graph avec les longeurs des aretes.
        
    '''
    #On cree une liste d'arete initialement vide
    liste_arrete=[]

    #Parcours de toutes les aretes du Graphe
    for arete in Graph.edges():
        #Recuperation des coordonnees X Y de chacune des extremites des aretes
        pos_a=position_sommet[arete[0]]
        pos_b=position_sommet[arete[1]]
        #Calcul de la longueur
        longueur=sqrt((pos_b[0]-pos_a[0])**2+(pos_b[1]-pos_a[1])**2)
        #Ajout du tuple (sommet_debut,sommet_fin,{'longeur':valeur_longeur}) dans la liste des aretes
        liste_arrete.append((arete[0],arete[1],{'longeur':longueur}))
    
    #Creation d'un graphe vide
    Graphe_final:nx.Graph=nx.Graph()
    #Ajout des aretes et renvoit
    Graphe_final.add_edges_from(liste_arrete)
    return Graphe_final

G,positions,alignements = lecture("graphe.txt")
G=longueur_arete(G,positions)
