# Optimisation positionnement des caméras sur un réseau
Projet BUT Réseaux &amp; Télécommunication en binôme. Nous devons optimiser le placement de caméra dans un réseau de couloirs en utilisant les graphes.<br>
<br>
<u>Fichier en entrée</u> : <br>
id_sommet x y  # sommet avec positions x y <br>
id_sommet x y  <br>
...<br>
! # separateur entre coordonées et les alignements des sommets<br>
id_sommet id_sommet; id_sommet id_sommet  # Alignement des sommets <br>
id_sommet id_sommet     <br>
<br>
<u>Exemple (cf <a href="https://github.com/LucasStagnette/camera_position/blob/main/exemple.PNG">exemple.png</a>):</u><br>
1 0 0<br>
2 1 2<br>
3 2 0<br>
4 6 0<br>
!<br>
1 3;3 4 # PAS ESPACES aux côtés du ";"<br>
1 2<br>
2 3<br>
