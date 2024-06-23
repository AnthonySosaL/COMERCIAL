# gestionar_bonificaciones.py
# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QStackedWidget, QComboBox, QDialog, QDialogButtonBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import cx_Oracle
import os

class GestionarBonificaciones(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.max_hours_per_month = 160  # Horas mensuales permitidas
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 790)
        self.setWindowTitle('Gestionar Bonificaciones')
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)

        # Layout principal
        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Limitar el ancho máximo del layout izquierdo
        left_layout_widget = QWidget()
        left_layout_widget.setLayout(left_layout)
        left_layout_widget.setMaximumWidth(420)

        # Left Layout
        self.nomcodigo_label = QLabel('Código de Nómina')
        self.nomcodigo_display = QComboBox()
        self.cargar_nominas()
        self.nomcodigo_display.currentIndexChanged.connect(self.actualizar_tabla_bonificaciones)
        left_layout.addWidget(self.nomcodigo_label)
        left_layout.addWidget(self.nomcodigo_display)

        self.valor_label = QLabel('Valor')
        self.valor_bonificacion = QLineEdit()
        self.valor_bonificacion.setReadOnly(True)
        left_layout.addWidget(self.valor_label)
        left_layout.addWidget(self.valor_bonificacion)

        self.horas_extras_label = QLabel('Cantidad de Horas Extras')
        self.horas_extras_input = QLineEdit()
        self.horas_extras_input.setVisible(False)
        left_layout.addWidget(self.horas_extras_label)
        left_layout.addWidget(self.horas_extras_input)

        self.bonificaciones_label = QLabel('Bonificación')
        self.bonificaciones_menu = QComboBox()
        self.bonificaciones_menu.currentIndexChanged.connect(self.cargar_valor_bonificacion)
        self.cargar_bonificaciones()
        left_layout.addWidget(self.bonificaciones_label)
        left_layout.addWidget(self.bonificaciones_menu)

        self.status_label = QLabel('Estado')
        self.status_menu = QComboBox()
        self.status_menu.addItems(['ACT', 'INA'])
        left_layout.addWidget(self.status_label)
        left_layout.addWidget(self.status_menu)

        # Botones con ancho limitado
        button_style = "background-color: #001f3f; color: white; font-size: 12pt; height: 40px; width: 300px;"

        self.finalizar_btn = QPushButton('Finalizar Bonificación', self)
        self.finalizar_btn.setStyleSheet(button_style)
        self.finalizar_btn.clicked.connect(self.finalizar_bonificacion)
        left_layout.addWidget(self.finalizar_btn)

        self.ver_todas_btn = QPushButton('Ver Todas las Nóminas', self)
        self.ver_todas_btn.setStyleSheet(button_style)
        self.ver_todas_btn.clicked.connect(self.mostrar_todas_nominas)
        left_layout.addWidget(self.ver_todas_btn)

        left_layout.addStretch()

        # Botón de salir
        self.volver_btn = QPushButton('Salir', self)
        self.volver_btn.setStyleSheet("background-color: #001f3f; color: white; font-size: 10pt;")
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        self.volver_btn.setFixedSize(100, 40)
        left_layout.addWidget(self.volver_btn)

        main_layout.addWidget(left_layout_widget)

        # Right Layout (table)
        self.tabla_bonificaciones = QTableWidget()
        self.tabla_bonificaciones.setColumnCount(6)
        self.tabla_bonificaciones.setHorizontalHeaderLabels(['Nómina', 'Bonificación', 'Valor', 'Estado', 'Editar', 'Eliminar'])
        self.tabla_bonificaciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.tabla_bonificaciones)

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        self.actualizar_tabla_bonificaciones()

    def cargar_nominas(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT NOMCODIGO FROM NOMINAS")
            nominas = cursor.fetchall()
            cursor.close()
            connection.close()
            for nomina in nominas:
                self.nomcodigo_display.addItem(nomina[0].strip())
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar las nóminas: {error.message}")

    def cargar_bonificaciones(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT BONCODIGO, BONDESCRIPCION FROM BONIFICACIONES")
            bonificaciones = cursor.fetchall()
            cursor.close()
            connection.close()
            for bonificacion in bonificaciones:
                self.bonificaciones_menu.addItem(f"{bonificacion[0].strip()} - {bonificacion[1].strip()}")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar las bonificaciones: {error.message}")

    def cargar_valor_bonificacion(self):
        boncodigo = self.bonificaciones_menu.currentText().split(" - ")[0].strip()
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT BONVALOR FROM BONIFICACIONES WHERE BONCODIGO = :boncodigo", {'boncodigo': boncodigo})
            bonvalor = cursor.fetchone()[0]
            self.valor_bonificacion.setText(str(bonvalor))

            # Mostrar/ocultar el campo de horas extras basado en la selección de bonificación
            if boncodigo == 'B1060':  # Suponiendo que B1060 es el código para horas extras
                self.horas_extras_label.setVisible(True)
                self.horas_extras_input.setVisible(True)
            else:
                self.horas_extras_label.setVisible(False)
                self.horas_extras_input.setVisible(False)

            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar el valor de la bonificación: {error.message}")

    def finalizar_bonificacion(self):
        confirm = QMessageBox.question(self, "Confirmar Bonificación", "¿Está seguro de que desea finalizar la bonificación?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        try:
            nomcodigo = self.nomcodigo_display.currentText().strip()
            boncodigo = self.bonificaciones_menu.currentText().split(" - ")[0].strip()
            valor = self.valor_bonificacion.text().strip()
            status = self.status_menu.currentText().strip().upper()

            if boncodigo == 'B1060':  # Suponiendo que B1060 es el código para horas extras
                horas_extras = self.horas_extras_input.text().strip()
                if horas_extras.isdigit():
                    if int(horas_extras) < 0:
                        raise ValueError("La cantidad de horas extras no puede ser negativa.")
                    if int(horas_extras) > self.max_hours_per_month:
                        QMessageBox.critical(self, "Error", f"La cantidad de horas extras no puede exceder las {self.max_hours_per_month} horas mensuales.")
                        return
                    valor = float(valor) * int(horas_extras)
                else:
                    QMessageBox.critical(self, "Error", "La cantidad de horas extras debe ser un número.")
                    return

            if not nomcodigo or not boncodigo or not valor:
                QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
                return

            valor_float = float(valor)
            if valor_float < 0:
                raise ValueError("El valor no puede ser negativo.")

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            # Insertar en BXN
            cursor.execute("""
                INSERT INTO BXN (BONCODIGO, NOMCODIGO, BXNVALOR, BXNSTATUS)
                VALUES (:1, :2, :3, :4)
            """, (boncodigo, nomcodigo, valor_float, status))

            # Actualizar el total pagado en la nómina
            cursor.callproc("actualizar_nomtotalpagado", [nomcodigo])

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Bonificación finalizada exitosamente.")
            self.actualizar_tabla_bonificaciones()
        except ValueError as ve:
            QMessageBox.critical(self, "Error de Valor", str(ve))
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 1:  # Unique constraint violation
                QMessageBox.critical(self, "Error de Conexión", "La bonificación ya existe para esta nómina.")
            else:
                QMessageBox.critical(self, "Error de Conexión", f"No se pudo finalizar la bonificación: {error.message}")

    def actualizar_tabla_bonificaciones(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            nom_codigo = self.nomcodigo_display.currentText().strip()
            if nom_codigo:
                cursor.execute("""
                    SELECT BXN.NOMCODIGO, BONIFICACIONES.BONCODIGO, BXN.BXNVALOR, BXN.BXNSTATUS
                    FROM BXN
                    JOIN BONIFICACIONES ON BXN.BONCODIGO = BONIFICACIONES.BONCODIGO
                    WHERE BXN.NOMCODIGO = :nom_codigo
                """, {'nom_codigo': nom_codigo})
            else:
                cursor.execute("""
                    SELECT BXN.NOMCODIGO, BONIFICACIONES.BONCODIGO, BXN.BXNVALOR, BXN.BXNSTATUS
                    FROM BXN
                    JOIN BONIFICACIONES ON BXN.BONCODIGO = BONIFICACIONES.BONCODIGO
                """)
            bonificaciones = cursor.fetchall()
            cursor.close()
            connection.close()

            self.tabla_bonificaciones.setRowCount(len(bonificaciones))
            for row, bonificacion in enumerate(bonificaciones):
                self.tabla_bonificaciones.setItem(row, 0, QTableWidgetItem(bonificacion[0]))
                self.tabla_bonificaciones.setItem(row, 1, QTableWidgetItem(bonificacion[1]))
                self.tabla_bonificaciones.setItem(row, 2, QTableWidgetItem(str(bonificacion[2])))
                self.tabla_bonificaciones.setItem(row, 3, QTableWidgetItem(bonificacion[3]))

                # Añadir botón de editar
                btn_editar = QPushButton()
                btn_editar.setIcon(QIcon('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/editar.png'))
                btn_editar.clicked.connect(lambda _, b=bonificacion: self.editar_bonificacion(b))
                self.tabla_bonificaciones.setCellWidget(row, 4, btn_editar)

                # Añadir botón de eliminar
                btn_eliminar = QPushButton()
                btn_eliminar.setIcon(QIcon('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/borrar.png'))
                btn_eliminar.clicked.connect(lambda _, b=bonificacion: self.eliminar_bonificacion(b))
                self.tabla_bonificaciones.setCellWidget(row, 5, btn_eliminar)

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo actualizar la tabla de bonificaciones: {error.message}")

    def editar_bonificacion(self, bonificacion):
        nomcodigo, boncodigo, valor, status = bonificacion

        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Bonificación")

        layout = QVBoxLayout(dialog)

        nuevo_valor_label = QLabel('Ingrese el nuevo valor:', dialog)
        nuevo_valor_input = QLineEdit(dialog)
        nuevo_valor_input.setText(str(valor))
        layout.addWidget(nuevo_valor_label)
        layout.addWidget(nuevo_valor_input)

        nuevo_status_label = QLabel('Seleccione el nuevo estado:', dialog)
        nuevo_status_input = QComboBox(dialog)
        nuevo_status_input.addItems(['ACT', 'INA'])
        nuevo_status_input.setCurrentText(status)
        layout.addWidget(nuevo_status_label)
        layout.addWidget(nuevo_status_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            confirm = QMessageBox.question(self, "Confirmar Edición", "¿Está seguro de que desea editar la bonificación?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.No:
                return
            nuevo_valor = nuevo_valor_input.text().strip()
            nuevo_status = nuevo_status_input.currentText().strip()

            if nuevo_valor:
                try:
                    nuevo_valor_float = float(nuevo_valor)
                    if nuevo_valor_float < 0:
                        raise ValueError("El valor no puede ser negativo.")

                    connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
                    cursor = connection.cursor()
                    cursor.execute("""
                        UPDATE BXN
                        SET BXNVALOR = :1, BXNSTATUS = :2
                        WHERE NOMCODIGO = :3 AND BONCODIGO = :4
                    """, (nuevo_valor_float, nuevo_status, nomcodigo, boncodigo))

                    cursor.callproc("actualizar_nomtotalpagado", [nomcodigo])

                    connection.commit()
                    cursor.close()
                    connection.close()

                    QMessageBox.information(self, "Éxito", "Bonificación editada exitosamente.")
                    self.actualizar_tabla_bonificaciones()
                except ValueError as ve:
                    QMessageBox.critical(self, "Error de Valor", str(ve))
                except cx_Oracle.DatabaseError as e:
                    error, = e.args
                    QMessageBox.critical(self, "Error de Conexión", f"No se pudo editar la bonificación: {error.message}")

    def eliminar_bonificacion(self, bonificacion):
        nomcodigo, boncodigo, _, _ = bonificacion
        confirm = QMessageBox.question(self, "Confirmar Eliminación", "¿Está seguro de que desea eliminar la bonificación?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE BXN
                SET BXNSTATUS = 'INA'
                WHERE NOMCODIGO = :1 AND BONCODIGO = :2
            """, (nomcodigo, boncodigo))

            cursor.callproc("actualizar_nomtotalpagado", [nomcodigo])

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Bonificación eliminada exitosamente.")
            self.actualizar_tabla_bonificaciones()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo eliminar la bonificación: {error.message}")

    def mostrar_todas_nominas(self):
        self.nomcodigo_display.setCurrentIndex(-1)
        self.actualizar_tabla_bonificaciones()

    def volver_al_inicio(self):
        if self.window_stack:
            ultima_ventana = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(ultima_ventana)
        else:
            self.parent_widget.setCurrentIndex(0)  # Asumiendo que la primera pantalla es el índice 0

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    gestionar_bonificaciones = GestionarBonificaciones(parent=stacked_widget)
    stacked_widget.addWidget(gestionar_bonificaciones)
    stacked_widget.show()
    sys.exit(app.exec_())
