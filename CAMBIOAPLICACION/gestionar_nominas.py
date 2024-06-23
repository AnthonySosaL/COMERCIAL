# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QStackedWidget, QComboBox, QDateEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDate
import cx_Oracle
import os
import datetime

class GestionarNominas(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 790)
        self.setWindowTitle('Gestionar Nóminas')

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
        self.nomcodigo_label = QLabel('Código de Nómina')
        self.nomcodigo_display = QLineEdit()
        self.nomcodigo_display.setReadOnly(True)
        left_layout.addWidget(self.nomcodigo_label)
        left_layout.addWidget(self.nomcodigo_display)

        self.empleado_label = QLabel('Empleado')
        self.empleados_menu = QComboBox()
        self.cargar_empleados()
        left_layout.addWidget(self.empleado_label)
        left_layout.addWidget(self.empleados_menu)

        self.anio_label = QLabel('Año')
        self.anio_input = QLineEdit()
        left_layout.addWidget(self.anio_label)
        left_layout.addWidget(self.anio_input)

        self.mes_label = QLabel('Mes')
        self.mes_input = QLineEdit()
        left_layout.addWidget(self.mes_label)
        left_layout.addWidget(self.mes_input)

        self.fecha_inicial_label = QLabel('Fecha Inicial')
        self.fecha_inicial_input = QDateEdit()
        self.fecha_inicial_input.setCalendarPopup(True)
        left_layout.addWidget(self.fecha_inicial_label)
        left_layout.addWidget(self.fecha_inicial_input)

        self.fecha_final_label = QLabel('Fecha Final')
        self.fecha_final_input = QDateEdit()
        self.fecha_final_input.setCalendarPopup(True)
        left_layout.addWidget(self.fecha_final_label)
        left_layout.addWidget(self.fecha_final_input)

        self.status_label = QLabel('Estado')
        self.status_menu = QComboBox()
        self.status_menu.addItems(['ACT', 'INA'])
        left_layout.addWidget(self.status_label)
        left_layout.addWidget(self.status_menu)

        button_style = "background-color: #001f3f; color: white; font-size: 12pt; height: 40px; width: 300px;"

        self.finalizar_btn = QPushButton('Finalizar Nómina', self)
        self.finalizar_btn.setStyleSheet(button_style)
        self.finalizar_btn.clicked.connect(self.finalizar_nomina)
        left_layout.addWidget(self.finalizar_btn)

        left_layout.addStretch()

        # Botón de salir
        self.volver_btn = QPushButton('Salir', self)
        self.volver_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 10pt;")
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        self.volver_btn.setFixedSize(100, 40)
        left_layout.addWidget(self.volver_btn)

        layout.addWidget(left_layout_widget)

        # Right Layout (table)
        self.tabla_nominas = QTableWidget()
        self.tabla_nominas.setColumnCount(8)
        self.tabla_nominas.setHorizontalHeaderLabels(['Código', 'Empleado', 'Año', 'Mes', 'Fecha Inicial', 'Fecha Final', 'Estado', 'Total Pagado'])
        self.tabla_nominas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.tabla_nominas)

        layout.addLayout(right_layout)

        self.setLayout(layout)
        self.obtener_codigo_nomina()
        self.actualizar_tabla_nominas()

    def obtener_codigo_nomina(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT 'NOM' || LPAD(NVL(MAX(TO_NUMBER(SUBSTR(NOMCODIGO, 4))), 0) + 1, 4, '0')
                FROM NOMINAS
            """)
            nuevo_nomcodigo = cursor.fetchone()[0]
            self.nomcodigo_display.setText(nuevo_nomcodigo)
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo obtener el código de nómina: {error.message}")

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

    def finalizar_nomina(self):
        confirm = QMessageBox.question(self, "Confirmar Nómina", "¿Está seguro de que desea finalizar la nómina?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        try:
            nomcodigo = self.nomcodigo_display.text().strip()
            empcodigo = self.empleados_menu.currentText().split(" - ")[0].strip()
            anio = self.anio_input.text().strip()
            mes = self.mes_input.text().strip()
            fecha_inicial = self.fecha_inicial_input.date().toString('yyyy-MM-dd')
            fecha_final = self.fecha_final_input.date().toString('yyyy-MM-dd')

            # Convertir a datetime en Python y luego formatear en inglés
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, '%Y-%m-%d').strftime('%d-%b-%y')
            fecha_final = datetime.datetime.strptime(fecha_final, '%Y-%m-%d').strftime('%d-%b-%y')

            status = self.status_menu.currentText().strip().upper()

            if fecha_inicial > fecha_final:
                QMessageBox.critical(self, "Error", "La fecha inicial no puede ser mayor que la fecha final.")
                return

            # Validar que la fecha inicial no sea mayor que la fecha actual
            if fecha_inicial > datetime.datetime.now().strftime('%d-%b-%y').upper():
                QMessageBox.critical(self, "Error", "La fecha inicial no puede ser mayor que la fecha actual.")
                return

            print(fecha_inicial)
            if not empcodigo or not anio or not mes or not fecha_inicial or not fecha_final:
                QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
                return

            if int(anio) < 1 or int(anio) > 9999:
                QMessageBox.critical(self, "Error", "El año debe estar entre 1 y 9999.")
                return

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            # Calcular el total pagado
            total_pagado = self.calcular_total_nomina(nomcodigo)
            print(fecha_inicial)
            # Insertar en NOMINAS
            cursor.execute("""
                INSERT INTO NOMINAS (NOMCODIGO, EMPCODIGO, NOMANIO, NOMMES, NOMFECHAINICIAL, NOMFECHAFINAL, NOMSTATUS, NOMTOTALPAGADO)
                VALUES (:1, :2, :3, :4, TO_DATE(:5, 'DD-MON-YY'), TO_DATE(:6, 'DD-MON-YY'), :7, :8)
            """, (nomcodigo, empcodigo, anio, mes, fecha_inicial, fecha_final, status, total_pagado))

            # Actualizar el campo NOMTOTALPAGADO
            cursor.execute("CALL actualizar_nomtotalpagado(:1)", [nomcodigo])

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Nómina finalizada exitosamente.")
            self.obtener_codigo_nomina()
            self.actualizar_tabla_nominas()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo finalizar la nómina: {error.message}")

    def actualizar_tabla_nominas(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT NOMCODIGO, EMPCODIGO, NOMANIO, NOMMES, NOMFECHAINICIAL, NOMFECHAFINAL, NOMSTATUS, NOMTOTALPAGADO
                FROM NOMINAS
            """)
            nominas = cursor.fetchall()
            cursor.close()
            connection.close()

            self.tabla_nominas.setRowCount(len(nominas))
            for row, nomina in enumerate(nominas):
                self.tabla_nominas.setItem(row, 0, QTableWidgetItem(nomina[0]))
                self.tabla_nominas.setItem(row, 1, QTableWidgetItem(nomina[1]))
                self.tabla_nominas.setItem(row, 2, QTableWidgetItem(nomina[2]))
                self.tabla_nominas.setItem(row, 3, QTableWidgetItem(nomina[3]))
                self.tabla_nominas.setItem(row, 4, QTableWidgetItem(nomina[4].strftime('%d-%b-%Y').upper() if isinstance(nomina[4], datetime.date) else str(nomina[4])))
                self.tabla_nominas.setItem(row, 5, QTableWidgetItem(nomina[5].strftime('%d-%b-%Y').upper() if isinstance(nomina[5], datetime.date) else str(nomina[5])))
                self.tabla_nominas.setItem(row, 6, QTableWidgetItem(nomina[6]))
                self.tabla_nominas.setItem(row, 7, QTableWidgetItem(str(nomina[7])))

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo actualizar la tabla de nóminas: {error.message}")

    def volver_al_inicio(self):
        if self.window_stack:
            ultima_ventana = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(ultima_ventana)
        else:
            self.parent_widget.setCurrentIndex(0)  # Asumiendo que la primera pantalla es el índice 0

    def calcular_total_nomina(self, nom_codigo):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT calcular_total_nomina(:1) FROM DUAL", [nom_codigo])
            total_nomina = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return total_nomina
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo calcular el total de la nómina: {error.message}")
            return 0

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    gestionar_nominas = GestionarNominas(parent=stacked_widget)
    stacked_widget.addWidget(gestionar_nominas)
    stacked_widget.show()
    sys.exit(app.exec_())
