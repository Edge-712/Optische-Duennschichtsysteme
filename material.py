import numpy as np

class Material:
    def __init__ (self, material, dicke, brechzahl):
        self.material = material
        self.dicke = dicke
        self.brechzahl = brechzahl
