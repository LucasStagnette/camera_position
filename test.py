distance = float(input("Entrez la distance de l'arete : "))

# calcule le nombre de points potentiels
nb_points = distance//10 - 1
if distance%10 != 0:
    nb_points +=1

# calcul l'espacement entre les poins potentiels
espacement = distance/(nb_points+1)

print(f"Il y a {int(nb_points)} points potentiels avec un espacement de {espacement}.")
