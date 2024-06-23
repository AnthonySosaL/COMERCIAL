# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QMessageBox, QStackedWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import cx_Oracle
import os
import datetime

class IngresarCompras(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.productos_en_ingreso = []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Ingresar Compras')

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
        self.ingcodigo_label = QLabel('Código de Ingreso')
        self.ingcodigo_display = QLineEdit()
        self.ingcodigo_display.setReadOnly(True)
        left_layout.addWidget(self.ingcodigo_label)
        left_layout.addWidget(self.ingcodigo_display)

        self.producto_label = QLabel('Producto')
        self.productos_menu = QComboBox()
        self.cargar_productos()
        left_layout.addWidget(self.producto_label)
        left_layout.addWidget(self.productos_menu)

        self.cantidad_label = QLabel('Cantidad')
        self.cantidad_input = QLineEdit()
        left_layout.addWidget(self.cantidad_label)
        left_layout.addWidget(self.cantidad_input)

        self.empleado_label = QLabel('Empleado')
        self.empleados_menu = QComboBox()
        self.cargar_empleados()
        left_layout.addWidget(self.empleado_label)
        left_layout.addWidget(self.empleados_menu)

        button_style = "background-color: #001f3f; color: white; font-size: 12pt; height: 40px; width: 300px;"

        self.ingresar_btn = QPushButton('Ingresar Producto', self)
        self.ingresar_btn.setStyleSheet(button_style)
        self.ingresar_btn.clicked.connect(self.ingresar_producto)
        left_layout.addWidget(self.ingresar_btn)

        self.finalizar_btn = QPushButton('Finalizar Ingreso', self)
        self.finalizar_btn.setStyleSheet(button_style)
        self.finalizar_btn.clicked.connect(self.finalizar_ingreso)
        left_layout.addWidget(self.finalizar_btn)

        left_layout.addStretch()

        self.volver_btn = QPushButton('Salir', self)
        self.volver_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 10pt;")
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        self.volver_btn.setFixedSize(100, 40)
        left_layout.addWidget(self.volver_btn)

        layout.addWidget(left_layout_widget)

        # Right Layout (table)
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(5)
        self.tabla_productos.setHorizontalHeaderLabels(['Producto', 'Cantidad', 'Código Ingreso', 'Eliminar', 'Editar'])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.tabla_productos)

        layout.addLayout(right_layout)

        self.setLayout(layout)

        self.obtener_codigo_ingreso()

    def obtener_codigo_ingreso(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT NVL(MAX(INGCODIGO), 0) + 1
                FROM INGRESOS
            """)
            nuevo_ingcodigo = cursor.fetchone()[0]
            self.ingcodigo_display.setText(str(nuevo_ingcodigo))
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo obtener el código de ingreso: {error.message}")

    def cargar_productos(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT PROCODIGO, PRODESCRIPCION FROM PRODUCTOS")
            productos = cursor.fetchall()
            cursor.close()
            connection.close()
            for producto in productos:
                self.productos_menu.addItem(f"{producto[0].strip()} - {producto[1].strip()}")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar los productos: {error.message}")

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

    def ingresar_producto(self):
        producto_seleccionado = self.productos_menu.currentText().split(" - ")[0].strip()
        cantidad = self.cantidad_input.text().strip()
        codigo_ingreso = self.ingcodigo_display.text().strip()

        if not producto_seleccionado or not cantidad:
            QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
            return

        # Verificar si el producto ya está en la lista para actualizarlo
        for item in self.productos_en_ingreso:
            if item['producto'] == producto_seleccionado:
                item['cantidad'] += float(cantidad)
                self.actualizar_tabla()
                return

        # Agregar el producto a la lista
        self.productos_en_ingreso.append({'producto': producto_seleccionado, 'cantidad': float(cantidad), 'codigo_ingreso': codigo_ingreso})
        self.actualizar_tabla()

    def actualizar_tabla(self):
        self.tabla_productos.setRowCount(len(self.productos_en_ingreso))
        for row, item in enumerate(self.productos_en_ingreso):
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(item['producto']))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(str(item['cantidad'])))
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(item['codigo_ingreso']))

            btn_eliminar = QPushButton()
            eliminar_pixmap = QPixmap('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/borrar.png')
            eliminar_icon = QIcon(eliminar_pixmap.scaled(24, 24))
            btn_eliminar.setIcon(eliminar_icon)
            btn_eliminar.clicked.connect(lambda _, r=row: self.eliminar_producto(r))
            self.tabla_productos.setCellWidget(row, 3, btn_eliminar)

            btn_editar = QPushButton()
            editar_pixmap = QPixmap('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/editar.png')
            editar_icon = QIcon(editar_pixmap.scaled(24, 24))
            btn_editar.setIcon(editar_icon)
            btn_editar.clicked.connect(lambda _, r=row: self.editar_producto(r))
            self.tabla_productos.setCellWidget(row, 4, btn_editar)

    def eliminar_producto(self, row):
        del self.productos_en_ingreso[row]
        self.actualizar_tabla()

    def editar_producto(self, row):
        item = self.productos_en_ingreso[row]
        self.productos_menu.setCurrentText(f"{item['producto']}")
        self.cantidad_input.setText(str(item['cantidad']))
        self.productos_en_ingreso.pop(row)
        self.actualizar_tabla()

    def finalizar_ingreso(self):
        confirm = QMessageBox.question(self, "Confirmar Ingreso", "¿Está seguro de que desea finalizar el ingreso?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        try:
            empcodigo = self.empleados_menu.currentText().split(" - ")[0].strip()
            ingfecha = datetime.datetime.now().strftime('%d-%b-%y')
            total_cantidad = sum(item['cantidad'] for item in self.productos_en_ingreso)
            codigo_ingreso = self.ingcodigo_display.text().strip()

            if not empcodigo or not total_cantidad:
                QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
                return

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            # Insertar en INGRESOS
            cursor.execute("""
                INSERT INTO INGRESOS (INGCODIGO, EMPCODIGO, INGDESCRIPCION, INGFECHA, INGCANTIDADTOTAL, INGREFERENCIA)
                VALUES (:1, :2, :3, TO_DATE(:4, 'DD-MON-YY'), :5, :6)
            """, (codigo_ingreso, empcodigo, f"Ingreso de productos por compra {codigo_ingreso}", ingfecha, total_cantidad, codigo_ingreso))

            # Insertar en PXI
            for item in self.productos_en_ingreso:
                cursor.execute("""
                    INSERT INTO PXI (INGCODIGO, PROCODIGO, PXICANTIDAD)
                    VALUES (:1, :2, :3)
                """, (codigo_ingreso, item['producto'], item['cantidad']))

                cursor.execute("""
                    UPDATE PRODUCTOS
                    SET PROINGRESOS = PROINGRESOS + :1
                    WHERE TRIM(PROCODIGO) = :2
                """, (item['cantidad'], item['producto']))

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Ingreso finalizado exitosamente.")
            self.obtener_codigo_ingreso()
            self.productos_en_ingreso = []
            self.actualizar_tabla()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo finalizar el ingreso: {error.message}")

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
    ingresar_compras = IngresarCompras(parent=stacked_widget)
    stacked_widget.addWidget(ingresar_compras)
    stacked_widget.show()
    sys.exit(app.exec_())
