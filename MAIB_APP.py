# ============================================================
# MAIB BANKING SYSTEM - SINGLE FILE VERSION (Optimized & Restyled)
# PyQt5 + MSSQL + All modules (Clients, Accounts, Transactions,
# Reports, Risk, Admin) in a SINGLE RUNNABLE FILE.
#
# LOGIC IS UNCHANGED – only visual / UI styling was improved.
# ============================================================

import sys
import pyodbc
from datetime import datetime
import hashlib  # For password hashing
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog,
    QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QTabWidget,
    QGridLayout, QFormLayout, QHeaderView, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor


# ============================================================
# DATABASE CONNECTION (MSSQL) - Use context manager for auto-close
# ============================================================
def get_db_connection():
    return pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-1BQ40CT;"
        "Database=MAIB_DB;"
        "Trusted_Connection=yes;"
    )


# ============================================================
# UTILITY: Hash Password
# ============================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
# SIMPLE MODELS (PYTHON OBJECTS)
# ============================================================
class Client:
    def __init__(self, id, nume, prenume, idnp, tel, email, adresa):
        self.id = id
        self.nume = nume
        self.prenume = prenume
        self.idnp = idnp
        self.tel = tel
        self.email = email
        self.adresa = adresa


class Account:
    def __init__(self, idc, nume, prenume, cont, tip, moneda, sold):
        self.idc = idc
        self.nume = nume
        self.prenume = prenume
        self.cont = cont
        self.tip = tip
        self.moneda = moneda
        self.sold = sold


class Transaction:
    def __init__(self, tip, suma, comision, metoda, data):
        self.tip = tip
        self.suma = suma
        self.comision = comision
        self.metoda = metoda
        self.data = data


# ============================================================
# LOGIN WINDOW (Premium UI)
# ============================================================
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAIB - Autentificare")
        self.setFixedSize(380, 280)

        # Modern gradient + glass card look
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #141E30,
                    stop:1 #243B55
                );
            }
            QLabel#titleLabel {
                font-size: 20px;
                font-weight: 700;
                color: #ffffff;
            }
            QLabel {
                font-size: 13px;
                color: #e0e6f0;
            }
            QLineEdit {
                padding: 8px 10px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 40);
                background: rgba(15, 23, 42, 200);
                color: #e5e7eb;
                selection-background-color: #38bdf8;
            }
            QLineEdit:focus {
                border: 1px solid #38bdf8;
                background: rgba(15, 23, 42, 230);
            }
            QPushButton {
                background-color: #38bdf8;
                color: #0f172a;
                padding: 9px 14px;
                border-radius: 10px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #0ea5e9;
            }
        """)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(0)

        # Card container
        card = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(18)

        card.setStyleSheet("""
            QWidget {
                background: rgba(15, 23, 42, 220);
                border-radius: 18px;
            }
        """)

        self.lblTitle = QLabel("Autentificare în Sistem MAIB")
        self.lblTitle.setObjectName("titleLabel")
        self.lblTitle.setAlignment(Qt.AlignCenter)
        self.lblTitle.setFont(QFont("Segoe UI", 16, QFont.Bold))
        card_layout.addWidget(self.lblTitle)

        self.txtUser = QLineEdit()
        self.txtUser.setPlaceholderText("Username")
        card_layout.addWidget(self.txtUser)

        self.txtPass = QLineEdit()
        self.txtPass.setPlaceholderText("Parola")
        self.txtPass.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.txtPass)

        self.btnLogin = QPushButton("LOGIN")
        card_layout.addWidget(self.btnLogin)

        card.setLayout(card_layout)
        outer_layout.addStretch()
        outer_layout.addWidget(card)
        outer_layout.addStretch()

        self.setLayout(outer_layout)

        self.btnLogin.clicked.connect(self.login)

    def login(self):
        user = self.txtUser.text().strip()
        # pwd = hash_password(self.txtPass.text().strip())  # Hash input password
        pwd = self.txtPass.text().strip()
        with get_db_connection() as conn:
            cur = conn.cursor()
            row = cur.execute("""
                SELECT u.username, r.nume_rol
                FROM Utilizatori u
                JOIN Roluri r ON u.id_rol = r.id_rol
                WHERE username=? AND parola=? AND activ=1
            """, (user, pwd)).fetchone()

        if not row:
            QMessageBox.warning(self, "Eroare", "Date incorecte!")
            return

        self.main = MainWindow(username=row[0], role=row[1])
        self.main.show()
        self.close()


# ============================================================
# MAIN WINDOW (TAB SYSTEM with Premium UI)
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self, username, role):
        super().__init__()
        self.setWindowTitle("MAIB Banking System")
        self.setGeometry(250, 100, 1150, 740)

        self.username = username
        self.role = role

        # ----- Top bar -----
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(12)

        self.lblTitle = QLabel("MAIB Banking System")
        self.lblTitle.setFont(QFont("Segoe UI", 16, QFont.Bold))
        top.addWidget(self.lblTitle)

        top.addStretch()

        self.lblUser = QLabel(f"Utilizator: {self.username}")
        self.lblUser.setFont(QFont("Segoe UI", 11))
        top.addWidget(self.lblUser)

        self.btnTheme = QPushButton("🌙")
        self.btnTheme.setFixedWidth(46)
        self.btnTheme.setToolTip("Schimbă tema (light / dark)")
        top.addWidget(self.btnTheme)

        # ----- Tabs -----
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setMovable(False)
        self.tabs.setDocumentMode(True)

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1f2933;
                border-radius: 14px;
                background: #020617;
            }
            QTabBar::tab {
                height: 44px;
                width: 170px;
                padding: 10px 12px;
                margin: 2px 0;
                border-radius: 10px;
                color: #e5e7eb;
                background: transparent;
                text-align: left;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10b981,
                    stop:1 #22c55e
                );
                color: #0b1120;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background: rgba(148, 163, 184, 60);
            }
        """)

        self.pageClients = ClientsPage()
        self.pageAccounts = AccountsPage()
        self.pageTransactions = TransactionsPage()
        self.pageReports = ReportsPage()
        self.pageRisk = RiskPage()
        self.pageAdmin = AdminPage()

        self.tabs.addTab(self.pageClients, "Clienți")
        self.tabs.addTab(self.pageAccounts, "Conturi")
        self.tabs.addTab(self.pageTransactions, "Tranzacții")
        self.tabs.addTab(self.pageReports, "Rapoarte")
        self.tabs.addTab(self.pageRisk, "Risc")

        if self.role == "admin":
            self.tabs.addTab(self.pageAdmin, "Administrare")

        # ----- Main layout -----
        main = QVBoxLayout()
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(12)
        main.addLayout(top)
        main.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main)
        self.setCentralWidget(container)

        # Connect theme switch
        self.darkMode = False
        self.btnTheme.clicked.connect(self.toggleTheme)
        self.applyLightTheme()  # Default theme

    def toggleTheme(self):
        if self.darkMode:
            self.applyLightTheme()
            self.darkMode = False
            self.btnTheme.setText("🌙")
        else:
            self.applyDarkTheme()
            self.darkMode = True
            self.btnTheme.setText("☀️")

    def applyLightTheme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #e5e7eb;
            }
            QWidget {
                font-family: "Segoe UI";
                font-size: 11px;
            }
            QLabel {
                color: #111827;
            }
            QLineEdit, QComboBox {
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px 8px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #38bdf8;
            }
            QPushButton {
                background: #0ea5e9;
                color: #0b1120;
                border-radius: 8px;
                padding: 7px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #0284c7;
            }
            QPushButton#dangerButton {
                background: #ef4444;
                color: #f9fafb;
            }
            QPushButton#dangerButton:hover {
                background: #b91c1c;
            }
            QPushButton#secondaryButton {
                background: #111827;
                color: #e5e7eb;
            }
            QPushButton#secondaryButton:hover {
                background: #020617;
            }
            QTableWidget {
                background: #f9fafb;
                gridline-color: #cbd5e1;
                border-radius: 10px;
            }
            QHeaderView::section {
                background: #e5e7eb;
                padding: 6px;
                border: none;
                font-weight: 600;
            }
        """)

    def applyDarkTheme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #020617;
            }
            QWidget {
                font-family: "Segoe UI";
                font-size: 11px;
                color: #e5e7eb;
            }
            QLabel {
                color: #e5e7eb;
            }
            QLineEdit, QComboBox {
                background: #020617;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 6px 8px;
                color: #e5e7eb;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #22c55e;
            }
            QPushButton {
                background: qlineargradient(
                    x1:0,y1:0, x2:1,y2:1,
                    stop:0 #22c55e,
                    stop:1 #16a34a
                );
                color: #020617;
                border-radius: 9px;
                padding: 7px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #22c55e;
            }
            QPushButton#dangerButton {
                background: #ef4444;
                color: #f9fafb;
            }
            QPushButton#dangerButton:hover {
                background: #b91c1c;
            }
            QPushButton#secondaryButton {
                background: #111827;
                color: #e5e7eb;
            }
            QPushButton#secondaryButton:hover {
                background: #020617;
            }
            QTableWidget {
                background: #020617;
                color: #e5e7eb;
                gridline-color: #1f2937;
                border-radius: 10px;
            }
            QHeaderView::section {
                background: #111827;
                color: #e5e7eb;
                padding: 6px;
                border: none;
                font-weight: 600;
            }
        """)


# ============================================================
# PAGE: CLIENTS (Improved UI & Validation)
# ============================================================
class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search
        searchLayout = QHBoxLayout()
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("Caută după nume, prenume, IDNP, telefon...")
        searchLayout.addWidget(self.searchBox)

        self.btnAdd = QPushButton("Adaugă Client")
        searchLayout.addWidget(self.btnAdd)

        layout.addLayout(searchLayout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nume", "Prenume", "IDNP", "Telefon", "Email", "Adresă"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Buttons
        btnLayout = QHBoxLayout()
        self.btnEdit = QPushButton("Editează")
        self.btnDelete = QPushButton("Șterge")
        self.btnDelete.setObjectName("dangerButton")
        btnLayout.addWidget(self.btnEdit)
        btnLayout.addWidget(self.btnDelete)

        layout.addLayout(btnLayout)
        self.setLayout(layout)

        self.load_clients()

        # Events
        self.searchBox.textChanged.connect(self.load_clients)
        self.btnAdd.clicked.connect(self.add_client)
        self.btnEdit.clicked.connect(self.edit_client)
        self.btnDelete.clicked.connect(self.delete_client)

    def load_clients(self):
        search = f"%{self.searchBox.text()}%"
        with get_db_connection() as conn:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT id_client, nume, prenume, idnp, telefon, email, adresa
                FROM Clienti
                WHERE activ=1 AND (
                    nume LIKE ? OR prenume LIKE ? OR idnp LIKE ? OR telefon LIKE ?
                )
            """, (search, search, search, search)).fetchall()

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, val in enumerate(r):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled)  # Read-only
                self.table.setItem(i, j, item)

    def add_client(self):
        dialog = AddClientDialog()
        if dialog.exec_():
            self.load_clients()

    def edit_client(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eroare", "Selectează un client!")
            return

        id_client = int(self.table.item(row, 0).text())
        dialog = EditClientDialog(id_client)
        if dialog.exec_():
            self.load_clients()

    def delete_client(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eroare", "Selectează un client!")
            return

        reply = QMessageBox.question(
            self,
            "Confirmare",
            "Sigur vrei să ștergi acest client?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            id_client = int(self.table.item(row, 0).text())
            with get_db_connection() as conn:
                conn.cursor().execute("UPDATE Clienti SET activ=0 WHERE id_client=?", (id_client,))
                conn.commit()
            self.load_clients()


# ============================================================
# DIALOG: ADD CLIENT (Improved with Validation)
# ============================================================
class AddClientDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă Client")
        self.setFixedSize(420, 410)
        self.setStyleSheet("""
            QDialog {
                background: #0f172a;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #1f2937;
                border-radius: 8px;
                background: #020617;
                color: #e5e7eb;
            }
            QLineEdit:focus {
                border: 1px solid #22c55e;
            }
            QPushButton {
                background-color: #22c55e;
                color: #020617;
                padding: 10px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QLabel {
                color: #e5e7eb;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.txtNume = QLineEdit()
        self.txtNume.setPlaceholderText("Nume")
        self.txtPrenume = QLineEdit()
        self.txtPrenume.setPlaceholderText("Prenume")
        self.txtIDNP = QLineEdit()
        self.txtIDNP.setPlaceholderText("IDNP (13 cifre)")
        self.txtTel = QLineEdit()
        self.txtTel.setPlaceholderText("Telefon")
        self.txtEmail = QLineEdit()
        self.txtEmail.setPlaceholderText("Email")
        self.txtAdr = QLineEdit()
        self.txtAdr.setPlaceholderText("Adresă")

        layout.addRow("Nume:", self.txtNume)
        layout.addRow("Prenume:", self.txtPrenume)
        layout.addRow("IDNP:", self.txtIDNP)
        layout.addRow("Telefon:", self.txtTel)
        layout.addRow("Email:", self.txtEmail)
        layout.addRow("Adresă:", self.txtAdr)

        self.btnSave = QPushButton("Salvează")
        layout.addRow(self.btnSave)

        self.setLayout(layout)
        self.btnSave.clicked.connect(self.save)

    def save(self):
        nume = self.txtNume.text().strip()
        prenume = self.txtPrenume.text().strip()
        idnp = self.txtIDNP.text().strip()
        tel = self.txtTel.text().strip()
        email = self.txtEmail.text().strip()
        adr = self.txtAdr.text().strip()

        if not all([nume, prenume, idnp, tel, email, adr]):
            QMessageBox.warning(self, "Eroare", "Toate câmpurile sunt obligatorii!")
            return

        if len(idnp) != 13 or not idnp.isdigit():
            QMessageBox.warning(self, "Eroare", "IDNP trebuie să aibă 13 cifre!")
            return

        with get_db_connection() as conn:
            cur = conn.cursor()
            existing = cur.execute("SELECT COUNT(*) FROM Clienti WHERE idnp=?", (idnp,)).fetchone()[0]
            if existing > 0:
                QMessageBox.warning(self, "Eroare", "IDNP deja există!")
                return

            cur.execute("""
                INSERT INTO Clienti(nume, prenume, idnp, telefon, email, adresa, activ)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (nume, prenume, idnp, tel, email, adr))
            conn.commit()

        self.accept()


# ============================================================
# DIALOG: EDIT CLIENT
# ============================================================
class EditClientDialog(QDialog):
    def __init__(self, id_client):
        super().__init__()
        self.id_client = id_client
        self.setWindowTitle("Editează Client")
        self.setFixedSize(420, 320)
        self.setStyleSheet("""
            QDialog {
                background: #0f172a;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #1f2937;
                border-radius: 8px;
                background: #020617;
                color: #e5e7eb;
            }
            QLineEdit:focus {
                border: 1px solid #22c55e;
            }
            QPushButton {
                background-color: #facc15;
                color: #0f172a;
                padding: 10px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #eab308;
            }
            QLabel {
                color: #e5e7eb;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.txtNume = QLineEdit()
        self.txtPrenume = QLineEdit()
        self.txtTel = QLineEdit()
        self.txtEmail = QLineEdit()
        self.txtAdr = QLineEdit()

        layout.addRow("Nume:", self.txtNume)
        layout.addRow("Prenume:", self.txtPrenume)
        layout.addRow("Telefon:", self.txtTel)
        layout.addRow("Email:", self.txtEmail)
        layout.addRow("Adresă:", self.txtAdr)

        self.btnSave = QPushButton("Salvează")
        layout.addRow(self.btnSave)

        self.setLayout(layout)
        self.load_data()
        self.btnSave.clicked.connect(self.save)

    def load_data(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            r = cur.execute("""
                SELECT nume, prenume, telefon, email, adresa
                FROM Clienti WHERE id_client=?
            """, (self.id_client,)).fetchone()

        if r:
            self.txtNume.setText(r[0])
            self.txtPrenume.setText(r[1])
            self.txtTel.setText(r[2])
            self.txtEmail.setText(r[3])
            self.txtAdr.setText(r[4])

    def save(self):
        nume = self.txtNume.text().strip()
        prenume = self.txtPrenume.text().strip()
        tel = self.txtTel.text().strip()
        email = self.txtEmail.text().strip()
        adr = self.txtAdr.text().strip()

        if not all([nume, prenume, tel, email, adr]):
            QMessageBox.warning(self, "Eroare", "Toate câmpurile sunt obligatorii!")
            return

        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE Clienti SET nume=?, prenume=?, telefon=?, email=?, adresa=?
                WHERE id_client=?
            """, (nume, prenume, tel, email, adr, self.id_client))
            conn.commit()

        self.accept()


# ============================================================
# PAGE: ACCOUNTS (Improved)
# ============================================================
class AccountsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search
        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Caută cont, nume client...")
        top.addWidget(self.search)

        self.btnAdd = QPushButton("Adaugă Cont")
        top.addWidget(self.btnAdd)

        layout.addLayout(top)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID Cont", "Nume", "Prenume",
            "Număr Cont", "Tip", "Moneda", "Sold"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Buttons
        bottom = QHBoxLayout()
        self.btnEdit = QPushButton("Editează")
        self.btnDelete = QPushButton("Dezactivează")
        self.btnDelete.setObjectName("dangerButton")
        bottom.addWidget(self.btnEdit)
        bottom.addWidget(self.btnDelete)
        layout.addLayout(bottom)

        self.setLayout(layout)

        self.load_accounts()

        self.search.textChanged.connect(self.load_accounts)
        self.btnAdd.clicked.connect(self.add_account)
        self.btnEdit.clicked.connect(self.edit_account)
        self.btnDelete.clicked.connect(self.delete_account)

    def load_accounts(self):
        s = f"%{self.search.text()}%"

        with get_db_connection() as conn:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT c.id_cont, cl.nume, cl.prenume,
                       c.numar_cont, c.tip_cont, c.moneda, c.sold
                FROM Conturi c
                JOIN Clienti cl ON c.id_client = cl.id_client
                WHERE c.activ = 1 AND (
                    cl.nume LIKE ? OR cl.prenume LIKE ? OR c.numar_cont LIKE ?
                )
            """, (s, s, s)).fetchall()

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, val in enumerate(r):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(i, j, item)

    def add_account(self):
        dialog = AddAccountDialog()
        if dialog.exec_():
            self.load_accounts()

    def edit_account(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eroare", "Selectează un cont!")
            return

        id_cont = int(self.table.item(row, 0).text())
        dialog = EditAccountDialog(id_cont)
        if dialog.exec_():
            self.load_accounts()

    def delete_account(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eroare", "Selectează un cont!")
            return

        reply = QMessageBox.question(
            self,
            "Confirmare",
            "Sigur vrei să dezactivezi acest cont?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            id_cont = int(self.table.item(row, 0).text())
            with get_db_connection() as conn:
                conn.cursor().execute("UPDATE Conturi SET activ=0 WHERE id_cont=?", (id_cont,))
                conn.commit()
            self.load_accounts()


# ============================================================
# DIALOG: ADD ACCOUNT (Validation added)
# ============================================================
class AddAccountDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă Cont")
        self.setFixedSize(420, 370)
        self.setStyleSheet("""
            QDialog {
                background: #020617;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #1f2937;
                border-radius: 8px;
                background: #0b1120;
                color: #e5e7eb;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #22c55e;
            }
            QPushButton {
                background-color: #22c55e;
                color: #020617;
                padding: 10px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QLabel {
                color: #e5e7eb;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.txtIdClient = QLineEdit()
        self.txtIdClient.setPlaceholderText("ID Client (existent)")
        layout.addRow("ID Client:", self.txtIdClient)

        self.txtNumar = QLineEdit()
        self.txtNumar.setPlaceholderText("Număr Cont (IBAN/format MAIB)")
        layout.addRow("Număr Cont:", self.txtNumar)

        self.cmbTip = QComboBox()
        self.cmbTip.addItems(["Curent", "Economii", "Credit"])
        layout.addRow("Tip Cont:", self.cmbTip)

        self.cmbMoneda = QComboBox()
        self.cmbMoneda.addItems(["MDL", "EUR", "USD", "RON"])
        layout.addRow("Monedă:", self.cmbMoneda)

        self.txtSold = QLineEdit()
        self.txtSold.setPlaceholderText("Sold inițial (ex: 0.00)")
        layout.addRow("Sold:", self.txtSold)

        self.btnSave = QPushButton("Salvează")
        layout.addRow(self.btnSave)

        self.setLayout(layout)
        self.btnSave.clicked.connect(self.save)

    def save(self):
        try:
            id_client = int(self.txtIdClient.text().strip())
            numar = self.txtNumar.text().strip()
            tip = self.cmbTip.currentText()
            moneda = self.cmbMoneda.currentText()
            sold = float(self.txtSold.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Eroare", "Date invalide! Verifică ID client și sold.")
            return

        if not numar:
            QMessageBox.warning(self, "Eroare", "Număr cont obligatoriu!")
            return

        with get_db_connection() as conn:
            cur = conn.cursor()
            # Check if client exists
            client_exists = cur.execute(
                "SELECT COUNT(*) FROM Clienti WHERE id_client=? AND activ=1",
                (id_client,)
            ).fetchone()[0]
            if client_exists == 0:
                QMessageBox.warning(self, "Eroare", "Clientul nu există!")
                return

            # Check unique account number
            acc_exists = cur.execute(
                "SELECT COUNT(*) FROM Conturi WHERE numar_cont=?",
                (numar,)
            ).fetchone()[0]
            if acc_exists > 0:
                QMessageBox.warning(self, "Eroare", "Număr cont deja există!")
                return

            cur.execute("""
                INSERT INTO Conturi(id_client, numar_cont, tip_cont, moneda, sold, activ)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (id_client, numar, tip, moneda, sold))
            conn.commit()

        self.accept()


# ============================================================
# DIALOG: EDIT ACCOUNT
# ============================================================
class EditAccountDialog(QDialog):
    def __init__(self, id_cont):
        super().__init__()
        self.id = id_cont
        self.setWindowTitle("Editează Cont")
        self.setFixedSize(380, 260)
        self.setStyleSheet("""
            QDialog {
                background: #020617;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #1f2937;
                border-radius: 8px;
                background: #0b1120;
                color: #e5e7eb;
            }
            QComboBox:focus {
                border: 1px solid #22c55e;
            }
            QPushButton {
                background-color: #facc15;
                color: #0f172a;
                padding: 10px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #eab308;
            }
            QLabel {
                color: #e5e7eb;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.cmbTip = QComboBox()
        self.cmbTip.addItems(["Curent", "Economii", "Credit"])
        layout.addRow("Tip Cont:", self.cmbTip)

        self.cmbMoneda = QComboBox()
        self.cmbMoneda.addItems(["MDL", "EUR", "USD", "RON"])
        layout.addRow("Monedă:", self.cmbMoneda)

        self.btnSave = QPushButton("Salvează")
        layout.addRow(self.btnSave)

        self.setLayout(layout)

        self.load_data()
        self.btnSave.clicked.connect(self.save)

    def load_data(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            row = cur.execute("""
                SELECT tip_cont, moneda FROM Conturi WHERE id_cont=?
            """, (self.id,)).fetchone()

        if row:
            self.cmbTip.setCurrentText(row[0])
            self.cmbMoneda.setCurrentText(row[1])

    def save(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE Conturi SET tip_cont=?, moneda=? WHERE id_cont=?
            """, (self.cmbTip.currentText(), self.cmbMoneda.currentText(), self.id))
            conn.commit()
        self.accept()


# ============================================================
# PAGE: TRANSACTIONS (Improved with Validation & Bug Fixes)
# ============================================================
class TransactionsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        self.cmbTip = QComboBox()
        self.cmbTip.addItems(["Depunere", "Retragere", "Transfer Intern", "Transfer Extern"])
        layout.addRow("Tip tranzacție:", self.cmbTip)

        self.txtSursa = QLineEdit()
        self.txtSursa.setPlaceholderText("Număr cont sursă")
        layout.addRow("Cont Sursă:", self.txtSursa)

        self.txtDest = QLineEdit()
        self.txtDest.setPlaceholderText("Număr cont destinație (doar la transfer)")
        layout.addRow("Cont Destinație:", self.txtDest)

        self.txtSuma = QLineEdit()
        self.txtSuma.setPlaceholderText("Sumă (ex: 100.00)")
        layout.addRow("Sumă:", self.txtSuma)

        self.cmbMetoda = QComboBox()
        self.cmbMetoda.addItems(["Cash", "Card", "Online"])
        layout.addRow("Metoda plății:", self.cmbMetoda)

        self.txtDetalii = QLineEdit()
        self.txtDetalii.setPlaceholderText("Detalii (opțional)")
        layout.addRow("Detalii:", self.txtDetalii)

        self.btnProceseaza = QPushButton("Procesează")
        layout.addRow(self.btnProceseaza)

        self.setLayout(layout)

        self.btnProceseaza.clicked.connect(self.process)

    def process(self):
        tip = self.cmbTip.currentText()
        cont_sursa = self.txtSursa.text().strip()
        cont_dest = self.txtDest.text().strip()
        metoda = self.cmbMetoda.currentText()
        detalii = self.txtDetalii.text().strip()

        try:
            suma = float(self.txtSuma.text().strip())
            if suma <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Eroare", "Sumă invalidă! Trebuie să fie un număr pozitiv.")
            return

        with get_db_connection() as conn:
            cur = conn.cursor()

            # Load source account
            src = cur.execute("""
                SELECT id_cont, sold, moneda FROM Conturi
                WHERE numar_cont=? AND activ=1
            """, (cont_sursa,)).fetchone()

            if not src:
                QMessageBox.warning(self, "Eroare", "Contul sursă nu există!")
                return

            id_src, sold_src, moneda_src = src

            # Load commissions
            com = cur.execute("""
                SELECT retragere_proc, retragere_fix, transfer_ext_proc, transfer_ext_fix
                FROM SetariComisioane WHERE id=1
            """).fetchone()

            if not com:
                QMessageBox.warning(self, "Eroare", "Setări comisioane lipsă!")
                return

            ret_proc, ret_fix, te_proc, te_fix = com

            if tip == "Depunere":
                new_balance = sold_src + suma
                cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (new_balance, id_src))
                cur.execute("""
                    INSERT INTO Tranzactii(id_cont_sursa, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                    VALUES (?, ?, ?, ?, 0, ?, ?)
                """, (id_src, tip, suma, moneda_src, metoda, detalii))
                conn.commit()
                QMessageBox.information(self, "Succes", "Depunere efectuată!")
                return

            if tip == "Retragere":
                comision = suma * (ret_proc / 100) + ret_fix
                total = suma + comision
                if sold_src < total:
                    QMessageBox.warning(self, "Eroare", "Fonduri insuficiente!")
                    return
                new_balance = sold_src - total
                cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (new_balance, id_src))
                cur.execute("""
                    INSERT INTO Tranzactii(id_cont_sursa, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (id_src, tip, suma, moneda_src, comision, metoda, detalii))
                conn.commit()
                QMessageBox.information(self, "Succes", "Retragere efectuată!")
                return

            if tip == "Transfer Intern":
                dest = cur.execute("""
                    SELECT id_cont, sold, moneda FROM Conturi
                    WHERE numar_cont=? AND activ=1
                """, (cont_dest,)).fetchone()
                if not dest:
                    QMessageBox.warning(self, "Eroare", "Cont destinație inexistent!")
                    return
                id_dest, sold_dest, moneda_dest = dest
                if moneda_src != moneda_dest:
                    QMessageBox.warning(self, "Eroare", "Monede diferite! Transfer intern doar în aceeași monedă.")
                    return
                if sold_src < suma:
                    QMessageBox.warning(self, "Eroare", "Fonduri insuficiente la sursă!")
                    return
                cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (sold_src - suma, id_src))
                cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (sold_dest + suma, id_dest))
                cur.execute("""
                    INSERT INTO Tranzactii(id_cont_sursa, id_cont_destinatie, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                    VALUES (?, ?, ?, ?, ?, 0, ?, ?)
                """, (id_src, id_dest, tip, suma, moneda_src, metoda, detalii))
                conn.commit()
                QMessageBox.information(self, "Succes", "Transfer intern realizat!")
                return

            if tip == "Transfer Extern":
                comision = suma * (te_proc / 100) + te_fix
                total = suma + comision
                if sold_src < total:
                    QMessageBox.warning(self, "Eroare", "Fonduri insuficiente!")
                    return
                new_balance = sold_src - total
                cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (new_balance, id_src))
                cur.execute("""
                    INSERT INTO Tranzactii(id_cont_sursa, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (id_src, tip, suma, moneda_src, comision, metoda, detalii))
                conn.commit()
                QMessageBox.information(self, "Succes", "Transfer extern efectuat!")
                return


# ============================================================
# PAGE: REPORTS
# ============================================================
class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        form = QFormLayout()
        self.txtCont = QLineEdit()
        self.txtCont.setPlaceholderText("Introdu numărul de cont...")
        form.addRow("Număr de cont:", self.txtCont)

        self.txtStart = QLineEdit()
        self.txtStart.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Data început:", self.txtStart)

        self.txtEnd = QLineEdit()
        self.txtEnd.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Data sfârșit:", self.txtEnd)

        layout.addLayout(form)

        self.btnGen = QPushButton("Generează Raport")
        layout.addWidget(self.btnGen)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Tip", "Sumă", "Comision", "Metoda", "Data", "Detalii"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.lblInfo = QLabel("")
        self.lblInfo.setWordWrap(True)
        layout.addWidget(self.lblInfo)

        self.setLayout(layout)

        self.btnGen.clicked.connect(self.gen_report)

    def gen_report(self):
        cont = self.txtCont.text().strip()
        start = self.txtStart.text().strip()
        end = self.txtEnd.text().strip()

        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Eroare", "Format dată invalid! Folosește YYYY-MM-DD.")
            return

        with get_db_connection() as conn:
            cur = conn.cursor()

            acc = cur.execute("""
                SELECT id_cont, sold, moneda
                FROM Conturi
                WHERE numar_cont=? AND activ=1
            """, (cont,)).fetchone()

            if not acc:
                QMessageBox.warning(self, "Eroare", "Contul nu există!")
                return

            id_cont, sold, moneda = acc

            rows = cur.execute("""
                SELECT tip_tranzactie, suma, comision,
                       metoda_plata, data_op, detalii
                FROM Tranzactii
                WHERE id_cont_sursa=? AND
                      data_op BETWEEN ? AND ?
                ORDER BY data_op DESC
            """, (id_cont, start, end + " 23:59:59")).fetchall()

        self.table.setRowCount(len(rows))

        total_in = 0
        total_out = 0
        total_com = 0

        for i, r in enumerate(rows):
            tip, suma, comision, metoda, data, detalii = r
            if tip == "Depunere":
                total_in += suma
            else:
                total_out += suma
            total_com += comision

            values = [tip, str(suma), str(comision), metoda, str(data), detalii or ""]
            for j, v in enumerate(values):
                self.table.setItem(i, j, QTableWidgetItem(v))

        summary = f"""
<b>Sold curent:</b> {sold:.2f} {moneda}<br>
<b>Total intrări:</b> {total_in:.2f} {moneda}<br>
<b>Total ieșiri:</b> {total_out:.2f} {moneda}<br>
<b>Total comisioane:</b> {total_com:.2f} {moneda}<br>
<b>Număr tranzacții:</b> {len(rows)}
"""
        self.lblInfo.setText(summary)


# ============================================================
# PAGE: RISK / AML (Improved Query)
# ============================================================
class RiskPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        self.btnScan = QPushButton("Scanează Tranzacții Suspecte")
        layout.addWidget(self.btnScan)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID Tranzacție", "ID Cont", "Tip", "Sumă", "Data"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.lblStatus = QLabel("")
        layout.addWidget(self.lblStatus)

        self.setLayout(layout)

        self.btnScan.clicked.connect(self.scan_risk)

    def scan_risk(self):
        with get_db_connection() as conn:
            cur = conn.cursor()

            suspicious = []

            # RULE 1: Transacții > 50.000
            big = cur.execute("""
                SELECT id_tranzactie, id_cont_sursa, tip_tranzactie, suma, data_op
                FROM Tranzactii
                WHERE suma > 50000
            """).fetchall()
            suspicious.extend(big)

            # RULE 2: 3+ tranzacții în 5 minute
            frequent_conts = cur.execute("""
                SELECT id_cont_sursa
                FROM Tranzactii
                GROUP BY id_cont_sursa, CAST(data_op AS DATE),
                         DATEPART(HOUR, data_op), DATEPART(MINUTE, data_op) / 5
                HAVING COUNT(*) >= 3
            """).fetchall()

            for row in frequent_conts:
                cont_id = row[0]
                txs = cur.execute("""
                    SELECT id_tranzactie, id_cont_sursa, tip_tranzactie, suma, data_op
                    FROM Tranzactii
                    WHERE id_cont_sursa=?
                """, (cont_id,)).fetchall()
                suspicious.extend(txs)

            # Remove duplicates
            unique = {row[0]: row for row in suspicious}.values()

        self.table.setRowCount(len(unique))
        for i, r in enumerate(unique):
            for j, val in enumerate(r):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

        if len(unique) == 0:
            self.lblStatus.setText("<b>Nicio tranzacție suspectă detectată.</b>")
        else:
            self.lblStatus.setText(f"<b>Au fost detectate {len(unique)} tranzacții suspecte!</b>")


# ============================================================
# PAGE: ADMINISTRARE
# ============================================================
class AdminPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        layout.addWidget(QLabel("<h3>Administrare Utilizatori & Setări</h3>"))

        btns = QHBoxLayout()
        self.btnAdd = QPushButton("Adaugă utilizator")
        self.btnEdit = QPushButton("Schimbă rol")
        self.btnReset = QPushButton("Resetează parolă")
        self.btnToggle = QPushButton("Activează / Dezactivează")
        self.btnToggle.setObjectName("secondaryButton")
        self.btnComisioane = QPushButton("Setări comisioane")

        btns.addWidget(self.btnAdd)
        btns.addWidget(self.btnEdit)
        btns.addWidget(self.btnReset)
        btns.addWidget(self.btnToggle)
        btns.addWidget(self.btnComisioane)

        layout.addLayout(btns)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Rol", "Activ"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.lblStatus = QLabel("")
        layout.addWidget(self.lblStatus)

        self.setLayout(layout)

        self.load_users()

        self.btnAdd.clicked.connect(self.add_user)
        self.btnEdit.clicked.connect(self.edit_user)
        self.btnReset.clicked.connect(self.reset_password)
        self.btnToggle.clicked.connect(self.toggle_user)
        self.btnComisioane.clicked.connect(self.edit_comisions)

    def load_users(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            rows = cur.execute("""
                SELECT u.id_user, u.username, r.nume_rol, u.activ
                FROM Utilizatori u
                JOIN Roluri r ON u.id_rol = r.id_rol
            """).fetchall()

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, v in enumerate(r):
                item = QTableWidgetItem(str(v))
                item.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(i, j, item)

    def add_user(self):
        dialog = AddUserDialog()
        if dialog.exec_():
            self.load_users()

    def edit_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eroare", "Selectează un utilizator!")
            return

        id_user = int(self.table.item(row, 0).text())
        dialog = EditRoleDialog(id_user)
        if dialog.exec_():
            self.load_users()

    def reset_password(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eroare", "Selectează un utilizator!")
            return

        reply = QMessageBox.question(
            self,
            "Confirmare",
            "Sigur vrei să resetezi parola la '1234'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            id_user = int(self.table.item(row, 0).text())
            with get_db_connection() as conn:
                conn.cursor().execute("""
                    UPDATE Utilizatori SET parola=? WHERE id_user=?
                """, (hash_password('1234'), id_user))
                conn.commit()
            self.lblStatus.setText("<b>Parola a fost resetată la '1234'.</b>")

    def toggle_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Eroare", "Selectează un utilizator!")
            return

        id_user = int(self.table.item(row, 0).text())
        active = int(self.table.item(row, 3).text())

        new_state = 0 if active == 1 else 1

        with get_db_connection() as conn:
            conn.cursor().execute("""
                UPDATE Utilizatori SET activ=? WHERE id_user=?
            """, (new_state, id_user))
            conn.commit()

        self.load_users()

    def edit_comisions(self):
        dialog = EditComisionDialog()
        dialog.exec_()


# ============================================================
# DIALOG: ADD USER (With Hashing)
# ============================================================
class AddUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă utilizator")
        self.setFixedSize(360, 310)
        self.setStyleSheet("""
            QDialog {
                background: #020617;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #1f2937;
                border-radius: 8px;
                background: #0b1120;
                color: #e5e7eb;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #38bdf8;
            }
            QPushButton {
                background-color: #22c55e;
                color: #020617;
                padding: 10px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QLabel {
                color: #e5e7eb;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.txtUser = QLineEdit()
        self.txtUser.setPlaceholderText("Username")
        layout.addRow("Username:", self.txtUser)

        self.txtPass = QLineEdit()
        self.txtPass.setPlaceholderText("Parola")
        self.txtPass.setEchoMode(QLineEdit.Password)
        layout.addRow("Parola:", self.txtPass)

        self.cmbRol = QComboBox()
        self.cmbRol.addItems(["admin", "operator"])
        layout.addRow("Rol:", self.cmbRol)

        self.btnSave = QPushButton("Salvează")
        layout.addRow(self.btnSave)

        self.setLayout(layout)
        self.btnSave.clicked.connect(self.save)

    def save(self):
        user = self.txtUser.text().strip()
        pwd = self.txtPass.text().strip()
        rol = self.cmbRol.currentText()

        if not user or not pwd:
            QMessageBox.warning(self, "Eroare", "Username și parola obligatorii!")
            return

        with get_db_connection() as conn:
            cur = conn.cursor()
            existing = cur.execute(
                "SELECT COUNT(*) FROM Utilizatori WHERE username=?",
                (user,)
            ).fetchone()[0]
            if existing > 0:
                QMessageBox.warning(self, "Eroare", "Username deja există!")
                return

            rid = cur.execute(
                "SELECT id_rol FROM Roluri WHERE nume_rol=?",
                (rol,)
            ).fetchone()[0]

            cur.execute("""
                INSERT INTO Utilizatori(username, parola, id_rol, activ)
                VALUES (?, ?, ?, 1)
            """, (user, hash_password(pwd), rid))
            conn.commit()

        self.accept()


# ============================================================
# DIALOG: EDIT ROLE
# ============================================================
class EditRoleDialog(QDialog):
    def __init__(self, id_user):
        super().__init__()
        self.id = id_user
        self.setWindowTitle("Schimbă rol")
        self.setFixedSize(310, 210)
        self.setStyleSheet("""
            QDialog {
                background: #020617;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #1f2937;
                border-radius: 8px;
                background: #0b1120;
                color: #e5e7eb;
            }
            QComboBox:focus {
                border: 1px solid #38bdf8;
            }
            QPushButton {
                background-color: #facc15;
                color: #0f172a;
                padding: 10px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #eab308;
            }
            QLabel {
                color: #e5e7eb;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.cmbRol = QComboBox()
        layout.addRow("Rol nou:", self.cmbRol)

        self.btnSave = QPushButton("Aplică")
        layout.addRow(self.btnSave)

        self.setLayout(layout)

        self.load_roles()
        self.btnSave.clicked.connect(self.save)

    def load_roles(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            rows = cur.execute("SELECT nume_rol FROM Roluri").fetchall()
        for r in rows:
            self.cmbRol.addItem(r[0])

    def save(self):
        role = self.cmbRol.currentText()
        with get_db_connection() as conn:
            cur = conn.cursor()
            id_rol = cur.execute(
                "SELECT id_rol FROM Roluri WHERE nume_rol=?",
                (role,)
            ).fetchone()[0]
            cur.execute("""
                UPDATE Utilizatori SET id_rol=? WHERE id_user=?
            """, (id_rol, self.id))
            conn.commit()
        self.accept()


# ============================================================
# DIALOG: EDIT TRANSACTION COMMISSIONS (Validation)
# ============================================================
class EditComisionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setări comisioane")
        self.setFixedSize(420, 320)
        self.setStyleSheet("""
            QDialog {
                background: #020617;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #1f2937;
                border-radius: 8px;
                background: #0b1120;
                color: #e5e7eb;
            }
            QLineEdit:focus {
                border: 1px solid #38bdf8;
            }
            QPushButton {
                background-color: #22c55e;
                color: #020617;
                padding: 10px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QLabel {
                color: #e5e7eb;
            }
        """)

        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.txtRetProc = QLineEdit()
        self.txtRetProc.setPlaceholderText("Retragere % (ex: 0.5)")
        layout.addRow("Retragere %:", self.txtRetProc)

        self.txtRetFix = QLineEdit()
        self.txtRetFix.setPlaceholderText("Retragere fix (ex: 3)")
        layout.addRow("Retragere fix:", self.txtRetFix)

        self.txtTEP = QLineEdit()
        self.txtTEP.setPlaceholderText("Transfer extern % (ex: 1.0)")
        layout.addRow("Transfer extern %:", self.txtTEP)

        self.txtTEF = QLineEdit()
        self.txtTEF.setPlaceholderText("Transfer extern fix (ex: 5)")
        layout.addRow("Transfer extern fix:", self.txtTEF)

        self.btnSave = QPushButton("Salvează")
        layout.addRow(self.btnSave)

        self.setLayout(layout)

        self.load_data()
        self.btnSave.clicked.connect(self.save)

    def load_data(self):
        with get_db_connection() as conn:
            cur = conn.cursor()
            row = cur.execute("""
                SELECT retragere_proc, retragere_fix, transfer_ext_proc, transfer_ext_fix
                FROM SetariComisioane WHERE id=1
            """).fetchone()

        if row:
            self.txtRetProc.setText(str(row[0]))
            self.txtRetFix.setText(str(row[1]))
            self.txtTEP.setText(str(row[2]))
            self.txtTEF.setText(str(row[3]))

    def save(self):
        try:
            ret_proc = float(self.txtRetProc.text().strip())
            ret_fix = float(self.txtRetFix.text().strip())
            te_proc = float(self.txtTEP.text().strip())
            te_fix = float(self.txtTEF.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Eroare", "Valori invalide! Trebuie să fie numere.")
            return

        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE SetariComisioane
                SET retragere_proc=?, retragere_fix=?, transfer_ext_proc=?, transfer_ext_fix=?
                WHERE id=1
            """, (ret_proc, ret_fix, te_proc, te_fix))
            conn.commit()

        QMessageBox.information(self, "Succes", "Comisioanele au fost actualizate.")
        self.accept()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
