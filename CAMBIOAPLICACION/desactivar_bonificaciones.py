# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import cx_Oracle
import os

class DesactivarBonificaciones(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 790)
        self.setWindowTitle('Desactivar Bonificaciones')

        # Fondo
        fondo = QLabel(self)
        fondo.setPixmap(QPixmap("C:/Users/antho/Downloads/fondo4.png"))
        fondo.setScaledContents(True)
        fondo.resize(1280, 790)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Botón de salir
        self.btn_salir = QPushButton('Salir', self)
        self.btn_salir.setStyleSheet("background-color: #001f3f; color: white; font-size: 10pt;")
        self.btn_salir.clicked.connect(self.volver_anterior_pantalla)
        self.btn_salir.setFixedSize(100, 40)

        # Posicionar el botón de salir en la esquina superior derecha
        self.btn_salir.move(1180, 10)  # Ajustar según sea necesario

        # Botón de desactivar bonificaciones
        self.desactivar_btn = QPushButton('Desactivar Bonificaciones', self)
        self.desactivar_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt; height: 50px; width: 300px;")
        self.desactivar_btn.clicked.connect(self.desactivar_bonificaciones)

        # Layout para centrar el botón de desactivar bonificaciones
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.desactivar_btn)

        # Añadir el layout al layout principal
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

    def desactivar_bonificaciones(self):
        confirm = QMessageBox.question(self, "Confirmar Desactivación", "¿Está seguro de que desea desactivar las bonificaciones de este mes?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            cursor.callproc("desactivar_bonificaciones_mes")

            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Bonificaciones desactivadas exitosamente.")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo desactivar las bonificaciones: {error.message}")

    def volver_anterior_pantalla(self):
        if self.window_stack:
            ultima_ventana = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(ultima_ventana)
        else:
            self.parent_widget.setCurrentIndex(0)  # Asumiendo que la primera pantalla es el índice 0

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    desactivar_bonificaciones = DesactivarBonificaciones()
    desactivar_bonificaciones.show()
    sys.exit(app.exec_())
