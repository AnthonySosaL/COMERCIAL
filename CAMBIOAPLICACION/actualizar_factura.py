# -*- coding: 1252 -*-
import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QDateEdit, QMessageBox
import cx_Oracle
import datetime

class ActualizarFactura(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Actualizar Factura')

        layout = QVBoxLayout()

        self.facnumero_label = QLabel('Número de Factura')
        self.entry_facnumero_manual = QLineEdit(self)
        layout.addWidget(self.facnumero_label)
        layout.addWidget(self.entry_facnumero_manual)

        self.cliente_label = QLabel('Código de Cliente')
        self.clientes_menu = QComboBox(self)
        self.cargar_clientes()
        layout.addWidget(self.cliente_label)
        layout.addWidget(self.clientes_menu)

        self.facfecha_label = QLabel('Fecha')
        self.entry_facfecha = QDateEdit(self)
        self.entry_facfecha.setCalendarPopup(True)
        self.entry_facfecha.setDisplayFormat('yyyy-MM-dd')
        layout.addWidget(self.facfecha_label)
        layout.addWidget(self.entry_facfecha)

        self.facdescuento_label = QLabel('Descuento')
        self.entry_facdescuento = QLineEdit(self)
        layout.addWidget(self.facdescuento_label)
        layout.addWidget(self.entry_facdescuento)

        self.formapago_label = QLabel('Forma de Pago')
        self.formapago_menu = QComboBox(self)
        self.formapago_menu.addItems(['Efectivo', 'Crédito', 'Débito', 'Transferencia'])
        layout.addWidget(self.formapago_label)
        layout.addWidget(self.formapago_menu)

        self.status_label = QLabel('Estado')
        self.status_menu = QComboBox(self)
        self.status_menu.addItems(['Procesada', 'Enviada', 'Entregada', 'Pagada', 'Cancelada'])
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_menu)

        self.actualizar_btn = QPushButton('Actualizar Factura', self)
        self.actualizar_btn.clicked.connect(self.actualizar)
        layout.addWidget(self.actualizar_btn)

        self.volver_btn = QPushButton('Salir', self)
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        layout.addWidget(self.volver_btn)

        self.setLayout(layout)

    def cargar_clientes(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT CLICODIGO, CLINOMBRE FROM CLIENTES")
            clientes = cursor.fetchall()
            cursor.close()
            connection.close()
            for cliente in clientes:
                self.clientes_menu.addItem(f"{cliente[0].strip()} - {cliente[1].strip()}")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar los clientes: {error.message}")

    def actualizar(self):
        try:
            facnumero = self.entry_facnumero_manual.text().strip()
            clicodigo = self.clientes_menu.currentText().split(" - ")[0].strip()
            facfecha = self.entry_facfecha.date().toString('yyyy-MM-dd')
            facdescuento = self.entry_facdescuento.text().strip()
            facformapago = self.formapago_menu.currentText().strip()
            facstatus = self.status_menu.currentText().strip()

            if not facnumero or not facfecha or not facdescuento or not facformapago or not facstatus:
                QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
                return

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE FACTURAS
                SET CLICODIGO = :1, FACFECHA = TO_DATE(:2, 'YYYY-MM-DD'), FACDESCUENTO = :3, FACFORMAPAGO = :4, FACSTATUS = :5
                WHERE TRIM(FACNUMERO) = :6
            """, (clicodigo, facfecha, facdescuento, facformapago, facstatus, facnumero))
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Factura actualizada exitosamente.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo actualizar la factura: {error.message}")

    def volver_al_inicio(self):
        self.parent_widget.setCurrentWidget(self.parent_widget.main_menu)
