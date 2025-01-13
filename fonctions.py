import networkx as nx
import matplotlib.pyplot as plt

from math import sqrt
from typing import List, Dict, Tuple, Set

def lecture(fichier:str) -> Tuple[nx.Graph,Dict[int,Tuple[float,float]], List[Set[int]]]:
    """
    Fonction qui lis les donnees d'un fichier et qui retourne le graphe, les positions et les droites
    Args:
        fichier (str): emplacement fichier entree
    Returns:
        Tuple[nx.Graph,Dict[int,Tuple[float,float]], List[Set[str]]]
    """

    #Initalisation des variables vides
    G:nx.Graph = nx.Graph()
    positions:Dict[int,Tuple[float,float]] = {}
    droites:List[Set[int]] = []

    with open(fichier, "r") as file:
        # lecture du fichier et separation de la partie position et alignement dans 2 variables
        contenue_fichier:List[str] = file.read().split("!")
        partie_pos:List[str] = contenue_fichier[0].split("\n")[0:-1]
        partie_alignements:List[str] = contenue_fichier[1].split("\n")[1:]

    # Extraction des positions
    for ligne in partie_pos:
        liste_points:List[str] = ligne.split(' ')
        positions[int(liste_points[0])] = (float(liste_points[1]), float(liste_points[2]))

    # Recuperation des aretes du graph et sommets alignes
    aretes:List[List[str]] = []
    for ligne in partie_alignements:
        #Ensemble des points sur la droite initialement vide
        droite = set()
        #Separe tout les nombre selon ';'
        for arete in ligne.split(';'):
            aretes.append(arete.split()) #Recupere tout les aretes de la ligne
            droite.update({int(i) for i in arete.split()}) #Recupere tout les sommet de la ligne
        droites.append(droite)  # Ajoute la droite à la liste des droites

    #Ajout des arete dans une liste et convertion des types
    edges:List[Tuple[int,int]] = [(int(i[0]),int(i[1])) for i in aretes]
    #Ajout des arete dans le Graph
    G.add_edges_from(edges)

    return (G,positions,droites)

def longueur_arete(position_sommet:Dict[int,Tuple[float,float]],sommet_1:int,sommet_2:int) -> float:
    """
    Calcule la longueur entre 2 sommets.

    Args:
        position_sommet (Dict[str:Tuple[str,str]): Coordonnees des sommets
        sommet_1 (int): Premier sommet
        sommet_2 (int): Second sommet

    Returns:
        float: Distance entre les deux sommets
    """
    
    #Recuperation des coordonnees X Y de chacune des extremite des aretes
    pos_sommet_1:Tuple[float,float] = position_sommet[sommet_1]
    pos_sommet_2:Tuple[float,float] = position_sommet[sommet_2]
    
    #Calcule de la longueur
    longueur:float = sqrt((pos_sommet_2[0]-pos_sommet_1[0])**2+(pos_sommet_2[1]-pos_sommet_1[1])**2)
    
    return longueur

def division_arete_trop_longue(Graph:nx.Graph,position_sommet:Dict[int,Tuple[float,float]],droites:List[Set[int]],arete:Tuple[int,int],longueur:float) -> Tuple[nx.Graph,Dict[int,Tuple[float,float]], List[Set[int]]]:
    """
    Divise une arete de plus de 10m en sous aretes.

    Args:
        Graph (nx.Graph): Graphe
        position_sommet (Dict[int,Tuple[float,float]]): Position des sommets
        droites (List[Set[int]]): Liste des droites
        arete (Tuple[int,int]): arete a divise
        longueur (float): longueur de l'arete deja calculer

    Returns:
        Tuple[nx.Graph,Dict[int,Tuple[float,float]], List[Set[str]]]: 
    """
    sommet_a,sommet_b = arete[0],arete[1]
    
    #Suprresion de l'arete trop longue
    Graph.remove_edge(sommet_a,sommet_b)

    #Calcule du nombre de postion potentiel necessaire
    nb_points:int = int(longueur//10 - 1)
    #Ajustement si necessaire
    if longueur%10 != 0:
        nb_points +=1
    #On calcule l'ecartement necessaire
    distance:float = longueur/(nb_points+1)

    premier_sommet:int = sommet_a

    #Liste temporaire des nouveau arete a rajouter sur le graph
    arete_temp = []
    #Liste temporaire des nouveau sommet a rajouter sur la droite
    align_temp = []

    #On doit crée nb+1 aretes
    for i in range(nb_points):

        #Preparation sommets intermediaire : Determiner le nom d nouveau sommet
        liste_sommet_prexistant: list[int] = sorted([int(i) for i in list(Graph.nodes())])

        #Nom du nouveau sommet :
        deuxieme_sommet:int = liste_sommet_prexistant[-1]+1

        #Calcul de sa positions
        pos_x=((i+1)*(position_sommet[sommet_b][0]+position_sommet[sommet_a][0])/(nb_points+1))
        pos_y=((i+1)*(position_sommet[sommet_b][1]+position_sommet[sommet_a][1])/(nb_points+1))

        #Ajout du nouveau sommet dans la liste des nouveaux sommets alignes
        align_temp.append(deuxieme_sommet)

        #Ajout du nouveau sommet dans le dictionaire des position
        if not(i==nb_points):
            position_sommet[deuxieme_sommet]=(pos_x,pos_y)

        #Ajout de la nouvelle arete dans la liste des nouvelle aretes
        arete_temp.append((premier_sommet,deuxieme_sommet,{'longueur':distance}))
        
        #Changement du premier sommet pour calculer la prochaine arete
        premier_sommet = deuxieme_sommet
    
    #Ajout de la derniere arete dans la liste des nouvelle aretes
    arete_temp.append((deuxieme_sommet,sommet_b,{'longueur':distance}))
    
    #Ajout des nouvelle arete dans le Graph
    Graph.add_edges_from(arete_temp)

    #Ajout des nouveau sommet sur la droite
    for droite in droites:
        # on regarde si l'arete est sur la droite
        if sommet_a in droite and sommet_b in droite:
            droites[droites.index(droite)].update(i for i in align_temp)

    return Graph,position_sommet,droites

def traitement_graph(Graph:nx.Graph,position_sommet:Dict[int,Tuple[float,float]],droites:List[Set[int]]) -> None :
    """
    Cette fonction prend en entré un graph et la postion de ces sommets,
    et retourne un graphe avec pour chaque arête la longueur de celle si, si elle fait plus de 10m l'arete est divisé en plus petit segment
    
    Args:
        Graphe (nx.Graph): Graphe des couloir
        position_sommet (Dict[str:Tuple[str,str]): Coordonnees des sommets
        droites (List[Set[int]]): Liste des droites

    Returns:
        None  
    """

    #Parcour de toute les aretes du Graph
    for arete in Graph.edges():

        #Calcule de sa longueur
        longueur:float = longueur_arete(position_sommet,arete[0],arete[1])

        #Ajout du label longueur
        Graph[arete[0]][arete[1]]['longueur']=longueur
        
    #Extraction de la liste des aretes 
    liste_arete_init:List[Tuple[int,int]] = list(Graph.edges())

    for arete in liste_arete_init:

        #Recuperation de la longueur de l'arete
        longueur:float = Graph[arete[0]][arete[1]].get('longueur')

        #Si elle fait plus de 10m, on divise l'arete
        if longueur > 10:
            Graph,position_sommet,droites = division_arete_trop_longue(Graph,position_sommet,droites,arete,longueur)

def valuation_arete(graphe, droites:list, positions:dict) -> None:
    '''
    Fonction qui calcul un poids pour chaque arete, le poids est definit en label dans le graphe

    Args:
        graphe (nx.graph): graphe des couloirs
        droites (list): liste des droites du Graph
        positions (dict): dictionnaire des sommets avec leur position
    
    '''

    # on parcours les aretes une a une
    for arete in list(graphe.edges()):

        # on definit deux variables avec le sommet de depart et d'arrivee de l'arete
        sommet1, sommet2 = arete[0], arete[1]

        # on definit le poids de chaque arete a 0
        graphe[sommet1][sommet2]["poids"] = 0

        # on parcours tous les droites 
        for droite in droites:
            # on regarde si l'arete est sur la droite
            if sommet1 in droite and sommet2 in droite:
                # on parcours tous les sommets de la droite pour voir si leur distance par rapport au 2 points de l'arete leur permet de la couvrir entierement
                for sommet in droite:
                    sommet:str
                    #Si c'est le cas :
                    if longueur_arete(positions, sommet, sommet1) <= 10 and longueur_arete(positions, sommet, sommet2) <= 10:
                        # alors on rajoute 1 au poids de l'arete
                        graphe[sommet1][sommet2]["poids"] += 1


def valuation_sommet(sommet:int, graphe:nx.Graph, v_min:int, v_max:int):

    graphe[sommet]["degree"] = [0 for i in range(v_min, v_max + 1)]
    for i in graphe.neighbors(sommet):
        graphe[sommet]["degree"][graphe[sommet][i]] += 1

    return graphe[sommet].get("degree")

def comparaison_sommet():
    pass
def main():
    pass
def affichage():
    pass

