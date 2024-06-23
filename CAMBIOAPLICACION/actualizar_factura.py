# -*- coding: 1252 -*-
import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QVBoxLayout, QPushButton, QMessageBox, QStackedWidget, QHBoxLayout, QFrame
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import cx_Oracle
import datetime

class ActualizarFactura(QtWidgets.QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 790)
        self.setWindowTitle('Actualizar Factura')

        # Establecer fondo de pantalla
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Contenedor central
        central_frame = QFrame(self)
        central_frame.setStyleSheet("background-color: white; border-radius: 10px;")
        central_frame.setFixedSize(400, 500)

        central_layout = QVBoxLayout(central_frame)
        central_layout.setContentsMargins(20, 20, 20, 20)
        central_layout.setSpacing(10)

        self.facnumero_label = QLabel('Número de Factura')
        self.entry_facnumero_manual = QLineEdit(self)
        central_layout.addWidget(self.facnumero_label)
        central_layout.addWidget(self.entry_facnumero_manual)

        self.cliente_label = QLabel('Código de Cliente')
        self.clientes_menu = QComboBox(self)
        self.cargar_clientes()
        central_layout.addWidget(self.cliente_label)
        central_layout.addWidget(self.clientes_menu)

        self.facdescuento_label = QLabel('Descuento')
        self.entry_facdescuento = QLineEdit(self)
        central_layout.addWidget(self.facdescuento_label)
        central_layout.addWidget(self.entry_facdescuento)

        self.formapago_label = QLabel('Forma de Pago')
        self.formapago_menu = QComboBox(self)
        self.formapago_menu.addItems(['Efectivo', 'Crédito', 'Débito', 'Transferencia'])
        central_layout.addWidget(self.formapago_label)
        central_layout.addWidget(self.formapago_menu)

        self.status_label = QLabel('Estado')
        self.status_menu = QComboBox(self)
        self.status_menu.addItems(['Procesada', 'Enviada', 'Entregada', 'Pagada', 'Cancelada'])
        central_layout.addWidget(self.status_label)
        central_layout.addWidget(self.status_menu)

        self.empleado_label = QLabel('Empleado que aprueba la salida')
        self.empleados_menu = QComboBox(self)
        self.cargar_empleados()
        central_layout.addWidget(self.empleado_label)
        central_layout.addWidget(self.empleados_menu)

        self.actualizar_btn = QPushButton('Actualizar Factura', self)
        self.actualizar_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt; height: 40px;")
        self.actualizar_btn.clicked.connect(self.actualizar)
        central_layout.addWidget(self.actualizar_btn)

        self.volver_btn = QPushButton('Salir', self)
        self.volver_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 10pt; height: 40px;")
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        central_layout.addWidget(self.volver_btn)

        main_layout.addWidget(central_frame, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)

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

    def cargar_empleados(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT EMPCODIGO, EMPNOMBRE1, EMPAPELLIDO1 FROM EMPLEADOS")
            empleados = cursor.fetchall()
            cursor.close()
            connection.close()
            for empleado in empleados:
                self.empleados_menu.addItem(f"{empleado[0].strip()} - {empleado[1].strip()} {empleado[2].strip()}")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar los empleados: {error.message}")

    def actualizar(self):
        try:
            facnumero = self.entry_facnumero_manual.text().strip()
            clicodigo = self.clientes_menu.currentText().split(" - ")[0].strip()
            facdescuento = self.entry_facdescuento.text().strip()
            facformapago = self.formapago_menu.currentText().strip()
            facstatus = self.status_menu.currentText().strip()

            if not facnumero or not facdescuento or not facformapago or not facstatus:
                QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
                return

            # Obtener estado actual
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT FACSTATUS
                FROM FACTURAS
                WHERE TRIM(FACNUMERO) = :1
            """, (facnumero,))
            estado_actual = cursor.fetchone()[0].strip()

            # Validaciones de cambio de estado
            if estado_actual == 'Pagada':
                if facstatus in ['Procesada', 'Enviada', 'Entregada']:
                    QMessageBox.critical(self, "Error", f"No se puede cambiar el estado de '{estado_actual}' a '{facstatus}'.")
                    cursor.close()
                    connection.close()
                    return
            elif estado_actual == 'Entregada':
                if facstatus in ['Procesada', 'Enviada']:
                    QMessageBox.critical(self, "Error", f"No se puede cambiar el estado de '{estado_actual}' a '{facstatus}'.")
                    cursor.close()
                    connection.close()
                    return
            elif estado_actual == 'Cancelada':
                QMessageBox.critical(self, "Error", "No se puede actualizar una factura cancelada.")
                cursor.close()
                connection.close()
                return

            # Actualizar factura
            if facstatus == 'Pagada':
                # Obtener el siguiente valor de SALCODIGO
                cursor.execute("""
                    SELECT NVL(MAX(SALCODIGO), 0) + 1
                    FROM SALIDAS
                """)
                nuevo_salcodigo = cursor.fetchone()[0]

                # Registrar salida y productos
                empcodigo = self.empleados_menu.currentText().split(" - ")[0].strip()

                # Obtener la cantidad total de productos en la factura
                cursor.execute("""
                    SELECT SUM(PXFCANTIDAD)
                    FROM PXF
                    WHERE TRIM(FACNUMERO) = :1
                """, (facnumero,))
                salcantidadtotal = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO SALIDAS (SALCODIGO, EMPCODIGO, SALDESCRIPCION, SALFECHA, SALCANTIDADTOTAL, SALREFERENCIA)
                    VALUES (:1, :2, :3, TO_DATE(:4, 'DD-MON-YY'), :5, :6)
                """, (nuevo_salcodigo, empcodigo.strip(), f"Salida de productos por factura {facnumero.strip()}", datetime.datetime.now().strftime('%d-%b-%y'), salcantidadtotal, facnumero.strip()))

                cursor.execute("""
                    SELECT PROCODIGO, PXFCANTIDAD
                    FROM PXF
                    WHERE TRIM(FACNUMERO) = :1
                """, (facnumero,))
                productos = cursor.fetchall()

                for producto in productos:
                    procodigo, pxscantidad = producto
                    cursor.execute("""
                        INSERT INTO PXS (SALCODIGO, PROCODIGO, PXSCANTIDAD)
                        VALUES (:1, :2, :3)
                    """, (nuevo_salcodigo, procodigo, pxscantidad))

            cursor.execute("""
                UPDATE FACTURAS
                SET CLICODIGO = :1, FACDESCUENTO = :2, FACFORMAPAGO = :3, FACSTATUS = :4
                WHERE TRIM(FACNUMERO) = :5
            """, (clicodigo, facdescuento, facformapago, facstatus, facnumero))

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Factura actualizada exitosamente.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo actualizar la factura: {error.message}")

    def volver_al_inicio(self):
        if self.window_stack:
            ultima_ventana = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(ultima_ventana)
        else:
            self.parent_widget.setCurrentIndex(0)  # Asumiendo que la primera pantalla es el índice 0

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    actualizar_factura = ActualizarFactura(parent=stacked_widget)
    stacked_widget.addWidget(actualizar_factura)
    stacked_widget.show()
    sys.exit(app.exec_())
