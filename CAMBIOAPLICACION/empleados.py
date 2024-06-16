# empleados.py
# -*- coding: 1252 -*-
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QMessageBox, QComboBox, QDateEdit, QStackedWidget)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QDate
import cx_Oracle
import os
import sys
from datetime import datetime

class Empleados(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent  # Guardar referencia al QStackedWidget
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Empleados")
        self.setFixedSize(1280, 790)

        # Fondo
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Contenedor de t�tulo y botones
        top_container = QWidget(self)
        top_layout = QVBoxLayout(top_container)
        
        # T�tulo
        self.label_titulo = QLabel("EMPLEADOS", self)
        self.label_titulo.setStyleSheet("font: bold 24pt 'Arial'; color: #001f3f; ")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.label_titulo)

        # Botones
        botones_layout = QHBoxLayout()

        self.btn_crear_empleado = QPushButton("Crear Nuevo Empleado", self)
        self.btn_crear_empleado.clicked.connect(self.crear_nuevo_empleado)
        self.btn_crear_empleado.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_crear_empleado)

        self.btn_mostrar_todos = QPushButton("Ver Empleados", self)
        self.btn_mostrar_todos.clicked.connect(self.cargar_empleados)
        self.btn_mostrar_todos.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_mostrar_todos)

        self.btn_buscar = QPushButton("Buscar", self)
        self.btn_buscar.clicked.connect(self.buscar_empleado)
        self.btn_buscar.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_buscar)

        self.search_entry = QLineEdit(self)
        self.search_entry.setPlaceholderText("Buscar empleado...")
        self.search_entry.setStyleSheet("font: 12pt 'Arial';")
        botones_layout.addWidget(self.search_entry)

        self.btn_salir = QPushButton("Salir", self)
        self.btn_salir.clicked.connect(self.volver_anterior)
        self.btn_salir.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_salir)

        # Ajustar la distribuci�n de los botones
        botones_layout.addStretch()

        top_layout.addLayout(botones_layout)

        # Contenedor para la tabla
        table_container = QWidget(self)
        table_layout = QVBoxLayout(table_container)

        # Tabla de empleados
        self.table = QTableWidget(self)
        self.table.setColumnCount(17)
        self.table.setHorizontalHeaderLabels(["Imagen", "C�digo", "Apellido 1", "Apellido 2", "Nombre 1", "Nombre 2", "Fecha Nac.", "Sexo", "Email", "Direcci�n", "Tipo Sangre", "Sueldo", "Banco", "Cuenta", "Estado", "Eliminar", "Editar"])
        self.table.setColumnWidth(0, 70)  # Imagen
        self.table.setColumnWidth(1, 80)  # C�digo
        self.table.setColumnWidth(2, 150)  # Apellido 1
        self.table.setColumnWidth(3, 150)  # Apellido 2
        self.table.setColumnWidth(4, 150)  # Nombre 1
        self.table.setColumnWidth(5, 150)  # Nombre 2
        self.table.setColumnWidth(6, 100)  # Fecha Nac.
        self.table.setColumnWidth(7, 50)  # Sexo
        self.table.setColumnWidth(8, 200)  # Email
        self.table.setColumnWidth(9, 200)  # Direcci�n
        self.table.setColumnWidth(10, 100)  # Tipo Sangre
        self.table.setColumnWidth(11, 100)  # Sueldo
        self.table.setColumnWidth(12, 100)  # Banco
        self.table.setColumnWidth(13, 100)  # Cuenta
        self.table.setColumnWidth(14, 80)  # Estado
        self.table.setColumnWidth(15, 80)  # Eliminar
        self.table.setColumnWidth(16, 80)  # Editar
        self.table.verticalHeader().setDefaultSectionSize(60)  # Ajustar el alto de cada fila
        self.cargar_empleados()
        table_layout.addWidget(self.table)

        # A�adir los contenedores al layout principal
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
            QMessageBox.critical(self, "Error", "No se puede volver al inicio porque el window_stack no est� configurado.")

    def cargar_empleados(self):
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
            cursor.execute("SELECT EMPCODIGO, EMPAPELLIDO1, EMPAPELLIDO2, EMPNOMBRE1, EMPNOMBRE2, EMPFECHANACIMIENTO, EMPSEXO, EMPEMAIL, EMPDIRECCION, EMPTIPOSANGRE, EMPSUELDO, EMPBANCO, EMPCUENTA, EMPSTATUS, FOTO_PATH FROM EMPLEADOS")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexi�n", f"No se pudo cargar los empleados: {error.message}")
            return []

    def agregar_fila(self, row_data):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # A�adir la imagen del empleado
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

        # Botones de acci�n
        btn_eliminar = QPushButton(self)
        btn_eliminar.setIcon(QIcon("C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/borrar.png"))
        btn_eliminar.setIconSize(QSize(30, 30))
        btn_eliminar.clicked.connect(lambda: self.eliminar_empleado(row_data[0]))
        
        btn_editar = QPushButton(self)
        btn_editar.setIcon(QIcon("C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/editar.png"))
        btn_editar.setIconSize(QSize(30, 30))
        btn_editar.clicked.connect(lambda: self.editar_empleado(row_data))
        
        btn_eliminar.setStyleSheet("background-color: #ff9999; color: white;")
        btn_editar.setStyleSheet("background-color: #99e6ff; color: white;")

        self.table.setCellWidget(row_position, 15, btn_eliminar)
        self.table.setCellWidget(row_position, 16, btn_editar)

    def buscar_empleado(self):
        search_term = self.search_entry.text().lower()
        resultados = [row for row in self.obtener_datos_reales() if search_term in str(row).lower()]
        self.table.setRowCount(0)
        for row_data in resultados:
            self.agregar_fila(row_data)

    def crear_nuevo_empleado(self):
        self.editar_empleado(None)

    def editar_empleado(self, row_data):
        edit_window = QWidget()
        edit_window.setWindowTitle("Editar Empleado" if row_data else "Crear Nuevo Empleado")
        edit_window.setFixedSize(600, 800)

        layout = QVBoxLayout()

        # Fondo para edit_window
        background_label = QLabel(edit_window)
        background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        background_label.setPixmap(background_pixmap)
        background_label.setScaledContents(True)
        background_label.setGeometry(0, 0, 600, 800)

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

        add_form_item("C�digo", row_data[0] if row_data else "")
        add_form_item("Apellido 1", row_data[1] if row_data else "")
        add_form_item("Apellido 2", row_data[2] if row_data else "")
        add_form_item("Nombre 1", row_data[3] if row_data else "")
        add_form_item("Nombre 2", row_data[4] if row_data else "")

        fecha_nac = QDateEdit(edit_window)
        fecha_nac.setCalendarPopup(True)
        if row_data and row_data[5]:
            fecha_nac.setDate(QDate(row_data[5].year, row_data[5].month, row_data[5].day))
        add_form_item("Fecha de Nacimiento", widget=fecha_nac)

        sexo = QComboBox(edit_window)
        sexo.addItems(["M", "F"])
        if row_data and row_data[6]:
            sexo.setCurrentText(row_data[6])
        add_form_item("Sexo", widget=sexo)

        add_form_item("Email", row_data[7] if row_data else "")
        add_form_item("Direcci�n", row_data[8] if row_data else "")

        tipo_sangre = QComboBox(edit_window)
        tipo_sangre.addItems(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-', 'RH+', 'RH-'])
        if row_data and row_data[9]:
            tipo_sangre.setCurrentText(row_data[9])
        add_form_item("Tipo de Sangre", widget=tipo_sangre)

        sueldo = QLineEdit(edit_window)
        if row_data and row_data[10]:
            sueldo.setText(str(row_data[10]))
        add_form_item("Sueldo", widget=sueldo)

        add_form_item("Banco", row_data[11] if row_data else "")
        add_form_item("Cuenta", row_data[12] if row_data else "")

        estado = QComboBox(edit_window)
        estado.addItems(["ACT", "INA"])
        if row_data and row_data[13]:
            estado.setCurrentText(row_data[13])
        add_form_item("Estado", widget=estado)

        lbl_img = QLabel("Imagen:", edit_window)
        lbl_img.setStyleSheet(f"color: {label_fg}; font: bold 12pt 'Arial';")
        img_path = QLineEdit(edit_window)
        img_path.setStyleSheet(f"background-color: {entry_bg}; font: 12pt 'Arial';")
        img_path.setText(row_data[14] if row_data else "")
        btn_img = QPushButton("Seleccionar Imagen", edit_window)
        btn_img.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        btn_img.clicked.connect(lambda: self.seleccionar_imagen(img_path))

        form_layout.addWidget(lbl_img)
        form_layout.addWidget(img_path)
        form_layout.addWidget(btn_img)

        layout.addLayout(form_layout)

        def guardar():
            # Validaciones
            if sueldo.text().strip() == "" or float(sueldo.text().strip()) < 0:
                QMessageBox.critical(edit_window, "Error", "El sueldo no puede estar vac�o ni ser negativo.")
                return

            if fecha_nac.date() > QDate.currentDate():
                QMessageBox.critical(edit_window, "Error", "La fecha de nacimiento no puede ser mayor a la fecha actual.")
                return

            nuevo_dato = (
                form_items["C�digo"].text().strip(),
                form_items["Apellido 1"].text().strip(),
                form_items["Apellido 2"].text().strip(),
                form_items["Nombre 1"].text().strip(),
                form_items["Nombre 2"].text().strip(),
                fecha_nac.date().toString('yyyy-MM-dd'),
                sexo.currentText(),
                form_items["Email"].text().strip(),
                form_items["Direcci�n"].text().strip(),
                tipo_sangre.currentText(),
                form_items["Sueldo"].text().strip(),
                form_items["Banco"].text().strip(),
                form_items["Cuenta"].text().strip(),
                estado.currentText(),
                img_path.text().strip() if img_path.text().strip() else 'path/to/default/image.png'
            )

            if row_data:
                self.actualizar_empleado_en_db(nuevo_dato)
            else:
                self.insertar_empleado_en_db(nuevo_dato)

            self.cargar_empleados()
            edit_window.close()

        btn_guardar = QPushButton("Guardar", edit_window)
        btn_guardar.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        btn_guardar.clicked.connect(guardar)
        layout.addWidget(btn_guardar)

        edit_window.setLayout(layout)
        edit_window.show()

    def seleccionar_imagen(self, img_path):
        file_path = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Image Files (*.png *.jpg *.jpeg)", options=QFileDialog.DontUseNativeDialog)[0]
        if file_path:
            img_path.setText(file_path)

    def eliminar_empleado(self, codigo):
        confirm = QMessageBox.question(self, "Confirmar eliminaci�n", "�Est� seguro que desea eliminar este empleado?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                username = os.environ.get('DB_USERNAME')
                password = os.environ.get('DB_PASSWORD')
                dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='comercial')
                connection = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
                cursor = connection.cursor()
                cursor.execute("DELETE FROM EMPLEADOS WHERE EMPCODIGO = :1", (codigo,))
                connection.commit()
                cursor.close()
                connection.close()
                self.cargar_empleados()
                QMessageBox.information(self, "�xito", "El empleado se ha eliminado correctamente.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QMessageBox.critical(self, "Error", f"Error al eliminar de la base de datos: {error.message}")

    def insertar_empleado_en_db(self, empleado):
        try:
            username = os.environ.get('DB_USERNAME')
            password = os.environ.get('DB_PASSWORD')
            dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='comercial')
            connection = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO EMPLEADOS (EMPCODIGO, EMPAPELLIDO1, EMPAPELLIDO2, EMPNOMBRE1, EMPNOMBRE2, EMPFECHANACIMIENTO, EMPSEXO, EMPEMAIL, EMPDIRECCION, EMPTIPOSANGRE, EMPSUELDO, EMPBANCO, EMPCUENTA, EMPSTATUS, FOTO_PATH)
                VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7, :8, :9, :10, :11, :12, :13, :14, :15)
            """, empleado)
            connection.commit()
            cursor.close()
            connection.close()
            QMessageBox.information(self, "�xito", "El nuevo empleado se ha a�adido correctamente.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error", f"Error al insertar en la base de datos: {error.message}")

    def actualizar_empleado_en_db(self, empleado):
        try:
            username = os.environ.get('DB_USERNAME')
            password = os.environ.get('DB_PASSWORD')
            dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='comercial')
            connection = cx_Oracle.connect(user=username, password=password, dsn=dsn_tns)
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE EMPLEADOS
                SET EMPAPELLIDO1 = :1, EMPAPELLIDO2 = :2, EMPNOMBRE1 = :3, EMPNOMBRE2 = :4, EMPFECHANACIMIENTO = TO_DATE(:5, 'YYYY-MM-DD'), EMPSEXO = :6, EMPEMAIL = :7, EMPDIRECCION = :8, EMPTIPOSANGRE = :9, EMPSUELDO = :10, EMPBANCO = :11, EMPCUENTA = :12, EMPSTATUS = :13, FOTO_PATH = :14
                WHERE TRIM(EMPCODIGO) = :15
            """, empleado[1:] + (empleado[0],))
            connection.commit()
            cursor.close()
            connection.close()
            QMessageBox.information(self, "�xito", "El empleado se ha actualizado correctamente.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error", f"Error al actualizar en la base de datos: {error.message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    empleados = Empleados(parent=stacked_widget)
    stacked_widget.addWidget(empleados)
    stacked_widget.show()
    sys.exit(app.exec_())
