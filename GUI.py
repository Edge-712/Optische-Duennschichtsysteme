import sys
import json
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from main import material_list, reflectance, Material
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QTableWidget,
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QHeaderView,
    QDialog,
    QLabel,
    QCheckBox,
)
from PyQt6.QtGui import QIcon, QPalette, QColor


class MainWindow(QMainWindow):
    def __init__(
        self,
    ):
        super().__init__()

        self.setWindowTitle("Optische Dünnschichtsysteme")
        self.resize(1280, 720)
        self.setWindowIcon(QIcon("./python.png"))
        self.central_widget = QWidget()
        self.default_page()
        self.setCentralWidget(self.central_widget)

    def default_page(self):
        """Anzeige der erstellten Graphen"""
        # Darstellung der ausgewählten Material-Werte in Tabelle und zusätzliche UI-Elemente
        self.grid = QTableWidget()
        self.grid.setColumnCount(3)
        self.grid.setHorizontalHeaderLabels(["Material", "Dicke in nm", ""])
        self.grid.horizontalHeader().setSectionResizeMode(  # type: ignore
            QHeaderView.ResizeMode.Stretch
        )

        self.insert_Row(None, 0)  # type: ignore
        self.insert_Row(None, 1)  # type: ignore

        # Neues Material erstellen
        new_material = QPushButton("Neues Material anlegen")
        new_material.clicked.connect(self.create_material)

        # Restliche UI-Elemente
        wavelength0 = QLineEdit()
        wavelength0.setPlaceholderText("1. Wellenlänge - 2. Wellenlänge (in nm)")

        angle = QLineEdit()
        angle.setPlaceholderText("Einfallswinkel: 0-89°C")

        polarization = QComboBox()
        polarization.addItem("Senkrecht")
        polarization.addItem("Parallel")

        run_button = QPushButton("Bestätigen")
        run_button.clicked.connect(
            lambda: self.create_Graph(
                wavelength0,
                polarization,
                angle,
            )
        )

        # Plot
        self.canvas = PlotCanvas()
        self.canvas.axes = self.canvas.figure.add_subplot()

        self.canvas.axes.set_title("Reflexionsspektrum")
        self.canvas.axes.set_xlabel("Wellenlänge [nm]")
        self.canvas.axes.set_ylabel("Reflexionsgrad R")
        self.canvas.axes.grid(True)

        toolbar = NavigationToolbar(self.canvas, self)
        reset_button = QPushButton("Zurücksetzen")
        reset_button.clicked.connect(self.reset)

        # Layout
        gridmat_layout = QVBoxLayout()
        gridmat_layout.addWidget(self.grid)
        gridmat_layout.addWidget(new_material)

        layout_v = QVBoxLayout()
        self.layout_h0 = QHBoxLayout()
        self.layout_h0.addLayout(gridmat_layout)
        self.layout_h0.addWidget(self.canvas)

        self.layout_h0.setStretch(1, 4)

        layout_h = QHBoxLayout()
        layout_h.addWidget(toolbar)
        layout_h.addWidget(reset_button)
        layout_v.addLayout(layout_h)
        layout_v.addLayout(self.layout_h0)

        layout_h = QHBoxLayout()
        layout_h.addWidget(wavelength0)
        layout_h.addWidget(angle)
        layout_h.addWidget(polarization)
        layout_h.addWidget(run_button)

        layout_v.addLayout(layout_h)

        self.central_widget.setLayout(layout_v)

    def create_Graph(
        self,
        wavelength0: QLineEdit,
        polarization: QComboBox,
        angle: QLineEdit,
    ):
        """Erstellt den nötigen Graph und aktualisiert die Plots"""

        try:
            wavelength_splits = wavelength0.text().split(",")
            wavelengths = [i.split("-") for i in wavelength_splits]

            if float(angle.text()) > 89 or float(angle.text()) < 0:
                raise ValueError()
            for items in wavelengths:
                if float(items[0]) <= 0 or float(items[1]) <= 0:
                    raise ValueError()

            # Speichern der User-Inputs
            new_material_list = []

            for i in range(0, self.grid.rowCount()):
                m = self.grid.cellWidget(i, 0).currentData()  # type: ignore

                if self.grid.rowCount() == 1:
                    raise ValueError
                if (i != 0 and i != self.grid.rowCount() - 1) and (
                    m.d <= 0 or m.d == np.inf
                ):
                    raise ValueError
                if (i == 0 or i == self.grid.rowCount() - 1) and m.d != np.inf:
                    raise ValueError
                new_material_list.append(m)

            wavelength_lists = [
                np.linspace(
                    float(pairs[0]) * 1e-9,
                    float(pairs[1]) * 1e-9,
                    400,
                )
                for pairs in wavelengths
            ]
            label = [i.name for i in new_material_list]
            label.append(angle.text() + "\u00b0")
            label.append(polarization.currentText())
            for wavelength_list in wavelength_lists:
                reflect_list = reflectance(
                    new_material_list,
                    wavelength_list,
                    polarization.currentText(),
                    float(angle.text()) * (np.pi / 180),
                )
                self.canvas.axes.plot(
                    wavelength_list * 1e9, reflect_list, label=str(label)
                )
                self.canvas.axes.legend()

            self.canvas.draw()

        except (ValueError, ZeroDivisionError, ArithmeticError):
            QMessageBox.warning(self, "Fehlermeldung", "Ungültige Auswahl")

    def delete_Row(self, combobox: QComboBox):
        """Entfernt nach Drücken des - Buttons die aktuelle Zeile"""
        for i in range(0, self.grid.rowCount() + 1):
            temp = self.grid.cellWidget(i, 0)
            if temp == combobox:
                self.canvas.setFocus()  # nicht Löschen, Mauszeigerfokus springt sonst zufällig hin und her
                self.grid.removeRow(i)
                break

    def insert_Row(self, combobox: QComboBox = None, counter: int = None):  # type: ignore
        """Fügt nach Drücken des + Buttons eine neue Zeile zwischen der aktuellen Zeile und der danach ein"""
        index = 0
        for i in range(0, self.grid.rowCount() + 1):
            temp = self.grid.cellWidget(i, 0)
            if temp == combobox:
                index += i + 1
                self.grid.insertRow(i + 1)
                break

        textfield_d = QLineEdit()
        button_widget = QWidget()
        button_box = QHBoxLayout()

        combobox0 = QComboBox()
        combobox0.setPlaceholderText("Presets")
        combobox0.activated.connect(lambda: self.set_values(combobox0, textfield_d))

        for material in material_list:
            combobox0.addItem(material.name, material)

        add_button = QPushButton()
        add_button.setIcon(QIcon.fromTheme("list-add"))
        add_button.clicked.connect(
            lambda checked=False, c=combobox0: self.insert_Row(c)
        )

        remove_button = QPushButton()
        remove_button.setIcon(QIcon.fromTheme("list-remove"))
        remove_button.clicked.connect(
            lambda checked=False, c=combobox0: self.delete_Row(c)
        )

        button_box.addWidget(remove_button)
        button_box.addWidget(add_button)
        button_box.setContentsMargins(0, 0, 0, 0)
        button_widget.setLayout(button_box)

        # Zum erstellen der ersten 2 Zeilen
        if combobox is None:
            self.grid.insertRow(counter)
            self.grid.setCellWidget(counter, 0, combobox0)
            self.grid.setCellWidget(counter, 1, textfield_d)
            if counter == 0:
                self.grid.setCellWidget(counter, 2, add_button)
            else:
                self.grid.setCellWidget(counter, 2, QLineEdit(""))
                self.grid.cellWidget(counter, 2).setEnabled(False)
        else:
            self.grid.setCellWidget(index, 0, combobox0)
            self.grid.setCellWidget(index, 1, textfield_d)
            self.grid.setCellWidget(index, 2, button_widget)

    def set_values(
        self,
        combobox: QComboBox,
        textfield_d: QLineEdit,
    ):
        """Passt die Leeren Textboxen bei Auswahl einer der Presets an"""
        textfield_d.setText(str(combobox.currentData().d))

    def reset(self):
        self.canvas.axes.clear()
        self.canvas.axes.set_title("Reflexionsspektrum")
        self.canvas.axes.set_xlabel("Wellenlänge [nm]")
        self.canvas.axes.set_ylabel("Reflexionsgrad R")
        self.canvas.axes.grid(True)
        self.canvas.draw()

    def create_material(self):
        dialog = QDialog()
        layoutv = QVBoxLayout()

        name = QLabel("Name: ")
        namef = QLineEdit()
        namef.setPlaceholderText("Material")
        layouth = QHBoxLayout()
        layouth.addWidget(name)
        layouth.addWidget(namef)
        layoutv.addLayout(layouth)

        index = QLabel("Brechungsindex: ")
        real = QLineEdit()
        real.setPlaceholderText("Reell")
        imaginary = QLineEdit()
        imaginary.setPlaceholderText("Imaginär")
        imaginary.setDisabled(True)
        check = QCheckBox()
        check.clicked.connect(lambda: imaginary.setDisabled(imaginary.isEnabled()))
        check.clicked.connect(lambda: imaginary.clear())

        layouth = QHBoxLayout()
        layouth.addWidget(index)
        layouth.addWidget(real)
        layouth.addWidget(imaginary)
        layouth.addWidget(check)

        layoutv.addLayout(layouth)

        confirm = QPushButton("Bestätigen")
        confirm.clicked.connect(lambda: self.check_index(namef.text(), real, imaginary))

        layoutv.addWidget(confirm)

        dialog.setLayout(layoutv)

        dialog.exec()

    def check_index(self, name: str, real: QLineEdit, imaginary: QLineEdit):
        if imaginary.isEnabled():
            n = complex(float(real.text()), float(imaginary.text()))
        else:
            n = float(real.text())

        material_list.append(Material(name, 100, n))
        jsonlist = [i.toJson() for i in material_list]

        with open("Material.json", "w") as file:
            json.dump(jsonlist, file, indent=4)


class PlotCanvas(FigureCanvasQTAgg):
    """Klasse zum Einfügen des Plots in UI"""

    def __init__(self, width=5, height=4, dpi=100, parent=None):
        super(PlotCanvas, self).__init__()


app = QApplication(sys.argv)
app.setStyle("Fusion")
# palette = QPalette()
# palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
# palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
# palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
# palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
# palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
# palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
# palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(118, 118, 118))

# app.setPalette(palette)

window = MainWindow()
window.show()
sys.exit(app.exec())
