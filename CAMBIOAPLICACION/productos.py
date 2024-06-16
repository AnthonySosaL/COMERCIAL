# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QStackedWidget, QComboBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QDate
import cx_Oracle
import os
import sys

class Productos(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent  # Guardar referencia al QStackedWidget
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Productos")
        self.setFixedSize(1280, 790)

        # Fondo
        fondo = QLabel(self)
        fondo.setPixmap(QPixmap("C:/Users/antho/Downloads/fondo4.png"))
        fondo.setScaledContents(True)
        fondo.resize(1280, 790)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Contenedor de título y botones
        top_container = QWidget(self)
        top_layout = QVBoxLayout(top_container)
        
        # Título
        self.label_titulo = QLabel("PRODUCTOS", self)
        self.label_titulo.setStyleSheet("font: bold 24pt 'Arial'; color: #001f3f; ")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.label_titulo)

        # Botones
        botones_layout = QHBoxLayout()

        self.btn_crear_producto = QPushButton("Crear Nuevo Producto", self)
        self.btn_crear_producto.clicked.connect(self.crear_nuevo_producto)
        self.btn_crear_producto.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_crear_producto)

        self.btn_mostrar_todos = QPushButton("Ver Productos", self)
        self.btn_mostrar_todos.clicked.connect(self.cargar_productos)
        self.btn_mostrar_todos.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_mostrar_todos)

        self.btn_buscar = QPushButton("Buscar", self)
        self.btn_buscar.clicked.connect(self.buscar_producto)
        self.btn_buscar.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_buscar)

        self.search_entry = QLineEdit(self)
        self.search_entry.setPlaceholderText("Buscar producto...")
        self.search_entry.setStyleSheet("font: 12pt 'Arial';")
        botones_layout.addWidget(self.search_entry)

        self.btn_salir = QPushButton("Salir", self)
        self.btn_salir.clicked.connect(self.volver_anterior)
        self.btn_salir.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_salir)

        # Ajustar la distribución de los botones
        botones_layout.addStretch()

        top_layout.addLayout(botones_layout)

        # Contenedor para la tabla
        table_container = QWidget(self)
        table_layout = QVBoxLayout(table_container)

        # Tabla de productos
        self.table = QTableWidget(self)
        self.table.setColumnCount(14)
        self.table.setHorizontalHeaderLabels(["Imagen", "Código", "Descripción", "Unidad Medida", "Saldo Inicial", "Ingresos", "Egresos", "Ajustes", "Saldo Final", "Costo U.M.", "Precio U.M.", "Estado", "Eliminar", "Editar"])
        self.table.setColumnWidth(0, 70)  # Imagen
        self.table.setColumnWidth(1, 80)  # Código
        self.table.setColumnWidth(2, 150)  # Descripción
        self.table.setColumnWidth(3, 80)  # Unidad Medida
        self.table.setColumnWidth(4, 80)  # Saldo Inicial
        self.table.setColumnWidth(5, 80)  # Ingresos
        self.table.setColumnWidth(6, 80)  # Egresos
        self.table.setColumnWidth(7, 80)  # Ajustes
        self.table.setColumnWidth(8, 80)  # Saldo Final
        self.table.setColumnWidth(9, 80)  # Costo U.M.
        self.table.setColumnWidth(10, 80)  # Precio U.M.
        self.table.setColumnWidth(11, 80)  # Estado
        self.table.setColumnWidth(12, 80)  # Eliminar
        self.table.setColumnWidth(13, 80)  # Editar
        self.table.verticalHeader().setDefaultSectionSize(60)  # Ajustar el alto de cada fila
        self.cargar_productos()
        table_layout.addWidget(self.table)

        # Añadir los contenedores al layout principal
        main_layout.addWidget(top_container)
        main_layout.addWidget(table_container)

        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def volver_anterior(self):
        if self.window_stack:
            last_window = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(last_window)
        else:
            QMessageBox.critical(self, "Error", "No se puede volver al inicio porque el window_stack no está configurado.")

    def cargar_productos(self):
        self.table.setRowCount(0)
        datos = self.obtener_datos_reales()
        for row_data in datos:
            self.agregar_fila(row_data)

    def obtener_datos_reales(self):
        try:
            username = os.environ.get('DB_USERNAME')
            password = os.environ.get('DB_PASSWORD')
            dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='comercial')
            connection = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
            cursor = connection.cursor()
            cursor.execute("SELECT PROCODIGO, PRODESCRIPCION, PROUNIDADMEDIDA, PROSALDOINICIAL, PROINGRESOS, PROEGRESOS, PROAJUSTES, PROSALDOFINAL, PROCOSTOUM, PROPRECIOUM, PROSTATUS, FOTO_PATH FROM PRODUCTOS")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar los productos: {error.message}")
            return []

    def agregar_fila(self, row_data):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Añadir la imagen del producto
        foto_path = row_data[-1] if row_data[-1] else 'C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/apoyo.png'
        if os.path.exists(foto_path):
            pixmap = QPixmap(foto_path).scaled(50, 50, Qt.KeepAspectRatio)
            lbl_img = QLabel(self)
            lbl_img.setPixmap(pixmap)
            lbl_img.setAlignment(Qt.AlignCenter)  # Centrar la imagen
            self.table.setCellWidget(row_position, 0, lbl_img)
        else:
            lbl_img = QLabel("No imagen", self)
            lbl_img.setAlignment(Qt.AlignCenter)  # Centrar el texto
            self.table.setCellWidget(row_position, 0, lbl_img)

        for col, item in enumerate(row_data[:-1]):
            self.table.setItem(row_position, col + 1, QTableWidgetItem(str(item)))

        # Botones de acción
        btn_eliminar = QPushButton(self)
        btn_eliminar.setIcon(QIcon("C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/borrar.png"))
        btn_eliminar.setIconSize(QSize(30, 30))
        btn_eliminar.clicked.connect(lambda: self.eliminar_producto(row_data[0]))
        
        btn_editar = QPushButton(self)
        btn_editar.setIcon(QIcon("C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/editar.png"))
        btn_editar.setIconSize(QSize(30, 30))
        btn_editar.clicked.connect(lambda: self.editar_producto(row_data))
        
        btn_eliminar.setStyleSheet("background-color: #ff9999; color: white;")
        btn_editar.setStyleSheet("background-color: #99e6ff; color: white;")

        self.table.setCellWidget(row_position, 12, btn_eliminar)
        self.table.setCellWidget(row_position, 13, btn_editar)

    def buscar_producto(self):
        search_term = self.search_entry.text().lower()
        resultados = [row for row in self.obtener_datos_reales() if search_term in str(row).lower()]
        self.table.setRowCount(0)
        for row_data in resultados:
            self.agregar_fila(row_data)

    def crear_nuevo_producto(self):
        self.editar_producto(None)

    def editar_producto(self, row_data):
        edit_window = QWidget()
        edit_window.setWindowTitle("Editar Producto" if row_data else "Crear Nuevo Producto")
        edit_window.setFixedSize(400, 600)

        layout = QVBoxLayout()

        # Fondo para edit_window
        background_label = QLabel(edit_window)
        background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        background_label.setPixmap(background_pixmap)
        background_label.setScaledContents(True)
        background_label.setGeometry(0, 0, 400, 600)

        entry_bg = "#f0f0f0"
        label_fg = "#333333"
        entry_font = ("Arial", 12)
        label_font = ("Arial", 12, "bold")

        form_layout = QVBoxLayout()
        form_items = {}

        def add_form_item(label, initial_value="", widget=None):
            lbl = QLabel(label, edit_window)
            lbl.setStyleSheet(f"color: {label_fg}; font: bold 12pt 'Arial';")
            form_items[label] = widget if widget else QLineEdit(edit_window)
            form_items[label].setStyleSheet(f"background-color: {entry_bg}; font: 12pt 'Arial';")
            if isinstance(form_items[label], QLineEdit):
                form_items[label].setText(str(initial_value))
            form_layout.addWidget(lbl)
            form_layout.addWidget(form_items[label])

        add_form_item("Código", row_data[0] if row_data else "")
        add_form_item("Descripción", row_data[1] if row_data else "")
        add_form_item("Unidad de Medida", row_data[2] if row_data else "")
        add_form_item("Saldo Inicial", row_data[3] if row_data else "")
        add_form_item("Ingresos", row_data[4] if row_data else "")
        add_form_item("Egresos", row_data[5] if row_data else "")
        add_form_item("Ajustes", row_data[6] if row_data else "")
        add_form_item("Saldo Final", row_data[7] if row_data else "")
        add_form_item("Costo U.M.", row_data[8] if row_data else "")
        add_form_item("Precio U.M.", row_data[9] if row_data else "")
        add_form_item("Estado", row_data[10] if row_data else "")

        lbl_img = QLabel("Imagen:", edit_window)
        lbl_img.setStyleSheet(f"color: {label_fg}; font: bold 12pt 'Arial';")
        img_path = QLineEdit(edit_window)
        img_path.setStyleSheet(f"background-color: {entry_bg}; font: 12pt 'Arial';")
        img_path.setText(row_data[11] if row_data else "")
        btn_img = QPushButton("Seleccionar Imagen", edit_window)
        btn_img.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        btn_img.clicked.connect(lambda: self.seleccionar_imagen(img_path))

        form_layout.addWidget(lbl_img)
        form_layout.addWidget(img_path)
        form_layout.addWidget(btn_img)

        layout.addLayout(form_layout)

        def guardar():
            # Validaciones
            if float(form_items["Saldo Inicial"].text().strip()) < 0 or float(form_items["Ingresos"].text().strip()) < 0 or float(form_items["Egresos"].text().strip()) < 0 or float(form_items["Ajustes"].text().strip()) < 0 or float(form_items["Saldo Final"].text().strip()) < 0 or float(form_items["Costo U.M."].text().strip()) < 0 or float(form_items["Precio U.M."].text().strip()) < 0:
                QMessageBox.critical(edit_window, "Error", "Los valores numéricos no pueden ser negativos.")
                return

            nuevo_dato = (
                form_items["Código"].text().strip(),
                form_items["Descripción"].text().strip(),
                form_items["Unidad de Medida"].text().strip(),
                form_items["Saldo Inicial"].text().strip(),
                form_items["Ingresos"].text().strip(),
                form_items["Egresos"].text().strip(),
                form_items["Ajustes"].text().strip(),
                form_items["Saldo Final"].text().strip(),
                form_items["Costo U.M."].text().strip(),
                form_items["Precio U.M."].text().strip(),
                form_items["Estado"].text().strip(),
                img_path.text().strip() if img_path.text().strip() else 'path/to/default/image.png'
            )

            if row_data:
                self.actualizar_producto_en_db(nuevo_dato)
            else:
                self.insertar_producto_en_db(nuevo_dato)

            self.cargar_productos()
            edit_window.close()

        btn_guardar = QPushButton("Guardar", edit_window)
        btn_guardar.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        btn_guardar.clicked.connect(guardar)
        layout.addWidget(btn_guardar)

        edit_window.setLayout(layout)
        edit_window.show()

    def seleccionar_imagen(self, img_path):
        file_path = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Image Files (*.png *.jpg *.jpeg)")[0]
        if file_path:
            img_path.setText(file_path)

    def eliminar_producto(self, codigo):
        confirm = QMessageBox.question(self, "Confirmar eliminación", "¿Está seguro que desea eliminar este producto?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                username = os.environ.get('DB_USERNAME')
                password = os.environ.get('DB_PASSWORD')
                dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='comercial')
                connection = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
                cursor = connection.cursor()
                cursor.execute("DELETE FROM PRODUCTOS WHERE PROCODIGO = :1", (codigo,))
                connection.commit()
                cursor.close()
                connection.close()
                self.cargar_productos()
                QMessageBox.information(self, "Éxito", "El producto se ha eliminado correctamente.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QMessageBox.critical(self, "Error", f"Error al eliminar de la base de datos: {error.message}")

    def insertar_producto_en_db(self, producto):
        try:
            username = os.environ.get('DB_USERNAME')
            password = os.environ.get('DB_PASSWORD')
            dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='comercial')
            connection = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO PRODUCTOS (PROCODIGO, PRODESCRIPCION, PROUNIDADMEDIDA, PROSALDOINICIAL, PROINGRESOS, PROEGRESOS, PROAJUSTES, PROSALDOFINAL, PROCOSTOUM, PROPRECIOUM, PROSTATUS, FOTO_PATH)
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)
            """, producto)
            connection.commit()
            cursor.close()
            connection.close()
            QMessageBox.information(self, "Éxito", "El nuevo producto se ha añadido correctamente.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error", f"Error al insertar en la base de datos: {error.message}")

    def actualizar_producto_en_db(self, producto):
        try:
            username = os.environ.get('DB_USERNAME')
            password = os.environ.get('DB_PASSWORD')
            dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='comercial')
            connection = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE PRODUCTOS
                SET PRODESCRIPCION = :1, PROUNIDADMEDIDA = :2, PROSALDOINICIAL = :3, PROINGRESOS = :4, PROEGRESOS = :5, PROAJUSTES = :6, PROSALDOFINAL = :7, PROCOSTOUM = :8, PROPRECIOUM = :9, PROSTATUS = :10, FOTO_PATH = :11
                WHERE TRIM(PROCODIGO) = :12
            """, producto[1:] + (producto[0],))
            connection.commit()
            cursor.close()
            connection.close()
            QMessageBox.information(self, "Éxito", "El producto se ha actualizado correctamente.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error", f"Error al actualizar en la base de datos: {error.message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    productos = Productos(parent=stacked_widget)
    stacked_widget.addWidget(productos)
    stacked_widget.show()
    sys.exit(app.exec_())
