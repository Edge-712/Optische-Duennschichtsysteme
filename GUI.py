import sys
import json
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
            self.grid = QTableWidget()
            self.grid.setColumnCount(3)
            self.grid.setHorizontalHeaderLabels(["Material", "Dicke in nm", ""])
            self.grid.horizontalHeader().setSectionResizeMode(  # type: ignore
                QHeaderView.ResizeMode.Stretch
            )
            self.insert_Row(None, 0)  # type: ignore
            self.insert_Row(None, 1)  # type: ignore
            new_material = QPushButton("Neues Material anlegen")
            new_material.clicked.connect(self.create_material)
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
            self.canvas = PlotCanvas()
            self.canvas.axes = self.canvas.figure.add_subplot()
            self.canvas.axes.set_title("Reflexionsspektrum")
            self.canvas.axes.set_xlabel("Wellenlänge [nm]")
            self.canvas.axes.set_ylabel("Reflexionsgrad R")
            self.canvas.axes.grid(True)
            toolbar = NavigationToolbar(self.canvas, self)
            reset_button = QPushButton("Zurücksetzen")
            reset_button.clicked.connect(self.reset)
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
            layout_h.addStretch(1)
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
        except Exception as e:
            QMessageBox.critical(
                self,
                "Kritischer Fehler",
                f"Fehler beim Erstellen der Standardseite: {e}",
            )
            raise

    def create_Graph(
        self,
        wavelength0: QLineEdit,
        polarization: QComboBox,
        angle: QLineEdit,
    ):
        try:
            wavelengths = wavelength0.text().split("-")
            angles = angle.text().split("-")
            for items in angles:
                if items.strip() == "":
                    if len(angles) > 1:
                        raise ValueError("Leeres Winkel-Feld in Bereichsangabe.")
                    continue
                try:
                    angle_value = float(items)
                except ValueError:
                    raise ValueError("Ungültiger Wert für Winkel.")
                if angle_value > 89 or angle_value < 0:
                    raise ValueError("Winkel muss zwischen 0 und 89 liegen.")
            for items in wavelengths:
                if items.strip() == "":
                    if len(wavelengths) > 1:
                        raise ValueError("Leeres Wellenlängen-Feld in Bereichsangabe.")
                    continue
                try:
                    wl_value = float(items)
                except ValueError:
                    raise ValueError("Ungültiger Wert für Wellenlänge.")
                if wl_value <= 0:
                    raise ValueError("Wellenlänge muss größer als 0 sein.")
            new_material_list = []
            if self.grid.rowCount() < 2:
                raise ValueError(
                    "Mindestens zwei Materialien (Medium und Substrat) sind erforderlich."
                )
            for i in range(0, self.grid.rowCount()):
                try:
                    material_combobox = self.grid.cellWidget(i, 0)
                    if not material_combobox or not isinstance(
                        material_combobox, QComboBox
                    ):
                        raise AttributeError("Material-Combobox nicht gefunden.")
                    m = material_combobox.currentData()
                    if m is None:
                        raise ValueError("Kein Material in Zeile ausgewählt.")
                    thickness_field = self.grid.cellWidget(i, 1)
                    if not thickness_field or not isinstance(
                        thickness_field, QLineEdit
                    ):
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
                    new_material_list.append(m)
                except (ValueError, AttributeError) as ve:
                    raise ValueError(f"Fehler in Zeile {i + 1}: {ve}")
            if len(wavelengths) > 1:
                if len(wavelengths) != 2:
                    raise ValueError(
                        "Wellenlängenbereich muss 1.Wellenlänge-2.Wellenlänge sein."
                    )
                if float(wavelengths[0]) >= float(wavelengths[1]):
                    raise ValueError("Erste Wellenlänge muss kleiner als zweite sein.")
                wavelength_lists = np.linspace(
                    float(wavelengths[0]) * 1e-9,
                    float(wavelengths[1]) * 1e-9,
                    400,
                )
                label = [i.name for i in new_material_list]
                label.append(angle.text() + "\u00b0")
                label.append(polarization.currentText())
                reflect_list = reflectance(
                    new_material_list,
                    wavelength_lists,
                    polarization.currentText(),
                    float(angles[0]) * (np.pi / 180),
                )
                self.canvas.axes.set_xlabel("Wellenlänge [nm]")
                self.canvas.axes.set_ylabel("Reflexionsgrad R")
                self.canvas.axes.plot(
                    wavelength_lists * 1e9, reflect_list, label=str(label)
                )
                self.canvas.axes.legend()
            elif len(angles) > 1:
                if len(angles) != 2:
                    raise ValueError("Winkelbereich muss 1.Winkel-2.Winkel sein.")
                if float(angles[0]) >= float(angles[1]):
                    raise ValueError("Erster Winkel muss kleiner als zweiter sein.")
                label = [i.name for i in new_material_list]
                label.append(wavelengths[0] + "nm")
                label.append(polarization.currentText())
                angles_rad = (
                    np.linspace(float(angles[0]), float(angles[1]), 100) * np.pi / 180
                )
                reflect_list = reflectance(
                    new_material_list,
                    float(wavelengths[0]) * 1e-9,
                    polarization.currentText(),
                    angles_rad,
                )
                self.canvas.axes.set_xlabel("Einfallswinkel (\u03c6)")
                self.canvas.axes.set_ylabel("Reflexion R")
                self.canvas.axes.plot(
                    angles_rad * 180 / np.pi, reflect_list, label=str(label)
                )
                self.canvas.axes.legend()
            else:
                if len(wavelengths) != 1 or len(angles) != 1:
                    raise ValueError(
                        "Geben Sie entweder einen Wellenlängenbereich oder einen Winkelbereich an, oder nur eine Wellenlänge und einen Winkel."
                    )
                wavelength_lists = np.array([float(wavelengths[0]) * 1e-9])
                angle_rad = float(angles[0]) * (np.pi / 180)
                reflect_list = reflectance(
                    new_material_list,
                    wavelength_lists,
                    polarization.currentText(),
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
                self.grid.cellWidget(index, 2).setEnabled(False)
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
        dialog = QDialog()
        layoutv = QVBoxLayout()
        dialog.setWindowTitle("Neues Material")
        try:
            dialog.setWindowIcon(QIcon("./python.png"))
        except:
            pass  # Ignorier Fehler beim Icon, da es nicht kritisch ist
        name = QLabel("Name: ")
        namef = QLineEdit()
        namef.setPlaceholderText("Material")
        layouth = QHBoxLayout()
        layouth.addWidget(name)
        layouth.addWidget(namef)
        layoutv.addLayout(layouth)
        calc_label = QLabel("Berechnungs-Typ: ")
        calc_type = QComboBox()
        calc_type.setPlaceholderText("Typ")
        calc_type.addItem("Sellmeier", userData=1)
        calc_type.addItem("Fester Brechungsindex", userData=0)
        calc_type.addItem("Formel", userData=2)
        calc_type.addItem("Interpolation", userData=3)
        layouth = QHBoxLayout()
        layouth.addWidget(calc_label)
        layouth.addWidget(calc_type)
        layoutv.addLayout(layouth)
        index = QLabel("Brechungsindex: ")
        real = QLineEdit()
        real.setPlaceholderText("Reell")
        real.setEnabled(False)
        imaginary = QLineEdit()
        imaginary.setPlaceholderText("Imaginär")
        imaginary.setEnabled(False)
        layouth = QHBoxLayout()
        layouth.addWidget(index)
        layouth.addWidget(real)
        layouth.addWidget(imaginary)
        layoutv.addLayout(layouth)
        coefficient_label = QLabel("Sellmeier-Koeffizienten")
        coefficientA = QLineEdit()
        coefficientA.setEnabled(False)
        coefficientA.setPlaceholderText("A=0")
        coefficientB = QLineEdit()
        coefficientB.setEnabled(False)
        coefficientB.setPlaceholderText("B1, B2, ...")
        coefficientC = QLineEdit()
        coefficientC.setEnabled(False)
        coefficientC.setPlaceholderText("C1, C2, ...")
        layouth = QHBoxLayout()
        layouth.addWidget(coefficient_label)
        layouth.addWidget(coefficientA)
        layouth.addWidget(coefficientB)
        layouth.addWidget(coefficientC)
        layoutv.addLayout(layouth)
        formula_label = QLabel("Formel:")
        formula = QLineEdit()
        formula.setPlaceholderText("Für Wellenlänge: x")
        formula.setEnabled(False)
        layouth = QHBoxLayout()
        layouth.addWidget(formula_label)
        layouth.addWidget(formula)
        layoutv.addLayout(layouth)
        table_label = QLabel("Tabelle")
        table = QPlainTextEdit()
        table.setEnabled(False)
        layouth = QHBoxLayout()
        layouth.addWidget(table_label)
        layouth.addWidget(table)
        layoutv.addLayout(layouth)
        confirm = QPushButton("Bestätigen")
        layoutv.addWidget(confirm)
        dialog.setLayout(layoutv)

        def switch_buttons():
            try:
                if calc_type.currentData() == 1:
                    coefficientA.setEnabled(True)
                    coefficientB.setEnabled(True)
                    coefficientC.setEnabled(True)
                    real.setEnabled(False)
                    imaginary.setEnabled(False)
                    formula.setEnabled(False)
                    table.setEnabled(False)
                elif calc_type.currentData() == 0:
                    coefficientA.setEnabled(False)
                    coefficientB.setEnabled(False)
                    coefficientC.setEnabled(False)
                    real.setEnabled(True)
                    imaginary.setEnabled(True)
                    formula.setEnabled(False)
                    table.setEnabled(False)
                elif calc_type.currentData() == 2:
                    coefficientA.setEnabled(False)
                    coefficientB.setEnabled(False)
                    coefficientC.setEnabled(False)
                    real.setEnabled(False)
                    imaginary.setEnabled(False)
                    formula.setEnabled(True)
                    table.setEnabled(False)
                elif calc_type.currentData() == 3:
                    coefficientA.setEnabled(False)
                    coefficientB.setEnabled(False)
                    coefficientC.setEnabled(False)
                    real.setEnabled(False)
                    imaginary.setEnabled(False)
                    formula.setEnabled(False)
                    table.setEnabled(True)
                else:
                    coefficientA.setEnabled(False)
                    coefficientB.setEnabled(False)
                    coefficientC.setEnabled(False)
                    real.setEnabled(False)
                    imaginary.setEnabled(False)
                    formula.setEnabled(False)
                    table.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(
                    dialog,
                    "Kritischer Fehler",
                    f"Fehler beim Umschalten der Buttons: {e}",
                )

        def parse_table_data(text):
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
                            raise ValueError(
                                f"Ungültiger numerischer Wert in Zeile: {line}"
                            )
                    else:
                        raise ValueError(
                            f"Mindestens zwei Werte pro Zeile erwartet: {line}"
                        )
                if not wls:
                    raise ValueError("Keine gültigen Daten in der Tabelle gefunden.")
            except ValueError as ve:
                QMessageBox.warning(
                    dialog, "Fehlermeldung", f"Fehler beim Parsen der Tabelle: {ve}"
                )
                return None
            except Exception as e:
                QMessageBox.critical(
                    dialog,
                    "Kritischer Fehler",
                    f"Ein unerwarteter Fehler ist beim Parsen der Tabelle aufgetreten: {e}",
                )
                return None
            return {"wavelengths": wls, "n_values": ns, "k_values": ks}

        def check_index():
            try:
                n = None
                if namef.text().isspace() or namef.text() == "":
                    raise NameError("Ihr Material benötigt einen Namen.")
                if calc_type.currentData() is None:
                    raise TypeError("Wählen Sie einen Berechnungstyp.")
                if calc_type.currentData() == 0:
                    try:
                        if real.text() == "":
                            raise ValueError(
                                "Reeller Teil des Brechungsindex ist leer."
                            )
                        real_temp = eval(real.text())
                        imaginary_temp = (
                            eval(imaginary.text()) if imaginary.text() != "" else 0
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
                            name=namef.text(),
                            n_type=calc_type.currentData(),
                            d=100,
                            n=n,
                        )
                    )
                elif calc_type.currentData() == 1:
                    if coefficientB.text() == "" or coefficientC.text() == "":
                        raise ValueError(
                            "Sellmeier-Koeffizienten B und C dürfen nicht leer sein."
                        )
                    try:
                        A_val = (
                            float(coefficientA.text())
                            if coefficientA.text() != ""
                            else 0.0
                        )
                    except ValueError:
                        raise ValueError("Ungültiger Wert für Sellmeier A.")
                    try:
                        bliststr = coefficientB.text().split(",")
                        blistfloat = [eval(i.strip()) for i in bliststr if i.strip()]
                        cliststr = coefficientC.text().split(",")
                        clistfloat = [eval(i.strip()) for i in cliststr if i.strip()]
                    except NameError:
                        raise SyntaxError(
                            "Ungültige Formel in Sellmeier-Koeffizienten."
                        )
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
                            name=namef.text(),
                            n_type=calc_type.currentData(),
                            d=100,
                            A=A_val,
                            B=blistfloat,
                            C=clistfloat,
                        )
                    )
                elif calc_type.currentData() == 3:
                    table_data = parse_table_data(table.toPlainText())
                    if table_data is None:
                        return
                    material_list.append(
                        Material(
                            name=namef.text(),
                            n_type=calc_type.currentData(),
                            d=100,
                            table=table_data,
                        )
                    )
                elif calc_type.currentData() == 2:
                    if formula.text().strip() == "":
                        raise ValueError("Formel darf nicht leer sein.")
                    if "x" not in formula.text():
                        raise ValueError(
                            "Die Formel muss 'x' für die Wellenlänge enthalten."
                        )
                    material_list.append(
                        Material(
                            name=namef.text(),
                            n_type=calc_type.currentData(),
                            d=100,
                            formula=formula.text(),
                        )
                    )
                jsonlist = [i.toJson() for i in material_list]
                try:
                    with open("Material.json", "w") as file:
                        json.dump(jsonlist, file, indent=4)
                    dialog.accept()
                except IOError as ioe:
                    raise IOError(f"Fehler beim Speichern der Materialdatei: {ioe}")
            except SyntaxError as se:
                QMessageBox.warning(
                    dialog, "Fehlermeldung", f"Ungültige Formel/Syntax: {se}"
                )
            except ValueError as ve:
                QMessageBox.warning(dialog, "Fehlermeldung", f"Ungültige Angabe: {ve}")
            except TypeError as te:
                QMessageBox.warning(dialog, "Fehlermeldung", str(te))
            except NameError as ne:
                QMessageBox.warning(dialog, "Fehlermeldung", str(ne))
            except IOError as ioe:
                QMessageBox.critical(dialog, "Kritischer Fehler", str(ioe))
            except Exception as e:
                QMessageBox.critical(
                    dialog,
                    "Kritischer Fehler",
                    f"Ein unerwarteter Fehler ist aufgetreten: {e}",
                )

        calc_type.activated.connect(switch_buttons)
        confirm.clicked.connect(check_index)
        dialog.exec()


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.figure = Figure(layout="constrained")
        try:
            super().__init__(self.figure)
        except Exception as e:
            raise Exception(f"Fehler beim Initialisieren von PlotCanvas: {e}")


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
