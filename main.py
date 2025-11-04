import numpy as np


class Material:
    """Material-Klasse für simplere Bearbeitung über GUI"""

    def __init__(self, name, d, n):
        self.d = d
        self.n = n
        self.name = name

    def __str__(self):
        return self.n


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


def transfer_matrix(n_list, d_list, wavelength, polarization, theta0):
    """Berechnet die Gesamttransfermatrix eines Mehrschichtsystems."""
    M = np.identity(2, dtype=complex)
    theta = [theta0]

    for i in range(len(n_list) - 1):
        n1, n2 = n_list[i], n_list[i + 1]
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

    n_list = [i.n for i in material_list]
    d_list = [i.d * 1e-9 for i in material_list if i.d != np.inf]

    for wl in wavelengths:
        M = transfer_matrix(n_list, d_list, wl, polarization, theta0)
        r = M[1, 0] / M[0, 0]
        R.append(np.abs(r) ** 2)
    return np.array(R)


# System im sichtbaren Bereich (MgF2, TiO2, Al2O3)
material_list = [
    Material("Luft", np.inf, 1.00 + 0j),
    Material("MgF2", 100, 1.38 + 0j),
    Material("TiO2", 100, 2.40 + 0j),
    Material("Al2O3", 100, 1.76 + 0j),
    Material("Glas", np.inf, 1.52 + 0j),
    Material("Beliebig", 0, 0 + 0j),
]
