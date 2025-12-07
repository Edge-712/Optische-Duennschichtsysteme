import numpy as np
import json


# /////////////////////////
#   d: Dicke in m
#   n: Brechungsindex
#   theta: Winkel in rad
#   wavelength: Wellenlänge in m
# ////////////////////////
class Material:
    """Material-Klasse zur Simulation von Schichtmaterialen und ihren Eigenschaften.

    Attributes:
        name (str): Name des Materials.
        name_type (int): Parameter der die Art der Berechnung des Brechungsindex definiert.
        d (float): Dicke der Schicht in Nanometer.
        A (float): Optionaler Parameter zur Sellmeier-Gleichung.
        B (float): B-Koeffizient der Sellmeier-Gleichung.
        C (float): C-Koeffizient der Sellmeier-Gleichung.
        n (complex): Optionale Komplexe Brechzahl, falls sich für einen fixen Wert entschieden wird.
        formula (string): Optionaler Benutzerdefinierte Formel zur Bestimmung des Brechungsindex.
    """

    def refractive_index(self, wavelength):
        """Berechnet den Brechungsindex auf die gewünschte Art und liefert ihn zurück.

        Args:
            wavelength: Für Funktion der Wellenlänge eine Liste an Wellenlängen, andernfalls eine einzige Wellenlänge in Meter.
        Returns:
            Liefert den Brechungsindex zurück.
        """
        wavelength = wavelength * 1e6
        if self.n_type == 0:
            return self.n
        elif self.n_type == 1:
            n = 0
            wl = wavelength**2
            for i in range(0, len(self.B) - 1):
                n += (self.B[i] * wl) / (wl - self.C[i])
            return np.sqrt(1 + self.A + n)
        elif self.n_type == 2:
            global_vars = {**np.__dict__}
            local_var = {"x": wavelength}
            return eval(self.formula.strip(), global_vars, local_var)
        else:
            return self.n

    def __init__(
        self,
        name: str,
        n_type: int,
        d: float = None,  # type: ignore
        A: float = 0,
        B: list = None,  # type: ignore
        C: list = None,  # type: ignore
        n: complex = 0,  # type: ignore
        formula: str = None,  # type: ignore
    ):
        self.name = name
        self.d = d
        self.n = n
        self.n_type = n_type
        self.A = A
        self.B = B
        self.C = C
        self.formula = formula

    def __str__(self):
        """To-String Methode für Ausgabe von Material-Objekten.

        Returns:
            Name des Materials.
        """
        return self.name

    def toJson(self):
        """Nimmt alle Parameter des Material-Objekts und formt sie in ein Dictionary.

        Returns:
            Dictionary in Form des Material-Objekts.
        """
        return {
            "name": self.name,
            "d": self.d,
            "n_type": self.n_type,
            "A": self.A,
            "B": self.B,
            "C": self.C,
            "n": str(self.n),
            "formula": self.formula,
        }

    @staticmethod
    def toMaterial():
        """Liest eine lokale Material.json ein und wandelt alle Daten in die Form eines Material-Objekts um.

        Returns:
            Material Array mit allen Objekten aus der Material.json im Root.

        """
        with open("Material.json", "r") as file:
            data = json.load(file)
            material_list = [
                Material(
                    name=i["name"],
                    d=i["d"],
                    n_type=i["n_type"],
                    A=i["A"],
                    B=i["B"],
                    C=i["C"],
                    n=complex(i["n"]),
                    formula=i["formula"],
                )
                for i in data
            ]
            return material_list


# Fresnel-Formeln & Transfermatrix
def fresnel_coefficients(n1, n2, theta1, polarization):
    """Berechnet Fresnel-Koeffizienten (Reflexion & Transmission)

    Args:
        n1 (float): Brechungsindex der linken Schicht.
        n2 (float): Brechungsindex der rechten Schicht.
        theta1 (float): Einfallswinkel in Radiant.
        polarization (string): Polarisation "Senkrecht" oder "Parallel".

    """
    theta2 = np.arcsin(n1 / n2 * np.sin(theta1))
    if polarization == "Senkrecht":
        r = (n1 * np.cos(theta1) - n2 * np.cos(theta2)) / (
            n1 * np.cos(theta1) + n2 * np.cos(theta2)
        )
        t = (2 * n1 * np.cos(theta1)) / (n1 * np.cos(theta1) + n2 * np.cos(theta2))
    elif polarization == "Parallel":
        r = (n2 * np.cos(theta1) - n1 * np.cos(theta2)) / (
            n2 * np.cos(theta1) + n1 * np.cos(theta2)
        )
        t = (2 * n1 * np.cos(theta1)) / (n2 * np.cos(theta1) + n1 * np.cos(theta2))
    else:
        raise ValueError("Polarization must be 's' or 'p'")
    return r, t, theta2


def transfer_matrix(material_list, d_list, wavelength, polarization, theta0):
    """Berechnet die Gesamttransfermatrix eines Mehrschichtsystems.

    Args:
        material_list (list): Liste an Material-Objekten.
        d_list (list): Liste der jeweiligen Dicken aus den Material-Objekten in Nanometer.
        wavelength (float, list): Für Funktion der Wellenlänge eine Liste an Wellenlängen, andernfalls eine einzige Wellenlänge in Meter.
        polarization (str): Polarisation als "Senkrecht" oder "Parallel".
        theta0 (float): Einfallswinkel in Radiant.
    """
    M = np.identity(2, dtype=complex)
    theta = [theta0]

    for i in range(len(material_list) - 1):
        n1, n2 = (
            material_list[i].refractive_index(wavelength),
            material_list[i + 1].refractive_index(wavelength),
        )
        r, t, theta2 = fresnel_coefficients(n1, n2, theta[-1], polarization)
        theta.append(theta2)

        D = (1 / t) * np.array([[1, r], [r, 1]], dtype=complex)
        if i < len(d_list):  # Schichten mit endlicher Dicke
            k0 = 2 * np.pi / wavelength
            beta = k0 * n2 * np.cos(theta2) * d_list[i]
            P = np.array(
                [[np.exp(-1j * beta), 0], [0, np.exp(1j * beta)]], dtype=complex
            )
            M = M @ D @ P
        else:
            M = M @ D
    return M


def reflectance(material_list, wavelengths, polarization, theta):
    """Berechnet den Reflexionsgrad als Funktion des Einfallswinkels oder der Wellenlänge.

    Args:
        material_list (list): Liste von Material-Objekten.
        wavelengths (list, float): Für Funktion der Wellenlänge eine Liste an Wellenlängen, andernfalls eine einzige Wellenlänge in Meter.
        polarization (str): Polarization als "Senkrecht" oder "Parallel".

    """
    R = []

    d_list = [i.d * 1e-9 for i in material_list if i.d != np.inf]

    wls = np.atleast_1d(wavelengths)
    thetas = np.atleast_1d(theta)

    for wl, theta0 in np.broadcast(wls, thetas):
        M = transfer_matrix(
            material_list, d_list, float(wl), polarization, float(theta0)
        )
        r = M[1, 0] / M[0, 0]
        R.append(np.abs(r) ** 2)
    return np.array(R)


material_list = Material.toMaterial()
