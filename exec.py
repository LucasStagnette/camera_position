from fonctions import *

#Lecture du fichier
G,positions,droites,associations_droites = lecture("fichier/graphe6.txt")

#Affichage de l'original
affichage_simple(G,positions)

#Pretraitement du Graph
graphe_original,v_min,v_max = pretraitement_graph(G,positions,droites,associations_droites)
affichage_debug(G,positions)

graphe_affichage,pos_cam = main(G,positions,droites,associations_droites,v_min,v_max)
print(pos_cam)
affichage_final(graphe_affichage,graphe_original,positions)
