from PyQt6.QtWidgets import *
import sys
from main import material_list

class MainWindow(QMainWindow):
    def __init__(self,):
        super().__init__()

        self.setWindowTitle("Optische Dünnschichtsysteme")
        self.setFixedSize(1280, 720)
        self.stack = QStackedWidget()

        self.home = self.create_home()

        self.stack.addWidget(self.home)

        self.setCentralWidget(self.stack)


    def create_home(self):
        """Default State der GUI"""
        page = QWidget()
        
        layout_v = QVBoxLayout(page)
        layout_h = QHBoxLayout()

        label = QLabel("Anzahl der Schichten: ")

        self.dropdown = QComboBox()
        self.dropdown.addItems([str(i) for i in range(1,100)])

        button = QPushButton("Bestätigen")
        button.clicked.connect(self.go_settings)

        layout_h.addWidget(label)
        layout_h.addWidget(self.dropdown)
        layout_h.addWidget(button)

        layout_v.addLayout(layout_h)
        layout_v.addStretch()
        layout_h.addStretch()

        return page

    def create_settings(self):
        """Auswahl der nötigen Parameter"""
        page = QWidget()
        layout_v = QVBoxLayout(page)

        for i in range(1, int(self.dropdown.currentText()) + 1):
            layout_h = QHBoxLayout()

            text = QLabel(f"{i}. Material: \t")
            dropdown = QComboBox()
            dropdown.setPlaceholderText("Presets")

            for material in material_list:
                dropdown.addItem(material.material)

            layout_h.addWidget(text)
            layout_h.addWidget(dropdown)
            layout_v.addLayout(layout_h)
            layout_h.addStretch()

        layout_h = QHBoxLayout()
        button = QPushButton("Bestätigen")

        layout_h.addWidget(button)
        layout_h.addStretch()

        layout_v.addLayout(layout_h)
        layout_v.addStretch()
        return page

    def go_home(self):
        """Wechselt Stack Widget auf Startseite"""
        self.stack.setCurrentIndex(0)

    def go_settings(self):
        """Wechselt Stack Widget zur Parameterauswahl"""
        self.settings = self.create_settings()
        self.stack.addWidget(self.settings)

        self.stack.setCurrentIndex(1)

app = QApplication(sys.argv)

window = MainWindow()
window.show()
sys.exit(app.exec())