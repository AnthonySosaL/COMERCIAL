# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QMessageBox, QStackedWidget
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import cx_Oracle
import os
from productos import Productos  # Asegúrate de que el módulo productos esté en el mismo directorio
from main_menu import MainMenu  # Asegúrate de que el módulo main_menu esté en el mismo directorio
from clientes import Clientes  # Importar el módulo clientes
from proveedores import Proveedores  # Importar el módulo proveedores
from empleados import Empleados  # Importar el módulo empleados
from admin import AdminWindow  # Importar el módulo admin
from administrarsys import AdministarDBA
class PrimeraPantalla(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent  # Guardar referencia al QStackedWidget
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Inicio de Sesión")
        self.setFixedSize(1280, 790)
        self.setStyleSheet("background-color: #f2dede;")

        self.bg_label = QLabel(self)
        self.bg_pixmap = QPixmap("C:/Users/antho/Downloads/fondo.png")
        self.bg_pixmap = self.bg_pixmap.scaled(1280, 790, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setGeometry(0, 0, 1280, 790)
        self.bg_label.lower()

        self.entry_username = QLineEdit(self)
        self.entry_username.setPlaceholderText("Usuario")
        self.entry_username.setText("cajero_ventas")
        self.entry_username.setStyleSheet(self.get_entry_style())
        self.entry_username.setGeometry(535, 489, 222, 27)

        self.entry_password = QLineEdit(self)
        self.entry_password.setPlaceholderText("Constraseña")
        self.entry_password.setText("ventas0602314387")
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.entry_password.setStyleSheet(self.get_entry_style())
        self.entry_password.setGeometry(535, 524, 222, 27)

        self.btn_mostrar_contrasena = QPushButton(self)
        self.mostrar_pixmap = QPixmap("C:/Users/antho/Downloads/ojo.png").scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.btn_mostrar_contrasena.setIcon(QIcon(self.mostrar_pixmap))
        self.btn_mostrar_contrasena.setIconSize(self.mostrar_pixmap.size())
        self.btn_mostrar_contrasena.setStyleSheet("background-color: #f8d7da; border: none;")
        self.btn_mostrar_contrasena.setGeometry(760, 524, 27, 27)
        self.btn_mostrar_contrasena.clicked.connect(self.mostrar_contrasena)

        self.instancia_var = QComboBox(self)
        self.instancia_opciones = ['Módulo de Administración', 'Módulo de Ventas', 'Módulo de Inventarios', 'Módulo de Compras', 'Módulo de Recursos Humanos']
        self.instancia_var.addItems(self.instancia_opciones)
        self.instancia_var.setStyleSheet("background-color: #001f3f; color: white;")
        self.instancia_var.setGeometry(535, 559, 222, 27)
        self.instancia_var.setCurrentIndex(0)

        self.btn_login = QPushButton("Log in", self)
        self.btn_login.setStyleSheet("background-color: #001f3f; color: white; font-size: 12pt;")
        self.btn_login.setGeometry(600, 609, 100, 30)
        self.btn_login.clicked.connect(self.iniciar_sesion)

        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def get_entry_style(self):
        return ("font: bold 12pt 'Helvetica';"
                "background-color: #f8d7da;"
                "border: none;"
                "color: #001f3f;"
                "border-bottom: 2px solid #f5c6cb;")

    def mostrar_contrasena(self):
        if self.entry_password.echoMode() == QLineEdit.Password:
            self.entry_password.setEchoMode(QLineEdit.Normal)
        else:
            self.entry_password.setEchoMode(QLineEdit.Password)

    def iniciar_sesion(self):
        username = self.entry_username.text().strip()
        password = self.entry_password.text().strip()
        instancia = self.instancia_var.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese el usuario y la contraseña.")
            return

        if username.upper() == 'SYS':
            if instancia != 'Módulo de Administración':
                QMessageBox.critical(self, "Acceso Denegado", "El usuario SYS solo puede acceder al Módulo de Administración.")
                return
            self.conectar_usuario_sys(username, password)
            return

        if not self.validar_usuario(username):
            QMessageBox.critical(self, "Acceso Denegado", "Usuario incorrecto.")
            return

        roles = self.validar_roles(username)

        if instancia == 'Módulo de Administración' and ('ADMIN_ROLE' in roles):
            self.conectar_usuario(username, password, roles, 'admin')
        elif instancia == 'Módulo de Ventas':
            if 'ROL_GESTION_VENTAS' in roles:
                self.conectar_usuario(username, password, roles, 'clientes')
            elif 'ROL_GESTION_VENTAS_CAJERO' in roles:
                self.conectar_usuario(username, password, roles, 'main_menu')
            else:
                QMessageBox.critical(self, "Acceso Denegado", "No tiene permisos suficientes para acceder.")
                return
        elif instancia == 'Módulo de Inventarios' and 'ROL_GESTION_INVENTARIOS' in roles:
            self.conectar_usuario(username, password, roles, 'productos')
        elif instancia == 'Módulo de Compras' and 'ROL_GESTION_COMPRAS' in roles:
            self.conectar_usuario(username, password, roles, 'proveedores')
        elif instancia == 'Módulo de Recursos Humanos' and 'ROL_GESTION_RRHH' in roles:
            self.conectar_usuario(username, password, roles, 'empleados')
        else:
            QMessageBox.critical(self, "Acceso Denegado", "No tiene permisos suficientes para acceder.")
            return

    def conectar_usuario(self, username, password, roles, modulo):
        try:
            dsn = cx_Oracle.makedsn("localhost", 1521, service_name="comercial")
            connection = cx_Oracle.connect(username, password, dsn)
            
            # Almacenar las credenciales en variables de entorno
            os.environ['DB_USERNAME'] = username
            os.environ['DB_PASSWORD'] = password

            # Navegar a la pantalla del módulo correspondiente
            if modulo == 'productos':
                productos_widget = Productos(parent=self.parent_widget, window_stack=self.window_stack)
                self.window_stack.append(self)
                self.parent_widget.addWidget(productos_widget)
                self.parent_widget.setCurrentWidget(productos_widget)
            elif modulo == 'main_menu':
                main_menu_widget = MainMenu(parent=self.parent_widget, window_stack=self.window_stack)
                self.window_stack.append(self)
                self.parent_widget.addWidget(main_menu_widget)
                self.parent_widget.setCurrentWidget(main_menu_widget)
            elif modulo == 'clientes':
                clientes_widget = Clientes(parent=self.parent_widget, window_stack=self.window_stack)
                self.window_stack.append(self)
                self.parent_widget.addWidget(clientes_widget)
                self.parent_widget.setCurrentWidget(clientes_widget)
            elif modulo == 'proveedores':
                proveedores_widget = Proveedores(parent=self.parent_widget, window_stack=self.window_stack)
                self.window_stack.append(self)
                self.parent_widget.addWidget(proveedores_widget)
                self.parent_widget.setCurrentWidget(proveedores_widget)
            elif modulo == 'empleados':
                empleados_widget = Empleados(parent=self.parent_widget, window_stack=self.window_stack)
                self.window_stack.append(self)
                self.parent_widget.addWidget(empleados_widget)
                self.parent_widget.setCurrentWidget(empleados_widget)
            elif modulo == 'admin':
                admin_widget = AdminWindow(parent=self.parent_widget, window_stack=self.window_stack)
                self.window_stack.append(self)
                self.parent_widget.addWidget(admin_widget)
                self.parent_widget.setCurrentWidget(admin_widget)
            else:
                # Lógica para otros módulos si existen
                pass

            QMessageBox.information(self, "Conexión Exitosa", f"Usuario '{username}' conectado exitosamente al módulo '{modulo}'.")

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 1017:  # ORA-01017: invalid username/password; logon denied
                QMessageBox.critical(self, "Error de Conexión", "Contraseña incorrecta.")
            else:
                QMessageBox.critical(self, "Error de Conexión", f"No se pudo conectar a la base de datos: {error.message}")

    def conectar_usuario_sys(self, username, password):
        try:
            dsn = cx_Oracle.makedsn("localhost", 1521, service_name="comercial")
            connection = cx_Oracle.connect(username, password, dsn, mode=cx_Oracle.SYSDBA)

            # Almacenar las credenciales en variables de entorno
            os.environ['DB_USERNAME'] = username
            os.environ['DB_PASSWORD'] = password

            # Navegar a la pantalla del módulo de administración
            admin_widget = AdministarDBA(parent=self.parent_widget, window_stack=self.window_stack)
            self.window_stack.append(self)
            self.parent_widget.addWidget(admin_widget)
            self.parent_widget.setCurrentWidget(admin_widget)

            QMessageBox.information(self, "Conexión Exitosa", f"Usuario '{username}' conectado exitosamente al módulo de administración.")

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 1017:  # ORA-01017: invalid username/password; logon denied
                QMessageBox.critical(self, "Error de Conexión", "Contraseña incorrecta.")
            else:
                QMessageBox.critical(self, "Error de Conexión", f"No se pudo conectar a la base de datos: {error.message}")

    def validar_usuario(self, username):
        connection = self.conectar_bd()
        if not connection:
            return False

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM DBA_ROLE_PRIVS WHERE GRANTEE = :username", {"username": username.upper()})
                user_exists = cursor.fetchone()[0] > 0
            return user_exists
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo validar el usuario: {error.message}")
            return False
        finally:
            connection.close()

    def validar_roles(self, username):
        connection = self.conectar_bd()
        if not connection:
            return []

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT GRANTED_ROLE FROM DBA_ROLE_PRIVS WHERE GRANTEE = :username", {"username": username.upper()})
                roles = cursor.fetchall()
                roles = [role[0] for role in roles]
            return roles
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo validar los roles: {error.message}")
            return []
        finally:
            connection.close()

    def conectar_bd(self):
        try:
            dsn = cx_Oracle.makedsn("localhost", 1521, service_name="comercial")
            connection = cx_Oracle.connect("consulta_roles", "0602314387", dsn)
            return connection
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo conectar a la base de datos: {error.message}")
            return None

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QStackedWidget
    import sys

    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    primera_pantalla = PrimeraPantalla(stacked_widget)
    stacked_widget.addWidget(primera_pantalla)
    stacked_widget.show()
    sys.exit(app.exec_())
