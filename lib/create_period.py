from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QLineEdit, \
    QGraphicsDropShadowEffect, QMessageBox

from lib.dbase import Session, Period


def show_message(title, message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec_()


class NewPeriodDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Naujas Periodas")
        # self.setGeometry(*small_windows_size)
        self.setStyleSheet("background-color: #f4f7fa; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        period_layout = QHBoxLayout()
        period_layout.setContentsMargins(20, 30, 50, 0)

        self.info_label = QLabel("Naujas Periodas")
        self.info_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.info_label.setStyleSheet("color: #007bfc;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.year_label, self.year_input = self.create_input_field("Metai:", "Pasirinkite metus")
        period_layout.addWidget(self.year_label)
        this_year = datetime.now().year
        self.year_input.addItems([str(year) for year in range(this_year - 1, this_year + 4)])
        self.year_input.setFixedWidth(70)  # Sumažiname plotį
        period_layout.addWidget(self.year_input)

        hspace = QLabel()
        hspace.setFixedWidth(30)
        period_layout.addWidget(hspace)

        self.month_label, self.month_input = self.create_input_field("Mėnuo:", "Pasirinkite mėnesį")
        period_layout.addWidget(self.month_label)
        self.month_input.addItems([f"{month:02}" for month in range(1, 13)])
        self.month_input.setFixedWidth(70)  # Sumažiname plotį
        period_layout.addWidget(self.month_input)

        layout.addLayout(period_layout)

        self.create_button = QPushButton("Sukurti periodą")
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #007bfc;
                color: white;
                padding: 10px;
                font-size: 12px;
                border-radius: 10px;
                border: none;
                margin: 50px;               
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        # self.create_button.setFixedSize(150, 40)
        self.create_button.clicked.connect(self.create_period)
        layout.addWidget(self.create_button)

        self.info_label = QLabel(f"Atvaizduojamas metų sąrašas yra -1 ir +3 nuo einamųjų metų\n"
                                 f"Už papildomą mokestį (600.00 € + PVM) galima pakoreguoti")
        # self.info_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.info_label.setStyleSheet("color: #888;")
        self.info_label.setAlignment(Qt.AlignBottom)
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def create_input_field(self, label_text, placeholder_text):
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 9, QFont.Bold))
        label.setStyleSheet("color: #343a40;")

        input_field = QComboBox() if "Pasirinkite" in placeholder_text else QLineEdit()
        input_field.setPlaceholderText(placeholder_text)
        input_field.setStyleSheet("padding: 5px; font-size: 11px; border-radius: 5px;")
        self.apply_shadow_effect(input_field)

        return label, input_field

    def apply_shadow_effect(self, widget):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def create_period(self):
        year = self.year_input.currentText()
        month = self.month_input.currentText()

        period_session = Session()
        try:
            existing_period = period_session.query(Period).filter_by(year=year, month=month).first()
            if existing_period:
                show_message("Klaida", f"Periodas '{year}-{month}' jau egzistuoja.")
                return

            new_period = Period(year=year, month=month)
            period_session.add(new_period)
            period_session.commit()
            show_message("Sėkmė", f"Naujas periodas '{year}-{month}' sukurtas sėkmingai.")
            self.accept()
        except Exception as e:
            show_message("Klaida", f"Klaida įrašant duomenis į duomenų bazę: {e}")
        finally:
            period_session.close()
