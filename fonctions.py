import networkx as nx
import matplotlib.pyplot as plt

from math import sqrt
from typing import List, Dict, Tuple

def lecture(fichier:str) -> Tuple[nx.Graph,Dict[int,Tuple[float,float]], List[List[int]]]:
    """
    Fonction qui lis les donnees d'un fichier et qui retourne le graphe, les positions et les alignements
    Args:
        fichier (str): emplacement fichier entree
    Returns:
        Tuple[nx.Graph,dict, list]
    """

    g = nx.Graph()
    positions ={}
    alignements = []

    with open(fichier, "r") as file:
        # lecture du fichier et separation de la partie position et alignement dans 2 variables
        a = file.read().split("!")
        partie_pos = a[0].split("\n")[0:-1]
        partie_alignement = a[1].split("\n")[1:]

        # placement des positions avec leur sommet dans un dico
        for point in partie_pos:
            list_point=point.split(' ')
            positions[int(list_point[0])] = (float(list_point[1]), float(list_point[2]))

        # placement des sommets alignes
        for ligne in partie_alignement:
            temp = []
            for caractere in ligne:
                # on verifie si c'est un nombre et qu'il n'a pas deja ete ajoute
                if caractere not in temp and caractere in ["0","1","2","3","4","5","6","7","8","9"]:
                    temp.append(int(caractere))
            alignements.append(temp)

    aretes = [i.split(";") for i in partie_alignement]
    aretes = [item for sublist in aretes for item in sublist]
    edges:List[Tuple[int,int]] = [(int(i[0]),int(i[2])) for i in aretes]
    g.add_edges_from(edges)

    return (g,positions,alignements)

def longueur_arete(position_sommet:Dict[int,Tuple[float,float]],sommet_1,sommet_2) -> float:
    """
    Calcule la longueur entre 2 sommets.

    Args:
        Graphe (nx.Graph): Graphe des couloir
        position_sommet (Dict[str:Tuple[str,str]): Coordonnees des sommets

    Returns:
        int: Distance entre les deux points
    """
    #Recuperation des coordonnees X Y de chacune des extremite des aretes
    sommet_a=position_sommet[int(sommet_1)]
    sommet_b=position_sommet[int(sommet_2)]
    #Calcule de la longueur
    longueur:float=sqrt((sommet_b[0]-sommet_a[0])**2+(sommet_b[1]-sommet_a[1])**2)
    return longueur

def division_arete_trop_longue(Graph:nx.Graph,position_sommet,arete,longueur):
    #Suprresion de l'arete trop longue
    Graph.remove_edge(arete[0],arete[1])

    #Calcule du nombre de postion potentiel necessaire
    nb_points:int = int(longueur//10 - 1)
    #Ajustement si nessecaire
    if longueur%10 != 0:
        nb_points +=1
    #On calcule l'ecartement nessecaire
    distance = longueur/(nb_points+1)

    premier_sommet=arete[0]
    liste_arrete=[]


    #On doit crée nb+1 arete
    for i in range(nb_points):
        print("i=",i)

        #Preparation sommets intermediaire
        sommet_prexistant:List=list(Graph.nodes())
        liste_sommet_prexistant=[int(i) for i in sommet_prexistant]
        liste_sommet_prexistant.sort()
        deuxieme_sommet=liste_sommet_prexistant[-1]+1

        
        #Calcul des positions
        pos_x=((i+1)*(position_sommet[arete[1]][0]+position_sommet[arete[0]][0])/(nb_points+1))
        pos_y=((i+1)*(position_sommet[arete[1]][1]+position_sommet[arete[0]][1])/(nb_points+1))

        #Ajout dans le dictionaire
        if not(i==nb_points):
            position_sommet[deuxieme_sommet]=(pos_x,pos_y)

        #Ajout de le new sommet dans le graph 
        liste_arrete.append((premier_sommet,deuxieme_sommet,{'longueur':distance}))
        premier_sommet=deuxieme_sommet

    #Ajout de la deuxieme arete qui manque
    liste_arrete.append((deuxieme_sommet,arete[1],{'longueur':distance}))
    Graph.add_edges_from(liste_arrete)
    return Graph,position_sommet

def traitement_graph(Graph:nx.Graph,position_sommet:Dict[int,Tuple[float,float]]) -> nx.Graph :
    """
    Cette fonction prend en entré un graph et la postion de ces sommets,
    et retourne un graphe avec pour chaque arête la longueur de celle si, si elle fait plus de 10m l'arete est divisé en plus petit segment
    
    Args:
        Graphe (nx.Graph): Graphe des couloir
        position_sommet (Dict[str:Tuple[str,str]): Coordonnees des sommets

    Returns:
        nx.Graph: Graph avec les longueur des arete.
        
    """

    #Parcour de toute les aretes du Graph
    for arete in Graph.edges():
        longueur=longueur_arete(position_sommet,arete[0],arete[1])
        Graph[arete[0]][arete[1]]['longueur']=longueur
    liste_arete_init=list(Graph.edges())
    
    for arete in liste_arete_init:
        longueur=Graph[arete[0]][arete[1]].get('longueur')
        print("arete:",arete,longueur)
        if longueur>10:
            Graph,position_sommet=division_arete_trop_longue(Graph,position_sommet,arete,longueur)
    return Graph

def valuation_arete(graphe, alignements:list, positions:dict):
    '''
    :param graphe: nx.graph ; graphe des couloirs
    :param alignements: list ; liste des groupes d'alignement
    :param positions: dict ; dictionnaire des sommets avec leur position
    Fonction qui calcul un poids pour chaque arete, le poids est definit en label dans le graphe
    '''

    # on parcours les aretes une a une
    for arete in list(graphe.edges()):

        # on definit deux variables avec le sommet de depart et d'arrivee de l'arete
        sommet1, sommet2 = arete[0], arete[1]
        # on definit le poids de chaque arete a 0
        graphe[sommet1][sommet2]["poids"] = 0

        # on parcours tous les groupes d'alignements
        for groupe in alignements:
            # on regarde si l'arete est dans le groupe d'alignement
            if str(sommet1) in groupe and str(sommet2) in groupe:
                # on parcours tous les sommets du groupe pour voir si leur distance aux 2 points de l'arete leur permet de la couvrir entierement
                for sommet in groupe:
                    if longueur_arete(positions, sommet, sommet1) <= 10 and longueur_arete(positions, sommet, sommet2) <= 10:
                        # alors on rajoute +1 au poids de l'arete
                        graphe[sommet1][sommet2]["poids"] += 1