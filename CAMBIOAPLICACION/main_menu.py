# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QStackedWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys

# Importar las clases de los módulos
from crearfactura import CrearFactura
from actualizar_factura import ActualizarFactura

class MainMenu(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gestión de Facturas")
        self.setFixedSize(1280, 790)

        # Fondo
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')  # Asegúrate de que la ruta sea correcta
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

        self.btn_create_invoice = QPushButton("Crear Factura", self)
        self.btn_create_invoice.setStyleSheet(btn_style)
        self.btn_create_invoice.setGeometry(540, 150, 200, 50)
        self.btn_create_invoice.clicked.connect(self.create_invoice)

        self.btn_update_invoice_status = QPushButton("Actualizar Factura", self)
        self.btn_update_invoice_status.setStyleSheet(btn_style)
        self.btn_update_invoice_status.setGeometry(540, 220, 200, 50)
        self.btn_update_invoice_status.clicked.connect(self.update_invoice_status)

        self.btn_volver_al_inicio = QPushButton("Salir", self)
        self.btn_volver_al_inicio.setStyleSheet(btn_style)
        self.btn_volver_al_inicio.setGeometry(540, 290, 200, 50)
        self.btn_volver_al_inicio.clicked.connect(self.volver_al_inicio)

    def create_invoice(self):
        nueva_ventana = CrearFactura(self.parent_widget, self.window_stack)
        self.window_stack.append(self)
        self.parent_widget.addWidget(nueva_ventana)
        self.parent_widget.setCurrentWidget(nueva_ventana)

    def update_invoice_status(self):
        nueva_ventana = ActualizarFactura(self.parent_widget, self.window_stack)
        self.window_stack.append(self)
        self.parent_widget.addWidget(nueva_ventana)
        self.parent_widget.setCurrentWidget(nueva_ventana)

    def volver_al_inicio(self):
        if self.window_stack:
            ultima_ventana = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(ultima_ventana)
        else:
            self.parent_widget.setCurrentIndex(0)  # Asumiendo que la primera pantalla es el índice 0

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QStackedWidget

    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    main_menu = MainMenu(parent=stacked_widget)
    stacked_widget.addWidget(main_menu)
    stacked_widget.show()
    sys.exit(app.exec_())
