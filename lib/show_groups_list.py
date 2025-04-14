import logging

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (QPushButton, QLabel, QGraphicsDropShadowEffect,
                             QVBoxLayout, QWidget, QGridLayout, QScrollArea, QDialog)

from lib.create_group import NewGroupDialog
from lib.dbase import CustomersGroup, Session
from lib.show_customers_list import CustomerListWindow


class GroupListWidget(QWidget):
    group_selected = pyqtSignal(object)  # Sukuriame signalą, kuris perduos grupę
    group_created = pyqtSignal()  # Signalas grupės sukūrimui
    customer_created = pyqtSignal()  # Klientų sąrašo atnaujinimo signalas

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_customer_list_window = None
        self.group_layout = QGridLayout()
        self.group_layout.setContentsMargins(20, 20, 20, 20)  # Nustatome paraštes: kairė, viršus, dešinė, apačia
        self.group_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(self.group_layout)
        self.setStyleSheet("background-color: #eee;")  # Nustatome fono spalvą
        self.previous_width = self.width()
        self.group_buttons = []
        self.new_group_button = None
        self.right_scroll = QScrollArea()
        self.load_groups()

        # Prijungti signalą, kad atnaujintų grupes, kai sukuriamas naujas klientas
        self.customer_created.connect(self.load_groups)

        # Prijungti signalą, kad atnaujintų grupes, kai sukuriama nauja grupė
        self.group_created.connect(
            self.load_groups)

    def _calculate_layout_params(self):
        """Apskaičiuoja išdėstymo parametrus su minimaliu tarpu tarp elementų."""
        item_width = 170
        item_height = 130
        spacing = 20  # Tiesiogiai nustatome tarpo reikšmę

        available_width = self.width() - spacing  # Sumažiname available_width
        items_per_row = max(1, available_width // (item_width + spacing))

        return items_per_row, item_width, item_height, spacing

    def resizeEvent(self, event):
        """Keičiantis lango dydžiui, atnaujiname grupių išdėstymą."""
        if abs(self.width() - self.previous_width) > 30:
            self.previous_width = self.width()
            QtCore.QTimer.singleShot(100, self.load_groups)  # Vėluojame 100ms, kad išvengtume per dažnų atnaujinimų
        super().resizeEvent(event)

    def clear_layout(self):
        """Pašalina visus widget'us iš QGridLayout, kad būtų galima iš naujo juos išdėstyti."""
        while self.group_layout.count():
            item = self.group_layout.takeAt(0)
            widget = item.widget()
            if widget and widget != self.new_group_button:
                widget.setParent(None)  # type: ignore
                widget.deleteLater()

    def load_groups(self):
        """Užkrauna ir atvaizduoja grupių sąrašą."""
        self.clear_layout()
        self.group_buttons.clear()

        items_per_row, item_width, item_height, spacing = self._calculate_layout_params()

        session = Session()  # <- Nauja sesija
        groups = session.query(CustomersGroup).all()
        for group in groups:
            self.group_buttons.append(
                self.create_group_button(group, item_width, item_height))

        if not self.new_group_button:
            self.new_group_button = self.create_new_group_button()

        self.update_group_layout(items_per_row, spacing)
        session.close()  # Nepamiršk uždaryti

    def update_group_layout(self, items_per_row, spacing):
        """Atnaujina mygtukų išdėstymą pagal naują lango dydį."""
        self.clear_layout()

        for current_item, button in enumerate(self.group_buttons):
            row, col = divmod(current_item, items_per_row)
            self.group_layout.addWidget(button, row, col)

        row, col = divmod(len(self.group_buttons), items_per_row)
        self.group_layout.addWidget(self.new_group_button, row, col)

        # Pridedame tarpus tarp eilučių
        for row in range(self.group_layout.rowCount() - 1):
            self.group_layout.setRowMinimumHeight(row, 130 + spacing)

    def create_group_button(self, group, item_width, item_height):
        """Sukuria mygtuką su grupės informacija."""
        group_button = QPushButton()
        group_button.setFixedSize(item_width, item_height)
        group_button.setStyleSheet(self.get_button_style(group.customers_group_balance))
        group_button.setGraphicsEffect(self.create_shadow(15, QColor(0, 0, 0, 100), -2, -1))

        # Pridėkite signalą, kuris atidarys grupės klientų sąrašą
        group_button.clicked.connect(lambda: self.group_selected.emit(group))

        layout = self.create_group_layout(group)
        group_button.setLayout(layout)

        return group_button

    def create_group_layout(self, group):
        layout = QVBoxLayout()
        name = QLabel(
            f'<b>{group.customers_group_name}</b> <span style="color: #555555; font-size: 10pt;"><sup>id: {group.id}</span>')
        name.setFont(QFont("Arial", 12, QFont.Bold))
        name.setStyleSheet("color: #007bfc; background-color: transparent;")
        name.setAlignment(Qt.AlignCenter)
        name.setGraphicsEffect(self.create_shadow(10, QColor(255, 255, 255, 255)))

        layout.addWidget(name)
        customers_count = QLabel(f"Klientų kiekis: {len(group.customers)}")
        customers_count.setStyleSheet("background-color: transparent;")
        layout.addWidget(customers_count)

        meter_id = QLabel(f"Skaitiklio ID: {group.customers_group_kwh_meter_id}")
        meter_id.setStyleSheet("background-color: transparent;")
        layout.addWidget(meter_id)

        meter_type = QLabel(f"Skaitiklio tipas: {group.customers_group_meter_type}")
        meter_type.setStyleSheet("background-color: transparent;")
        layout.addWidget(meter_type)

        balance = QLabel(f"Grupės sąskaitos likutis: {group.customers_group_balance:.2f}")
        balance.setStyleSheet("background-color: transparent;")
        layout.addWidget(balance)

        return layout

    def eventFilter(self, obj, event):
        """Keičia „Nauja grupė“ mygtuko tekstą pelės įvedimo/išvedimo metu."""
        if isinstance(obj, QPushButton) and obj == self.new_group_button:
            label = obj.findChild(QLabel)  # Surandame QLabel mygtuko viduje
            if not label:
                return super().eventFilter(obj, event)

            if event.type() == QEvent.Enter:
                label.setText("+")
                label.setFont(QFont("Arial", 72, QFont.Bold))
                label.setStyleSheet("color: white; background-color: transparent;")  # Nustatome permatomą foną
            elif event.type() == QEvent.Leave:
                label.setText("Nauja Grupė")
                label.setFont(QFont("Arial", 16, QFont.Bold))
                label.setStyleSheet("color: white; background-color: transparent;")  # Nustatome permatomą foną

        return super().eventFilter(obj, event)

    def create_new_group_button(self):
        """Sukuria 'Nauja Grupė' mygtuką su centruotu tekstu ir šešėliu."""
        new_group_button = QPushButton()
        new_group_button.setFixedSize(170, 130)
        new_group_button.setGraphicsEffect(self.create_shadow(15, QColor(0, 0, 0, 100), -2, -1))
        new_group_button.setStyleSheet("""
                    QPushButton {
                        background-color: #f5f5f5;
                        border-radius: 10px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #fafafa;
                    }
                """)
        new_group_button.clicked.connect(self.open_new_group_dialog)

        # Sukuriame centrinį išdėstymą mygtuko viduje
        layout = QVBoxLayout(new_group_button)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sukuriame QLabel, kuris bus viduje
        label = QLabel("Nauja Grupė")
        label.setFont(QFont("Arial", 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; background-color: transparent;")

        # Sukuriame šešėlį tekstui
        label.setGraphicsEffect(self.create_shadow(6, QColor(0, 0, 0, 150), 2, 2))

        layout.addWidget(label)

        # Pridedame įvykio filtrą animacijoms (+ simboliui)
        new_group_button.installEventFilter(self)

        return new_group_button

    def create_shadow(self, blur_radius, color, x_offset=0, y_offset=0):
        """Sukuria šešėlio efektą."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(color)
        shadow.setOffset(x_offset, y_offset)
        return shadow

    @staticmethod
    # def get_button_style(bg_color="#f5f5f5"):  # be @staticmethod, reikia "def get_button_style(self, bg_color="#f5f5f5"):"
    def get_button_style(balance):  # be @staticmethod, reikia def get_button_style(self, bg_color="#f5f5f5"):
        """Grąžina bendrą mygtuko stilių."""

        if 0 > balance > (-4):
            return f"""
                        QPushButton {{
                            background-color: #faf5f5;
                            border: 0px solid #faf5f5;
                            border-radius: 10px;
                        }}
                        QPushButton:hover {{
                            background-color: #fafafa;
                        }}
                    """
        elif balance < (-4):
            return f"""
                        QPushButton {{
                            background-color: #fae5e5;
                            border: 0px solid #f00000;
                            border-radius: 10px;
                        }}
                        QPushButton:hover {{
                            background-color: #fafafa;
                        }}
                    """
        else:
            return f"""
                        QPushButton {{
                            background-color: #f5f5f5;
                            border: 0px solid #cccccc;
                            border-radius: 10px;
                        }}
                        QPushButton:hover {{
                            background-color: #fafafa;
                        }}
                    """

    def open_new_group_dialog(self):
        """Atidaro naujos grupės kūrimo dialogą."""
        dialog = NewGroupDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.group_created.emit()

    # Pridėkite signalą, kuris bus iškviestas, kai sukuriamas naujas klientas:
    def create_customer(self):
        # Kai sukuriamas klientas, išsiųskite signalą
        self.customer_created.emit()
