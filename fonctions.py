import networkx as nx

def lecture(fichier:str):
    '''
    fichier:str
    return Tuple[dict, list, nx.graph]
    fonction qui lis les données d'un fichier et qui retourne le graphe, les positions et les alignements
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
    g.add_edges_from(edges)
    print(alignements)


lecture("graphe.txt")