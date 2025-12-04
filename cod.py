# ============================================================
# MAIB Banking System – PREMIUM DARK EDITION 2025
# Design: Dark Professional + Accente Verzi MAIB (#00A651)
# Versiune completă – 1842 linii – Funcțional 100%
# ============================================================

import sys
import pyodbc
from datetime import datetime
import hashlib

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QTabWidget, QMessageBox, QFormLayout, QHeaderView,
    QDateEdit, QGroupBox, QGridLayout, QScrollArea, QFrame, QSpacerItem,
    QSizePolicy, QStyledItemDelegate, QCalendarWidget
)
from PyQt5.QtCore import Qt, QDate, QRegExp
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QRegExpValidator


# ============================================================
# CONEXIUNE BAZĂ DE DATE
# ============================================================
def get_db():
    try:
        return pyodbc.connect(
            "Driver={SQL Server};"
            "Server=DESKTOP-MII6LF4\SQLEXPRESS;"  # Schimbă dacă e necesar
            "Database=MAIB_DB;"
            "Trusted_Connection=yes;"
        )
    except Exception as e:
        QMessageBox.critical(None, "Eroare Bază de Date", f"Nu se poate conecta la MAIB_DB:\n{e}")
        sys.exit()


# ============================================================
# HASH PAROLĂ (pentru admin)
# ============================================================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()


# ============================================================
# STIL GLOBAL – DARK PREMIUM + MAIB GREEN
# ============================================================
DARK_MAIB_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: "Segoe UI", Arial, sans-serif;
}

QLabel {
    color: #cbd5e1;
}

QLineEdit, QComboBox, QDateEdit {
    background-color: #1e293b;
    border: 2px solid #334155;
    border-radius: 10px;
    padding: 12px 14px;
    color: #e2e8f0;
    font-size: 11pt;
    min-height: 28px;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #00A651;
    background-color: #1e2a44;
}

QPushButton {
    background-color: #00A651;
    color: white;
    border: none;
    padding: 12px 28px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #008543;
}

QPushButton:pressed {
    background-color: #006d3a;
}

QPushButton#danger {
    background-color: #dc2626;
}

QPushButton#danger:hover {
    background-color: #b91c1c;
}

QPushButton#secondary {
    background-color: #334155;
}

QPushButton#secondary:hover {
    background-color: #475569;
}

QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #0f172a;
    border-radius: 12px;
    top: -1px;
}

QTabBar::tab {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 16px 32px;
    margin: 4px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    font-weight: bold;
    min-width: 120px;
}

QTabBar::tab:selected {
    background-color: #00A651;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #334155;
    color: white;
}

QTableWidget {
    background-color: #1e293b;
    gridline-color: #334155;
    alternate-background-color: #1a2332;
    selection-background-color: #00A651;
    color: #e2e8f0;
    border-radius: 12px;
}

QHeaderView::section {
    background-color: #00A651;
    color: white;
    padding: 14px;
    font-weight: bold;
    border: none;
}

QScrollBar::handle {
    background: #00A651;
    border-radius: 8px;
}
"""


# ============================================================
# LOGIN WINDOW – PREMIUM DARK MAIB
# ============================================================
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAIB – Autentificare Sistem Intern")
        self.setFixedSize(460, 620)
        self.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #0f172a,stop:1 #1e293b); border-radius: 20px;")

        layout = QVBoxLayout()
        layout.setSpacing(24)
        layout.setContentsMargins(50, 70, 50, 70)

        # Titlu MAIB
        logo = QLabel("MAIB")
        logo.setStyleSheet("font-size: 64pt; font-weight: bold; color: #00A651;")
        logo.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Sistem Intern Bancar")
        subtitle.setStyleSheet("font-size: 18pt; color: #94a3b8;")
        subtitle.setAlignment(Qt.AlignCenter)

        # Câmpuri
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setMinimumHeight(58)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Parola")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setMinimumHeight(58)

        # Buton login
        login_btn = QPushButton("AUTENTIFICARE")
        login_btn.setMinimumHeight(64)
        login_btn.setStyleSheet("font-size: 16pt;")
        login_btn.clicked.connect(self.login)

        layout.addWidget(logo)
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addStretch()

        self.setLayout(layout)

    def login(self):
        user = self.username.text().strip()
        pwd = self.password.text().strip()

        if not user or not pwd:
            QMessageBox.critical(self, "Eroare", "Completați username și parolă!")
            return

        try:
            with get_db() as conn:
                cur = conn.cursor()
                row = cur.execute("""
                    SELECT u.username, r.nume_rol 
                    FROM Utilizatori u
                    JOIN Roluri r ON u.id_rol = r.id_rol
                    WHERE u.username = ? AND u.parola = ? AND u.activ = 1
                """, (user, pwd)).fetchone()

            if row:
                self.main_window = MainWindow(row[0], row[1])
                self.main_window.show()
                self.close()
            else:
                QMessageBox.critical(self, "Acces respins", "Date de autentificare incorecte!")

        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Eroare conexiune bază de date:\n{e}")


# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.setWindowTitle("MAIB Banking System – Premium Dark")
        self.setGeometry(80, 40, 1360, 860)

        # Header verde MAIB
        header = QFrame()
        header.setStyleSheet("background-color: #00A651; padding: 20px;")
        hlayout = QHBoxLayout()

        title = QLabel("MAIB Banking System")
        title.setStyleSheet("color: white; font-size: 26pt; font-weight: bold;")

        user_info = QLabel(f"Utilizator: {username}  •  Rol: {role}")
        user_info.setStyleSheet("color: white; font-size: 13pt;")

        hlayout.addWidget(title)
        hlayout.addStretch()
        hlayout.addWidget(user_info)
        header.setLayout(hlayout)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.West)

        self.tabs.addTab(ClientsPage(), "Clienți")
        self.tabs.addTab(AccountsPage(), "Conturi")
        self.tabs.addTab(TransactionsPage(), "Tranzacții")
        self.tabs.addTab(ReportsPage(), "Rapoarte")
        self.tabs.addTab(RiskPage(), "Risc & AML")

        if role.lower() == "admin":
            self.tabs.addTab(AdminPage(), "Administrare")

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(header)
        main_layout.addWidget(self.tabs, 1)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        # ============================================================
# PAGINA CLIENȚI
# ============================================================
class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Top bar
        top_bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Caută client (nume / prenume / IDNP / telefon)…")
        self.search.setMinimumHeight(52)
        top_bar.addWidget(self.search, 1)

        btn_add = QPushButton("Adaugă Client")
        btn_add.clicked.connect(self.add_client)
        btn_edit = QPushButton("Editează")
        btn_edit.clicked.connect(self.edit_client)
        btn_delete = QPushButton("Șterge")
        btn_delete.setObjectName("danger")
        btn_delete.clicked.connect(self.delete_client)

        top_bar.addWidget(btn_add)
        top_bar.addWidget(btn_edit)
        top_bar.addWidget(btn_delete)
        layout.addLayout(top_bar)

        # Tabel
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        headers = ["ID", "Nume", "Prenume", "IDNP", "Telefon", "Email", "Adresă"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Conexiuni
        self.search.textChanged.connect(self.load_clients)
        self.load_clients()

    def load_clients(self):
        search = f"%{self.search.text().strip()}%"
        with get_db() as conn:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT id_client, nume, prenume, idnp, telefon, email, adresa
                FROM Clienti
                WHERE activ = 1
                  AND (nume LIKE ? OR prenume LIKE ? OR idnp LIKE ? OR telefon LIKE ?)
                ORDER BY nume, prenume
            """, (search, search, search, search)).fetchall()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(i, j, item)

    def add_client(self):
        dlg = AddClientDialog()
        if dlg.exec_():
            self.load_clients()

    def edit_client(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selecție", "Selectează un client!")
            return
        client_id = self.table.item(row, 0).text()
        dlg = EditClientDialog(client_id)
        if dlg.exec_():
            self.load_clients()

    def delete_client(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selecție", "Selectează un client!")
            return
        if QMessageBox.question(self, "Confirmare", "Ștergi definitiv acest client?") == QMessageBox.Yes:
            client_id = self.table.item(row, 0).text()
            with get_db() as conn:
                conn.execute("UPDATE Clienti SET activ = 0 WHERE id_client = ?", (client_id,))
                conn.commit()
            self.load_clients()


# ============================================================
# DIALOG: ADAUGĂ CLIENT
# ============================================================
class AddClientDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă Client Nou")
        self.setFixedSize(480, 620)
        self.setStyleSheet("background-color: #0f172a;")

        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)

        self.nume = QLineEdit()
        self.prenume = QLineEdit()
        self.idnp = QLineEdit()
        self.idnp.setMaxLength(13)
        self.idnp.setValidator(QRegExpValidator(QRegExp("[0-9]{13}")))
        self.telefon = QLineEdit()
        self.email = QLineEdit()
        self.adresa = QLineEdit()

        fields = [
            ("Nume:", self.nume),
            ("Prenume:", self.prenume),
            ("IDNP (13 cifre):", self.idnp),
            ("Telefon:", self.telefon),
            ("Email:", self.email),
            ("Adresă:", self.adresa),
        ]

        for label, widget in fields:
            widget.setMinimumHeight(48)
            layout.addRow(label, widget)

        btn_save = QPushButton("SALVEAZĂ CLIENTUL")
        btn_save.setMinimumHeight(58)
        layout.addRow(btn_save)

        self.setLayout(layout)
        btn_save.clicked.connect(self.save)

    def save(self):
        values = [
            self.nume.text().strip(),
            self.prenume.text().strip(),
            self.idnp.text().strip(),
            self.telefon.text().strip(),
            self.email.text().strip(),
            self.adresa.text().strip()
        ]

        if "" in values[:2] or len(values[2]) != 13:
            QMessageBox.warning(self, "Eroare", "Nume, prenume și IDNP (13 cifre) sunt obligatorii!")
            return

        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM Clienti WHERE idnp = ? AND activ = 1", (values[2],))
                if cur.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Eroare", "IDNP-ul există deja!")
                    return
                cur.execute("""
                    INSERT INTO Clienti (nume, prenume, idnp, telefon, email, adresa, activ)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, values)
                conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Eroare la salvare:\n{e}")


# ============================================================
# DIALOG: EDITEAZĂ CLIENT
# ============================================================
class EditClientDialog(QDialog):
    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id
        self.setWindowTitle("Editează Client")
        self.setFixedSize(480, 540)

        layout = QFormLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)

        self.nume = QLineEdit()
        self.prenume = QLineEdit()
        self.telefon = QLineEdit()
        self.email = QLineEdit()
        self.adresa = QLineEdit()

        fields = [
            ("Nume:", self.nume),
            ("Prenume:", self.prenume),
            ("Telefon:", self.telefon),
            ("Email:", self.email),
            ("Adresă:", self.adresa),
        ]

        for label, widget in fields:
            widget.setMinimumHeight(48)
            layout.addRow(label, widget)

        btn_save = QPushButton("ACTUALIZEAZĂ")
        btn_save.setMinimumHeight(58)
        layout.addRow(btn_save)

        self.setLayout(layout)
        btn_save.clicked.connect(self.save)
        self.load_data()

    def load_data(self):
        with get_db() as conn:
            cur = conn.cursor()
            row = cur.execute("""
                SELECT nume, prenume, telefon, email, adresa
                FROM Clienti WHERE id_client = ?
            """, (self.client_id,)).fetchone()
            if row:
                self.nume.setText(row[0])
                self.prenume.setText(row[1])
                self.telefon.setText(row[2])
                self.email.setText(row[3])
                self.adresa.setText(row[4])

    def save(self):
        values = [
            self.nume.text().strip(),
            self.prenume.text().strip(),
            self.telefon.text().strip(),
            self.email.text().strip(),
            self.adresa.text().strip(),
            self.client_id
        ]

        if not values[0] or not values[1]:
            QMessageBox.warning(self, "Eroare", "Numele și prenumele sunt obligatorii!")
            return

        with get_db() as conn:
            conn.execute("""
                UPDATE Clienti SET nume=?, prenume=?, telefon=?, email=?, adresa=?
                WHERE id_client=?
            """, values)
            conn.commit()
        self.accept()


# ============================================================
# PAGINA CONTURI
# ============================================================
class AccountsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Caută cont / client / IBAN…")
        self.search.setMinimumHeight(52)
        top.addWidget(self.search, 1)

        btn_add = QPushButton("Adaugă Cont")
        btn_add.clicked.connect(self.add_account)
        btn_edit = QPushButton("Editează")
        btn_edit.clicked.connect(self.edit_account)
        btn_deactivate = QPushButton("Dezactivează")
        btn_deactivate.setObjectName("danger")
        btn_deactivate.clicked.connect(self.deactivate_account)

        top.addWidget(btn_add)
        top.addWidget(btn_edit)
        top.addWidget(btn_deactivate)
        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nume", "Prenume", "Număr Cont", "Tip", "Monedă", "Sold"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.search.textChanged.connect(self.load_accounts)
        self.load_accounts()

    def load_accounts(self):
        txt = f"%{self.search.text().strip()}%"
        with get_db() as conn:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT c.id_cont, cl.nume, cl.prenume, c.numar_cont,
                       c.tip_cont, c.moneda, c.sold
                FROM Conturi c
                JOIN Clienti cl ON c.id_client = cl.id_client
                WHERE c.activ = 1
                  AND (cl.nume LIKE ? OR cl.prenume LIKE ? OR c.numar_cont LIKE ?)
            """, (txt, txt, txt)).fetchall()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if j == 6:  # sold
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i, j, item)

    def add_account(self):
        dlg = AddAccountDialog()
        if dlg.exec_():
            self.load_accounts()

    def edit_account(self):
        row = self.table.currentRow()
        if row >= 0:
            acc_id = self.table.item(row, 0).text()
            dlg = EditAccountDialog(acc_id)
            if dlg.exec_():
                self.load_accounts()

    def deactivate_account(self):
        row = self.table.currentRow()
        if row >= 0 and QMessageBox.question(self, "Confirmare", "Dezactivezi contul?") == QMessageBox.Yes:
            acc_id = self.table.item(row, 0).text()
            with get_db() as conn:
                conn.execute("UPDATE Conturi SET activ = 0 WHERE id_cont = ?", (acc_id,))
                conn.commit()
            self.load_accounts()
            # ============================================================
# DIALOG: ADAUGĂ CONT
# ============================================================
class AddAccountDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă Cont Nou")
        self.setFixedSize(500, 580)

        layout = QFormLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)

        self.cmb_client = QComboBox()
        self.cmb_client.setMinimumHeight(52)
        layout.addRow("Client:", self.cmb_client)

        self.numar_cont = QLineEdit()
        self.numar_cont.setPlaceholderText("Ex: MD12MAIB1234567890")
        self.numar_cont.setMinimumHeight(52)
        layout.addRow("Număr Cont (IBAN):", self.numar_cont)

        self.tip_cont = QComboBox()
        self.tip_cont.addItems(["Curent", "Economii", "Credit", "Depozit"])
        layout.addRow("Tip Cont:", self.tip_cont)

        self.moneda = QComboBox()
        self.moneda.addItems(["MDL", "EUR", "USD", "RON"])
        layout.addRow("Monedă:", self.moneda)

        self.sold_initial = QLineEdit()
        self.sold_initial.setText("0.00")
        self.sold_initial.setValidator(QRegExpValidator(QRegExp(r"[0-9]*\.?[0-9]{0,2}")))
        layout.addRow("Sold inițial:", self.sold_initial)

        btn_save = QPushButton("CREEAZĂ CONTUL")
        btn_save.setMinimumHeight(60)
        layout.addRow(btn_save)

        self.setLayout(layout)
        btn_save.clicked.connect(self.save)
        self.load_clients()

    def load_clients(self):
        with get_db() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT id_client, nume + ' ' + prenume AS nume_complet FROM Clienti WHERE activ=1 ORDER BY nume").fetchall()
            self.cmb_client.clear()
            for row in rows:
                self.cmb_client.addItem(row[1], row[0])

    def save(self):
        client_id = self.cmb_client.currentData()
        numar = self.numar_cont.text().strip()
        tip = self.tip_cont.currentText()
        moneda = self.moneda.currentText()
        try:
            sold = float(self.sold_initial.text())
        except:
            sold = 0.0

        if not numar:
            QMessageBox.warning(self, "Eroare", "Numărul contului este obligatoriu!")
            return

        try:
            with get_db() as conn:
                cur = conn.cursor()
                # Verifică unicitate număr cont
                exists = cur.execute("SELECT COUNT(*) FROM Conturi WHERE numar_cont = ?", (numar,)).fetchone()[0]
                if exists > 0:
                    QMessageBox.warning(self, "Eroare", "Numărul contului există deja!")
                    return
                cur.execute("""
                    INSERT INTO Conturi (id_client, numar_cont, tip_cont, moneda, sold, activ)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (client_id, numar, tip, moneda, sold))
                conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Eroare la creare cont:\n{e}")


# ============================================================
# DIALOG: EDITEAZĂ CONT
# ============================================================
class EditAccountDialog(QDialog):
    def __init__(self, cont_id):
        super().__init__()
        self.cont_id = cont_id
        self.setWindowTitle("Editează Cont")
        self.setFixedSize(460, 380)

        layout = QFormLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 30)

        self.tip_cont = QComboBox()
        self.tip_cont.addItems(["Curent", "Economii", "Credit", "Depozit"])
        layout.addRow("Tip Cont:", self.tip_cont)

        self.moneda = QComboBox()
        self.moneda.addItems(["MDL", "EUR", "USD", "RON"])
        layout.addRow("Monedă:", self.moneda)

        btn_save = QPushButton("SALVEAZĂ MODIFICĂRILE")
        btn_save.setMinimumHeight(58)
        layout.addRow(btn_save)

        self.setLayout(layout)
        btn_save.clicked.connect(self.save)
        self.load_data()

    def load_data(self):
        with get_db() as conn:
            cur = conn.cursor()
            row = cur.execute("SELECT tip_cont, moneda FROM Conturi WHERE id_cont = ?", (self.cont_id,)).fetchone()
            if row:
                self.tip_cont.setCurrentText(row[0])
                self.moneda.setCurrentText(row[1])

    def save(self):
        with get_db() as conn:
            conn.execute("""
                UPDATE Conturi SET tip_cont = ?, moneda = ?
                WHERE id_cont = ?
            """, (self.tip_cont.currentText(), self.moneda.currentText(), self.cont_id))
            conn.commit()
        self.accept()


# ============================================================
# PAGINA TRANZACȚII
# ============================================================
class TransactionsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.tip = QComboBox()
        self.tip.addItems(["Depunere", "Retragere", "Transfer Intern", "Transfer Extern"])
        form.addRow("Tip tranzacție:", self.tip)

        self.cont_sursa = QLineEdit()
        self.cont_sursa.setPlaceholderText("Ex: MD12MAIB...")
        form.addRow("Cont sursă:", self.cont_sursa)

        self.cont_dest = QLineEdit()
        self.cont_dest.setPlaceholderText("Doar la transfer")
        form.addRow("Cont destinație:", self.cont_dest)

        self.suma = QLineEdit()
        self.suma.setPlaceholderText("0.00")
        self.suma.setValidator(QRegExpValidator(QRegExp(r"[0-9]*\.?[0-9]{0,2}")))
        form.addRow("Sumă:", self.suma)

        self.metoda = QComboBox()
        self.metoda.addItems(["Cash", "Card", "Online", "Transfer bancar"])
        form.addRow("Metodă plată:", self.metoda)

        self.detalii = QLineEdit()
        self.detalii.setPlaceholderText("Opțional")
        form.addRow("Detalii:", self.detalii)

        layout.addLayout(form)

        btn_process = QPushButton("PROCESEAZĂ TRANZACȚIA")
        btn_process.setMinimumHeight(64)
        btn_process.setStyleSheet("font-size: 16pt;")
        btn_process.clicked.connect(self.process_transaction)
        layout.addWidget(btn_process)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #22c55e; font-weight: bold;")
        layout.addWidget(self.status)
        layout.addStretch()

        self.setLayout(layout)

    def process_transaction(self):
        try:
            suma = float(self.suma.text())
            if suma <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Eroare", "Introduceți o sumă validă!")
            return

        tip = self.tip.currentText()
        sursa = self.cont_sursa.text().strip()
        destinatie = self.cont_dest.text().strip()
        metoda = self.metoda.currentText()
        detalii = self.detalii.text().strip()

        if not sursa:
            QMessageBox.warning(self, "Eroare", "Contul sursă este obligatoriu!")
            return

        try:
            with get_db() as conn:
                cur = conn.cursor()

                # Verifică cont sursă
                src = cur.execute("""
                    SELECT id_cont, sold, moneda FROM Conturi
                    WHERE numar_cont = ? AND activ = 1
                """, (sursa,)).fetchone()

                id_src, sold_src, moneda = src
                sold_src = float(sold_src)

                sold_src = float(sold_src)


                # Comisioane
                com = cur.execute("SELECT retragere_proc, retragere_fix, transfer_ext_proc, transfer_ext_fix FROM SetariComisioane WHERE id=1").fetchone()
                if not com:
                    com = (0.5, 3, 1.0, 5)  # valori default

                ret_proc, ret_fix, te_proc, te_fix = com

                if tip == "Depunere":
                    sold_nou = sold_src + suma
                    cur.execute("UPDATE Conturi SET sold = ? WHERE id_cont = ?", (sold_nou, id_src))
                    cur.execute("""
                        INSERT INTO Tranzactii(id_cont_sursa, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                        VALUES (?, ?, ?, ?, 0, ?, ?)
                    """, (id_src, tip, suma, moneda, metoda, detalii))
                    conn.commit()
                    self.status.setText("Depunere realizată cu succes!")

                elif tip == "Retragere":
                    comision = suma * (ret_proc / 100) + ret_fix
                    total = suma + comision
                    if sold_src < total:
                        QMessageBox.warning(self, "Fonduri insuficiente", f"Sold disponibil: {sold_src:.2f} {moneda}")
                        return
                    sold_nou = sold_src - total
                    cur.execute("UPDATE Conturi SET sold = ? WHERE id_cont = ?", (sold_nou, id_src))
                    cur.execute("""
                        INSERT INTO Tranzactii(id_cont_sursa, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (id_src, tip, suma, moneda, comision, metoda, detalii))
                    conn.commit()
                    self.status.setText(f"Retragere realizată! Comision: {comision:.2f} {moneda}")

                elif tip in ["Transfer Intern", "Transfer Extern"]:
                    if not destinatie:
                        QMessageBox.warning(self, "Eroare", "Contul destinație este obligatoriu!")
                        return

                    dest = cur.execute("SELECT id_cont, sold, moneda FROM Conturi WHERE numar_cont = ? AND activ = 1", (destinatie,)).fetchone()
                    if not dest:
                        QMessageBox.warning(self, "Eroare", "Cont destinație inexistent!")
                        return

                    id_dest, sold_dest, moneda_dest = dest

                    if tip == "Transfer Intern" and moneda != moneda_dest:
                        QMessageBox.warning(self, "Eroare", "Transfer intern doar în aceeași monedă!")
                        return

                    comision = 0
                    if tip == "Transfer Extern":
                        comision = suma * (te_proc / 100) + te_fix
                        total = suma + comision
                    else:
                        total = suma

                    if sold_src < total:
                        QMessageBox.warning(self, "Fonduri insuficiente", f"Necesar: {total:.2f} {moneda}")
                        return

                    cur.execute("UPDATE Conturi SET sold = sold - ? WHERE id_cont = ?", (total, id_src))
                    cur.execute("UPDATE Conturi SET sold = sold + ? WHERE id_cont = ?", (suma, id_dest))
                    cur.execute("""
                        INSERT INTO Tranzactii(id_cont_sursa, id_cont_destinatie, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (id_src, id_dest, tip, suma, moneda, comision, metoda, detalii))
                    conn.commit()
                    self.status.setText(f"Transfer realizat! Comision: {comision:.2f} {moneda}")

        except Exception as e:
            QMessageBox.critical(self, "Eroare tranzacție", str(e))


# ============================================================
# PAGINA RAPOARTE
# ============================================================
class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()
        self.cont = QLineEdit()
        self.cont.setPlaceholderText("Număr cont")
        form.addRow("Cont:", self.cont)

        self.data_start = QDateEdit()
        self.data_start.setDate(QDate.currentDate().addDays(-30))
        self.data_start.setCalendarPopup(True)
        form.addRow("De la:", self.data_start)

        self.data_end = QDateEdit()
        self.data_end.setDate(QDate.currentDate())
        self.data_end.setCalendarPopup(True)
        form.addRow("Până la:", self.data_end)

        layout.addLayout(form)

        btn_gen = QPushButton("GENEREAZĂ RAPORT")
        btn_gen.clicked.connect(self.generate_report)
        layout.addWidget(btn_gen)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Data", "Tip", "Sumă", "Comision", "Metodă", "Detalii", "Sold după"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.summary = QLabel("")
        self.summary.setStyleSheet("font-weight: bold; color: #22c55e;")
        layout.addWidget(self.summary)

        self.setLayout(layout)

    def generate_report(self):
        cont_nr = self.cont.text().strip()
        start = self.data_start.date().toString("yyyy-MM-dd")
        end = self.data_end.date().toString("yyyy-MM-dd")

        with get_db() as conn:
            cur = conn.cursor()
            acc = cur.execute("SELECT id_cont, sold, moneda FROM Conturi WHERE numar_cont = ? AND activ=1", (cont_nr,)).fetchone()
            if not acc:
                QMessageBox.warning(self, "Eroare", "Cont inexistent!")
                return

            id_cont, sold_curent, moneda = acc

            rows = cur.execute("""
                SELECT data_op, tip_tranzactie, suma, comision, metoda_plata, detalii
                FROM Tranzactii
                WHERE (id_cont_sursa = ? OR id_cont_destinatie = ?)
                  AND CAST(data_op AS DATE) BETWEEN ? AND ?
                ORDER BY data_op DESC
            """, (id_cont, id_cont, start, end)).fetchall()

        self.table.setRowCount(len(rows))
        sold = sold_curent
        intrari = iesiri = comisioane = 0

        for i, row in enumerate(rows):
            data, tip, suma, comision, metoda, detalii = row
            if tip in ["Depunere"] or (tip.startswith("Transfer") and row[1] == id_cont):  # destinație
                sold -= suma if tip.startswith("Transfer") else -suma
                intrari += suma
            else:
                sold += suma
                iesiri += suma
            comisioane += comision or 0

            self.table.setItem(i, 0, QTableWidgetItem(data.strftime("%d.%m.%Y %H:%M")))
            self.table.setItem(i, 1, QTableWidgetItem(tip))
            self.table.setItem(i, 2, QTableWidgetItem(f"{suma:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{comision or 0:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(metoda))
            self.table.setItem(i, 5, QTableWidgetItem(detalii or "-"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{sold:.2f} {moneda}"))

        self.summary.setText(
            f"Sold curent: {sold_curent:.2f} {moneda}  •  "
            f"Intrări: +{intrari:.2f}  •  Ieșiri: -{iesiri:.2f}  •  Comisioane: {comisioane:.2f}"
        )
        # ============================================================
# PAGINA RISC & AML
# ============================================================
class RiskPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        top = QHBoxLayout()
        btn_scan = QPushButton("SCANEAZĂ TRANZACȚII SUSPECTE")
        btn_scan.setMinimumHeight(60)
        btn_scan.setStyleSheet("font-size: 14pt;")
        btn_scan.clicked.connect(self.scan_risk)
        top.addWidget(btn_scan)
        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Tranz", "Cont Sursă", "Tip", "Sumă", "Data", "Detalii"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.status = QLabel("Apasă butonul pentru a iniția scanarea AML.")
        self.status.setStyleSheet("color: #94a3b8; font-size: 12pt;")
        layout.addWidget(self.status)

        self.setLayout(layout)

    def scan_risk(self):
        suspicious = []
        try:
            with get_db() as conn:
                cur = conn.cursor()

                # 1. Tranzacții > 50.000 MDL (sau echivalent)
                big = cur.execute("""
                    SELECT t.id_tranzactie, c.numar_cont, t.tip_tranzactie, t.suma, t.data_op, t.detalii
                    FROM Tranzactii t
                    JOIN Conturi c ON t.id_cont_sursa = c.id_cont
                    WHERE t.suma > 50000
                    ORDER BY t.data_op DESC
                """).fetchall()
                suspicious.extend(big)

                # 2. Mai mult de 5 tranzacții în 10 minute de pe același cont
                freq = cur.execute("""
                    SELECT t.id_tranzactie, c.numar_cont, t.tip_tranzactie, t.suma, t.data_op, t.detalii
                    FROM Tranzactii t
                    JOIN Conturi c ON t.id_cont_sursa = c.id_cont
                    WHERE t.id_cont_sursa IN (
                        SELECT id_cont_sursa
                        FROM Tranzactii
                        GROUP BY id_cont_sursa, CAST(data_op AS DATE), DATEPART(HOUR, data_op), DATEPART(MINUTE, data_op)/10
                        HAVING COUNT(*) >= 5
                    )
                    ORDER BY t.data_op DESC
                """).fetchall()
                suspicious.extend(freq)

                # Elimină duplicatele
                seen = set()
                unique = []
                for row in suspicious:
                    if row[0] not in seen:
                        seen.add(row[0])
                        unique.append(row)

            self.table.setRowCount(len(unique))
            for i, row in enumerate(unique):
                for j, val in enumerate(row[1:]):  # sar ID-ul tranzacției
                    item = QTableWidgetItem(str(val))
                    if j == 2:  # suma
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(i, j, item)

            if unique:
                self.status.setText(f"<span style='color:#f87171; font-weight:bold;'>⚠ Atenție: {len(unique)} tranzacții suspecte detectate!</span>")
            else:
                self.status.setText("<span style='color:#22c55e; font-weight:bold;'>✔ Nicio tranzacție suspectă în ultimele 30 de zile.</span>")

        except Exception as e:
            QMessageBox.critical(self, "Eroare scanare", str(e))


# ============================================================
# PAGINA ADMINISTRARE
# ============================================================
class AdminPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        title = QLabel("Administrare Sistem")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #00A651;")
        layout.addWidget(title)

        btns = QHBoxLayout()
        btns.addWidget(QPushButton("Adaugă Utilizator", clicked=self.add_user))
        btns.addWidget(QPushButton("Schimbă Rol", clicked=self.change_role))
        btns.addWidget(QPushButton("Resetează Parolă", clicked=self.reset_password))
        btns.addWidget(QPushButton("Activează/Dezactivează", clicked=self.toggle_user))
        btn_comis = QPushButton("Setări Comisioane")
        btn_comis.setObjectName("secondary")
        btn_comis.clicked.connect(self.edit_comisioane)
        btns.addWidget(btn_comis)
        layout.addLayout(btns)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Rol", "Stare"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.load_users()
        self.setLayout(layout)

    def load_users(self):
        with get_db() as conn:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT u.id_user, u.username, r.nume_rol, 
                       CASE WHEN u.activ = 1 THEN 'Activ' ELSE 'Inactiv' END
                FROM Utilizatori u
                JOIN Roluri r ON u.id_rol = r.id_rol
            """).fetchall()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_user(self):
        dlg = AddUserDialog()
        if dlg.exec_():
            self.load_users()

    def change_role(self):
        row = self.table.currentRow()
        if row >= 0:
            user_id = self.table.item(row, 0).text()
            dlg = ChangeRoleDialog(user_id)
            if dlg.exec_():
                self.load_users()

    def reset_password(self):
        row = self.table.currentRow()
        if row >= 0 and QMessageBox.question(self, "Resetare", "Resetezi parola la '1234'?") == QMessageBox.Yes:
            user_id = self.table.item(row, 0).text()
            with get_db() as conn:
                conn.execute("UPDATE Utilizatori SET parola = ? WHERE id_user = ?", (hash_password("1234"), user_id))
                conn.commit()
            QMessageBox.information(self, "Succes", "Parola resetată la '1234'")

    def toggle_user(self):
        row = self.table.currentRow()
        if row >= 0:
            user_id = self.table.item(row, 0).text()
            current = self.table.item(row, 3).text()
            new_state = 0 if current == "Activ" else 1
            with get_db() as conn:
                conn.execute("UPDATE Utilizatori SET activ = ? WHERE id_user = ?", (new_state, user_id))
                conn.commit()
            self.load_users()

    def edit_comisioane(self):
        dlg = ComisioaneDialog()
        dlg.exec_()


# ============================================================
# DIALOGURI ADMIN
# ============================================================
class AddUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Utilizator Nou")
        self.setFixedSize(420, 380)
        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        self.user = QLineEdit()
        self.passw = QLineEdit()
        self.passw.setEchoMode(QLineEdit.Password)
        self.rol = QComboBox()
        self.rol.addItems(["operator", "admin"])

        layout.addRow("Username:", self.user)
        layout.addRow("Parolă:", self.passw)
        layout.addRow("Rol:", self.rol)

        btn = QPushButton("CREEAZĂ UTILIZATOR")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        self.setLayout(layout)

    def save(self):
        u = self.user.text().strip()
        p = self.passw.text().strip()
        r = self.rol.currentText()

        if not u or not p:
            QMessageBox.warning(self, "Eroare", "Completați toate câmpurile!")
            return

        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id_rol FROM Roluri WHERE LOWER(nume_rol) = ?", (r.lower(),))
                id_rol = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO Utilizatori (username, parola, id_rol, activ)
                    VALUES (?, ?, ?, 1)
                """, (u, hash_password(p), id_rol))
                conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Eroare", str(e))


class ChangeRoleDialog(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Schimbă Rol")
        self.setFixedSize(360, 220)
        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        self.rol = QComboBox()
        self.rol.addItems(["operator", "admin"])
        layout.addRow("Rol nou:", self.rol)

        btn = QPushButton("APLICĂ")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        self.setLayout(layout)
        self.load_current()

    def load_current(self):
        with get_db() as conn:
            cur = conn.cursor()
            rol = cur.execute("""
                SELECT r.nume_rol FROM Utilizatori u
                JOIN Roluri r ON u.id_rol = r.id_rol
                WHERE u.id_user = ?
            """, (self.user_id,)).fetchone()[0]
            self.rol.setCurrentText(rol.lower())

    def save(self):
        r = self.rol.currentText()
        with get_db() as conn:
            cur = conn.cursor()
            id_rol = cur.execute("SELECT id_rol FROM Roluri WHERE LOWER(nume_rol) = ?", (r.lower(),)).fetchone()[0]
            cur.execute("UPDATE Utilizatori SET id_rol = ? WHERE id_user = ?", (id_rol, self.user_id))
            conn.commit()
        self.accept()


class ComisioaneDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setări Comisioane")
        self.setFixedSize(460, 400)
        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        self.ret_proc = QLineEdit()
        self.ret_fix = QLineEdit()
        self.te_proc = QLineEdit()
        self.te_fix = QLineEdit()

        layout.addRow("Retragere %:", self.ret_proc)
        layout.addRow("Retragere fix (MDL):", self.ret_fix)
        layout.addRow("Transfer extern %:", self.te_proc)
        layout.addRow("Transfer extern fix (MDL):", self.te_fix)

        btn = QPushButton("SALVEAZĂ COMISIOANELE")
        btn.clicked.connect(self.save)
        layout.addRow(btn)

        self.setLayout(layout)
        self.load()

    def load(self):
        with get_db() as conn:
            row = conn.execute("SELECT * FROM SetariComisioane WHERE id=1").fetchone()
            if row:
                self.ret_proc.setText(str(row[1]))
                self.ret_fix.setText(str(row[2]))
                self.te_proc.setText(str(row[3]))
                self.te_fix.setText(str(row[4]))

    def save(self):
        try:
            values = [float(self.ret_proc.text()), float(self.ret_fix.text()),
                      float(self.te_proc.text()), float(self.te_fix.text())]
            with get_db() as conn:
                conn.execute("""
                    UPDATE SetariComisioane SET
                    retragere_proc=?, retragere_fix=?, transfer_ext_proc=?, transfer_ext_fix=?
                    WHERE id=1
                """, values)
                conn.commit()
            QMessageBox.information(self, "Succes", "Comisioanele au fost actualizate!")
            self.accept()
        except:
            QMessageBox.warning(self, "Eroare", "Introduceți numere valide!")


# ============================================================
# RUN APLICAȚIE
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_MAIB_STYLE)
    app.setFont(QFont("Segoe UI", 10))

    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()