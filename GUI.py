import sys
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from main import material_list, reflectance
from PyQt6.QtWidgets import (
    QStackedWidget,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QApplication,
    QMessageBox,
)


class MainWindow(QMainWindow):
    def __init__(
        self,
    ):
        super().__init__()

        # Später einzulesene Variablen
        self.setWindowTitle("Optische Dünnschichtsysteme")
        self.dropdown_list = []
        self.material_count = QComboBox()

        # Layout-Konfiguration
        self.stack = QStackedWidget()
        self.home = self.create_home()
        self.settings = self.create_graph()
        self.graph = self.create_graph()
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.settings)
        self.stack.addWidget(self.graph)
        self.setCentralWidget(self.stack)

    def create_home(self):
        """Default State der GUI"""
        # UI-Elemente
        label = QLabel("Anzahl der Schichten: ")

        dropdown = QComboBox()
        dropdown.addItems([str(i) for i in range(1, 20)])
        self.material_count = dropdown

        button = QPushButton("Bestätigen")
        button.clicked.connect(self.go_settings)

        # Layout
        page = QWidget()
        layout_v = QVBoxLayout(page)

        layout_h = QHBoxLayout()
        layout_h.addWidget(label)
        layout_h.addWidget(dropdown)
        layout_h.addWidget(button)
        layout_h.addStretch()

        layout_v.addLayout(layout_h)
        layout_v.addStretch()

        return page

    def create_settings(self):
        """Auswahl der nötigen Parameter"""
        page = QWidget()
        layout_v = QVBoxLayout(page)

        # Generation angegebener Menge an Dropdown-Menüs und andere UI-Elemente
        for i in range(1, int(self.material_count.currentText()) + 1):
            layout_h = QHBoxLayout()
            text = QLabel(f"{i}. Material: \t")
            dropdown = QComboBox()
            dropdown.setPlaceholderText("Presets")
            self.dropdown_list.append(dropdown)
            for material in material_list:
                dropdown.addItem(material.name, material)

            layout_h.addWidget(text)
            layout_h.addWidget(dropdown)
            layout_h.addStretch()
            layout_v.addLayout(layout_h)

        button = QPushButton("Bestätigen")
        button.clicked.connect(self.go_graph)

        # Layout
        layout_h = QHBoxLayout()
        layout_h.addWidget(button)
        layout_h.addStretch()

        layout_v.addLayout(layout_h)
        layout_v.addStretch()

        return page

    def create_graph(self):
        """Anzeige der erstellten Graphen"""
        # Darstellung der ausgewählten Material-Werte in Tabelle und zusätzliche UI-Elemente
        new_material_list = []
        for menus in self.dropdown_list:
            new_material_list.append(menus.currentData())
        grid = QTableWidget()
        grid.setRowCount(len(new_material_list))
        grid.setColumnCount(3)
        grid.setHorizontalHeaderLabels(["Material", "Dicke in nm", "Brechungsindex"])
        grid.resizeColumnsToContents()
        grid.horizontalHeader().setStretchLastSection(True)
        for i, material in enumerate(new_material_list):
            grid.setItem(i, 0, QTableWidgetItem(material.name))
            grid.setItem(i, 1, QTableWidgetItem(str(material.d)))
            grid.setItem(i, 2, QTableWidgetItem(str(material.n)))

        button = QPushButton("Zurücksetzen")
        button.clicked.connect(self.go_home)

        # Berechnung der Reflektion
        wavelengths_vis = np.linspace(400e-9, 800e-9, 400)
        r_vis = reflectance(new_material_list, wavelengths_vis)

        # Plot als UI-Element
        canvas = PlotCanvas()
        canvas.axes.plot(wavelengths_vis * 1e9, r_vis, color="blue")
        canvas.axes.set_title("Reflexionsspektrum (sichtbar)")
        canvas.axes.set_xlabel("Wellenlänge [nm]")
        canvas.axes.set_ylabel("Reflexionsgrad R")
        canvas.axes.grid(True)

        # Layout
        page = QWidget()
        layout_v = QVBoxLayout(page)

        layout_h = QHBoxLayout()
        layout_h.addWidget(grid)
        layout_h.addWidget(canvas)

        layout_v.addLayout(layout_h)
        layout_v.addWidget(button)

        return page

    def go_graph(self):
        """Wechselt Stack-Widget zur Graphenanzeige und übernimmt die Gewählten Parameter"""
        try:
            self.graph = self.create_graph()
            self.stack.addWidget(self.graph)
            self.stack.setCurrentWidget(self.graph)
        except AttributeError:
            QMessageBox.warning(
                self, "Ungültige Auswahl", "Wählen Sie Ihre Materialien aus!"
            )

    def go_home(self):
        """Wechselt Stack-Widget auf Startseite"""
        self.dropdown_list.clear()
        self.stack.removeWidget(self.home)
        self.home = self.create_home()
        self.stack.addWidget(self.home)
        self.stack.setCurrentWidget(self.home)

    def go_settings(self):
        """Wechselt Stack-Widget zur Parameterauswahl"""
        self.stack.removeWidget(self.settings)
        self.settings = self.create_settings()
        self.stack.addWidget(self.settings)
        self.stack.setCurrentWidget(self.settings)


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
