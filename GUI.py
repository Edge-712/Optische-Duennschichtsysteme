import sys
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from main import material_list, reflectance
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QTableWidget,
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QToolButton,
    QStyle,
)
from PyQt6.QtGui import QColor, QPalette, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(
        self,
    ):
        super().__init__()

        self.setWindowTitle("Optische Dünnschichtsysteme")
        self.resize(1280, 720)
        self.central_widget = QWidget()
        self.create_graph()
        self.setCentralWidget(self.central_widget)

    def create_graph(self):
        """Anzeige der erstellten Graphen"""
        # Darstellung der ausgewählten Material-Werte in Tabelle und zusätzliche UI-Elemente
        self.grid = QTableWidget()
        self.grid.setColumnCount(3)
        self.grid.setHorizontalHeaderLabels(
            ["Material", "Dicke in nm", "Brechungsindex"]
        )
        self.grid.resizeColumnsToContents()
        self.grid.horizontalHeader().setStretchLastSection(True)

        # Restliche UI-Elemente
        add_button = QToolButton()
        add_button.setIcon(QIcon.fromTheme("list-add"))
        add_button.clicked.connect(self.add_Row)

        remove_button = QToolButton()
        remove_button.setIcon(QIcon.fromTheme("list-remove"))
        remove_button.clicked.connect(self.remove_Row)

        # Plot als UI-Element
        canvas = PlotCanvas()
        canvas.axes.plot(2 * 1e9, 3, color="blue")
        canvas.axes.set_title("Reflexionsspektrum (sichtbar)")
        canvas.axes.set_xlabel("Wellenlänge [nm]")
        canvas.axes.set_ylabel("Reflexionsgrad R")
        canvas.axes.grid(True)

        # Layout
        layout_v = QVBoxLayout()
        layout_h = QHBoxLayout()
        layout_h.addWidget(self.grid)
        layout_h.addWidget(canvas)
        layout_h.setStretch(0, 1)
        layout_h.setStretch(1, 3)
        layout_v.addLayout(layout_h)

        layout_h = QHBoxLayout()
        layout_h.addWidget(add_button)
        layout_h.addWidget(remove_button)
        layout_h.addStretch()

        layout_v.addLayout(layout_h)

        self.central_widget.setLayout(layout_v)

    def add_Row(self):
        self.grid.setRowCount(self.grid.rowCount() + 1)

        textfield_n = QLineEdit()
        textfield_d = QLineEdit()

        combobox = QComboBox()
        combobox.setPlaceholderText("Presets")
        combobox.currentIndexChanged.connect(
            lambda text: self.set_values(combobox, textfield_d, textfield_n)
        )

        for material in material_list:
            combobox.addItem(material.name, material)

        self.grid.setCellWidget(self.grid.rowCount() - 1, 0, combobox)
        self.grid.setCellWidget(self.grid.rowCount() - 1, 1, textfield_d)
        self.grid.setCellWidget(self.grid.rowCount() - 1, 2, textfield_n)

    def remove_Row(self):
        self.grid.setRowCount(self.grid.rowCount() - 1)

    def set_values(
        self, combobox: QComboBox, textfield_d: QLineEdit, textfield_n: QLineEdit
    ):
        textfield_d.setText(str(combobox.currentData().d))
        textfield_n.setText(str(combobox.currentData().n))


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
