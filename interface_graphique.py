
import tkinter as tk
from fonctions import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog

# initialisation des variables
nb_cameras = 0
a = False
canvas_widget = None
file_name = None


# fonction pour importer un fichier dans notre IG
def importer_fichier():
    global a, G, pos, droites, assos, v_min, v_max, fichier, file_name, nb_cameras
    fichier = filedialog.askopenfilename(
        title = "Importer un fichier",
        filetypes=[("Fichiers texte", "*.txt")]
    )
    file_name = fichier
    if fichier:
        if a:
            canvas_widget.pack_forget()
            canvas_widget.destroy()
        G, pos, droites, assos = lecture(fichier)
        O, v_min, v_max = pretraitement_graph(G, pos, droites, assos)
        affichage_simple(O, pos, frame_affichage)
        nb_cameras = 0
        cameras_var.set(f"Nombre de caméras : {nb_cameras}")
        a = True

# fonction pour positionner les caméras
def resolution():
    global canvas_widget, a, nb_cameras

    if a:

        G, pos, droites, assos = lecture(fichier)
        O, v_min, v_max = pretraitement_graph(G, pos, droites, assos)

        Graphe_final, liste = main(G, pos, droites, assos, v_min, v_max)
        nb_cameras = len(liste)
        canvas_widget.pack_forget()
        canvas_widget.destroy()
        affichage_final(Graphe_final, O, pos, frame_affichage)
        cameras_var.set(f"Nombre de caméras : {nb_cameras}")
        print(nb_cameras)

# exporter l'image du graphe actuel
def exporter_fichier():
    fichier = filedialog.asksaveasfilename(
        title="Enregistrer l'image sous",
        defaultextension=".png",
        filetypes=[("Fichiers PNG", "*.png"), ("Fichiers JPEG", "*.jpg")]
    )
    if fichier:  # Vérifie si l'utilisateur n'a pas annulé
        plt.savefig(fichier)
        plt.close()

# afficher le graphe avant les caméras
def affichage_simple(G: nx.Graph, pos: Dict[int, Tuple[float, float]], frame: tk.Frame):
    global canvas_widget, a
    # Création d'une figure matplotlib
    fig, ax = plt.subplots()
    ax.clear()  # S'assurer que la figure est vide avant d'ajouter des éléments

    # Dessiner le graphe
    nx.draw_networkx_edges(G,pos,width=5) #Affiches les aretes colore
    nx.draw_networkx_nodes(G, pos,node_color='black',node_size=250) #Affiche les intersection ou y a pas de cam
    nx.draw_networkx_labels(G, pos,font_color="white",font_size=10) #Affiche le numero des sommet original
    #ax.set_facecolor('#F598C3')
    fig.patch.set_facecolor('#F598C3')
    plt.grid()

    # Créer un canvas pour insérer la figure dans tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    canvas.draw()
    a = True

# afficher le graphe final avec les caméras
def affichage_final(G:nx.Graph, O:nx.Graph, pos:Dict[int,Tuple[float,float]], frame:tk.Frame) -> None:
    """
    Affiche le graphe dans une fentre pyplot

    Args:
        G (nx.Graph): Graphe a affichee
        O (nx.Graph): Graphe a initiale sans sommet rajouter
        pos (Dict[int,Tuple[float,float]]): positions des sommets

    Returns:
        None
    """
    global a, canvas_widget

    #Listes des couleurs a utilisé
    colors = [
    "red", "blue", "green", "orange", "purple", "pink", "yellow", "cyan",
    "magenta", "brown", "black", "white",  "lightblue", "lightgreen",
    "darkred", "darkblue", "darkgreen", "gold", "teal", "lime", "navy",
    "coral", "chocolate", "indigo", "violet", "orchid", "tan", "salmon",
    "khaki", "turquoise", "azure", "olive", "maroon"
    ]

    # suppression du dessin actuel

    # Création d'une figure matplotlib
    fig, ax = plt.subplots()
    ax.clear()  # S'assurer que la figure est vide avant d'ajouter des éléments

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
    #Repositionne les label pour que il soit au millieux de la case
    nx.draw_networkx_labels(O, pos,font_color="white",font_size=10) #Affiche le numero des sommet original
    fig.patch.set_facecolor('#F598C3')
    plt.grid()

    # Créer un canvas pour insérer la figure dans tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    canvas.draw()
    a = True

# fonction pour annuler le placement des caméras et revenir au graphe de base
def undo():
    global a
    if a:
        canvas_widget.pack_forget()
        canvas_widget.destroy()
        G, pos, droites, assos = lecture(fichier)
        e, v_min, v_max = pretraitement_graph(G, pos, droites, assos)
        affichage_simple(G, pos, frame_affichage)
        cameras_var.set(f"Nombre de caméras : 0")
        a = True

# Création de la fenêtre tkinter
root = tk.Tk()
root.title("Algorithme pour caméras")

# personnalisation de la fenetre
root.title("Implantation d'un réseau de caméras de surveillance")
root.geometry("1080x720")
root.minsize(1080, 720)
root.maxsize(1080, 720)
root.iconbitmap("spy.ico")
root.config(background='#FFFFFF')
root.rowconfigure(0, weight=1)
root.rowconfigure(2, weight=3)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)

# initialisation du nombre de caméras
cameras_var = tk.StringVar()
cameras_var.set(f"Nombre de caméras : {nb_cameras}")

# creation du titre
title = tk.Label(root, text="Outil de positionnement de caméras", font=("Arial", 20), fg='black', bg='#81CEFE')
title.grid(row=0, column=0, columnspan=2, sticky="nsew")

# creation des frames solution affichage
frame_affichage = tk.Frame(root, relief="sunken", bd=5, bg='#F598C3')
frame_solution = tk.Frame(root, relief="sunken", bd=5, bg='#55FB78')

# organisation des frames
frame_solution.grid(row=2, column=0, sticky="nsew")
frame_affichage.grid(row=1, column=1, rowspan=2, sticky="nsew")

# remplissage frame solution
solution = tk.Label(frame_solution, text="Solution :", bg='#55FB78', font=("Arial", 15))
fic = tk.Button(frame_solution, text="Charger fichier", command=lambda : importer_fichier(), width=20, height=2)
resolve = tk.Button(frame_solution, text='Résoudre', width=20, height=2, command=lambda : resolution())
annule = tk.Button(frame_solution, text='Annuler', width=20, height=2, command=lambda : undo())
cameras = tk.Label(frame_solution, textvariable=cameras_var, bg='#55FB78')
export = tk.Button(frame_solution, text="Exporter", command=lambda : exporter_fichier(), width=20, height=2)

# pack frame solution
solution.pack(side="top", pady="10")
cameras.pack(pady="10")
fic.pack(pady=5)
resolve.pack(pady=5)
annule.pack(pady=5)
export.pack(pady=5)


# remplissage frame affichage
affich = tk.Label(frame_affichage, text="Graphe : ", bg='#F598C3', font=("Arial", 15))

# pack frame affichage
affich.pack(pady=10)

# lancement de la fenetre
root.mainloop()