# -*- coding: 1252 -*-
import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from primera_pantalla import PrimeraPantalla
from main_menu import MainMenu

class Aplicacion(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Aplicación PyQt5 con Múltiples Pantallas')

        self.primera_pantalla = PrimeraPantalla(self)
        self.main_menu = MainMenu(self)

        self.addWidget(self.primera_pantalla)
        self.addWidget(self.main_menu)

        self.setCurrentWidget(self.primera_pantalla)

    def center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

def main():
    app = QApplication(sys.argv)
    aplicacion = Aplicacion()
    aplicacion.show()
    aplicacion.center()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
