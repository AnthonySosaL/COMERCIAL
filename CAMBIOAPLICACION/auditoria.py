# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QFileDialog,QHeaderView
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import cx_Oracle
import os
import sys

class Auditoria(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent  # Guardar referencia al QStackedWidget
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Auditoría")
        self.setFixedSize(1280, 790)

        # Fondo
        fondo = QLabel(self)
        fondo.setPixmap(QPixmap("C:/Users/antho/Downloads/fondo4.png"))
        fondo.setScaledContents(True)
        fondo.resize(1280, 790)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Contenedor para la tabla
        table_container = QWidget(self)
        table_layout = QVBoxLayout(table_container)

        # Tabla de auditoría
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Usuario", "Fecha", "Tabla", "IP", "Cambio"])
        self.table.setColumnWidth(0, 160)  # Usuario
        self.table.setColumnWidth(1, 160)  # Fecha
        self.table.setColumnWidth(2, 160)  # Tabla
        self.table.setColumnWidth(3, 160)  # IP
        self.table.setColumnWidth(4, 160)  # Cambio
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cargar_datos()
        table_layout.addWidget(self.table)

        # Añadir el contenedor de la tabla al layout principal
        main_layout.addWidget(table_container)

        # Botones
        botones_layout = QHBoxLayout()

        self.btn_salir = QPushButton("Salir", self)
        self.btn_salir.clicked.connect(self.volver_anterior)
        self.btn_salir.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_salir)

        self.btn_reporte = QPushButton("Generar Reporte", self)
        self.btn_reporte.clicked.connect(self.generar_reporte)
        self.btn_reporte.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        botones_layout.addWidget(self.btn_reporte)

        main_layout.addLayout(botones_layout)

        self.setLayout(main_layout)

    def volver_anterior(self):
        if self.window_stack:
            last_window = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(last_window)
        else:
            QMessageBox.critical(self, "Error", "No se puede volver al inicio porque el window_stack no está configurado.")

    def cargar_datos(self):
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
            cursor.execute("SELECT usuario, fecha, tabla, ip, cambio FROM auditoria")
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar los datos de auditoría: {error.message}")
            return []

    def agregar_fila(self, row_data):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for col, item in enumerate(row_data):
            self.table.setItem(row_position, col, QTableWidgetItem(str(item)))

    def generar_reporte(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            try:
                with open(file_path, "w") as file:
                    for row_id in range(self.table.rowCount()):
                        row_data = [self.table.item(row_id, col).text() for col in range(self.table.columnCount())]
                        file.write(f"{row_data}\n")
                QMessageBox.information(self, "Reporte", "Reporte generado exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo generar el reporte: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    auditoria = Auditoria()
    auditoria.show()
    sys.exit(app.exec_())
