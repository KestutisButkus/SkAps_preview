import os
import shutil
from datetime import datetime


def create_backup():
    db_path = 'lib/dbase.db'

    # Sukurti backup katalogą, jei jis neegzistuoja
    if not os.path.exists('lib/backup'):
        os.makedirs('lib/backup')

    # Sukurti dbase.db kopiją į backup katalogą su šiandienos data pavadinime
    try:
        backup_path = f"lib/backup/dbase_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, backup_path)
        print(f"atsarginė kopija sukurta: {backup_path}")
    except FileNotFoundError:
        print("Duomenų bazės failas neegzistuoja. Atsarginė kopija nesukurta.")
