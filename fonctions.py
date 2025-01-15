import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from random import randint
from typing import List, Dict, Tuple, Set


def lecture(
    fichier:str) -> Tuple[
        nx.Graph,
        Dict[int,Tuple[float,float]],
        Dict[int,Set[int]],
        Dict[int,Set[int]]]:
    """
    Fonction qui lis les donnees d'un fichier et qui retourne le graphe, les positions et les droites

    Args:
        fichier (str): Nom/emplacement fichier entree
    Returns:
        nx.Graph: Graphe
        Dict[int,Tuple[float,float]] Dictionaire des positions
        Dict[int,Set[int]]: Dictionaire des droites
        Dict[int,Set[int]]: Dictionaire des associations des droite
    """

    #Initalisation des variables vides
    G:nx.Graph = nx.Graph()
    positions:Dict[int,Tuple[float,float]] = {}
    droites:Dict[int,Set[int]] = {}
    assos_droites:Dict[int,Set[int]] = {}

    with open(fichier, "r") as file:
        # lecture du fichier et separation de la partie position et alignement dans 2 variables
        contenue_fichier:List[str] = file.read().split("!")
        partie_pos:List[str] = contenue_fichier[0].split("\n")[0:-1]
        partie_alignements:List[str] = contenue_fichier[1].split("\n")[1:]

    # Extraction des positions
    for ligne in partie_pos:
        liste_points:List[str] = ligne.split(' ')
        positions[int(liste_points[0])] = (float(liste_points[1]), float(liste_points[2]))

    # Recuperation des aretes du graph et des droites
    aretes:List[List[str]] = []
    cnt_drt=0
    for ligne in partie_alignements:
        #Ensemble des points sur la droite initialement vide
        droite = set()
        #Separe tout les nombre selon ';'
        for arete in ligne.split(';'):
            aretes.append(arete.split()) #Recupere tout les aretes de la ligne
            droite.update({int(i) for i in arete.split()}) #Recupere tout les sommet de la ligne
        #Ajouts des point sur la droite
        droites[cnt_drt]=droite
        cnt_drt+=1

    #Ajout des arete dans une liste et convertion des types
    edges:List[Tuple[int,int]] = [(int(i[0]),int(i[1])) for i in aretes]

    del cnt_drt,aretes

    #Creation des set pour les associations
    for sommet in positions.keys():
        assos_droites[sommet]=set()
    #Ajout des droites de chaque sommets
    for nom,sommets in droites.items():
        for sommet in sommets:
            assos_droites[sommet].add(nom)

    
    #Ajout des arete dans le graphe
    G.add_edges_from(edges)

    return (G,positions,droites,assos_droites)

def longueur_arete(
    positions_sommets:Dict[int,Tuple[float,float]],
    sommet_1:int,
    sommet_2:int
    ) -> float:
    """
    Calcule la longueur entre 2 sommets.

    Args:
        positions_sommets (Dict[int,Tuple[float,float]]): Coordonnees des sommets
        sommet_1 (int): Premier sommet
        sommet_2 (int): Second sommet

    Returns:
        float: Distance entre les deux sommets
    """
    
    #Recuperation des coordonnees X Y de chacune des extremite des aretes
    pos_sommet_1:Tuple[float,float] = positions_sommets[sommet_1]
    pos_sommet_2:Tuple[float,float] = positions_sommets[sommet_2]
    
    #Calcule de la longueur
    longueur:float = sqrt((pos_sommet_2[0]-pos_sommet_1[0])**2+(pos_sommet_2[1]-pos_sommet_1[1])**2)
    
    return longueur

def cherche_droite(
        associations_droites:Dict[int,Set[int]],
        sommet_A:int,
        sommet_B:int) -> int:
    """
    Reenvoie le nom de la droite commune a deux sommets    
    
    Args:
        associations_droites (Dict[int,Set[int]]): dictionnaire d'assosiation des droites
        sommet_A (int): Premier sommet
        sommet_B (int): Second sommet

    Returns:
        int: Nom de la droite
    """
    #Extraction des droites ou sont present A et B
    droites_A=associations_droites[sommet_A]
    droites_B=associations_droites[sommet_B]

    #Cherche et retourne la droite en commun
    for i in droites_A:
        for k in droites_B:
            if k == i:
                return k
    return None

def division_arete_trop_longue(
        graphe:nx.Graph,
        positions_sommets:Dict[int,Tuple[float,float]],
        droites:Dict[int,Set[int]],
        associations_droites:Dict[int,Set[int]],
        arete_initial:Tuple[int,int],
        longueur:float) -> Tuple[
            nx.Graph,
            Dict[int,Tuple[float,float]],
            Dict[int,Set[int]],
            Dict[int,Set[int]]
            ]:
    """
    Divise une arete de plus de 10m en sous aretes.

    Args:
        graphe (nx.Graph): Graphe
        positions_sommets (Dict[int,Tuple[float,float]]): Position des sommets
        droites (List[Set[int]]): Liste des droites
        arete_initial (Tuple[int,int]): arete a divise
        longueur (float): longueur de l'arete deja calculer

    Returns:
        nx.Graph: Graphe
        Dict[int,Tuple[float,float]] Dictionaire des positions
        Dict[int,Set[int]]: Dictionaire des droites
        Dict[int,Set[int]]: Dictionaire des associations des droite
    """
    sommet_A,sommet_B = arete_initial[0],arete_initial[1]
    
    #Suprresion de l'arete trop longue
    graphe.remove_edge(sommet_A,sommet_B)

    #Calcule du nombre de postion potentiel necessaire
    nb_points:int = int(longueur//10 - 1)
    #Ajustement si necessaire
    if longueur%10 != 0:
        nb_points +=1
    #On calcule l'ecartement necessaire
    distance:float = longueur/(nb_points+1)

    #On initalise le premier sommet au sommet A
    premier_sommet:int = sommet_A

    #Liste temporaire des nouveau arete a rajouter sur le graph
    arete_temp = []
    #Liste temporaire des nouveau sommet a rajouter sur la droite
    align_temp = []

    vecteur:Tuple[float,float] = (positions_sommets[sommet_B][0]-positions_sommets[sommet_A][0],positions_sommets[sommet_B][1]-positions_sommets[sommet_A][1])
    pos_x_A = positions_sommets[sommet_A][0]
    pos_y_A = positions_sommets[sommet_A][1]
    #On doit cree nb+1 aretes
    for i in range(1,nb_points+1):

        #Preparation sommets intermediaire : Determiner le nom d nouveau sommet
        liste_sommet_prexistant: list[int] = sorted([int(i) for i in list(graphe.nodes())])

        #Nom du nouveau sommet :
        deuxieme_sommet:int = liste_sommet_prexistant[-1]+1
        #Calcul de sa positions
        pos_x = pos_x_A + i * vecteur[0]/(nb_points+1)
        pos_y = pos_y_A + i * vecteur[1]/(nb_points+1)
        
        #Ajout du nouveau sommet dans la liste des nouveaux sommets alignes
        align_temp.append(deuxieme_sommet)

        #Ajout du nouveau sommet dans le dictionaire des position
        #if not(i==nb_points):
        positions_sommets[deuxieme_sommet]=(pos_x,pos_y)

        #Ajout de la nouvelle arete dans la liste des nouvelle aretes
        arete_temp.append((premier_sommet,deuxieme_sommet,{'longueur':distance}))
        
        #Ajout du nouveau sommet dans le graphe.
        graphe.add_node(deuxieme_sommet)

        #Changement du premier sommet pour calculer la prochaine arete
        premier_sommet = deuxieme_sommet
    
    #Ajout de la derniere arete dans la liste des nouvelle aretes
    arete_temp.append((deuxieme_sommet,sommet_B,{'longueur':distance}))
    
    #Ajout des nouvelle arete dans le graphe
    graphe.add_edges_from(arete_temp)

    #Ajout des nouveau sommet sur la droite
    droite_originel=cherche_droite(associations_droites,sommet_A,sommet_B)
    droites[droite_originel].update(align_temp)

    #Creation des set pour les associations de droite
    for sommet in align_temp:
        associations_droites[sommet]=set()
        associations_droites[sommet].add(droite_originel)

    return graphe,positions_sommets,droites,associations_droites

def pretraitement_graph(
        graphe:nx.Graph,
        positions_sommets:Dict[int,Tuple[float,float]],
        droites:Dict[int,Set[int]],
        associations_droites:Dict[int,Set[int]]) -> Tuple[
            nx.Graph,
            int,
            int] :
    """
    Cette fonction prend en entre un graph, la postion de ces sommets, les dictionnaire de droites et d'association
    Si une arete fait plus de 10m l'arete est divise en sous aretes
    Elle modifie le graphe en ajoutant pour chaque arête sa longueur et son poid.
    Retourne le poids min et max des aretes
    
    Args:
        graphe (nx.Graph): Graphe des couloir
        positions_sommets (Dict[str:Tuple[str,str]): Coordonnees des sommets
        droites (List[Set[int]]): Liste des droites

    Returns:
        nx.Graph: Graphe orignal
        int: poids minimum des aretes
        int: poids maximum des aretes
    """
    #Copie du Graph a renvoye:
    original=graphe.copy()
    #Parcour de toute les aretes du Graph
    for arete in graphe.edges():

        #Calcule de sa longueur
        longueur:float = longueur_arete(positions_sommets,arete[0],arete[1])

        #Ajout du label longueur
        graphe[arete[0]][arete[1]]['longueur']=longueur

               
    #Extraction de la liste des aretes 
    liste_arete_init:List[Tuple[int,int]] = list(graphe.edges())

    #Calcul des longueur et division
    for arete in liste_arete_init:

        #Recuperation de la longueur de l'arete
        longueur = graphe[arete[0]][arete[1]].get('longueur')

        #Si elle fait plus de 10m, on divise l'arete
        if longueur > 10:
            graphe,positions_sommets,droites,associations_droites = division_arete_trop_longue(graphe,positions_sommets,droites,associations_droites,arete,longueur)
    
    #Calcul des poids
    for arete in list(graphe.edges()):
        # on definit deux variables avec le sommet de depart et d'arrivee de l'arete
        sommet1, sommet2 = arete[0], arete[1]

        # on definit le poids de chaque arete a 0
        graphe[sommet1][sommet2]["poids"] = 0

        # on parcours tous les droites 
        for droite in droites.values():
            # on regarde si l'arete est sur la droite
            if sommet1 in droite and sommet2 in droite:
                # on parcours tous les sommets de la droite pour voir si leur distance par rapport au 2 points de l'arete leur permet de la couvrir entierement
                for sommet in droite:
                    sommet:str
                    #Si c'est le cas :
                    if longueur_arete(positions_sommets, sommet, sommet1) <= 10 and longueur_arete(positions_sommets, sommet, sommet2) <= 10:
                        # alors on rajoute 1 au poids de l'arete
                        graphe[sommet1][sommet2]["poids"] += 1

    #Determination des valeurs min et max
    v_min=99999
    v_max=0
    for arete in list(graphe.edges()):
        #Recuperation du poids de l'arete
        poids=graphe[arete[0]][arete[1]].get('poids')
        #Si il est plus grand que le max
        if poids > v_max:
            #On change le max
            v_max = poids
        #Si il est plus petit que le min
        elif poids < v_min:
            #On change le min
            v_min = poids
    return (original,v_min,v_max)

def valuation_sommet(
        graphe:nx.Graph,
        aretes_voisines_indirect:List[Tuple[int, int]],
        sommet:int,
        v_min:int,
        v_max:int) -> None:
    """
    Cette fonction calcule la portee de chaque sommet si on y place une camera, en tenant compte des arete deja couvertes

    Args:
        graphe (nx.Graph): graphe
        aretes_voisines_indirect(list[tuple[int, int]]): Liste des arete que le sommet peut couvrir mais pas directement accessible
        v_min (int): poids minimum des aretes
        v_max (int): poids maximum des aretes

    Returns:
        None
    """
    
    #Initialisation des liste vide pour l'aret
    graphe.nodes[sommet]["portee"] = [0 for i in range(v_min, 2*v_max)]
    
    #Pour voisin du sommet
    for voisins in graphe.neighbors(sommet):

        #met la valeur du degree      On ajoute un a la portee d'indice : le poids de l'arete jusqu'au sommet voisin et soustrait 2 au poids
        graphe.nodes[sommet]["portee"][int(graphe[sommet][voisins].get("poids"))-2] += 1

    #Pour chaque arete a la portee du sommet
    #for arete in aretes_voisines_indirect:
    #    #On comptabilise le poid de cette arete dans la portee du sommet
    #    graphe.nodes[sommet]["portee"][int(graphe[arete[0]][arete[1]].get("poids"))] += 1

def comparaison_sommet(graphe:nx.Graph,sommet_A:int,sommet_B:int) -> int:
    """
    Compare la liste "portee" de deux sommet celui qui a la valeur la plus grande valeur en plus petit indice

    Args:
        graphe (nx.Graph): graphe
        aretes_voisines_indirect(list[tuple[int, int]]): Liste des arete que le sommet peut couvrir mais pas directement accessible
        v_min (int): poids minimum des aretes
        v_max (int): poids maximum des aretes

    Returns:
        int: sommet le plus "grand"
    """
    #Pour i allant de 0 a la longeur de la liste 
    for i in range(len(graphe.nodes[sommet_A].get("portee"))):
        some1 = graphe.nodes[sommet_A].get("portee")[i]
        some2 = graphe.nodes[sommet_B].get("portee")[i]

        #On compare les element d'indice i on retourne le sommet qui a le plus grand, en cas d'egalite on passe a l'indice suivant. 
        if some1 == some2:
            pass
        elif some1 > some2:
            return sommet_A
        elif some1 < some2:
            return sommet_B
        
    return sommet_A

def liste_voisin_eloignes(
        positions_sommets:Dict[int,Tuple[float,float]],
        droites:Dict[int,Set[int]],
        associations_droites:Dict[int,Set[int]],
        sommet:int) -> List[List[int]]:
    """
    Renvoie la liste des voisin a la porte du sommet
    
    Args:
        positions_sommets (Dict[int,Tuple[float,float]]): Position des sommets
        droites (List[Set[int]]): Liste des droites
        sommet (Tuple[int,int]): sommet a considere

    Returns:
        List[List[int]]
    """
    Resultat:List[List[int]]=[]

    #Droites auxquel le sommet appartient
    droites_du_sommet:set[int] = associations_droites[sommet]

    #Pour chaqu'une de ces droites
    for droite in droites_du_sommet:
        #On recupere tout les elements de cette droite
        Resultat.append(list(droites[droite]))
        
    #Liste temporaire des sommets a retirer
    to_rem=[]
    #Pour chaque droite deja presente dans le resultat
    for d in Resultat:
        #On retire le sommet en question
        d.remove(sommet)
        #Pour chaque sommet sur cette droite
        for s in d:
            #Si la longeur entre sommet et s est de plus de 10 m
            if longueur_arete(positions_sommets,s,sommet)>10:
                #On enleve se sommet
                d.remove(s)
        #Si la droite a moin de 2 element, il y a pas d'arete que le sommet peut couvir
        if len(d)<2:
            #On suprime cette droite
            to_rem.append(d)

    #Supression des dit element
    for i in to_rem:
        Resultat.remove(i)
        
    return list(Resultat)

def aretes_sur_droite(
        graphe:nx.Graph,
        sommet:int,
        sommets:List[List[int]]  ) -> List[Tuple[int,int]]:
    """
    Pour un sommet donne, renvoie la liste des arete qu'il peut couvrir mais qui ne sont pas ses voisine
    
    Args:
        graphe (nx.Graph): Graphe
        sommet (int): Sommet a considere
        sommets (Tuple[int,int]): Liste des solet

    Returns:
        List[Tuple[int,int]]: Liste des aretes a portee du sommet
    
    """
    #On initialise la liste resultat vide
    Resultat:List[Tuple[int,int]]=[]
    #Pour chaque arete
    for sommet1,sommet2 in graphe.edges():
        #Pour chaque lot de sommet dans la liste sommet atteignable
        for sommet in sommets:
            #si il y a une arete qui est comprise dans se lot
            if sommet1 in sommet and sommet2 in sommet:
                #Alors on l'ajoute dans la liste des arete atteignable
                Resultat.append((sommet1,sommet2))

    return Resultat

def main(
        graphe:nx.Graph,
        positions:Dict[int,Tuple[float,float]],
        droites:Dict[int,Set[int]],
        associations_droites:Dict[int,Set[int]],
        v_min:int,
        v_max:int) -> Tuple[
            nx.Graph,
            List[int]]:
    """
    Traite le graphe selon l'aglo deffinit
    
    Args:
        graphe (nx.Graph): Graphe
        positions (Dict[int,Tuple[float,float]]): Dictionaire des positions
        droites (Dict[int,Set[int]]): Dictionaire des droites
        associations_droites (Dict[int,Set[int]]): Dictionaire des associations des droite
        v_min (int): poids minimum des aretes
        v_max (int): poids maximum des aretes
    Returns:
        nx.Graph: Copie du graphe pour l'affichage
        List[int]: Liste des sommets ou l'on place une camera
    """
    #Copie du graphe pour differencie l'affichage du traitement*
    graphe_affichage = graphe.copy()

    #Liste des Id de camera
    id:List[int]=[-1]
    #Position des camera
    pos_cam=[]

    #Tant que il reste des arete dans le graphe
    while list(graphe.edges()):
        #Dictionaire des arete voisine atteignable
        dict_aretes_voisines_indirect={}
        #Pour chaque sommet:
        for sommet in graphe.nodes():
            #On calcul sa portee en fonction des arete du graph
            voisins_indirect = liste_voisin_eloignes(positions,droites,associations_droites,sommet)
            dict_aretes_voisines_indirect[sommet] = aretes_sur_droite(graphe,sommet,voisins_indirect)
            valuation_sommet(graphe,dict_aretes_voisines_indirect[sommet],sommet,v_min,v_max)

        #On prend un sommet au hazard comme meilleu sommet
        best = list(graphe.nodes())[0]

        #On parcour les sommet pour voir si y en a pas un meilleur
        for sommet in graphe.nodes():
            best = comparaison_sommet(graphe,best,sommet)
        #On ajoute la camera 
        pos_cam.append(best)
        id.append(id[-1]+1)
        placement_camera(graphe,graphe_affichage,best,dict_aretes_voisines_indirect[best],id[-1])

    return graphe_affichage,pos_cam
        
def placement_camera(
        graphe:nx.Graph,
        graphe_affichage:nx.Graph,
        sommet:int,
        aretes_voisines_indirect:List[Tuple[int, int]],
        id_cam:int) ->None :
    """
    Place officielement une camera sur un sommet. Modifie difrectement les graphes
    
    Args:
        graphe (nx.Graph): Grpahe sur lequel on travail
        graphe_affichage (nx.Graph): graphe a colorie utilisé pour l'affichage
        sommet (int): sommet ou l'on place une camera
        aretes_voisines_indirect (list[tuple[int, int]]):
        id_cam (int): id de la nouvelle camera
    
    Returns:
        None
    """
    #Suppression du sommet et des arete couverte couvert par la camera
    graphe.remove_node(sommet)
    graphe.remove_edges_from(aretes_voisines_indirect)

    #On ajoute l'id de la camera sur le sommet...
    graphe_affichage.nodes[sommet]["cam_id"] = id_cam

    #... et sur chaque arete couverte, d'abors indirect
    for arete in aretes_voisines_indirect:
        if not "cam_id" in graphe_affichage.edges[arete]:
            graphe_affichage.edges[arete]["cam_id"] = id_cam

    # puis dirctement connecter au sommet
    for voisin in list(graphe_affichage.neighbors(sommet)):
        graphe_affichage.edges[(voisin,sommet)]["cam_id"] = id_cam

def grille_affichage(pos:Dict[int,Tuple[float,float]]):
    # Obtenir les limites des positions des nœuds
    x_values, y_values = zip(*pos.values())
    x_min, x_max = np.floor(min(x_values)), np.ceil(max(x_values))
    y_min, y_max = np.floor(min(y_values)), np.ceil(max(y_values))

    # Définir les limites des axes pour aligner avec la grille
    plt.xlim(x_min - 1, x_max + 1)  # Ajout d'une marge
    plt.ylim(y_min - 1, y_max + 1)  # Ajout d'une marge

    # Configurer la grille pour une unité par case
    plt.xticks(np.arange(x_min - 1, x_max + 2, 1))  # Ticks tous les 1 sur x
    plt.yticks(np.arange(y_min - 1, y_max + 2, 1))  # Ticks tous les 1 sur y
    plt.grid(visible=True, which='both', color='gray', linestyle='--', linewidth=0.5)

    # Fixer l'aspect des axes pour que 1 unité sur x = 1 unité sur y
    plt.gca().set_aspect('equal', adjustable='box')

def affichage_simple(
        G:nx.Graph,
        pos:Dict[int,Tuple[float,float]]) -> None:
    """
    Affiche le graphe dans une fentre pyplot

    Args:
        G (nx.Graph): Graphe a affichee
        pos (Dict[int,Tuple[float,float]]): positions des sommets

    Returns:
        None
    """


    nx.draw_networkx_edges(G,pos,width=5) #Affiches les aretes colore
    nx.draw_networkx_nodes(G, pos,node_color='black',node_size=250) #Affiche les intersection ou y a pas de cam
    nx.draw_networkx_labels(G, pos,font_color="white",font_size=10) #Affiche le numero des sommet original
    grille_affichage(pos)
    plt.show()

def affichage_debug(
        G:nx.Graph,
        pos:Dict[int,Tuple[float,float]]) -> None:
    """
    Affiche le graphe dans une fentre pyplot

    Args:
        G (nx.Graph): Graphe a affichee
        pos (Dict[int,Tuple[float,float]]): positions des sommets

    Returns:
        None
    """ 
    nx.draw_networkx_edges(G, pos) #Affiche les aretes
    nx.draw_networkx_edge_labels(G, pos) #Affcihes les labele des aretes
    nx.draw_networkx_labels(G, pos) #Affiche les numero des sommet
    nx.draw_networkx_nodes(G, pos, node_size=400) #Affiche les sommet
    #grille_affichage(pos)
    plt.show()

def affichage_final(
        G:nx.Graph,
        O:nx.Graph,
        pos:Dict[int,Tuple[float,float]]) -> None:
    """
    Affiche le graphe dans une fentre pyplot

    Args:
        G (nx.Graph): Graphe a affichee
        O (nx.Graph): Graphe a initiale sans sommet rajouter
        pos (Dict[int,Tuple[float,float]]): positions des sommets

    Returns:
        None
    """
    #Listes des couleurs a utilisé
    colors = [
    "red", "blue", "green", "orange", "purple", "pink", "yellow", "cyan",
    "magenta", "brown", "black", "white",  "lightblue", "lightgreen",
    "darkred", "darkblue", "darkgreen", "gold", "teal", "lime", "navy",
    "coral", "chocolate", "indigo", "violet", "orchid", "tan", "salmon",
    "khaki", "turquoise", "azure", "olive", "maroon"
    ]


    edge_colors = []
    #Construis la liste des couleur en fonctions des cam_id
    for u, v, data in G.edges(data=True):
        edge_colors.append(colors[data.get('cam_id')])

    node_cam = [] #Noeud ou il y a des camera
    node_cam_col=[] #Couleur des Noeud avec des camera
    node_sans_cam =[] #Noeud sans camera

    #Pour chaque noeud on trie si il a une camera ou non (sans tenir compte des noeud rajouter sur les couloir trop long)
    for n,data in G.nodes(data=True):
        if 'cam_id' in data:
            node_cam_col.append(colors[data.get('cam_id')])
            node_cam.append(n)
        elif n in O.nodes:
            node_sans_cam.append(n)

    nx.draw_networkx_edges(G,pos,edge_color=edge_colors,width=5) #Affiches les aretes colore
    nx.draw_networkx_nodes(G, pos,node_color='black',nodelist=node_sans_cam,node_size=250) #Affiche les intersection ou y a pas de cam
    nx.draw_networkx_nodes(G, pos,node_color=node_cam_col,nodelist=node_cam,node_size=500) #Affiche les cameras

    nx.draw_networkx_labels(O, pos,font_color="white",font_size=10) #Affiche le numero des sommet original

    grille_affichage(pos)
    plt.show()

