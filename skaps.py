import logging
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QVBoxLayout, QScrollArea, QSplitter, QTextEdit, \
    QLabel, QSizePolicy

from config.config import main_window_size, main_windows_margins, fonas
from lib.backup import create_backup
from lib.bank_account import AccountForm
from lib.dbase import engine, Base
from lib.show_groups_list import GroupListWidget

# Sukonfigūruokite log žurnalą
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log',
                    filemode='w')

create_backup()
db_path = 'lib/dbase.db'
if not os.path.exists(db_path):
    Base.metadata.create_all(engine)
    logging.info("Duomenų bazė sukurta sėkmingai.")


class OutputRedirector:
    """Nukreipia sys.stdout ir sys.stderr į GUI valdiklį."""

    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.append(text.strip())

    def flush(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_customer_list_window = None
        self.account_form = AccountForm()
        self.setWindowTitle('"SkAps" (programa skaitiklių apskaita)')
        self.setGeometry(*main_window_size)
        self.setStyleSheet(f"QMainWindow {{ background-color: {fonas[1]}; border: none; }}")

        self.create_menu_bar()  # Sukuriame meniu juostą

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(*main_windows_margins)
        central_widget.setLayout(main_layout)

        splitter = QSplitter(Qt.Horizontal)

        self.group_list_widget = GroupListWidget()
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(self.group_list_widget)
        left_scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        splitter.addWidget(left_scroll)

        background_label = QLabel()
        pixmap = QPixmap("lib/second.png")
        background_label.setPixmap(pixmap)
        background_label.setScaledContents(True)
        background_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setWidget(background_label)
        self.right_scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        splitter.addWidget(self.right_scroll)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([610, 690])

        main_layout.addWidget(splitter)

        # Sukuriame logų išvedimo lauką
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(20)  # aukštis
        self.log_output.setStyleSheet("QTextEdit { background-color: transparent; border: 1px solid #ddd; }")
        self.log_output.setText("Status:") # Pridėti tekstą "Status:"
        # main_layout.addWidget(self.log_output)

        # Nukreipiame terminalo pranešimus į GUI
        sys.stdout = OutputRedirector(self.log_output)
        sys.stderr = OutputRedirector(self.log_output)

        self.group_list_widget.group_created.connect(self.group_list_widget.load_groups)
        self.group_list_widget.group_selected.connect(self.show_customers_list)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar { background-color: #f8f9fa; border-radius: 8px; padding: 5px; border: 0px solid #ddd; }
            QMenuBar::item { color: #495057; padding: 8px 12px; margin: 3px; border-radius: 5px; }
            QMenuBar::item:selected { background-color: #e9ecef; border-radius: 5px; }
            QMenuBar::item:pressed { background-color: #dee2e6; }
            QMenu { background-color: #ffffff; border: 0px solid #ced4da; border-radius: 5px; }
            QMenu::item { color: #495057; padding: 6px 10px; border-radius: 5px; }
            QMenu::item:selected { background-color: #e9ecef; }
        """)

        bank_menu = menu_bar.addMenu("Banko sąskaitos")

        manage_accounts_action = QAction("Valdyti sąskaitas", self)
        manage_accounts_action.triggered.connect(self.open_account_form)
        bank_menu.addAction(manage_accounts_action)

    def open_account_form(self):
        self.account_form.show()

    def show_customers_list(self, group):
        logging.debug(f"Rodo klientų sąrašą grupei: {group.customers_group_name}, ID: {group.id}")
        from lib.show_customers_list import CustomerListWindow
        customer_list_window = CustomerListWindow(group)

        customer_list_window.customer_created.connect(self.group_list_widget.load_groups)

        # Uždaryti ir ištrinti ankstesnį klientų sąrašą, jei jis egzistuoja
        if self.current_customer_list_window is not None:
            logging.debug("Uždaro ankstesnį klientų sąrašą")
            self.current_customer_list_window.close()
            self.current_customer_list_window.deleteLater()

        self.current_customer_list_window = customer_list_window

        self.right_scroll.takeWidget()
        self.right_scroll.setWidget(customer_list_window)
        logging.debug("Nustato naują klientų sąrašą")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logging.info("Programa paleista sėkmingai.")
    sys.exit(app.exec_())