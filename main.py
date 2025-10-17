import numpy as np
from material import Material

#Berechnung der Matrix fürs Einbeziehen der Phasenverschiebung
def Phasenmatrix(wellenlänge, brechzahl1, brechzahl2, dicke, theta1, polarisation):
    print(theta1)
    theta2 = np.arcsin(brechzahl1 * np.sin(theta1) / brechzahl2)    #Ausfallswinkel
    if(dicke == np.inf):
        phasenverschiebung = 0
    else:
        phasenverschiebung = (2 * np.pi)/wellenlänge * brechzahl2 * dicke * np.cos(theta2)
    if(polarisation == 0):      #senkrecht
        q = brechzahl2 * np.cos(theta2)
    elif(polarisation == 1):    #parallel
        q = np.cos(theta2) / brechzahl2     
    return (np.array([[np.cos(phasenverschiebung), (1j/q) * np.sin(phasenverschiebung)], 
                    [1j * q * np.sin(phasenverschiebung), np.cos(phasenverschiebung)]]))

#Berechung der Matrix fürs Einbeziehen der Transmission und Reflexion
def Übergangsmatrix():
    return

#Berechung des Absoprtionskoeffizienten für variierenden Brechszahl
def Absorptionskoeffizient():
    return

#Berechnung der Gesamtmatrix durch erstellen von Übergangs- und Phasenmatrix
def Gesamtmatrix(wellenlänge, schichten, theta1, polarisation):
    matrixliste = []
    gsmtmatrix = np.identity(2)         #Einheitsmatrix, wenn Problem -> ,dtype = complex
    for i in range(len(schichten) - 1):
        matrixliste.append(Phasenmatrix(
            wellenlänge, schichten[i].brechzahl,
            schichten[i+1].brechzahl,
            schichten[i].dicke,
            theta1,
            polarisation
            ))
        theta1 = np.arcsin(schichten[i].brechzahl * np.sin(theta1) / schichten[i+1].brechzahl)
    for matrix in matrixliste:
        gsmtmatrix = gsmtmatrix @ matrix 
    return gsmtmatrix

#Material-Preset
schichten = [
    Material("Luft", np.inf, 1.0002916),
    Material("MgF2", 102, 1.3949),
    Material("TiO2", 105, 2.8717),
    Material("AL2O3", 79, 1.7819),
    Material("Glas", np.inf, 1.3995 + 0.0369j)
]

#Dicke und Wellenlänge in nm
einfallswinkel = np.pi/3
wellenlänge = 450
senkrecht = 0
parallel = 1