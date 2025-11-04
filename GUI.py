import sys
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from main import material_list, reflectance, Material
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QTableWidget,
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QToolButton,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QHeaderView,
)
from PyQt6.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(
        self,
    ):
        super().__init__()

        self.setWindowTitle("Optische Dünnschichtsysteme")
        self.resize(1280, 720)
        self.central_widget = QWidget()
        self.default_page()
        self.setCentralWidget(self.central_widget)

    def default_page(self):
        """Anzeige der erstellten Graphen"""
        # Darstellung der ausgewählten Material-Werte in Tabelle und zusätzliche UI-Elemente
        self.grid = QTableWidget()
        self.grid.setColumnCount(4)
        self.grid.setHorizontalHeaderLabels(
            [
                "Material",
                "Dicke in nm",
                "n-Real",
                "n-Imaginär",
            ]
        )
        self.grid.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # Restliche UI-Elemente
        add_button = QToolButton()
        add_button.setIcon(QIcon.fromTheme("list-add"))
        add_button.clicked.connect(self.add_Row)

        remove_button = QToolButton()
        remove_button.setIcon(QIcon.fromTheme("list-remove"))
        remove_button.clicked.connect(self.remove_Row)

        wavelength0 = QLineEdit()
        wavelength0.setPlaceholderText("1. Wellenlänge in nm")

        wavelength1 = QLineEdit()
        wavelength1.setPlaceholderText("2. Wellenlänge in nm")

        angle = QLineEdit()
        angle.setPlaceholderText("Einfallswinkel: 0-90°C")

        polarization = QComboBox()
        polarization.addItem("Senkrecht")
        polarization.addItem("Parallel")

        run_button = QPushButton("Bestätigen")
        run_button.clicked.connect(
            lambda: self.create_Graph(
                wavelength0,
                wavelength1,
                polarization,
                angle,
            )
        )

        self.canvas = PlotCanvas()
        self.canvas.axes.set_title("Reflexionsspektrum (sichtbar)")
        self.canvas.axes.set_xlabel("Wellenlänge [nm]")
        self.canvas.axes.set_ylabel("Reflexionsgrad R")
        self.canvas.axes.grid(True)

        # Layout
        layout_v = QVBoxLayout()
        self.layout_h0 = QHBoxLayout()
        self.layout_h0.addWidget(self.grid)
        self.layout_h0.addWidget(self.canvas)
        self.layout_h0.setStretch(0, 2)
        self.layout_h0.setStretch(1, 4)
        layout_v.addLayout(self.layout_h0)

        layout_h = QHBoxLayout()
        layout_h.addWidget(add_button)
        layout_h.addWidget(remove_button)
        layout_h.addWidget(wavelength0)
        layout_h.addWidget(wavelength1)
        layout_h.addWidget(angle)
        layout_h.addWidget(polarization)
        layout_h.addWidget(run_button)

        layout_v.addLayout(layout_h)

        self.central_widget.setLayout(layout_v)

    def create_Graph(
        self,
        wavelength0: QLineEdit,
        wavelength1: QLineEdit,
        polarization: QComboBox,
        angle: QLineEdit,
    ):
        """Erstellt den nötigen Graph und aktualisiert die Plots"""
        try:
            if (
                float(angle.text()) > 89
                or float(angle.text()) < 0
                or float(wavelength0.text()) <= 0
                or float(wavelength1.text()) <= 0
            ):
                raise ValueError()

            # Speichern der User-Inputs
            new_material_list = []

            for i in range(0, self.grid.rowCount()):
                name = self.grid.cellWidget(i, 0).currentText()
                d = float(self.grid.cellWidget(i, 1).text())
                n_r = self.grid.cellWidget(i, 2).text()
                n_i = self.grid.cellWidget(i, 3).text()
                n_string = n_r + "+" + n_i + "j"
                n = complex(n_string)
                if self.grid.rowCount() == 1:
                    raise ValueError
                if (i != 0 and i != self.grid.rowCount() - 1) and (
                    n.real == 0 or n.real < 0 or d <= 0 or d == np.inf
                ):
                    raise ValueError
                if (i == 0 or i == self.grid.rowCount() - 1) and d != np.inf:
                    raise ValueError
                new_material_list.append(Material(name, d, n))

            wavelength_list = np.linspace(
                float(wavelength0.text()) * 1e-9, float(wavelength1.text()) * 1e-9, 400
            )
            reflect_list = reflectance(
                new_material_list,
                wavelength_list,
                polarization.currentText(),
                float(angle.text()) * (np.pi / 180),
            )
            self.canvas.axes.clear()
            self.canvas.axes.plot(wavelength_list * 1e9, reflect_list, color="blue")
            self.canvas.axes.set_title("Reflexionsspektrum (sichtbar)")
            self.canvas.axes.set_xlabel("Wellenlänge [nm]")
            self.canvas.axes.set_ylabel("Reflexionsgrad R")
            self.canvas.axes.grid(True)
            self.canvas.draw()

        except (ValueError, ZeroDivisionError, ArithmeticError):
            QMessageBox.warning(self, "Fehlermeldung", "Ungültige Auswahl")

    def add_Row(self):
        """Fügt beim Bestätigen des + Buttons neue Zeilen hinzu"""
        self.grid.setRowCount(self.grid.rowCount() + 1)

        textfield_n_r = QLineEdit()
        textfield_n_i = QLineEdit()
        textfield_d = QLineEdit()

        combobox = QComboBox()
        combobox.setPlaceholderText("Presets")
        combobox.activated.connect(
            lambda: self.set_values(combobox, textfield_d, textfield_n_r, textfield_n_i)
        )

        for material in material_list:
            combobox.addItem(material.name, material)

        self.grid.setCellWidget(self.grid.rowCount() - 1, 0, combobox)
        self.grid.setCellWidget(self.grid.rowCount() - 1, 1, textfield_d)
        self.grid.setCellWidget(self.grid.rowCount() - 1, 2, textfield_n_r)
        self.grid.setCellWidget(self.grid.rowCount() - 1, 3, textfield_n_i)

    def remove_Row(self):
        """Entfernt beim entfernen des - Buttons eine Zeile"""
        self.grid.setRowCount(self.grid.rowCount() - 1)

    def set_values(
        self,
        combobox: QComboBox,
        textfield_d: QLineEdit,
        textfield_n_r: QLineEdit,
        textfield_n_i: QLineEdit,
    ):
        """Passt die Leeren Textboxen bei Auswahl einer der Presets an"""
        textfield_d.setText(str(combobox.currentData().d))
        textfield_n_r.setText(str(combobox.currentData().n.real))
        textfield_n_i.setText(str(combobox.currentData().n.imag))


class PlotCanvas(FigureCanvasQTAgg):
    """Klasse zum Einfügen des Plots in UI"""

    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(PlotCanvas, self).__init__(fig)


app = QApplication(sys.argv)
app.setStyle("Fusion")

window = MainWindow()
window.show()
sys.exit(app.exec())
