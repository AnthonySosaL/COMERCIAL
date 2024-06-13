# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from crearfactura import CrearFactura
from actualizar_factura import ActualizarFactura

class MainMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gestión de Facturas")
        self.setFixedSize(1280, 790)

        layout = QVBoxLayout()

        btn_create_invoice = QPushButton('Crear Factura', self)
        btn_create_invoice.clicked.connect(self.create_invoice)
        layout.addWidget(btn_create_invoice)

        btn_update_invoice_status = QPushButton('Actualizar Factura', self)
        btn_update_invoice_status.clicked.connect(self.update_invoice_status)
        layout.addWidget(btn_update_invoice_status)

        btn_volver_al_inicio = QPushButton('Salir', self)
        btn_volver_al_inicio.clicked.connect(self.volver_al_inicio)
        layout.addWidget(btn_volver_al_inicio)

        self.setLayout(layout)

    def create_invoice(self):
        self.parent_widget.addWidget(CrearFactura(self.parent_widget))
        self.parent_widget.setCurrentWidget(self.parent_widget.widget(self.parent_widget.count() - 1))

    def update_invoice_status(self):
        self.parent_widget.addWidget(ActualizarFactura(self.parent_widget))
        self.parent_widget.setCurrentWidget(self.parent_widget.widget(self.parent_widget.count() - 1))

    def volver_al_inicio(self):
        self.parent_widget.setCurrentWidget(self.parent_widget.primera_pantalla)
