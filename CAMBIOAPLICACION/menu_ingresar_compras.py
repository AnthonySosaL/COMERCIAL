# menu_ingresar_compras.py
# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from ingresar_compras import IngresarCompras  # Asegúrate de tener el módulo ingresar_compras en el mismo directorio

class MenuIngresarCompras(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Menú de Ingresar Compras')

        # Establecer fondo de pantalla
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)

        layout = QVBoxLayout()

        # Botón para ingresar compras
        self.ingresar_compras_btn = QPushButton('Ingresar Compras', self)
        self.ingresar_compras_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt; height: 50px; width: 300px;")
        self.ingresar_compras_btn.clicked.connect(self.ir_a_ingresar_compras)

        # Botón para salir
        self.salir_btn = QPushButton('Salir', self)
        self.salir_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt; height: 50px; width: 300px;")
        self.salir_btn.clicked.connect(self.volver_al_inicio)

        # Añadir botones al layout y centrarlos
        layout.addStretch()
        layout.addWidget(self.ingresar_compras_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.salir_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def ir_a_ingresar_compras(self):
        ingresar_compras_widget = IngresarCompras(parent=self.parent_widget, window_stack=self.window_stack)
        self.window_stack.append(self)
        self.parent_widget.addWidget(ingresar_compras_widget)
        self.parent_widget.setCurrentWidget(ingresar_compras_widget)

    def volver_al_inicio(self):
        if self.window_stack:
            ultima_ventana = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(ultima_ventana)
        else:
            self.parent_widget.setCurrentIndex(0)  # Asumiendo que la primera pantalla es el índice 0

