import numpy as np

# /////////////////////////
#   d: Dicke in m
#   n: Brechungsindex
#   theta: Winkel in rad
#   wavelength: Wellenlänge in m
# ////////////////////////


class Material:
    """Material-Klasse für simplere Bearbeitung über GUI"""

    def refractive_index(self, wavelength):
        if self.name == "Luft":
            return 1 + (1.181494e-4 + (9.708931e-3) / (75.4 - wavelength ** (-2)))

        elif self.name == "MgF\u2082":
            return np.sqrt(
                1.27620
                + (0.60967 * wavelength**2) / (wavelength**2 - 0.08636**2)
                + (0.0080 * wavelength**2) / (wavelength**2 - 18.0**2)
                + (2.14973 * wavelength**2) / (wavelength**2 - 25.0**2)
            )
        elif self.name == "TiO\u2082":
            return np.sqrt(5.913 + 0.2441 / (wavelength**2 - 0.0803))
        elif self.name == "Al\u2082O\u2083":
            return np.sqrt(
                1
                + (1.4313493 * wavelength**2) / (wavelength**2 - 0.0726631**2)
                + (0.65054713 * wavelength**2) / (wavelength**2 - 0.1193242**2)
                + (5.3414021 * wavelength**2) / (wavelength**2 - 18.028251**2)
            )
        elif self.name == "Glas":
            return np.sqrt(
                1
                + (1.1273555 * wavelength**2) / (wavelength**2 - 0.00720341707)
                + (0.124412303 * wavelength**2) / (wavelength**2 - 0.0269835916)
                + (0.827100531 * wavelength**2) / (wavelength**2 - 100.384588)
            )
        else:
            return self.n

    def __init__(self, name, d, n=None):
        self.d = d
        self.n = n
        self.name = name

    def __str__(self):
        return self.name


# Fresnel-Formeln & Transfermatrix
def fresnel_coefficients(n1, n2, theta1, polarization):
    """Berechne Fresnel-Koeffizienten (Reflexion & Transmission)"""
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
    """Berechnet die Gesamttransfermatrix eines Mehrschichtsystems."""
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


def reflectance(material_list, wavelengths, polarization, theta0):
    """Berechnet den Reflexionsgrad R(λ)"""
    R = []

    d_list = [i.d * 1e-9 for i in material_list if i.d != np.inf]

    for wl in wavelengths:
        M = transfer_matrix(material_list, d_list, wl, polarization, theta0)
        r = M[1, 0] / M[0, 0]
        R.append(np.abs(r) ** 2)
    return np.array(R)


# System im sichtbaren Bereich (MgF2, TiO2, Al2O3)
material_list = [
    Material("Luft", np.inf, 1.00 + 0j),
    Material("MgF\u2082", 100, 1.38 + 0j),
    Material("TiO\u2082", 100, 2.40 + 0j),
    Material("Al\u2082O\u2083", 100, 1.76 + 0j),
    Material("Glas", np.inf, 1.52 + 0j),
    Material("Beliebig", 0, 0 + 0j),
]
