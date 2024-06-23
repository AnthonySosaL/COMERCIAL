# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QMessageBox, QStackedWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import cx_Oracle
import os
import datetime

class AjustarInventarios(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.productos_en_ajuste = []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Ajustar Inventarios')

        # Establecer fondo de pantalla
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)

        layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Limitar el ancho máximo del layout izquierdo
        left_layout_widget = QWidget()
        left_layout_widget.setLayout(left_layout)
        left_layout_widget.setMaximumWidth(420)

        # Left Layout
        self.ajucodigo_label = QLabel('Código de Ajuste')
        self.ajucodigo_display = QLineEdit()
        self.ajucodigo_display.setReadOnly(True)
        left_layout.addWidget(self.ajucodigo_label)
        left_layout.addWidget(self.ajucodigo_display)

        self.factura_label = QLabel('Factura')
        self.facturas_menu = QComboBox()
        self.cargar_facturas()
        left_layout.addWidget(self.factura_label)
        left_layout.addWidget(self.facturas_menu)

        self.cargar_factura_btn = QPushButton('Cargar Factura', self)
        self.cargar_factura_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt;")
        self.cargar_factura_btn.clicked.connect(self.cargar_productos_factura)
        left_layout.addWidget(self.cargar_factura_btn)

        self.factura_status_label = QLabel('Estado de la Factura')
        self.factura_status_display = QLineEdit()
        self.factura_status_display.setReadOnly(True)
        left_layout.addWidget(self.factura_status_label)
        left_layout.addWidget(self.factura_status_display)

        self.descripcion_label = QLabel('Descripción del Ajuste')
        self.descripcion_input = QLineEdit()
        left_layout.addWidget(self.descripcion_label)
        left_layout.addWidget(self.descripcion_input)

        self.empleado_label = QLabel('Empleado')
        self.empleados_menu = QComboBox()
        self.cargar_empleados()
        left_layout.addWidget(self.empleado_label)
        left_layout.addWidget(self.empleados_menu)

        self.finalizar_btn = QPushButton('Finalizar Ajuste', self)
        self.finalizar_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt;")
        self.finalizar_btn.clicked.connect(self.finalizar_ajuste)
        left_layout.addWidget(self.finalizar_btn)

        self.volver_btn = QPushButton('Salir', self)
        self.volver_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt;")
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        left_layout.addWidget(self.volver_btn)

        layout.addWidget(left_layout_widget)

        # Right Layout (table)
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(3)
        self.tabla_productos.setHorizontalHeaderLabels(['Producto', 'Nombre del Producto', 'Cantidad'])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.tabla_productos)

        layout.addLayout(right_layout)

        self.setLayout(layout)

        self.obtener_codigo_ajuste()

    def obtener_codigo_ajuste(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT NVL(MAX(AJUCODIGO), 0) + 1
                FROM AJUSTES
            """)
            nuevo_ajucodigo = cursor.fetchone()[0]
            self.ajucodigo_display.setText(str(nuevo_ajucodigo))
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo obtener el código de ajuste: {error.message}")

    def cargar_facturas(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT FACNUMERO FROM FACTURAS")
            facturas = cursor.fetchall()
            cursor.close()
            connection.close()
            for factura in facturas:
                self.facturas_menu.addItem(factura[0].strip())
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar las facturas: {error.message}")

    def cargar_productos_factura(self):
        factura_seleccionada = self.facturas_menu.currentText().strip()
        if not factura_seleccionada:
            self.factura_status_display.clear()
            self.productos_en_ajuste = []
            self.actualizar_tabla()
            self.finalizar_btn.setEnabled(False)
            return

        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT FACSTATUS 
                FROM FACTURAS 
                WHERE TRIM(FACNUMERO) = :factura
            """, {'factura': factura_seleccionada})
            factura = cursor.fetchone()
            if factura:
                self.factura_status_display.setText(factura[0])
                if factura[0].strip().upper() == 'CANCELADA':
                    self.finalizar_btn.setEnabled(True)
                else:
                    self.finalizar_btn.setEnabled(True)

            cursor.execute("""
                SELECT PXF.PROCODIGO, P.PRODESCRIPCION, PXF.PXFCANTIDAD
                FROM PXF
                JOIN PRODUCTOS P ON PXF.PROCODIGO = P.PROCODIGO
                WHERE TRIM(PXF.FACNUMERO) = :factura
            """, {'factura': factura_seleccionada})
            productos = cursor.fetchall()
            cursor.close()
            connection.close()

            self.productos_en_ajuste = [{'producto': prod[0].strip(), 'nombre': prod[1].strip(), 'cantidad': prod[2]} for prod in productos]
            self.actualizar_tabla()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar los productos de la factura: {error.message}")

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

    def actualizar_tabla(self):
        self.tabla_productos.setRowCount(len(self.productos_en_ajuste))
        for row, item in enumerate(self.productos_en_ajuste):
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(item['producto']))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(item['nombre']))
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(str(item['cantidad'])))

    def finalizar_ajuste(self):
        factura_status = self.factura_status_display.text().strip().upper()
        if factura_status == 'CANCELADA':
            QMessageBox.warning(self, "Advertencia", "La factura ya está cancelada y no se puede realizar el ajuste.")
            return

        confirm = QMessageBox.question(self, "Confirmar Ajuste", "¿Está seguro de que desea finalizar el ajuste y cancelar la factura?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        factura_seleccionada = self.facturas_menu.currentText().strip()
        if not factura_seleccionada:
            return

        try:
            empcodigo = self.empleados_menu.currentText().split(" - ")[0].strip()
            ajufecha = datetime.datetime.now().strftime('%d-%b-%y')
            ajucantidadtotal = sum(item['cantidad'] for item in self.productos_en_ajuste)
            ajucodigo = self.ajucodigo_display.text().strip()
            ajudescripcion = self.descripcion_input.text().strip()

            if not empcodigo or not ajucantidadtotal:
                QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
                return

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            print(ajufecha)
            # Insertar en AJUSTES
            cursor.execute("""
                INSERT INTO AJUSTES (AJUCODIGO, EMPCODIGO, AJUDESCRIPCION, AJUFECHA, AJUCANTIDADTOTAL)
                VALUES (:1, :2, :3, TO_DATE(:4, 'DD-MON-YY'), :5)
            """, (ajucodigo, empcodigo, ajudescripcion, ajufecha, ajucantidadtotal))

            # Insertar en PXA
            for item in self.productos_en_ajuste:
                cursor.execute("""
                    INSERT INTO PXA (AJUCODIGO, PROCODIGO, PXACANTIDAD)
                    VALUES (:1, :2, :3)
                """, (ajucodigo, item['producto'], item['cantidad']))

                cursor.execute("""
                    UPDATE PRODUCTOS
                    SET PROAJUSTES = PROAJUSTES + :1
                    WHERE TRIM(PROCODIGO) = :2
                """, (item['cantidad'], item['producto']))

            # Cambiar el estado de la factura a Cancelada
            cursor.execute("""
                UPDATE FACTURAS
                SET FACSTATUS = 'Cancelada'
                WHERE TRIM(FACNUMERO) = :1
            """, (factura_seleccionada,))

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Ajuste finalizado y factura cancelada exitosamente.")
            self.obtener_codigo_ajuste()
            self.productos_en_ajuste = []
            self.actualizar_tabla()
            self.factura_status_display.setText("Cancelada")
            self.finalizar_btn.setEnabled(False)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo finalizar el ajuste: {error.message}")

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
    ajustar_inventarios = AjustarInventarios(parent=stacked_widget)
    stacked_widget.addWidget(ajustar_inventarios)
    stacked_widget.show()
    sys.exit(app.exec_())
