# -*- coding: 1252 -*-
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget,
                             QLineEdit, QPushButton, QCheckBox, QMessageBox, QComboBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import cx_Oracle
import sys
import os

class AdministarDBA(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.connection = None
        self.initUI()
        self.conectar_db()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 790)
        self.setWindowTitle('Administrar DBA')
        
        # Fondo
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)
        
        layout = QVBoxLayout(self)
        
        # Sección de Rol
        role_layout = QHBoxLayout()
        
        role_label = QLabel("Nombre del Rol:")
        role_label.setStyleSheet("font: bold 12pt 'Arial'; color: #001f3f; background-color: #f2dede;")
        self.role_entry = QLineEdit(self)
        self.role_entry.setStyleSheet("font: 12pt 'Arial'; background-color: #f8d7da;")
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_entry)
        
        layout.addLayout(role_layout)

        # Sección de Tabla
        table_layout = QHBoxLayout()
        
        table_label = QLabel("Nombre de la Tabla:")
        table_label.setStyleSheet("font: bold 12pt 'Arial'; color: #001f3f; background-color: #f2dede;")
        self.table_entry = QLineEdit(self)
        self.table_entry.setStyleSheet("font: 12pt 'Arial'; background-color: #f8d7da;")
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.table_entry)
        
        layout.addLayout(table_layout)

        # Sección de Permisos
        permissions_layout = QHBoxLayout()
        
        permissions_label = QLabel("Permisos:")
        permissions_label.setStyleSheet("font: bold 12pt 'Arial'; color: #001f3f; background-color: #f2dede;")
        self.select_cb = QCheckBox("SELECT", self)
        self.select_cb.setStyleSheet("background-color: #f2dede;")
        self.insert_cb = QCheckBox("INSERT", self)
        self.insert_cb.setStyleSheet("background-color: #f2dede;")
        self.update_cb = QCheckBox("UPDATE", self)
        self.update_cb.setStyleSheet("background-color: #f2dede;")
        self.delete_cb = QCheckBox("DELETE", self)
        self.delete_cb.setStyleSheet("background-color: #f2dede;")
        
        permissions_layout.addWidget(permissions_label)
        permissions_layout.addWidget(self.select_cb)
        permissions_layout.addWidget(self.insert_cb)
        permissions_layout.addWidget(self.update_cb)
        permissions_layout.addWidget(self.delete_cb)
        
        layout.addLayout(permissions_layout)

        # Botones para roles y permisos
        role_buttons_layout = QHBoxLayout()
        
        self.create_role_btn = QPushButton("Crear Rol", self)
        self.create_role_btn.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        self.create_role_btn.clicked.connect(self.crear_rol)
        self.assign_permissions_btn = QPushButton("Asignar Permisos", self)
        self.assign_permissions_btn.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        self.assign_permissions_btn.clicked.connect(self.asignar_permisos)
        self.delete_role_btn = QPushButton("Eliminar Rol", self)
        self.delete_role_btn.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        self.delete_role_btn.clicked.connect(self.eliminar_rol)
        
        role_buttons_layout.addWidget(self.create_role_btn)
        role_buttons_layout.addWidget(self.assign_permissions_btn)
        role_buttons_layout.addWidget(self.delete_role_btn)
        
        layout.addLayout(role_buttons_layout)

        # Sección de usuario
        user_layout = QHBoxLayout()
        
        user_label = QLabel("Nombre de Usuario:")
        user_label.setStyleSheet("font: bold 12pt 'Arial'; color: #001f3f; background-color: #f2dede;")
        self.user_entry = QLineEdit(self)
        self.user_entry.setStyleSheet("font: 12pt 'Arial'; background-color: #f8d7da;")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_entry)
        
        layout.addLayout(user_layout)

        # Sección de contraseña
        password_layout = QHBoxLayout()
        
        password_label = QLabel("Contraseña:")
        password_label.setStyleSheet("font: bold 12pt 'Arial'; color: #001f3f; background-color: #f2dede;")
        self.password_entry = QLineEdit(self)
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet("font: 12pt 'Arial'; background-color: #f8d7da;")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_entry)
        
        layout.addLayout(password_layout)

        # Sección de asignar rol
        role_assign_layout = QHBoxLayout()
        
        role_assign_label = QLabel("Rol a Asignar:")
        role_assign_label.setStyleSheet("font: bold 12pt 'Arial'; color: #001f3f; background-color: #f2dede;")
        self.role_assign_entry = QLineEdit(self)
        self.role_assign_entry.setStyleSheet("font: 12pt 'Arial'; background-color: #f8d7da;")
        role_assign_layout.addWidget(role_assign_label)
        role_assign_layout.addWidget(self.role_assign_entry)
        
        layout.addLayout(role_assign_layout)

        # Botones para usuario
        user_buttons_layout = QHBoxLayout()
        
        self.create_user_btn = QPushButton("Crear Usuario", self)
        self.create_user_btn.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        self.create_user_btn.clicked.connect(self.crear_usuario)
        self.assign_role_btn = QPushButton("Asignar Rol a Usuario", self)
        self.assign_role_btn.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        self.assign_role_btn.clicked.connect(self.asignar_rol)
        
        user_buttons_layout.addWidget(self.create_user_btn)
        user_buttons_layout.addWidget(self.assign_role_btn)
        
        layout.addLayout(user_buttons_layout)

        # Botón para eliminar usuario
        delete_user_layout = QHBoxLayout()
        
        delete_user_label = QLabel("Eliminar Usuario:")
        delete_user_label.setStyleSheet("font: bold 12pt 'Arial'; color: #001f3f; background-color: #f2dede;")
        self.delete_user_entry = QLineEdit(self)
        self.delete_user_entry.setStyleSheet("font: 12pt 'Arial'; background-color: #f8d7da;")
        delete_user_layout.addWidget(delete_user_label)
        delete_user_layout.addWidget(self.delete_user_entry)
        
        self.delete_user_btn = QPushButton("Eliminar Usuario", self)
        self.delete_user_btn.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        self.delete_user_btn.clicked.connect(self.eliminar_usuario)
        
        layout.addLayout(delete_user_layout)
        layout.addWidget(self.delete_user_btn)

        # Botón para volver
        self.back_btn = QPushButton("Volver", self)
        self.back_btn.setStyleSheet("background-color: #001f3f; color: white; font: bold 12pt 'Arial';")
        self.back_btn.clicked.connect(self.volver_al_inicio)
        layout.addWidget(self.back_btn)

    def conectar_db(self):
        try:
            dsn = cx_Oracle.makedsn("localhost", 1521, service_name="comercial")
            self.connection = cx_Oracle.connect("sys", "password", dsn, mode=cx_Oracle.SYSDBA)
            print("Conexión establecida correctamente.")
        except cx_Oracle.DatabaseError as e:
            self.connection = None
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo conectar a la base de datos: {error.message}")
            print(f"Error de Conexión: {error.message}")

    def eliminar_rol(self):
        if self.connection is None:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return
        
        role_name = self.role_entry.text().strip()
        if not role_name:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese el nombre del rol a eliminar.")
            return

        confirmar = QMessageBox.question(self, "Confirmar Eliminación", f"¿Está seguro de que desea eliminar el rol '{role_name}'?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmar == QMessageBox.Yes:
            cursor = self.connection.cursor()
            try:
                cursor.execute(f'DROP ROLE {role_name}')
                QMessageBox.information(self, "Resultado", f"Rol '{role_name}' eliminado correctamente.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QMessageBox.critical(self, "Error", f"Error: {error.message}")
            finally:
                cursor.close()

    def eliminar_usuario(self):
        if self.connection is None:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return
        
        username = self.delete_user_entry.text().strip()
        if not username:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese el nombre del usuario a eliminar.")
            return

        confirmar = QMessageBox.question(self, "Confirmar Eliminación", f"¿Está seguro de que desea eliminar el usuario '{username}'?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmar == QMessageBox.Yes:
            cursor = self.connection.cursor()
            try:
                cursor.callproc('ELIMINAR_USUARIO', [username])
                QMessageBox.information(self, "Resultado", f"Usuario '{username}' eliminado correctamente.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QMessageBox.critical(self, "Error", f"Error: {error.message}")
            finally:
                cursor.close()

    def crear_rol(self):
        if self.connection is None:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return
        
        role_name = self.role_entry.text().strip()
        if not role_name:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese el nombre del rol.")
            return

        confirmar = QMessageBox.question(self, "Confirmar Creación", f"¿Está seguro de que desea crear el rol '{role_name}'?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmar == QMessageBox.Yes:
            cursor = self.connection.cursor()
            try:
                cursor.callproc('CREAR_ROL', [role_name])
                QMessageBox.information(self, "Resultado", f"Rol '{role_name}' creado correctamente.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QMessageBox.critical(self, "Error", f"Error: {error.message}")
            finally:
                cursor.close()

    def obtener_permisos(self):
        permisos = []
        if self.select_cb.isChecked():
            permisos.append('SELECT')
        if self.insert_cb.isChecked():
            permisos.append('INSERT')
        if self.update_cb.isChecked():
            permisos.append('UPDATE')
        if self.delete_cb.isChecked():
            permisos.append('DELETE')
        return ', '.join(permisos)

    def asignar_permisos(self):
        if self.connection is None:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return
        
        role_name = self.role_entry.text().strip()
        table_name = self.table_entry.text().strip()
        permissions = self.obtener_permisos()

        if not role_name or not table_name or not permissions:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese todos los datos necesarios.")
            return

        confirmar = QMessageBox.question(self, "Confirmar Asignación", f"¿Está seguro de que desea asignar los permisos seleccionados al rol '{role_name}'?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmar == QMessageBox.Yes:
            cursor = self.connection.cursor()
            try:
                full_table_name = f"DB_ADMIN.{table_name}"  # Añadir el prefijo DB_ADMIN al nombre de la tabla
                cursor.callproc('ASIGNAR_PERMISOS', [role_name, full_table_name, permissions])
                QMessageBox.information(self, "Resultado", f"Permisos '{permissions}' asignados a rol '{role_name}' en la tabla '{full_table_name}' correctamente.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QMessageBox.critical(self, "Error", f"Error: {error.message}")
            finally:
                cursor.close()

    def crear_usuario(self):
        if self.connection is None:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return
    
        username = self.user_entry.text().strip()
        password = self.password_entry.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese todos los datos del usuario.")
            return

        confirmar = QMessageBox.question(self, "Confirmar Creación", f"¿Está seguro de que desea crear el usuario '{username}'?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmar == QMessageBox.Yes:
            cursor = self.connection.cursor()
            try:
                cursor.callproc('CREAR_USUARIO', [username, password])
                QMessageBox.information(self, "Resultado", f"Usuario '{username}' creado correctamente.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                if error.code == 1920:  # Código de error para "usuario ya existe"
                    QMessageBox.critical(self, "Error", f"El usuario '{username}' ya existe.")
                else:
                    QMessageBox.critical(self, "Error", f"Error: {error.message}")
            finally:
                cursor.close()


    def asignar_rol(self):
        if self.connection is None:
            QMessageBox.critical(self, "Error", "No hay conexión a la base de datos.")
            return
        
        username = self.user_entry.text().strip()
        role_name = self.role_assign_entry.text().strip()

        if not username or not role_name:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese todos los datos del usuario y el rol.")
            return

        confirmar = QMessageBox.question(self, "Confirmar Asignación", f"¿Está seguro de que desea asignar el rol '{role_name}' al usuario '{username}'?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmar == QMessageBox.Yes:
            cursor = self.connection.cursor()
            try:
                cursor.callproc('ASIGNAR_ROL', [username, role_name])
                QMessageBox.information(self, "Resultado", f"Rol '{role_name}' asignado a usuario '{username}' correctamente.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QMessageBox.critical(self, "Error", f"Error: {error.message}")
            finally:
                cursor.close()

    def volver_al_inicio(self):
        if self.parent_widget:
            self.parent_widget.setCurrentIndex(0)  # Asumiendo que PrimeraPantalla es el primer widget añadido al QStackedWidget
        else:
            QMessageBox.critical(self, "Error", "No se puede volver al inicio porque el parent_widget no está configurado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    admin_window = AdministarDBA(parent=stacked_widget)
    stacked_widget.addWidget(admin_window)
    stacked_widget.show()
    sys.exit(app.exec_())
