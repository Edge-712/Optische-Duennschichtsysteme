import numpy as np
import matplotlib.pyplot as plt


class Material:
    """Material-Klasse für simplere Bearbeitung über GUI"""

    def __init__(self, name, d, n):
        self.d = d
        self.n = n
        self.name = name

    def __str__(self):
        return self.n
    

# Fresnel-Formeln & Transfermatrix
def fresnel_coefficients(n1, n2, theta1, polarization="s"):
    """Berechne Fresnel-Koeffizienten (Reflexion & Transmission)"""
    theta2 = np.arcsin(n1 / n2 * np.sin(theta1))
    if polarization == "s":
        r = (n1 * np.cos(theta1) - n2 * np.cos(theta2)) / (
            n1 * np.cos(theta1) + n2 * np.cos(theta2)
        )
        t = (2 * n1 * np.cos(theta1)) / (n1 * np.cos(theta1) + n2 * np.cos(theta2))
    elif polarization == "p":
        r = (n2 * np.cos(theta1) - n1 * np.cos(theta2)) / (
            n2 * np.cos(theta1) + n1 * np.cos(theta2)
        )
        t = (2 * n1 * np.cos(theta1)) / (n2 * np.cos(theta1) + n1 * np.cos(theta2))
    else:
        raise ValueError("Polarization must be 's' or 'p'")
    return r, t, theta2

def transfer_matrix(n_list, d_list, wavelength, theta0=0, polarization="s"):
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

def reflectance(material_list, wavelengths, theta0=0, polarization="s"):
    """Berechnet den Reflexionsgrad R(λ)"""
    R = []

    n_list = [i.n for i in material_list]
    d_list = [i.d * 1e-9 for i in material_list if i.d != 0]

    for wl in wavelengths:
        M = transfer_matrix(n_list, d_list, wl, theta0, polarization)
        r = M[1, 0] / M[0, 0]
        R.append(np.abs(r) ** 2)
    return np.array(R)


# System im sichtbaren Bereich (MgF2, TiO2, Al2O3)
material_list = [
    Material("Luft", 0, 1.00),
    Material("MgF2", 102, 1.38),
    Material("TiO2", 105, 2.40),
    Material("Al2O3", 79, 1.76),
    Material("Glas", 0, 1.52),
]

# print("=== Sichtbares System ===")
# for i, material in enumerate(material_list):
#     if i == 0:
#         print(f"{i+1:2d}: {material.material} (Einfallsmedium, n = {material.n})")
#     elif i == len(material_list) - 1:
#         print(f"{i+1:2d}: {material.material} (Substrat, n = {material.n})")
#     else:
#         print(f"{i+1:2d}: {material.material} (n = {material.n}, d = {material.d} nm)")

# #EUV-Spiegel (Mo/Si-Mehrschichtsystem)

# # Komplexe Brechzahlen bei 13.5 nm
# n_Mo = 1 - 7.6044e-2 - 6.4100e-3j
# n_Si = 1 - 9.3781e-4 - 1.7260e-3j
# n_sub = 1.00  # z. B. Quarz oder Vakuum

# # 40 Bilagen Mo/Si
# N_pairs = 40
# lambda_design = 13.5e-9

# # Für EUV-Wellen ist optimale Dicke etwa λ/4n für konstruktive Interferenz
# d_Mo = lambda_design / (4 * np.real(n_Mo))
# d_Si = lambda_design / (4 * np.real(n_Si))

# n_list_euv = [1.0]  # Vakuum als Einfallmedium
# d_list_euv = []

# for _ in range(N_pairs):
#     n_list_euv += [n_Mo, n_Si]
#     d_list_euv += [d_Mo, d_Si]

# n_list_euv += [n_sub]

# # Ausgabe
# print("\n=== EUV-Multilayer (Mo/Si) ===")
# print(f"Brechzahl Mo: {n_Mo:.4f}")
# print(f"Brechzahl Si: {n_Si:.4f}")
# print(f"Dicke Mo: {d_Mo*1e9:.2f} nm")
# print(f"Dicke Si: {d_Si*1e9:.2f} nm")
# print(f"Anzahl Bilagen: {N_pairs}")

# # Simulation
# wavelengths_euv = np.linspace(10e-9, 40e-9, 300)
# R_euv = reflectance(n_list_euv, d_list_euv, wavelengths_euv)

# ============================================================
# PLOTS
# ============================================================

# plt.figure(figsize=(10, 5))
# plt.subplot(1, 2, 1)
# plt.plot(wavelengths_vis * 1e9, R_vis, color='blue')
# plt.title("Reflexionsspektrum (sichtbar)\nMgF₂ / TiO₂ / Al₂O₃ auf Glas")
# plt.xlabel("Wellenlänge [nm]")
# plt.ylabel("Reflexionsgrad R")
# plt.grid(True)

# plt.subplot(1, 2, 2)
# plt.plot(wavelengths_euv * 1e9, R_euv, color='red')
# plt.title("Reflexionsspektrum (EUV)\n40× (Mo/Si)-Schichten")
# plt.xlabel("Wellenlänge [nm]")
# plt.ylabel("Reflexionsgrad R")
# plt.grid(True)

# plt.tight_layout()
# plt.show()
