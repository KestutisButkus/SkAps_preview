import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, \
    QMessageBox, \
    QGroupBox, QGraphicsDropShadowEffect, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from config.config import box_windows_margins, small_windows_size
from lib.dbase import session, CustomersGroup, BankAccount


def bootstrap_style():
    """ Qt Style Sheets (QSS) imituojantys Bootstrap temą """
    return """
            QWidget {
                background-color: #FAFCFD;
            }
            QLabel {
                color: #343a40;                
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 0px solid #ced4da;
                border-radius: 5px;                
                background-color: white;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 5px;
                border-radius: 5px;                
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """


class AccountForm(QWidget):
    def __init__(self):
        super().__init__()
        self.assign_button = None
        self.account_combo = None
        self.account_list_label = None
        self.group_combo = None
        self.group_label = None
        self.submit_button = None
        self.account_number_input = None
        self.account_number_label = None
        self.group_list = None
        self.init_ui()

    def init_ui(self):
        """ Inicializuoja vartotojo sąsają """
        self.setWindowTitle('Banko Sąskaitų Valdymas')
        self.setGeometry(*small_windows_size)
        self.setContentsMargins(*box_windows_margins)
        self.setStyleSheet(bootstrap_style())

        main_layout = QHBoxLayout()

        # Kairės pusės išdėstymas
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 20, 0)

        # Sukuriame grupės rėmelį
        group_box = QGroupBox("Grupės su priskirtomis sąskaitomis")
        group_box_layout = QVBoxLayout()

        # Grupės sąrašas
        self.group_list = QListWidget()
        self.group_list.setMinimumWidth(400)
        self.group_list.setStyleSheet("""
            QListWidget {
                background-color: #fff;
                border: 1px solid #eee;
                border-radius: 10px;
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #8899aa;
                color: white;
            }
        """)
        self.populate_group_list()
        group_box_layout.addWidget(self.group_list)

        group_box.setLayout(group_box_layout)
        group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 10px;                
                padding: 20px;
            }
        """)

        left_layout.addWidget(group_box)

        main_layout.addLayout(left_layout)

        # Dešinės pusės išdėstymas
        right_layout = QVBoxLayout()

        # Sukuriame grupės rėmelį
        account_group = QGroupBox("Naujos sąskaitos kūrimas")
        account_layout = QVBoxLayout()

        # Sąskaitos numerio įvestis
        self.account_number_label = QLabel('Naujos sąskaitos numeris:')
        self.account_number_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.account_number_label.setStyleSheet("color: #888; background-color: transparent;")
        account_layout.addWidget(self.account_number_label)

        self.account_number_input = QLineEdit()
        self.account_number_input.setPlaceholderText("Įveskite sąskaitos numerį")
        account_layout.addWidget(self.account_number_input)

        # Sukūrimo mygtukas
        self.submit_button = QPushButton('Sukurti naują sąskaitą')
        self.submit_button.clicked.connect(self.submit_form)
        account_layout.addWidget(self.submit_button)

        account_group.setLayout(account_layout)
        # Nustatome rėmelio stilių
        account_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 10px;                
                padding: 20px;
            }            
        """)
        # Pridedame šešėlį rėmeliui ir kitiems elementams
        self.account_number_input.setGraphicsEffect(self.create_shadow(5, Qt.gray))  # Įvesties lauko šešėlis

        # Įtraukiame rėmelį į pagrindinį išdėstymą
        right_layout.addWidget(account_group)
        right_layout.addSpacing(50)  # Prideda papildomą tarpą tarp elementų

        # 2. Sukuriame "Sąskaitos priskyrimo" formą su šešėliu
        assign_group = QGroupBox(" Sąskaitos priskyrimas ")
        assign_group.setStyleSheet("background-color: white")
        assign_layout = QVBoxLayout()

        self.group_label = QLabel('Pasirinkti Grupę:')
        self.group_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.group_label.setStyleSheet("color: #888; background-color: transparent;")
        assign_layout.addWidget(self.group_label)

        self.group_combo = QComboBox()
        self.populate_groups()
        self.group_combo.setStyleSheet(
            "background-color: #fff; border: 0px solid #ccc; padding: 5px; border-radius: 5px;")
        assign_layout.addWidget(self.group_combo)
        self.group_combo.setGraphicsEffect(self.create_shadow(5, Qt.gray))  # Grupės pasirinkimo šešėlis

        assign_layout.addSpacing(20)

        # Sąskaitų pasirinkimas
        self.account_list_label = QLabel('Pasirinkti sąskaitą:')
        self.account_list_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.account_list_label.setStyleSheet("color: #888; background-color: transparent;")
        assign_layout.addWidget(self.account_list_label)

        self.account_combo = QComboBox()
        self.populate_accounts()
        self.account_combo.setStyleSheet(
            "background-color: #fff; border: 0px solid #ccc; padding: 5px; border-radius: 5px;")
        assign_layout.addWidget(self.account_combo)
        self.account_combo.setGraphicsEffect(self.create_shadow(5, Qt.gray))  # Sąskaitų pasirinkimo šešėlis

        assign_layout.addSpacing(20)

        # Priskyrimo mygtukas
        self.assign_button = QPushButton('Priskirti sąskaitą')
        self.assign_button.clicked.connect(self.assign_existing_account)
        assign_layout.addWidget(self.assign_button)
        self.assign_button.setGraphicsEffect(self.create_shadow(5, Qt.gray))  # Mygtuko šešėlis
        assign_layout.addSpacing(10)  # Prideda papildomą tarpą tarp elementų

        assign_group.setLayout(assign_layout)
        # Nustatome rėmelio stilių
        assign_group.setStyleSheet("""
                    QGroupBox {
                        border: 1px solid #cccccc;                        
                        border-radius: 10px;
                        padding: 20px;
                    }
                """)

        right_layout.addWidget(assign_group)

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

    def populate_group_list(self):
        """Užpildo grupių sąrašą su joms priskirtomis sąskaitomis."""
        self.group_list.clear()
        groups = session.query(CustomersGroup).all()

        for group in groups:
            item = QListWidgetItem()

            # Sukuriame grupės pavadinimą (bold) ir sąskaitų numerius su atitraukimu
            group_label = QLabel(f'{group.customers_group_name}:')
            group_label.setStyleSheet("font-weight: bold; background: transparent; border: none")
            accounts_text = '\n'.join([f'• {account.account_number}' for account in group.accounts])
            accounts_label = QLabel(accounts_text)
            accounts_label.setIndent(30)
            accounts_label.setStyleSheet("background: transparent; padding: 2px; border: none")

            # Widget'as su layout
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(group_label)
            layout.addWidget(accounts_label)
            layout.setSpacing(2)
            layout.setContentsMargins(5, 5, 5, 5)
            widget.setLayout(layout)
            widget.setStyleSheet("""
                background: transparent;
                border-radius: 5px;
                border: 1px solid #bbdfff;
            """)

            # Nustatome elementui dydį ir pridedame jį į sąrašą
            item.setSizeHint(widget.sizeHint())
            self.group_list.addItem(item)
            self.group_list.setItemWidget(item, widget)

        self.group_list.setSpacing(2)
        self.group_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.group_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.group_list.itemSelectionChanged.connect(self.update_selection)

    def update_selection(self):
        """Atnaujina grupės pasirinkimo stilių."""
        for index in range(self.group_list.count()):
            item = self.group_list.item(index)
            widget = self.group_list.itemWidget(item)
            widget.setStyleSheet("""
                background-color: #007bff; color: #ffffff;
            """ if item.isSelected() else """
                background: transparent; border-radius: 5px; border: 1px solid #bbdfff;
            """)

    def populate_groups(self):
        """ Užpildo grupių pasirinkimo laukelį """
        self.group_combo.clear()
        groups = session.query(CustomersGroup).all()
        for group in groups:
            self.group_combo.addItem(group.customers_group_name)

    def populate_accounts(self):
        """ Užpildo sąskaitų pasirinkimo laukelį """
        self.account_combo.clear()
        accounts = session.query(BankAccount).all()
        for account in accounts:
            self.account_combo.addItem(account.account_number)

    def submit_form(self):
        """ Sukuria naują sąskaitą """
        account_number = self.account_number_input.text().strip()

        if not account_number:
            self.show_message("Klaida", "Sąskaitos numeris negali būti tuščias!", QMessageBox.Critical)
            return

        existing_account = session.query(BankAccount).filter_by(account_number=account_number).first()
        if existing_account:
            self.show_message("Klaida", "Tokia sąskaita jau egzistuoja!", QMessageBox.Warning)
            return

        new_account = BankAccount(account_number=account_number)
        session.add(new_account)
        session.commit()
        self.populate_accounts()
        self.populate_group_list()
        self.show_message("Sėkmė", f'Sąskaita "{account_number}" sukurta.', QMessageBox.Information)

    def assign_existing_account(self):
        """ Priskiria esamą sąskaitą pasirinktai grupei """
        selected_account_number = self.account_combo.currentText()
        selected_group = self.group_combo.currentText()

        if not selected_account_number:
            self.show_message("Klaida", "Pasirinkite sąskaitą!", QMessageBox.Critical)
            return

        account = session.query(BankAccount).filter_by(account_number=selected_account_number).first()
        group = session.query(CustomersGroup).filter_by(customers_group_name=selected_group).first()

        if account and group:
            if account in group.accounts:
                self.show_message("Informacija", "Ši sąskaita jau priskirta šiai grupei!", QMessageBox.Information)
                return
            group.accounts.append(account)
            session.commit()
            self.populate_group_list()
            self.show_message("Sėkmė", f'Sąskaita "{selected_account_number}" priskirta grupei "{selected_group}"',
                              QMessageBox.Information)
        else:
            self.show_message("Klaida", "Nepavyko priskirti sąskaitos grupei.", QMessageBox.Warning)

    def show_message(self, title, text, icon):
        """ Parodo pranešimą lange """
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec_()

    def create_shadow(self, blur_radius, color, x_offset=0, y_offset=0):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(color)
        shadow.setOffset(x_offset, y_offset)
        return shadow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = AccountForm()
    form.show()
    sys.exit(app.exec_())
