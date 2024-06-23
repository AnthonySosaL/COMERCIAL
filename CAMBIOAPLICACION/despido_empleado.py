# despido_empleado.py
# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QStackedWidget, QDateEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDate, Qt
import cx_Oracle
import os
import datetime

class DespidoEmpleado(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):

        self.setGeometry(100, 100, 1280, 790)
        self.setWindowTitle('Despido Intempestivo de Empleado')

        # Fondo
        fondo = QLabel(self)
        fondo.setPixmap(QPixmap("C:/Users/antho/Downloads/fondo4.png"))
        fondo.setScaledContents(True)
        fondo.resize(1280, 790)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Botón de salir
        self.volver_btn = QPushButton('Salir', self)
        self.volver_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 10pt;")
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        self.volver_btn.setFixedSize(100, 40)

        # Posicionar el botón de salir en la esquina superior derecha
        self.volver_btn.move(1180, 10)  # Ajustar según sea necesario

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.emp_codigo_label = QLabel('Código de Empleado')
        self.emp_codigo_input = QComboBox()
        self.cargar_empleados()
        layout.addWidget(self.emp_codigo_label)
        layout.addWidget(self.emp_codigo_input)

        self.fecha_inicial_label = QLabel('Fecha Inicial')
        self.fecha_inicial_input = QDateEdit()
        self.fecha_inicial_input.setCalendarPopup(True)
        self.fecha_inicial_input.setDate(QDate.currentDate())
        layout.addWidget(self.fecha_inicial_label)
        layout.addWidget(self.fecha_inicial_input)

        self.fecha_final_label = QLabel('Fecha de Despido')
        self.fecha_final_input = QDateEdit()
        self.fecha_final_input.setCalendarPopup(True)
        self.fecha_final_input.setDate(QDate.currentDate())
        layout.addWidget(self.fecha_final_label)
        layout.addWidget(self.fecha_final_input)

        self.generar_nomina_btn = QPushButton('Generar Nómina de Despido', self)
        self.generar_nomina_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt;")
        self.generar_nomina_btn.clicked.connect(self.generar_nomina)
        layout.addWidget(self.generar_nomina_btn)

        # Añadir el layout al layout principal
        main_layout.addLayout(layout)

        self.setLayout(main_layout)


    def cargar_empleados(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT EMPCODIGO FROM EMPLEADOS WHERE EMPSTATUS = 'ACT'")
            empleados = cursor.fetchall()
            cursor.close()
            connection.close()
            for empleado in empleados:
                self.emp_codigo_input.addItem(empleado[0].strip())
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar los empleados: {error.message}")

    def generar_nomina(self):
        emp_codigo = self.emp_codigo_input.currentText().strip()
        fecha_inicial = self.fecha_inicial_input.date().toString('yyyy-MM-dd')
        fecha_final = self.fecha_final_input.date().toString('yyyy-MM-dd')
        fecha_actual = QDate.currentDate().toString('yyyy-MM-dd')

        # Validar que la fecha inicial no sea mayor que la fecha final
        if fecha_inicial > fecha_final:
            QMessageBox.critical(self, "Error", "La fecha inicial no puede ser mayor que la fecha final.")
            return

        # Validar que la fecha inicial no sea mayor que la fecha actual
        if fecha_inicial > fecha_actual:
            QMessageBox.critical(self, "Error", "La fecha inicial no puede ser mayor que la fecha actual.")
            return

        if not emp_codigo or not fecha_inicial or not fecha_final:
            QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
            return
        confirm = QMessageBox.question(self, "Confirmar Generación de Nómina", "¿Está seguro de que desea generar la nómina de despido para este empleado?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            # Generar código de nómina único
            cursor.execute("""
                SELECT 'NOM' || LPAD(NVL(MAX(TO_NUMBER(SUBSTR(NOMCODIGO, 4))), 0) + 1, 4, '0')
                FROM NOMINAS
            """)
            nom_codigo = cursor.fetchone()[0]

            # Convertir fechas a formato requerido
            fecha_inicial = datetime.datetime.strptime(fecha_inicial, '%Y-%m-%d').strftime('%d-%b-%y').upper()
            fecha_final = datetime.datetime.strptime(fecha_final, '%Y-%m-%d').strftime('%d-%b-%y').upper()

            # Crear la nómina
            cursor.execute("""
                INSERT INTO NOMINAS (NOMCODIGO, EMPCODIGO, NOMANIO, NOMMES, NOMFECHAINICIAL, NOMFECHAFINAL, NOMSTATUS, NOMTOTALPAGADO)
                VALUES (:1, :2, TO_CHAR(SYSDATE, 'YYYY'), TO_CHAR(SYSDATE, 'MM'), TO_DATE(:3, 'DD-MON-YY'), TO_DATE(:4, 'DD-MON-YY'), 'ACT', 0)
            """, (nom_codigo, emp_codigo, fecha_inicial, fecha_final))

            # Calcular bonificaciones y descuentos
            cursor.callproc("actualizar_nomtotalpagado", [nom_codigo])

            # Actualizar estado del empleado a 'INA'
            cursor.execute("""
                UPDATE EMPLEADOS
                SET EMPSTATUS = 'DES'
                WHERE EMPCODIGO = :1
            """, (emp_codigo,))

            # Confirmar cambios
            connection.commit()

            QMessageBox.information(self, "Éxito", f"Nómina generada exitosamente para el empleado {emp_codigo} con el código de nómina {nom_codigo}. Empleado marcado como inactivo.")

            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo generar la nómina: {error.message}")

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
    despido_empleado = DespidoEmpleado(parent=stacked_widget)
    stacked_widget.addWidget(despido_empleado)
    stacked_widget.show()
    sys.exit(app.exec_())
