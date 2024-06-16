# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
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
    import sys

    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    main_menu = MainMenu(parent=stacked_widget)
    stacked_widget.addWidget(main_menu)
    stacked_widget.show()
    sys.exit(app.exec_())
