import sys
import json
import copy
import numpy as np
from matplotlib.figure import Figure
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
    QPlainTextEdit,
)
from PyQt6.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(
        self,
    ):
        try:
            super().__init__()
            self.setWindowTitle("Optische Dünnschichtsysteme")
            self.resize(1280, 720)
            self.setWindowIcon(QIcon("./python.png"))
            self.central_widget = QWidget()
            self.default_page()
            self.setCentralWidget(self.central_widget)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Kritischer Fehler",
                f"Fehler beim Initialisieren der Hauptfenster: {e}",
            )
            raise

    def default_page(self):
        try:
            self.setup_table()
            self.setup_graph()
            self.setup_fields()
            self.setup_layout()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Kritischer Fehler",
                f"Fehler beim Erstellen der Standardseite: {e}",
            )
            raise

    def setup_table(self):
        self.grid = QTableWidget()
        self.grid.setColumnCount(3)
        self.grid.setHorizontalHeaderLabels(["Material", "Dicke in nm", ""])
        self.grid.horizontalHeader().setSectionResizeMode(  # type: ignore
            QHeaderView.ResizeMode.Stretch
        )
        self.insert_Row(None, 0)  # type: ignore
        self.insert_Row(None, 1)  # type: ignore

    def setup_graph(self):
        self.canvas = PlotCanvas()
        self.canvas.axes = self.canvas.figure.add_subplot()
        self.canvas.axes.set_title("Reflexionsspektrum")
        self.canvas.axes.set_xlabel("Wellenlänge [nm]")
        self.canvas.axes.set_ylabel("Reflexionsgrad R")
        self.canvas.axes.grid(True)

    def setup_fields(self):
        self.new_material = QPushButton("Neues Material anlegen")
        self.new_material.clicked.connect(self.create_material)
        self.wavelength = QLineEdit()
        self.wavelength.setPlaceholderText("1. Wellenlänge - 2. Wellenlänge (in nm)")
        self.angle = QLineEdit()
        self.angle.setPlaceholderText("Einfallswinkel: 0-89°C")
        self.polarization = QComboBox()
        self.polarization.addItem("Senkrecht")
        self.polarization.addItem("Parallel")
        self.run_button = QPushButton("Bestätigen")
        self.run_button.clicked.connect(self.plot_function)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.reset_button = QPushButton("Zurücksetzen")
        self.reset_button.clicked.connect(self.reset)

    def setup_layout(self):
        gridmat_layout = QVBoxLayout()
        gridmat_layout.addWidget(self.grid)
        gridmat_layout.addWidget(self.new_material)
        layout_v = QVBoxLayout()
        layout_h0 = QHBoxLayout()
        layout_h0.addLayout(gridmat_layout)
        layout_h0.addWidget(self.canvas)
        layout_h0.setStretch(1, 4)
        layout_h = QHBoxLayout()
        layout_h.addWidget(self.toolbar)
        layout_h.addStretch(1)
        layout_h.addWidget(self.reset_button)
        layout_v.addLayout(layout_h)
        layout_v.addLayout(layout_h0)
        layout_h = QHBoxLayout()
        layout_h.addWidget(self.wavelength)
        layout_h.addWidget(self.angle)
        layout_h.addWidget(self.polarization)
        layout_h.addWidget(self.run_button)
        layout_v.addLayout(layout_h)
        self.central_widget.setLayout(layout_v)

    def plot_function(self):
        try:
            self.validate_inputs()
            if len(self.wavelengths) > 1:
                wavelength_lists = np.linspace(
                    float(self.wavelengths[0]) * 1e-9,
                    float(self.wavelengths[1]) * 1e-9,
                    400,
                )
                label = [i.name for i in self.new_material_list]
                label.append(self.angle.text() + "\u00b0")
                label.append(self.polarization.currentText())
                reflect_list = reflectance(
                    self.new_material_list,
                    wavelength_lists,
                    self.polarization.currentText(),
                    float(self.angles[0]) * (np.pi / 180),
                )
                self.canvas.axes.set_xlabel("Wellenlänge [nm]")
                self.canvas.axes.set_ylabel("Reflexionsgrad R")
                self.canvas.axes.plot(
                    wavelength_lists * 1e9, reflect_list, label=str(label)
                )
                self.canvas.axes.legend()
            elif len(self.angles) > 1:
                label = [i.name for i in self.new_material_list]
                label.append(self.wavelengths[0] + "nm")
                label.append(self.polarization.currentText())
                angles_rad = (
                    np.linspace(float(self.angles[0]), float(self.angles[1]), 100)
                    * np.pi
                    / 180
                )
                reflect_list = reflectance(
                    self.new_material_list,
                    float(self.wavelengths[0]) * 1e-9,
                    self.polarization.currentText(),
                    angles_rad,
                )
                self.canvas.axes.set_xlabel("Einfallswinkel (\u03c6)")
                self.canvas.axes.set_ylabel("Reflexion R")
                self.canvas.axes.plot(
                    angles_rad * 180 / np.pi, reflect_list, label=str(label)
                )
                self.canvas.axes.legend()
            else:
                wavelength_lists = np.array([float(self.wavelengths[0]) * 1e-9])
                angle_rad = float(self.angles[0]) * (np.pi / 180)
                reflect_list = reflectance(
                    self.new_material_list,
                    wavelength_lists,
                    self.polarization.currentText(),
                    angle_rad,
                )
                QMessageBox.information(
                    self, "Ergebnis", f"Reflexionsgrad R: {reflect_list[0]:.4f}"
                )
            self.canvas.draw()
        except (ValueError, ZeroDivisionError, ArithmeticError) as e:
            QMessageBox.warning(
                self, "Fehlermeldung", f"Ungültige Auswahl oder Berechnungsfehler: {e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Kritischer Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten: {e}",
            )

    def validate_inputs(self):
        self.new_material_list = []
        self.wavelengths = self.wavelength.text().split("-")
        self.angles = self.angle.text().split("-")
        for items in self.angles:
            if items.strip() == "":
                if len(self.angles) > 1:
                    raise ValueError("Leeres Winkel-Feld in Bereichsangabe.")
                continue
            try:
                angle_value = float(items)
            except ValueError:
                raise ValueError("Ungültiger Wert für Winkel.")
            if angle_value > 89 or angle_value < 0:
                raise ValueError("Winkel muss zwischen 0 und 89 liegen.")
        for items in self.wavelengths:
            if items.strip() == "":
                if len(self.wavelengths) > 1:
                    raise ValueError("Leeres Wellenlängen-Feld in Bereichsangabe.")
                continue
            try:
                wl_value = float(items)
            except ValueError:
                raise ValueError("Ungültiger Wert für Wellenlänge.")
            if wl_value <= 0:
                raise ValueError("Wellenlänge muss größer als 0 sein.")
        for i in range(0, self.grid.rowCount()):
            try:
                material_combobox = self.grid.cellWidget(i, 0)
                if not material_combobox or not isinstance(
                    material_combobox, QComboBox
                ):
                    raise AttributeError("Material-Combobox nicht gefunden.")
                m = copy.copy(material_combobox.currentData())
                if m is None:
                    raise ValueError("Kein Material in Zeile ausgewählt.")
                thickness_field = self.grid.cellWidget(i, 1)
                if not thickness_field or not isinstance(thickness_field, QLineEdit):
                    raise AttributeError("Dicken-Textfeld nicht gefunden.")
                thickness_text = thickness_field.text()
                if thickness_text.lower() in ("inf", "unendlich"):
                    m.d = np.inf
                else:
                    try:
                        m.d = float(thickness_text)
                    except ValueError:
                        raise ValueError("Ungültige Dicke.")
                if i != 0 and i != self.grid.rowCount() - 1:
                    if m.d <= 0 or m.d == np.inf:
                        raise ValueError(
                            "Dicke einer Schicht muss positiv und endlich sein."
                        )
                elif i == 0 or i == self.grid.rowCount() - 1:
                    if m.d != np.inf:
                        raise ValueError(
                            "Dicke des umgebenden Mediums oder Substrats muss unendlich sein."
                        )
                self.new_material_list.append(m)
            except (ValueError, AttributeError) as ve:
                raise ValueError(f"Fehler in Zeile {i + 1}: {ve}")
        if (
            len(self.wavelengths) > 2
            or len(self.angles) > 2
            or (len(self.wavelengths) == 2 and len(self.angles) == 2)
        ):
            raise ValueError("Bitte maximal einen Bereich (x-y) angeben.")
        if len(self.wavelengths) > 1:
            if len(self.wavelengths) != 2:
                raise ValueError(
                    "Wellenlängenbereich muss 1.Wellenlänge-2.Wellenlänge sein."
                )
            if float(self.wavelengths[0]) >= float(self.wavelengths[1]):
                raise ValueError("Erste Wellenlänge muss kleiner als zweite sein.")
        elif len(self.angles) > 1:
            if len(self.angles) != 2:
                raise ValueError("Winkelbereich muss 1.Winkel-2.Winkel sein.")
            if float(self.angles[0]) >= float(self.angles[1]):
                raise ValueError("Erster Winkel muss kleiner als zweiter sein.")
        else:
            if len(self.wavelengths) != 1 and len(self.angles) != 1:
                raise ValueError(
                    "Geben Sie entweder einen Wellenlängenbereich oder einen Winkelbereich an, oder nur eine Wellenlänge und einen Winkel."
                )

    def delete_Row(self, combobox: QComboBox):
        try:
            for i in range(0, self.grid.rowCount()):
                temp = self.grid.cellWidget(i, 0)
                if temp == combobox:
                    if i == 0 or i == self.grid.rowCount() - 1:
                        QMessageBox.warning(
                            self,
                            "Fehlermeldung",
                            "Das umgebende Medium und das Substrat können nicht gelöscht werden.",
                        )
                        return
                    self.canvas.setFocus()
                    self.grid.removeRow(i)
                    break
        except Exception as e:
            QMessageBox.critical(
                self, "Kritischer Fehler", f"Fehler beim Löschen der Zeile: {e}"
            )

    def insert_Row(self, combobox: QComboBox = None, counter: int = None):  # type: ignore
        try:
            index = self.grid.rowCount() - 1
            if combobox is not None:
                for i in range(0, self.grid.rowCount()):
                    temp = self.grid.cellWidget(i, 0)
                    if temp == combobox:
                        if i == self.grid.rowCount() - 1:
                            QMessageBox.warning(
                                self,
                                "Fehlermeldung",
                                "Eine neue Schicht kann nicht nach dem Substrat eingefügt werden.",
                            )
                            return
                        index = i + 1
                        break
            if counter is not None:
                index = counter

            self.grid.insertRow(index)
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
            self.grid.setCellWidget(index, 0, combobox0)
            self.grid.setCellWidget(index, 1, textfield_d)
            if index == 0:
                self.grid.setCellWidget(index, 2, add_button)
                textfield_d.setText("inf")
                textfield_d.setEnabled(False)
            elif index == self.grid.rowCount() - 1:
                self.grid.setCellWidget(index, 2, QLineEdit(""))
                self.grid.cellWidget(index, 2).setEnabled(False)  # type: ignore
                textfield_d.setText("inf")
                textfield_d.setEnabled(False)
            else:
                self.grid.setCellWidget(index, 2, button_widget)
                textfield_d.setText("100")
        except Exception as e:
            QMessageBox.critical(
                self, "Kritischer Fehler", f"Fehler beim Einfügen der Zeile: {e}"
            )

    def set_values(
        self,
        combobox: QComboBox,
        textfield_d: QLineEdit,
    ):
        try:
            current_data = combobox.currentData()
            if current_data is not None:
                if textfield_d.isEnabled():
                    textfield_d.setText(str(current_data.d))
        except Exception as e:
            QMessageBox.critical(
                self, "Kritischer Fehler", f"Fehler beim Setzen der Werte: {e}"
            )

    def reset(self):
        try:
            self.canvas.axes.clear()
            self.canvas.axes.set_title("Reflexionsspektrum")
            self.canvas.axes.set_xlabel("Wellenlänge [nm]")
            self.canvas.axes.set_ylabel("Reflexionsgrad R")
            self.canvas.axes.grid(True)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Kritischer Fehler",
                f"Fehler beim Zurücksetzen des Diagramms: {e}",
            )

    def create_material(self):
        dialog = MaterialDialog(self)
        dialog.exec()
        self.refresh_grid_combos()

    def refresh_grid_combos(self):
        for i in range(self.grid.rowCount()):
            combobox = self.grid.cellWidget(i, 0)
            if isinstance(combobox, QComboBox):
                current_idx = combobox.currentIndex()
                combobox.blockSignals(True)
                combobox.clear()
                for material in material_list:
                    combobox.addItem(material.name, material)
                combobox.setCurrentIndex(current_idx)
                combobox.blockSignals(False)


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.figure = Figure(layout="constrained")
        try:
            super().__init__(self.figure)
        except Exception as e:
            raise Exception(f"Fehler beim Initialisieren von PlotCanvas: {e}")


class MaterialDialog(QDialog):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        try:
            self.setWindowIcon(QIcon("./python.png"))
            self.setWindowTitle("Neues Material")
            self.setup_UI()
        except BaseException:
            pass  # ignoriert Fehler beim Icon, da es nicht kritisch ist

    def check_index(self):
        try:
            n = None
            if self.namef.text().isspace() or self.namef.text() == "":
                raise NameError("Ihr Material benötigt einen Namen.")
            if self.calc_type.currentData() is None:
                raise TypeError("Wählen Sie einen Berechnungstyp.")
            if self.calc_type.currentData() == 0:
                try:
                    if self.real.text() == "":
                        raise ValueError("Reeller Teil des Brechungsindex ist leer.")
                    real_temp = eval(self.real.text())
                    imaginary_temp = (
                        eval(self.imaginary.text())
                        if self.imaginary.text() != ""
                        else 0
                    )
                    if real_temp <= 0 or imaginary_temp < 0:
                        raise ValueError(
                            "Brechungsindex muss reell > 0 und imaginär >= 0 sein."
                        )
                    n = complex(real_temp, imaginary_temp)
                except NameError:
                    raise SyntaxError("Ungültige Formel im Brechungsindex-Feld.")
                except (ValueError, TypeError):
                    raise ValueError("Ungültiger Wert für Brechungsindex.")
                material_list.append(
                    Material(
                        name=self.namef.text(),
                        n_type=self.calc_type.currentData(),
                        d=100,
                        n=n,
                    )
                )
            elif self.calc_type.currentData() == 1:
                if self.coefficientB.text() == "" or self.coefficientC.text() == "":
                    raise ValueError(
                        "Sellmeier-Koeffizienten B und C dürfen nicht leer sein."
                    )
                try:
                    A_val = (
                        float(self.coefficientA.text())
                        if self.coefficientA.text() != ""
                        else 0.0
                    )
                except ValueError:
                    raise ValueError("Ungültiger Wert für Sellmeier A.")
                try:
                    bliststr = self.coefficientB.text().split(",")
                    blistfloat = [eval(i.strip()) for i in bliststr if i.strip()]
                    cliststr = self.coefficientC.text().split(",")
                    clistfloat = [eval(i.strip()) for i in cliststr if i.strip()]
                except NameError:
                    raise SyntaxError("Ungültige Formel in Sellmeier-Koeffizienten.")
                except (ValueError, TypeError):
                    raise ValueError("Ungültige Werte in Sellmeier-Koeffizienten.")
                if len(blistfloat) != len(clistfloat) or not blistfloat:
                    raise ValueError(
                        "Die Anzahl der B- und C-Koeffizienten muss übereinstimmen und darf nicht leer sein."
                    )
                if any(c <= 0 for c in clistfloat):
                    raise ValueError("Alle C-Koeffizienten müssen positiv sein.")
                material_list.append(
                    Material(
                        name=self.namef.text(),
                        n_type=self.calc_type.currentData(),
                        d=100,
                        A=A_val,
                        B=blistfloat,
                        C=clistfloat,
                    )
                )
            elif self.calc_type.currentData() == 3:
                table_data = self.parse_table_data(self.table.toPlainText())
                if table_data is None:
                    return
                material_list.append(
                    Material(
                        name=self.namef.text(),
                        n_type=self.calc_type.currentData(),
                        d=100,
                        table=table_data,
                    )
                )
            elif self.calc_type.currentData() == 2:
                if self.formula.text().strip() == "":
                    raise ValueError("Formel darf nicht leer sein.")
                if "x" not in self.formula.text():
                    raise ValueError(
                        "Die Formel muss 'x' für die Wellenlänge enthalten."
                    )
                material_list.append(
                    Material(
                        name=self.namef.text(),
                        n_type=self.calc_type.currentData(),
                        d=100,
                        formula=self.formula.text(),
                    )
                )
            jsonlist = [i.toJson() for i in material_list]
            try:
                with open("Material.json", "w") as file:
                    json.dump(jsonlist, file, indent=4)
                self.accept()
            except IOError as ioe:
                raise IOError(f"Fehler beim Speichern der Materialdatei: {ioe}")
        except SyntaxError as se:
            QMessageBox.warning(self, "Fehlermeldung", f"Ungültige Formel/Syntax: {se}")
        except ValueError as ve:
            QMessageBox.warning(self, "Fehlermeldung", f"Ungültige Angabe: {ve}")
        except TypeError as te:
            QMessageBox.warning(self, "Fehlermeldung", str(te))
        except NameError as ne:
            QMessageBox.warning(self, "Fehlermeldung", str(ne))
        except IOError as ioe:
            QMessageBox.critical(self, "Kritischer Fehler", str(ioe))
        except Exception as e:
            QMessageBox.critical(
                self,
                "Kritischer Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten: {e}",
            )

    def parse_table_data(self, text):
        wls, ns, ks = [], [], []
        lines = text.strip().split("\n")
        try:
            for line in lines:
                line = line.strip()
                if not line or line[0].isalpha() or line.startswith("#"):
                    continue
                parts = line.replace(",", ".").replace(";", " ").split()
                if len(parts) >= 2:
                    try:
                        wls.append(float(parts[0]))
                        ns.append(float(parts[1]))
                        ks.append(float(parts[2]) if len(parts) > 2 else 0.0)
                    except ValueError:
                        raise ValueError(f"Ungültiger Wert in Zeile: {line}")
                else:
                    raise ValueError(
                        f"Mindestens zwei Werte pro Zeile erwartet: {line}"
                    )
            if not wls:
                raise ValueError("Keine gültigen Daten in der Tabelle gefunden.")
        except ValueError as ve:
            QMessageBox.warning(
                self, "Fehlermeldung", f"Fehler beim Parsen der Tabelle: {ve}"
            )
            return None
        except Exception as e:
            QMessageBox.critical(
                self,
                "Kritischer Fehler",
                f"Ein unerwarteter Fehler ist beim Parsen der Tabelle aufgetreten: {e}",
            )
            return None
        return {"wavelengths": wls, "n_values": ns, "k_values": ks}

    def switch_buttons(self):
        try:
            if self.calc_type.currentData() == 1:
                self.coefficientA.setEnabled(True)
                self.coefficientB.setEnabled(True)
                self.coefficientC.setEnabled(True)
                self.real.setEnabled(False)
                self.imaginary.setEnabled(False)
                self.formula.setEnabled(False)
                self.table.setEnabled(False)
            elif self.calc_type.currentData() == 0:
                self.coefficientA.setEnabled(False)
                self.coefficientB.setEnabled(False)
                self.coefficientC.setEnabled(False)
                self.real.setEnabled(True)
                self.imaginary.setEnabled(True)
                self.formula.setEnabled(False)
                self.table.setEnabled(False)
            elif self.calc_type.currentData() == 2:
                self.coefficientA.setEnabled(False)
                self.coefficientB.setEnabled(False)
                self.coefficientC.setEnabled(False)
                self.real.setEnabled(False)
                self.imaginary.setEnabled(False)
                self.formula.setEnabled(True)
                self.table.setEnabled(False)
            elif self.calc_type.currentData() == 3:
                self.coefficientA.setEnabled(False)
                self.coefficientB.setEnabled(False)
                self.coefficientC.setEnabled(False)
                self.real.setEnabled(False)
                self.imaginary.setEnabled(False)
                self.formula.setEnabled(False)
                self.table.setEnabled(True)
            else:
                self.coefficientA.setEnabled(False)
                self.coefficientB.setEnabled(False)
                self.coefficientC.setEnabled(False)
                self.real.setEnabled(False)
                self.imaginary.setEnabled(False)
                self.formula.setEnabled(False)
                self.table.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Kritischer Fehler",
                f"Fehler beim Umschalten der Buttons: {e}",
            )

    def setup_UI(self):
        self.name = QLabel("Name: ")
        self.namef = QLineEdit()
        self.namef.setPlaceholderText("Material")

        layouth = QHBoxLayout()
        layoutv = QVBoxLayout()
        layouth.addWidget(self.name)
        layouth.addWidget(self.namef)
        layoutv.addLayout(layouth)

        self.calc_label = QLabel("Berechnungs-Typ: ")
        self.calc_type = QComboBox()
        self.calc_type.setPlaceholderText("Typ")
        self.calc_type.addItem("Sellmeier", userData=1)
        self.calc_type.addItem("Fester Brechungsindex", userData=0)
        self.calc_type.addItem("Formel", userData=2)
        self.calc_type.addItem("Interpolation", userData=3)

        layouth = QHBoxLayout()
        layouth.addWidget(self.calc_label)
        layouth.addWidget(self.calc_type)
        layoutv.addLayout(layouth)

        index = QLabel("Brechungsindex: ")
        self.real = QLineEdit()
        self.real.setPlaceholderText("Reell")
        self.real.setEnabled(False)
        self.imaginary = QLineEdit()
        self.imaginary.setPlaceholderText("Imaginär")
        self.imaginary.setEnabled(False)
        layouth = QHBoxLayout()
        layouth.addWidget(index)
        layouth.addWidget(self.real)
        layouth.addWidget(self.imaginary)
        layoutv.addLayout(layouth)

        self.coefficient_label = QLabel("Sellmeier-Koeffizienten")
        self.coefficientA = QLineEdit()
        self.coefficientA.setEnabled(False)
        self.coefficientA.setPlaceholderText("A=0")
        self.coefficientB = QLineEdit()
        self.coefficientB.setEnabled(False)
        self.coefficientB.setPlaceholderText("B1, B2, ...")
        self.coefficientC = QLineEdit()
        self.coefficientC.setEnabled(False)
        self.coefficientC.setPlaceholderText("C1, C2, ...")
        layouth = QHBoxLayout()
        layouth.addWidget(self.coefficient_label)
        layouth.addWidget(self.coefficientA)
        layouth.addWidget(self.coefficientB)
        layouth.addWidget(self.coefficientC)
        layoutv.addLayout(layouth)

        self.formula_label = QLabel("Formel:")
        self.formula = QLineEdit()
        self.formula.setPlaceholderText("Für Wellenlänge: x")
        self.formula.setEnabled(False)
        layouth = QHBoxLayout()
        layouth.addWidget(self.formula_label)
        layouth.addWidget(self.formula)
        layoutv.addLayout(layouth)

        self.table_label = QLabel("Tabelle")
        self.table = QPlainTextEdit()
        self.table.setEnabled(False)
        layouth = QHBoxLayout()
        layouth.addWidget(self.table_label)
        layouth.addWidget(self.table)
        layoutv.addLayout(layouth)

        self.confirm = QPushButton("Bestätigen")
        layoutv.addWidget(self.confirm)
        self.setLayout(layoutv)

        self.calc_type.activated.connect(self.switch_buttons)
        self.confirm.clicked.connect(self.check_index)


try:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
except Exception as e:
    QMessageBox.critical(
        None,
        "Kritischer Anwendungsfehler",
        f"Die Anwendung konnte nicht gestartet werden: {e}",
    )
    sys.exit(1)
