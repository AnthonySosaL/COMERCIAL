# -*- coding: 1252 -*-
import sys
import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QCalendarWidget
import cx_Oracle

class CrearFactura(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Generar Factura')

        # Establecer fondo de pantalla
        self.background_label = QtWidgets.QLabel(self)
        self.background_pixmap = QtGui.QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)

        layout = QtWidgets.QHBoxLayout()

        left_layout = QtWidgets.QVBoxLayout()
        right_layout = QtWidgets.QVBoxLayout()

        # Limitar el ancho máximo del layout izquierdo
        left_layout_widget = QtWidgets.QWidget()
        left_layout_widget.setLayout(left_layout)
        left_layout_widget.setMaximumWidth(420)

        # Left Layout - Generar Factura
        self.facnumero_label = QtWidgets.QLabel('Número de Factura')
        self.facnumero_input = QtWidgets.QLineEdit()
        self.facnumero_input.setReadOnly(True)
        left_layout.addWidget(self.facnumero_label)
        left_layout.addWidget(self.facnumero_input)

        self.facfecha_label = QtWidgets.QLabel('Fecha')
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setFixedWidth(400)
        self.calendar.setFixedHeight(300)
        self.calendar.clicked.connect(self.update_date)
        left_layout.addWidget(self.facfecha_label)
        left_layout.addWidget(self.calendar)

        self.facfecha_input = QtWidgets.QLineEdit()
        self.facfecha_input.setReadOnly(True)
        left_layout.addWidget(self.facfecha_input)

        self.facdescuento_label = QtWidgets.QLabel('Descuento')
        self.facdescuento_input = QtWidgets.QLineEdit()
        left_layout.addWidget(self.facdescuento_label)
        left_layout.addWidget(self.facdescuento_input)

        self.cliente_label = QtWidgets.QLabel('Código de Cliente')
        self.clientes_menu = QtWidgets.QComboBox()
        left_layout.addWidget(self.cliente_label)
        left_layout.addWidget(self.clientes_menu)

        self.formapago_label = QtWidgets.QLabel('Forma de Pago')
        self.formapago_menu = QtWidgets.QComboBox()
        self.formapago_menu.addItems(['Efectivo', 'Crédito', 'Débito', 'Transferencia'])
        left_layout.addWidget(self.formapago_label)
        left_layout.addWidget(self.formapago_menu)

        self.generar_btn = QtWidgets.QPushButton('Generar Factura', self)
        self.generar_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.generar_btn.clicked.connect(self.generar_factura)
        left_layout.addWidget(self.generar_btn)

        self.volver_btn = QtWidgets.QPushButton('Salir', self)
        self.volver_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        left_layout.addWidget(self.volver_btn)

        # Right Layout - Agregar Producto a Factura
        self.factura_label = QtWidgets.QLabel('Número de Factura para Agregar Productos')
        self.factura_input = QtWidgets.QLineEdit()
        right_layout.addWidget(self.factura_label)
        right_layout.addWidget(self.factura_input)

        self.seleccionar_btn = QtWidgets.QPushButton('Seleccionar Factura', self)
        self.seleccionar_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.seleccionar_btn.clicked.connect(self.seleccionar_factura)
        right_layout.addWidget(self.seleccionar_btn)

        self.productos_label = QtWidgets.QLabel('Productos de la Factura')
        self.productos_table = QtWidgets.QTableWidget()
        self.productos_table.setColumnCount(7)
        self.productos_table.setHorizontalHeaderLabels(["Código", "Descripción", "Cantidad", "Valor", "Subtotal", "Imagen", "Eliminar"])
        self.productos_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        right_layout.addWidget(self.productos_label)
        right_layout.addWidget(self.productos_table)

        self.agregar_producto_btn = QtWidgets.QPushButton('Agregar Producto a Factura', self)
        self.agregar_producto_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.agregar_producto_btn.clicked.connect(self.agregar_producto_a_factura)
        right_layout.addWidget(self.agregar_producto_btn)

        layout.addWidget(left_layout_widget)
        layout.addLayout(right_layout)

        self.setLayout(layout)
        self.cargar_clientes()
        self.actualizar_numero_factura()

    def update_date(self, date):
        self.facfecha_input.setText(date.toString('yyyy-MM-dd'))

    def volver_al_inicio(self):
        self.parent_widget.setCurrentWidget(self.parent_widget.main_menu)

    def generar_factura(self):
        try:
            facnumero = self.facnumero_input.text()
            cliente_seleccionado = self.clientes_menu.currentText()
            clicodigo = cliente_seleccionado.split(" - ")[0]
            facfecha = self.facfecha_input.text()
            facdescuento = self.facdescuento_input.text()
            facformapago = self.formapago_menu.currentText()
            facstatus = "Creada"

            facfecha_oracle = datetime.strptime(facfecha, '%Y-%m-%d').strftime('%d-%b-%Y')

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO FACTURAS (FACNUMERO, CLICODIGO, FACFECHA, FACSUBTOTAL, FACDESCUENTO, FACIVA, FACICE, FACFORMAPAGO, FACSTATUS)
                VALUES (:1, :2, TO_DATE(:3, 'DD-MON-YYYY'), 0, :4, 0, 0, :5, :6)
            """, (facnumero, clicodigo, facfecha_oracle, facdescuento, facformapago, facstatus))
            connection.commit()
            cursor.close()
            connection.close()
            QtWidgets.QMessageBox.information(self, 'Éxito', 'Factura generada exitosamente.')
            self.actualizar_numero_factura()

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo generar la factura: {error.message}')

    def actualizar_numero_factura(self):
        nuevo_numero = self.generar_numero_factura()
        self.facnumero_input.setReadOnly(False)
        self.facnumero_input.setText(nuevo_numero)
        self.facnumero_input.setReadOnly(True)

    def seleccionar_factura(self):
        facnumero = self.factura_input.text()
        self.cargar_productos(facnumero)

    def agregar_producto_a_factura(self):
        producto_window = ProductoWindow(self.factura_input.text(), self)
        producto_window.exec_()

    def cargar_clientes(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT CLICODIGO, CLINOMBRE FROM CLIENTES")
            clientes = cursor.fetchall()
            for cliente in clientes:
                self.clientes_menu.addItem(f"{cliente[0]} - {cliente[1]}")
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo cargar los clientes: {error.message}')

    def cargar_productos(self, facnumero):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT PXF.PROCODIGO, P.PRODESCRIPCION, PXF.PXFCANTIDAD, PXF.PXFVALOR, PXF.PXFSUBTOTAL, P.FOTO_PATH
                FROM PXF 
                JOIN PRODUCTOS P ON PXF.PROCODIGO = P.PROCODIGO 
                WHERE TRIM(PXF.FACNUMERO) = :1
            """, (facnumero,))
            productos = cursor.fetchall()
            self.productos_table.setRowCount(0)
            for row_num, producto in enumerate(productos):
                self.productos_table.insertRow(row_num)
                for col_num, data in enumerate(producto):
                    if col_num == 5:  # Si es la columna de la imagen
                        item = QtWidgets.QTableWidgetItem()
                        if data:  # Si hay una ruta de imagen
                            pixmap = QtGui.QPixmap(data)
                        else:  # Si no hay ruta de imagen, usar imagen por defecto
                            pixmap = QtGui.QPixmap('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/apoyo.png')
                        icon = QtGui.QIcon(pixmap)
                        item.setIcon(icon)
                        self.productos_table.setItem(row_num, col_num, item)
                    else:
                        self.productos_table.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(data)))

                # Añadir botón de eliminar en la última columna
                eliminar_btn = QtWidgets.QPushButton('Eliminar', self)
                eliminar_btn.clicked.connect(lambda ch, row=row_num, procodigo=producto[0]: self.eliminar_producto(row, facnumero, procodigo))
                self.productos_table.setCellWidget(row_num, 6, eliminar_btn)

            self.productos_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo cargar los productos: {error.message}')

    def eliminar_producto(self, row, facnumero, procodigo):
        facnumero = facnumero.strip()
        procodigo = procodigo.strip()
        reply = QtWidgets.QMessageBox.question(self, 'Confirmar Eliminación',
                                               f'¿Está seguro de que desea eliminar el producto {procodigo} de la factura {facnumero}?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
                cursor = connection.cursor()
                cursor.execute("DELETE FROM PXF WHERE TRIM(FACNUMERO) = :1 AND TRIM(PROCODIGO) = :2", (facnumero, procodigo))
                connection.commit()
                cursor.close()
                connection.close()
                QtWidgets.QMessageBox.information(self, 'Éxito', 'Producto eliminado de la factura exitosamente.')
                self.cargar_productos(facnumero)
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo eliminar el producto: {error.message}')

    def generar_numero_factura(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT FACNUMERO FROM FACTURAS")
            facturas = cursor.fetchall()
            max_num = 0
            for fac in facturas:
                num = int(fac[0].split('-')[1])
                if num > max_num:
                    max_num = num
            nuevo_numero = max_num + 1
            fac_numero_generado = f"FAC-{nuevo_numero:03d}"
            cursor.close()
            connection.close()
            return fac_numero_generado
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo generar el número de factura: {error.message}')
            return "FAC-001"

class ProductoWindow(QtWidgets.QDialog):
    def __init__(self, facnumero, parent):
        super().__init__(parent)
        self.facnumero = facnumero
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Agregar Producto a Factura')

        layout = QtWidgets.QVBoxLayout()

        self.producto_label = QtWidgets.QLabel('Código de Producto')
        self.productos_menu = QtWidgets.QComboBox()
        self.cargar_productos()
        layout.addWidget(self.producto_label)
        layout.addWidget(self.productos_menu)

        self.cantidad_label = QtWidgets.QLabel('Cantidad')
        self.cantidad_input = QtWidgets.QLineEdit()
        layout.addWidget(self.cantidad_label)
        layout.addWidget(self.cantidad_input)

        self.valor_label = QtWidgets.QLabel('Valor')
        self.valor_input = QtWidgets.QLineEdit()
        self.valor_input.setReadOnly(True)
        layout.addWidget(self.valor_label)
        layout.addWidget(self.valor_input)

        self.agregar_btn = QtWidgets.QPushButton('Agregar Producto', self)
        self.agregar_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.agregar_btn.clicked.connect(self.on_agregar_producto)
        layout.addWidget(self.agregar_btn)

        self.setLayout(layout)
        self.productos_menu.currentIndexChanged.connect(self.on_producto_change)

    def on_producto_change(self):
        self.cargar_valor_producto(self.productos_menu.currentText(), self.valor_input)

    def on_agregar_producto(self):
        self.agregar_producto(self.facnumero, self.productos_menu.currentText(), self.cantidad_input.text(), self.valor_input.text())

    def cargar_productos(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT PROCODIGO, PRODESCRIPCION FROM PRODUCTOS")
            productos = cursor.fetchall()
            for producto in productos:
                self.productos_menu.addItem(f"{producto[0]} - {producto[1]}")
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo cargar los productos: {error.message}')

    def cargar_valor_producto(self, selected_producto, valor_input):
        procodigo = selected_producto.split(' - ')[0].strip()
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            sql_query = "SELECT PROPRECIOUM FROM PRODUCTOS WHERE TRIM(PROCODIGO) = :1"
            cursor.execute(sql_query, {'1': procodigo})
            producto = cursor.fetchone()
            if producto:
                valor_input.setReadOnly(False)
                valor_input.setText(str(producto[0]))
                valor_input.setReadOnly(True)
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', 'No se encontraron datos del producto.')
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo obtener el valor del producto: {error.message}')

    def agregar_producto(self, facnumero, procodigo, cantidad, valor):
        try:
            procodigo = procodigo.split(' - ')[0].strip()
            pxf_cantidad = cantidad
            pxf_valor = valor
            if not pxf_cantidad or not pxf_valor:
                QtWidgets.QMessageBox.critical(self, 'Error', 'La cantidad y el valor no pueden estar vacíos.')
                return
            pxf_subtotal = float(pxf_cantidad) * float(pxf_valor)
            pxf_status = "ACT"
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO PXF (FACNUMERO, PROCODIGO, PXFCANTIDAD, PXFVALOR, PXFSUBTOTAL, PXFSTATUS)
                VALUES (:1, :2, :3, :4, :5, :6)
            """, (facnumero, procodigo, pxf_cantidad, pxf_valor, pxf_subtotal, pxf_status))
            connection.commit()
            cursor.close()
            connection.close()
            QtWidgets.QMessageBox.information(self, 'Éxito', 'Producto agregado a la factura exitosamente.')
            self.parent.cargar_productos(facnumero)
            self.close()
        except ValueError as ve:
            QtWidgets.QMessageBox.critical(self, 'Error de Valor', f'Error al convertir a float: {ve}')
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo agregar el producto a la factura: {error.message}')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = CrearFactura()
    ex.show()
    sys.exit(app.exec_())
