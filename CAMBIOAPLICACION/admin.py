# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QStackedWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os

# Importar las clases de los módulos
from productos import Productos
from clientes import Clientes
from proveedores import Proveedores
from empleados import Empleados

class AdminWindow(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent  # Guardar referencia al QStackedWidget
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Administración")
        self.setFixedSize(1280, 790)  # Asegúrate de que el tamaño sea consistente

        # Fondo
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)

        # Título
        self.label_titulo = QLabel("Seleccione un módulo para administrar", self)
        self.label_titulo.setStyleSheet("font: bold 16pt 'Arial'; color: #001f3f;")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setGeometry(340, 50, 600, 50)

        # Contenedor de botones
        btn_style = "background-color: #001f3f; color: white; font: bold 12pt 'Arial'; height: 50px; width: 200px;"

        self.btn_clientes = QPushButton("Clientes", self)
        self.btn_clientes.setStyleSheet(btn_style)
        self.btn_clientes.setGeometry(540, 150, 200, 50)
        self.btn_clientes.clicked.connect(self.abrir_clientes)

        self.btn_productos = QPushButton("Productos", self)
        self.btn_productos.setStyleSheet(btn_style)
        self.btn_productos.setGeometry(540, 220, 200, 50)
        self.btn_productos.clicked.connect(self.abrir_productos)

        self.btn_proveedores = QPushButton("Proveedores", self)
        self.btn_proveedores.setStyleSheet(btn_style)
        self.btn_proveedores.setGeometry(540, 290, 200, 50)
        self.btn_proveedores.clicked.connect(self.abrir_proveedores)

        self.btn_empleados = QPushButton("Empleados", self)
        self.btn_empleados.setStyleSheet(btn_style)
        self.btn_empleados.setGeometry(540, 360, 200, 50)
        self.btn_empleados.clicked.connect(self.abrir_empleados)

        self.btn_auditoria = QPushButton("Auditoría", self)
        self.btn_auditoria.setStyleSheet(btn_style)
        self.btn_auditoria.setGeometry(540, 430, 200, 50)
        self.btn_auditoria.clicked.connect(self.abrir_auditoria)

        self.btn_salir = QPushButton("Salir", self)
        self.btn_salir.setStyleSheet(btn_style)
        self.btn_salir.setGeometry(540, 500, 200, 50)
        self.btn_salir.clicked.connect(self.volver_al_inicio)

    def abrir_clientes(self):
        self.cambiar_ventana(Clientes)

    def abrir_productos(self):
        self.cambiar_ventana(Productos)

    def abrir_proveedores(self):
        self.cambiar_ventana(Proveedores)

    def abrir_empleados(self):
        self.cambiar_ventana(Empleados)

    def abrir_auditoria(self):
        self.cambiar_ventana(Auditoria)

    def volver_al_inicio(self):
        if self.window_stack:
            last_window = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(last_window)
        else:
            QMessageBox.critical(self, "Error", "No se puede volver al inicio porque el window_stack no está configurado.")

    def cambiar_ventana(self, modulo_clase):
        try:
            widget = modulo_clase(parent=self.parent_widget, window_stack=self.window_stack)
            self.window_stack.append(self)
            self.parent_widget.addWidget(widget)
            self.parent_widget.setCurrentWidget(widget)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cambiar de ventana: {str(e)}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QStackedWidget
    import sys

    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    admin_window = AdminWindow(parent=stacked_widget)
    stacked_widget.addWidget(admin_window)
    stacked_widget.show()
    sys.exit(app.exec_())
