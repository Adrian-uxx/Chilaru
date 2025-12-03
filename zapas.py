import pyodbc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog,
    QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QTabWidget
)
from PyQt5.QtCore import Qt
import sys

# ============================================================
# CONEXIUNE LA BAZA DE DATE
# ============================================================
def get_db():
    return pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-1BQ40CT;"
        "Database=MAIB_DB;"
        "Trusted_Connection=yes;"
    )

# ============================================================
# FEREASTRĂ LOGIN
# ============================================================
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAIB - Autentificare")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        lbl = QLabel("Autentificare")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        self.txtUser = QLineEdit()
        self.txtUser.setPlaceholderText("Username")
        self.txtPass = QLineEdit()
        self.txtPass.setPlaceholderText("Parola")
        self.txtPass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.txtUser)
        layout.addWidget(self.txtPass)

        self.btnLogin = QPushButton("Login")
        layout.addWidget(self.btnLogin)

        self.setLayout(layout)
        self.btnLogin.clicked.connect(self.login)

    def login(self):
        user = self.txtUser.text().strip()
        pwd = self.txtPass.text().strip()

        conn = get_db()
        cur = conn.cursor()

        row = cur.execute("""
            SELECT u.username, r.nume_rol
            FROM Utilizatori u
            JOIN Roluri r ON u.id_rol = r.id_rol
            WHERE u.username=? AND u.parola=? AND u.activ=1
        """, (user, pwd)).fetchone()

        if not row:
            QMessageBox.warning(self, "Eroare", "Username sau parolă greșită!")
            return

        self.main = MainWindow(username=row[0], role=row[1])
        self.main.show()
        self.close()

# ============================================================
# PAGINA CLIENTI
# ============================================================
class ClientsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        top = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Caută client (nume / prenume / IDNP)...")
        self.btnAdd = QPushButton("Adaugă client")
        self.btnEdit = QPushButton("Editează")
        self.btnDelete = QPushButton("Șterge")

        top.addWidget(self.search)
        top.addWidget(self.btnAdd)
        top.addWidget(self.btnEdit)
        top.addWidget(self.btnDelete)

        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nume", "Prenume", "IDNP", "Telefon", "Email", "Adresă"]
        )
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.search.textChanged.connect(self.load_clients)
        self.btnAdd.clicked.connect(self.add_client)
        self.btnEdit.clicked.connect(self.edit_client)
        self.btnDelete.clicked.connect(self.delete_client)

        self.load_clients()

    def load_clients(self):
        text = f"%{self.search.text().strip()}%"
        conn = get_db()
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT id_client, nume, prenume, idnp, telefon, email, adresa
            FROM Clienti
            WHERE activ=1 AND (nume LIKE ? OR prenume LIKE ? OR idnp LIKE ?)
        """, (text, text, text)).fetchall()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_client(self):
        dlg = AddClientDialog()
        if dlg.exec_():
            self.load_clients()

    def edit_client(self):
        r = self.table.currentRow()
        if r < 0:
            return
        id_client = int(self.table.item(r, 0).text())
        dlg = EditClientDialog(id_client)
        if dlg.exec_():
            self.load_clients()

    def delete_client(self):
        r = self.table.currentRow()
        if r < 0:
            return
        id_client = int(self.table.item(r, 0).text())
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE Clienti SET activ=0 WHERE id_client=?", (id_client,))
        conn.commit()
        self.accounts_page.load_accounts()
        self.load_clients()

class AddClientDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă client")
        self.setFixedSize(300, 260)

        layout = QVBoxLayout()
        self.txtNume = QLineEdit(); self.txtNume.setPlaceholderText("Nume")
        self.txtPrenume = QLineEdit(); self.txtPrenume.setPlaceholderText("Prenume")
        self.txtIDNP = QLineEdit(); self.txtIDNP.setPlaceholderText("IDNP (13 cifre)")
        self.txtTel = QLineEdit(); self.txtTel.setPlaceholderText("Telefon")
        self.txtEmail = QLineEdit(); self.txtEmail.setPlaceholderText("Email")
        self.txtAdr = QLineEdit(); self.txtAdr.setPlaceholderText("Adresă")

        for w in [self.txtNume, self.txtPrenume, self.txtIDNP, self.txtTel, self.txtEmail, self.txtAdr]:
            layout.addWidget(w)

        self.btnSave = QPushButton("Salvează")
        layout.addWidget(self.btnSave)
        self.setLayout(layout)

        self.btnSave.clicked.connect(self.save)

    def save(self):
        if len(self.txtIDNP.text().strip()) != 13:
            QMessageBox.warning(self, "Eroare", "IDNP trebuie să aibă 13 cifre!")
            return

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Clienti(nume, prenume, idnp, telefon, email, adresa, activ)
            VALUES (?,?,?,?,?,?,1)
        """, (
            self.txtNume.text(),
            self.txtPrenume.text(),
            self.txtIDNP.text(),
            self.txtTel.text(),
            self.txtEmail.text(),
            self.txtAdr.text()
        ))
        conn.commit()
        self.accounts_page.load_accounts()
        self.accept()

class EditClientDialog(QDialog):
    def __init__(self, id_client):
        super().__init__()
        self.id_client = id_client
        self.setWindowTitle("Editează client")
        self.setFixedSize(300, 230)

        layout = QVBoxLayout()
        self.txtNume = QLineEdit()
        self.txtPrenume = QLineEdit()
        self.txtTel = QLineEdit()
        self.txtEmail = QLineEdit()
        self.txtAdr = QLineEdit()

        for w in [self.txtNume, self.txtPrenume, self.txtTel, self.txtEmail, self.txtAdr]:
            layout.addWidget(w)

        self.btnSave = QPushButton("Salvează")
        layout.addWidget(self.btnSave)
        self.setLayout(layout)

        self.btnSave.clicked.connect(self.save)
        self.load_data()

    def load_data(self):
        conn = get_db()
        cur = conn.cursor()
        row = cur.execute("""
            SELECT nume, prenume, telefon, email, adresa
            FROM Clienti WHERE id_client=?
        """, (self.id_client,)).fetchone()
        if row:
            self.txtNume.setText(row[0])
            self.txtPrenume.setText(row[1])
            self.txtTel.setText(row[2])
            self.txtEmail.setText(row[3])
            self.txtAdr.setText(row[4])

    def save(self):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Clienti
            SET nume=?, prenume=?, telefon=?, email=?, adresa=?
            WHERE id_client=?
        """, (
            self.txtNume.text(),
            self.txtPrenume.text(),
            self.txtTel.text(),
            self.txtEmail.text(),
            self.txtAdr.text(),
            self.id_client
        ))
        conn.commit()
        self.accounts_page.load_accounts()
        self.accept()

# ============================================================
# PAGINA CONTURI
# ============================================================
class AccountsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        top = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Caută cont sau client...")
        self.btnAdd = QPushButton("Adaugă cont")
        self.btnEdit = QPushButton("Editează")
        self.btnDelete = QPushButton("Dezactivează")

        top.addWidget(self.search)
        top.addWidget(self.btnAdd)
        top.addWidget(self.btnEdit)
        top.addWidget(self.btnDelete)

        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID cont", "Nume", "Prenume", "Număr cont", "Tip", "Monedă", "Sold"]
        )
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.search.textChanged.connect(self.load_accounts)
        self.btnAdd.clicked.connect(self.add_account)
        self.btnEdit.clicked.connect(self.edit_account)
        self.btnDelete.clicked.connect(self.delete_account)

        self.load_accounts()

    def load_accounts(self):
        txt = f"%{self.search.text().strip()}%"
        conn = get_db()
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT c.id_cont, cl.nume, cl.prenume,
                   c.numar_cont, c.tip_cont, c.moneda, c.sold
            FROM Conturi c
            JOIN Clienti cl ON c.id_client = cl.id_client
            WHERE c.activ = 1
              AND (cl.nume LIKE ? OR cl.prenume LIKE ? OR c.numar_cont LIKE ?)
        """, (txt, txt, txt)).fetchall()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_account(self):
        dlg = AddAccountDialog()
        if dlg.exec_():
            self.load_accounts()

    def edit_account(self):
        r = self.table.currentRow()
        if r < 0:
            return
        id_cont = int(self.table.item(r, 0).text())
        dlg = EditAccountDialog(id_cont)
        if dlg.exec_():
            self.load_accounts()

    def delete_account(self):
        r = self.table.currentRow()
        if r < 0:
            return
        id_cont = int(self.table.item(r, 0).text())
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE Conturi SET activ=0 WHERE id_cont=?", (id_cont,))
        conn.commit()
        self.accounts_page.load_accounts()
        self.load_accounts()

class AddAccountDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă cont")
        self.setFixedSize(300, 260)

        layout = QVBoxLayout()

        self.cmbClient = QComboBox()
        layout.addWidget(QLabel("Client:"))
        layout.addWidget(self.cmbClient)

        self.txtNumar = QLineEdit(); self.txtNumar.setPlaceholderText("Număr cont")
        self.cmbTip = QComboBox(); self.cmbTip.addItems(["Curent", "Economii", "Credit"])
        self.cmbMoneda = QComboBox(); self.cmbMoneda.addItems(["MDL", "EUR", "USD"])
        self.txtSold = QLineEdit(); self.txtSold.setPlaceholderText("Sold inițial")

        for w in [self.txtNumar, self.cmbTip, self.cmbMoneda, self.txtSold]:
            layout.addWidget(w)

        self.btnSave = QPushButton("Salvează")
        layout.addWidget(self.btnSave)

        self.setLayout(layout)
        self.btnSave.clicked.connect(self.save)
        self.load_clients()

    def load_clients(self):
        conn = get_db()
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT id_client, nume, prenume FROM Clienti WHERE activ=1
        """).fetchall()
        self.cmbClient.clear()
        for r in rows:
            self.cmbClient.addItem(f"{r[0]} - {r[1]} {r[2]}", r[0])

    def save(self):
        id_client = self.cmbClient.currentData()
        if not id_client:
            QMessageBox.warning(self, "Eroare", "Nu există clienți activi!")
            return

        try:
            sold_ini = float(self.txtSold.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Eroare", "Sold invalid!")
            return

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Conturi(id_client, numar_cont, tip_cont, moneda, sold, activ)
            VALUES (?,?,?,?,?,1)
        """, (
            id_client,
            self.txtNumar.text(),
            self.cmbTip.currentText(),
            self.cmbMoneda.currentText(),
            sold_ini
        ))
        conn.commit()
        self.accounts_page.load_accounts()
        self.accept()

class EditAccountDialog(QDialog):
    def __init__(self, id_cont):
        super().__init__()
        self.id_cont = id_cont
        self.setWindowTitle("Editează cont")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        self.cmbTip = QComboBox(); self.cmbTip.addItems(["Curent", "Economii", "Credit"])
        self.cmbMoneda = QComboBox(); self.cmbMoneda.addItems(["MDL", "EUR", "USD"])

        layout.addWidget(self.cmbTip)
        layout.addWidget(self.cmbMoneda)

        self.btnSave = QPushButton("Salvează")
        layout.addWidget(self.btnSave)

        self.setLayout(layout)
        self.btnSave.clicked.connect(self.save)
        self.load_data()

    def load_data(self):
        conn = get_db()
        cur = conn.cursor()
        row = cur.execute("""
            SELECT tip_cont, moneda
            FROM Conturi WHERE id_cont=?
        """, (self.id_cont,)).fetchone()
        if row:
            self.cmbTip.setCurrentText(row[0])
            self.cmbMoneda.setCurrentText(row[1])

    def save(self):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Conturi SET tip_cont=?, moneda=?
            WHERE id_cont=?
        """, (
            self.cmbTip.currentText(),
            self.cmbMoneda.currentText(),
            self.id_cont
        ))
        conn.commit()
        self.accounts_page.load_accounts()
        self.accept()

# ============================================================
# PAGINA TRANZACȚII
# ============================================================
class TransactionsPage(QWidget):
    def __init__(self, accounts_page):
        super().__init__()
        self.accounts_page = accounts_page

        layout = QVBoxLayout()
        self.cmbTip = QComboBox()
        self.cmbTip.addItems(["Depunere", "Retragere", "Transfer intern"])

        self.txtSursa = QLineEdit(); self.txtSursa.setPlaceholderText("Număr cont sursă")
        self.txtDest = QLineEdit(); self.txtDest.setPlaceholderText("Număr cont destinație (la transfer)")
        self.txtSuma = QLineEdit(); self.txtSuma.setPlaceholderText("Sumă")
        self.btnProceseaza = QPushButton("Procesează tranzacția")

        for w in [self.cmbTip, self.txtSursa, self.txtDest, self.txtSuma, self.btnProceseaza]:
            layout.addWidget(w)

        self.setLayout(layout)
        self.btnProceseaza.clicked.connect(self.process)

    def process(self):
        conn = get_db()
        cur = conn.cursor()

        tip = self.cmbTip.currentText()
        cont_sursa = self.txtSursa.text().strip()
        cont_dest = self.txtDest.text().strip()

        try:
            suma = float(self.txtSuma.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Eroare", "Sumă invalidă!")
            return

        # cont sursă
        src = cur.execute("""
            SELECT id_cont, sold FROM Conturi
            WHERE numar_cont=? AND activ=1
        """, (cont_sursa,)).fetchone()

        if not src:
            QMessageBox.warning(self, "Eroare", "Cont sursă inexistent!")
            return

        id_src, sold_src = src
        sold_src = float(sold_src)

        # DEPUNERE
        if tip == "Depunere":
            new_balance = sold_src + suma
            cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (new_balance, id_src))
            cur.execute("""
                INSERT INTO Tranzactii(id_cont_sursa, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                VALUES (?, 'Depunere', ?, 'MDL', 0, 'Cash', 'Depunere în numerar')
            """, (id_src, suma))
            conn.commit()
            self.accounts_page.load_accounts()
            QMessageBox.information(self, "Succes", "Depunere efectuată!")
            return

        # RETRAGERE
        if tip == "Retragere":
            setari = cur.execute("""
                SELECT retragere_proc, retragere_fix
                FROM SetariComisioane WHERE id=1
            """).fetchone()
            proc, fix = map(float, setari)
            comision = round(suma * proc / 100 + fix, 2)
            total = suma + comision

            if sold_src < total:
                QMessageBox.warning(self, "Eroare", "Fonduri insuficiente!")
                return

            new_balance = sold_src - total
            cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (new_balance, id_src))
            cur.execute("""
                INSERT INTO Tranzactii(id_cont_sursa, tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                VALUES (?, 'Retragere', ?, 'MDL', ?, 'Cash', 'Retragere cu comision')
            """, (id_src, suma, comision))
            conn.commit()
            self.accounts_page.load_accounts()
            QMessageBox.information(self, "Succes", "Retragere efectuată!")
            return

        # TRANSFER INTERN
        if tip == "Transfer intern":
            dest = cur.execute("""
                SELECT id_cont, sold FROM Conturi
                WHERE numar_cont=? AND activ=1
            """, (cont_dest,)).fetchone()
            if not dest:
                QMessageBox.warning(self, "Eroare", "Cont destinație inexistent!")
                return

            id_dest, sold_dest = dest
            sold_dest = float(sold_dest)

            if sold_src < suma:
                QMessageBox.warning(self, "Eroare", "Fonduri insuficiente!")
                return

            new_src = sold_src - suma
            new_dest = sold_dest + suma

            cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (new_src, id_src))
            cur.execute("UPDATE Conturi SET sold=? WHERE id_cont=?", (new_dest, id_dest))

            cur.execute("""
                INSERT INTO Tranzactii(id_cont_sursa, id_cont_destinatie,
                    tip_tranzactie, suma, moneda, comision, metoda_plata, detalii)
                VALUES (?, ?, 'Transfer intern', ?, 'MDL', 0, 'Online', 'Transfer între conturi MAIB')
            """, (id_src, id_dest, suma))
            conn.commit()
            self.accounts_page.load_accounts()
            QMessageBox.information(self, "Succes", "Transfer intern efectuat!")
            return

# ============================================================
# PAGINA RAPOARTE
# ============================================================
class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.txtCont = QLineEdit(); self.txtCont.setPlaceholderText("Număr cont")
        self.txtStart = QLineEdit(); self.txtStart.setPlaceholderText("Data început (YYYY-MM-DD)")
        self.txtEnd = QLineEdit(); self.txtEnd.setPlaceholderText("Data sfârșit (YYYY-MM-DD)")
        self.btnGen = QPushButton("Generează raport")

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Tip", "Sumă", "Comision", "Metodă", "Data", "Detalii"]
        )
        self.lblSummary = QLabel()

        for w in [self.txtCont, self.txtStart, self.txtEnd, self.btnGen, self.table, self.lblSummary]:
            layout.addWidget(w)

        self.setLayout(layout)
        self.btnGen.clicked.connect(self.gen_report)

    def gen_report(self):
        cont = self.txtCont.text().strip()
        start = self.txtStart.text().strip()
        end = self.txtEnd.text().strip()

        conn = get_db()
        cur = conn.cursor()

        acc = cur.execute("""
            SELECT id_cont, sold, moneda
            FROM Conturi
            WHERE numar_cont=? AND activ=1
        """, (cont,)).fetchone()

        if not acc:
            QMessageBox.warning(self, "Eroare", "Cont inexistent!")
            return

        id_cont, sold, moneda = acc
        sold = float(sold)

        rows = cur.execute("""
            SELECT tip_tranzactie, suma, comision, metoda_plata, data_op, detalii
            FROM Tranzactii
            WHERE id_cont_sursa=? AND data_op BETWEEN ? AND ?
            ORDER BY data_op DESC
        """, (id_cont, start, end)).fetchall()

        self.table.setRowCount(len(rows))
        total_in = 0.0
        total_out = 0.0

        for i, r in enumerate(rows):
            tip, suma, comision, metoda, data, detalii = r
            suma = float(suma)
            comision = float(comision)
            if tip == "Depunere":
                total_in += suma
            else:
                total_out += suma

            vals = [tip, suma, comision, metoda, str(data), detalii]
            for j, v in enumerate(vals):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))

        self.lblSummary.setText(
            f"Sold curent: {sold} {moneda} | Intrări: {total_in} {moneda} | "
            f"Ieșiri: {total_out} {moneda} | Nr. tranzacții: {len(rows)}"
        )

# ============================================================
# PAGINA RISC (simplă)
# ============================================================
class RiskPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.btnScan = QPushButton("Scanează tranzacții mari (> 50 000)")
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID tranz.", "ID cont", "Tip", "Sumă", "Data"]
        )
        self.lbl = QLabel()

        layout.addWidget(self.btnScan)
        layout.addWidget(self.table)
        layout.addWidget(self.lbl)
        self.setLayout(layout)

        self.btnScan.clicked.connect(self.scan)

    def scan(self):
        conn = get_db()
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT id_tranzactie, id_cont_sursa, tip_tranzactie, suma, data_op
            FROM Tranzactii
            WHERE suma > 50000
            ORDER BY data_op DESC
        """).fetchall()

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, v in enumerate(r):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))

        if rows:
            self.lbl.setText(f"Au fost găsite {len(rows)} tranzacții mari.")
        else:
            self.lbl.setText("Nu există tranzacții suspecte în acest moment.")

# ============================================================
# PAGINA ADMIN
# ============================================================
class AdminPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        top = QHBoxLayout()

        self.btnAdd = QPushButton("Adaugă utilizator")
        self.btnRole = QPushButton("Schimbă rol")
        self.btnToggle = QPushButton("Activează/Dezactivează")
        self.btnReset = QPushButton("Resetare parolă")
        self.btnComision = QPushButton("Comisioane retragere")

        for b in [self.btnAdd, self.btnRole, self.btnToggle, self.btnReset, self.btnComision]:
            top.addWidget(b)

        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Rol", "Activ"])
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_users()
        self.btnAdd.clicked.connect(self.add_user)
        self.btnRole.clicked.connect(self.change_role)
        self.btnToggle.clicked.connect(self.toggle_user)
        self.btnReset.clicked.connect(self.reset_pass)
        self.btnComision.clicked.connect(self.edit_comision)

    def load_users(self):
        conn = get_db()
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT u.id_user, u.username, r.nume_rol, u.activ
            FROM Utilizatori u
            JOIN Roluri r ON u.id_rol = r.id_rol
        """).fetchall()

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, v in enumerate(r):
                self.table.setItem(i, j, QTableWidgetItem(str(v)))

    def add_user(self):
        dlg = AddUserDialog()
        if dlg.exec_():
            self.load_users()

    def change_role(self):
        r = self.table.currentRow()
        if r < 0:
            return
        id_user = int(self.table.item(r, 0).text())
        dlg = EditRoleDialog(id_user)
        if dlg.exec_():
            self.load_users()

    def toggle_user(self):
        r = self.table.currentRow()
        if r < 0:
            return
        id_user = int(self.table.item(r, 0).text())
        active_text = self.table.item(r, 3).text()
        is_active = active_text in ("1", "True", "true")
        new_state = 0 if is_active else 1

        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE Utilizatori SET activ=? WHERE id_user=?", (new_state, id_user))
        conn.commit()
        self.accounts_page.load_accounts()
        self.accounts_page.load_accounts()
        self.load_users()

    def reset_pass(self):
        r = self.table.currentRow()
        if r < 0:
            return
        id_user = int(self.table.item(r, 0).text())
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE Utilizatori SET parola='1234' WHERE id_user=?", (id_user,))
        conn.commit()
        self.accounts_page.load_accounts()
        QMessageBox.information(self, "Info", "Parola a fost resetată la 1234.")

    def edit_comision(self):
        dlg = EditComisionDialog()
        dlg.exec_()

class AddUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adaugă utilizator")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        self.txtUser = QLineEdit(); self.txtUser.setPlaceholderText("Username")
        self.txtPass = QLineEdit(); self.txtPass.setPlaceholderText("Parola")
        self.cmbRol = QComboBox()

        layout.addWidget(self.txtUser)
        layout.addWidget(self.txtPass)
        layout.addWidget(self.cmbRol)

        self.btnSave = QPushButton("Salvează")
        layout.addWidget(self.btnSave)
        self.setLayout(layout)

        self.btnSave.clicked.connect(self.save)
        self.load_roles()

    def load_roles(self):
        conn = get_db()
        cur = conn.cursor()
        rows = cur.execute("SELECT id_rol, nume_rol FROM Roluri").fetchall()
        self.cmbRol.clear()
        for r in rows:
            self.cmbRol.addItem(r[1], r[0])

    def save(self):
        username = self.txtUser.text().strip()
        parola = self.txtPass.text().strip()
        id_rol = self.cmbRol.currentData()

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Utilizatori(username, parola, id_rol, activ)
            VALUES (?,?,?,1)
        """, (username, parola, id_rol))
        conn.commit()
        self.accounts_page.load_accounts()
        self.accept()

class EditRoleDialog(QDialog):
    def __init__(self, id_user):
        super().__init__()
        self.id_user = id_user
        self.setWindowTitle("Schimbă rol")
        self.setFixedSize(250, 150)

        layout = QVBoxLayout()
        self.cmbRol = QComboBox()
        layout.addWidget(self.cmbRol)

        self.btnSave = QPushButton("Salvează")
        layout.addWidget(self.btnSave)
        self.setLayout(layout)

        self.btnSave.clicked.connect(self.save)
        self.load_roles()

    def load_roles(self):
        conn = get_db()
        cur = conn.cursor()
        rows = cur.execute("SELECT id_rol, nume_rol FROM Roluri").fetchall()
        self.cmbRol.clear()
        for r in rows:
            self.cmbRol.addItem(r[1], r[0])

    def save(self):
        id_rol = self.cmbRol.currentData()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Utilizatori SET id_rol=? WHERE id_user=?
        """, (id_rol, self.id_user))
        conn.commit()
        self.accounts_page.load_accounts()
        self.accept()

class EditComisionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setări comisioane retragere")
        self.setFixedSize(300, 180)

        layout = QVBoxLayout()
        self.txtRetProc = QLineEdit(); self.txtRetProc.setPlaceholderText("Procents (ex: 0.5)")
        self.txtRetFix = QLineEdit(); self.txtRetFix.setPlaceholderText("Fix (ex: 3.0)")
        self.btnSave = QPushButton("Salvează")

        for w in [self.txtRetProc, self.txtRetFix, self.btnSave]:
            layout.addWidget(w)

        self.setLayout(layout)
        self.btnSave.clicked.connect(self.save)
        self.load_data()

    def load_data(self):
        conn = get_db()
        cur = conn.cursor()
        row = cur.execute("""
            SELECT retragere_proc, retragere_fix
            FROM SetariComisioane WHERE id=1
        """).fetchone()
        if row:
            self.txtRetProc.setText(str(row[0]))
            self.txtRetFix.setText(str(row[1]))

    def save(self):
        try:
            proc = float(self.txtRetProc.text())
            fix = float(self.txtRetFix.text())
        except ValueError:
            QMessageBox.warning(self, "Eroare", "Valori invalide!")
            return

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE SetariComisioane
            SET retragere_proc=?, retragere_fix=?
            WHERE id=1
        """, (proc, fix))
        conn.commit()
        self.accounts_page.load_accounts()
        QMessageBox.information(self, "Succes", "Comisioanele au fost actualizate.")
        self.accept()

# ============================================================
# FEREASTRA PRINCIPALĂ
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self, username, role):
        super().__init__()
        self.setWindowTitle("MAIB Banking System")
        self.setGeometry(200, 100, 900, 600)

        self.username = username
        self.role = role
        self.dark = False

        top = QHBoxLayout()
        self.lblUser = QLabel(f"Utilizator: {self.username} (rol: {self.role})")
        self.btnTheme = QPushButton("🌙 / ☀️")

        top.addWidget(self.lblUser)
        top.addWidget(self.btnTheme)

        self.tabs = QTabWidget()
        self.pageClients = ClientsPage()
        self.pageAccounts = AccountsPage()
        self.pageTransactions = TransactionsPage(self.pageAccounts)
        self.pageReports = ReportsPage()
        self.pageRisk = RiskPage()

        self.tabs.addTab(self.pageClients, "Clienți")
        self.tabs.addTab(self.pageAccounts, "Conturi")
        self.tabs.addTab(self.pageTransactions, "Tranzacții")
        self.tabs.addTab(self.pageReports, "Rapoarte")
        self.tabs.addTab(self.pageRisk, "Risc")

        if self.role == "admin":
            self.pageAdmin = AdminPage()
            self.tabs.addTab(self.pageAdmin, "Admin")

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.btnTheme.clicked.connect(self.toggle_theme)

    def toggle_theme(self):
        if self.dark:
            self.setStyleSheet("")
            self.dark = False
        else:
            self.setStyleSheet(
                "QWidget { background-color: #222; color: white; } "
                "QLineEdit { background-color: #333; color: white; } "
                "QTableWidget { background-color: #333; color: white; } "
                "QPushButton { background-color: #444; color: white; }"
            )
            self.dark = True

# ============================================================
# MAIN
# ============================================================
def main():
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
