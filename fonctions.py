import networkx as nx
import matplotlib.pyplot as plt

from math import sqrt
from random import randint
from typing import List, Dict, Tuple, Set

def lecture(fichier:str) -> Tuple[nx.Graph,Dict[int,Tuple[float,float]],Dict[int,Set[int]],Dict[int,Set[int]]]:
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

def cherche_droite(
        associations_droites:Dict[int,Set[int]],
        sommet_A:int,
        sommet_B:int) -> int:
    """
    Reenvoie le nom de la droite commune a deux sommet
    """
    #Extractin des droite ou sont présent A et B
    droites_A=associations_droites[sommet_A]
    droites_B=associations_droites[sommet_B]

    #Cherche et retourne la droite en commun
    for i in droites_A:
        for k in droites_B:
            if k == i:
                return k
    return None

def liste_voisin_eloignes(
        position_sommet:Dict[int,Tuple[float,float]],
        droites:Dict[int,Set[int]],
        associations_droites:Dict[int,Set[int]],
        sommet:int) -> List[int]:
    """Renvoie la liste des voisin a la porté du sommet"""
    R:list[List[int,int]]=list()
    droites_du_sommet:set[int] = associations_droites[sommet]
    for droite in droites_du_sommet:
        R.append(list(droites[droite]))
    #for voisin in Graph.neighbors(sommet):
    #    R.remove(voisin)
    to_rem=[]
    for d in R:
        d.remove(sommet)
        for s in d:
            if longueur_arete(position_sommet,s,sommet)>10:
                d.remove(s)
        if len(d)<2:
            to_rem.append(d)
    for i in to_rem:
        R.remove(i)
    return list(R)

def aretes_sur_droite(
        graphe:nx.Graph,
        sommet:int,
        sommets:List[int]  ) -> List[Tuple[int,int]]:
    """Pour un sommet donné, renvoie la liste des arete qu'il peut couvrir mais qui ne sont pas ses voisine"""
    R:List[Tuple[int,int]]=[]
    for sommet1,sommet2 in graphe.edges():
        for sommet in sommets:
            if sommet1 in sommet and sommet2 in sommet:
                R.append((sommet1,sommet2))
    return R

def division_arete_trop_longue(
        graphe:nx.Graph,
        position_sommet:Dict[int,Tuple[float,float]],
        droites:Dict[int,Set[int]],
        associations_droites:Dict[int,Set[int]],
        arete:Tuple[int,int],
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
        position_sommet (Dict[int,Tuple[float,float]]): Position des sommets
        droites (List[Set[int]]): Liste des droites
        arete (Tuple[int,int]): arete a divise
        longueur (float): longueur de l'arete deja calculer

    Returns:
        Tuple[nx.Graph,Dict[int,Tuple[float,float]], List[Set[str]]]: 
    """
    sommet_a,sommet_b = arete[0],arete[1]
    
    #Suprresion de l'arete trop longue
    graphe.remove_edge(sommet_a,sommet_b)

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
        liste_sommet_prexistant: list[int] = sorted([int(i) for i in list(graphe.nodes())])

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
    
    #Ajout des nouvelle arete dans le graphe
    graphe.add_edges_from(arete_temp)

    #Ajout des nouveau sommet sur la droite
    droite_originel=cherche_droite(associations_droites,sommet_a,sommet_b)
    droites[droite_originel].update(align_temp)

    #Creation des set pour les associations
    for sommet in align_temp:
        associations_droites[sommet]=set()
        associations_droites[sommet].add(droite_originel)

    return graphe,position_sommet,droites,associations_droites

def pretraitement_graph(
        graphe:nx.Graph,
        position_sommet:Dict[int,Tuple[float,float]],
        droites:Dict[int,Set[int]],
        associations_droites:Dict[int,Set[int]]) -> Tuple[int,int] :
    """
    Cette fonction prend en entré un graph et la postion de ces sommets,
    Si une arete fait plus de 10m l'arete est divisé en sous aretes
    et retourne un graphe avec pour chaque arête sa longueur et son poid. 
    
    Args:
        graphe (nx.Graph): Graphe des couloir
        position_sommet (Dict[str:Tuple[str,str]): Coordonnees des sommets
        droites (List[Set[int]]): Liste des droites

    Returns:
        None  
    """

    #Parcour de toute les aretes du Graph
    for arete in graphe.edges():

        #Calcule de sa longueur
        longueur:float = longueur_arete(position_sommet,arete[0],arete[1])

        #Ajout du label longueur
        graphe[arete[0]][arete[1]]['longueur']=longueur

               
    #Extraction de la liste des aretes 
    liste_arete_init:List[Tuple[int,int]] = list(graphe.edges())

    for arete in liste_arete_init:

        #Recuperation de la longueur de l'arete
        longueur:float = graphe[arete[0]][arete[1]].get('longueur')

        #Si elle fait plus de 10m, on divise l'arete
        if longueur > 10:
            graphe,position_sommet,droites,associations_droites = division_arete_trop_longue(graphe,position_sommet,droites,associations_droites,arete,longueur)

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
                    if longueur_arete(position_sommet, sommet, sommet1) <= 10 and longueur_arete(position_sommet, sommet, sommet2) <= 10:
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

    return (v_min,v_max)

def valuation_sommet(graphe:nx.Graph,
        aretes_voisines_indirect,
        sommet:int,
        v_min:int,
        v_max:int):
    
    #Initialisation des liste vide pour l'aret
    graphe.nodes[sommet]["portee"] = [0 for i in range(v_min, 2*v_max)]
    
    for voisins in graphe.neighbors(sommet):
        #met la valeur du degree      recupere le poids de l'arete soustrait 2 et ajoute 1 au degree

        graphe.nodes[sommet]["portee"][int(graphe[sommet][voisins].get("poids"))-2] += 1

    for arete in aretes_voisines_indirect:
        graphe.nodes[sommet]["portee"][int(graphe[arete[0]][arete[1]].get("poids"))] += 1

    return graphe


def comparaison_sommet(G:nx.Graph,sommet_A:int,sommet_B:int) -> int:
    """
    Compare la liste des poid des arete adjancente a des sommet et renvoie celui qui a la valeur préféré
    """
    for i in range(len(G.nodes[sommet_A].get("portee"))):
        some1 = G.nodes[sommet_A].get("portee")[i]
        some2 = G.nodes[sommet_B].get("portee")[i]
        if some1 == some2:
            pass
        elif some1 > some2:
            return sommet_A
        elif some1 < some2:
            return sommet_B
    return sommet_A

def main(graphe:nx.Graph,
        positions:Dict[int,Tuple[float,float]],
        droites:Dict[int,Set[int]],
        associations_droites:Dict[int,Set[int]],
        v_min:int,
        v_max:int):
    graphe_affichage = graphe.copy()
    id=[0]
    while list(graphe.edges()):
        dict_aretes_voisines_indirect={}
        for sommet in graphe.nodes():
            voisins_indirect = liste_voisin_eloignes(positions,droites,associations_droites,sommet)
            dict_aretes_voisines_indirect[sommet] = aretes_sur_droite(graphe,sommet,voisins_indirect)
            valuation_sommet(graphe,dict_aretes_voisines_indirect[sommet],sommet,v_min,v_max)
        best = list(graphe.nodes())[0]

        for sommet in graphe.nodes():
            
            best = comparaison_sommet(graphe,best,sommet)

        id.append(id[-1]+1)
        #print(best)
        placement_camera(graphe,graphe_affichage,best,dict_aretes_voisines_indirect[best],id[-1])

    return graphe_affichage
        

def placement_camera(graphe:nx.Graph,graphe_affichage:nx.Graph,sommet:int,aretes_voisines_indirect,id_cam:int):
    graphe.remove_node(sommet)
    graphe.remove_edges_from(aretes_voisines_indirect)

    graphe_affichage.nodes[sommet]["cam_id"] = id_cam
    for arete in aretes_voisines_indirect:
        if not "cam_id" in graphe_affichage.edges[arete]:
            graphe_affichage.edges[arete]["cam_id"] = id_cam
    for voisin in list(graphe_affichage.neighbors(sommet)):
        graphe_affichage.edges[(voisin,sommet)]["cam_id"] = id_cam



def affichage(G:nx.Graph,pos:Dict[int,Tuple[float,float]],debug:bool=False,color=True):
    nx.draw_networkx_edges(G, pos)
    if color:
        colors = [
        "red", "blue", "green", "orange", "purple", "pink", "yellow", "cyan",
        "magenta", "brown", "black", "white",  "lightblue", "lightgreen",
        "darkred", "darkblue", "darkgreen", "gold", "teal", "lime", "navy",
        "coral", "chocolate", "indigo", "violet", "orchid", "tan", "salmon",
        "khaki", "turquoise", "azure", "olive", "maroon"
        ]
        def obtenir_couleur(data):
            cam_id = data.get('cam_id', None)
            return colors[cam_id % len(colors)] if cam_id is not None else "gray"

        # Couleurs des nœuds
        couleurs_noeuds = [obtenir_couleur(G.nodes[n]) for n in G.nodes]

        # Couleurs des arêtes
        couleurs_aretes = [obtenir_couleur(data) for _, _, data in G.edges(data=True)]
        
        nx.draw(G, pos, with_labels=True, node_color=couleurs_noeuds, edge_color=couleurs_aretes, node_size=500, width=2)

    if debug:
        nx.draw_networkx_edge_labels(G, pos)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_nodes(G, pos, node_size=400)
    plt.show()
    pass
