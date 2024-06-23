# menu_nominas.py
# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from gestionar_nominas import GestionarNominas
from gestionar_bonificaciones import GestionarBonificaciones
from gestionar_descuentos import GestionarDescuentos
from desactivar_bonificaciones import DesactivarBonificaciones
from despido_empleado import DespidoEmpleado  # Asegúrate de que el módulo esté en el mismo directorio

class MenuNominas(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 790)
        self.setWindowTitle('Menú de Nóminas')

        # Fondo
        fondo = QLabel(self)
        fondo.setPixmap(QPixmap("C:/Users/antho/Downloads/fondo4.png"))
        fondo.setScaledContents(True)
        fondo.resize(1280, 790)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Contenedor central para los botones
        button_container = QWidget(self)
        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignCenter)

        # Botones
        btn_style = "background-color: #001f3f; color: white; font-size: 12pt; height: 50px; width: 300px;"

        self.btn_gestionar_nominas = QPushButton('Gestionar Nóminas', self)
        self.btn_gestionar_nominas.setStyleSheet(btn_style)
        self.btn_gestionar_nominas.clicked.connect(self.abrir_gestionar_nominas)
        button_layout.addWidget(self.btn_gestionar_nominas)

        self.btn_gestionar_bonificaciones = QPushButton('Gestionar Bonificaciones', self)
        self.btn_gestionar_bonificaciones.setStyleSheet(btn_style)
        self.btn_gestionar_bonificaciones.clicked.connect(self.abrir_gestionar_bonificaciones)
        button_layout.addWidget(self.btn_gestionar_bonificaciones)

        self.btn_gestionar_descuentos = QPushButton('Gestionar Descuentos', self)
        self.btn_gestionar_descuentos.setStyleSheet(btn_style)
        self.btn_gestionar_descuentos.clicked.connect(self.abrir_gestionar_descuentos)
        button_layout.addWidget(self.btn_gestionar_descuentos)

        self.btn_desactivar_bonificaciones = QPushButton('Desactivar Bonificaciones', self)
        self.btn_desactivar_bonificaciones.setStyleSheet(btn_style)
        self.btn_desactivar_bonificaciones.clicked.connect(self.abrir_desactivar_bonificaciones)
        button_layout.addWidget(self.btn_desactivar_bonificaciones)

        self.btn_despido_empleado = QPushButton('Despido Empleado', self)
        self.btn_despido_empleado.setStyleSheet(btn_style)
        self.btn_despido_empleado.clicked.connect(self.abrir_despido_empleado)
        button_layout.addWidget(self.btn_despido_empleado)

        self.btn_salir = QPushButton('Salir', self)
        self.btn_salir.setStyleSheet(btn_style)
        self.btn_salir.clicked.connect(self.volver_al_inicio)
        button_layout.addWidget(self.btn_salir)

        # Centrar los botones en el layout principal
        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def abrir_gestionar_nominas(self):
        gestionar_nominas_widget = GestionarNominas(parent=self.parent_widget, window_stack=self.window_stack)
        self.window_stack.append(self)
        self.parent_widget.addWidget(gestionar_nominas_widget)
        self.parent_widget.setCurrentWidget(gestionar_nominas_widget)

    def abrir_gestionar_bonificaciones(self):
        gestionar_bonificaciones_widget = GestionarBonificaciones(parent=self.parent_widget, window_stack=self.window_stack)
        self.window_stack.append(self)
        self.parent_widget.addWidget(gestionar_bonificaciones_widget)
        self.parent_widget.setCurrentWidget(gestionar_bonificaciones_widget)

    def abrir_gestionar_descuentos(self):
        gestionar_descuentos_widget = GestionarDescuentos(parent=self.parent_widget, window_stack=self.window_stack)
        self.window_stack.append(self)
        self.parent_widget.addWidget(gestionar_descuentos_widget)
        self.parent_widget.setCurrentWidget(gestionar_descuentos_widget)

    def abrir_desactivar_bonificaciones(self):
        desactivar_bonificaciones_widget = DesactivarBonificaciones(parent=self.parent_widget, window_stack=self.window_stack)
        self.window_stack.append(self)
        self.parent_widget.addWidget(desactivar_bonificaciones_widget)
        self.parent_widget.setCurrentWidget(desactivar_bonificaciones_widget)

    def abrir_despido_empleado(self):
        despido_empleado_widget = DespidoEmpleado(parent=self.parent_widget, window_stack=self.window_stack)
        self.window_stack.append(self)
        self.parent_widget.addWidget(despido_empleado_widget)
        self.parent_widget.setCurrentWidget(despido_empleado_widget)

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
    menu_nominas = MenuNominas(stacked_widget)
    stacked_widget.addWidget(menu_nominas)
    stacked_widget.show()
    sys.exit(app.exec_())
