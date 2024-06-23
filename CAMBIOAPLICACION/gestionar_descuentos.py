# gestionar_descuentos.py
# -*- coding: 1252 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QStackedWidget, QComboBox, QDialog, QDialogButtonBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import cx_Oracle
import os

class GestionarDescuentos(QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 790)
        self.setWindowTitle('Gestionar Descuentos')

        # Fondo
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
        self.nomcodigo_display.currentIndexChanged.connect(self.actualizar_tabla_descuentos)
        left_layout.addWidget(self.nomcodigo_label)
        left_layout.addWidget(self.nomcodigo_display)

        self.valor_label = QLabel('Valor')
        self.valor_descuento = QLineEdit()
        self.valor_descuento.setReadOnly(True)
        left_layout.addWidget(self.valor_label)
        left_layout.addWidget(self.valor_descuento)

        self.descuentos_label = QLabel('Descuento')
        self.descuentos_menu = QComboBox()
        self.descuentos_menu.currentIndexChanged.connect(self.cargar_valor_descuento)
        self.cargar_descuentos()
        left_layout.addWidget(self.descuentos_label)
        left_layout.addWidget(self.descuentos_menu)

        self.status_label = QLabel('Estado')
        self.status_menu = QComboBox()
        self.status_menu.addItems(['ACT', 'INA'])
        left_layout.addWidget(self.status_label)
        left_layout.addWidget(self.status_menu)

        # Botones con ancho limitado
        button_style = "background-color: #001f3f; color: white; font-size: 12pt; height: 40px; width: 300px;"

        self.finalizar_btn = QPushButton('Finalizar Descuento', self)
        self.finalizar_btn.setStyleSheet(button_style)
        self.finalizar_btn.clicked.connect(self.finalizar_descuento)
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
        self.tabla_descuentos = QTableWidget()
        self.tabla_descuentos.setColumnCount(6)
        self.tabla_descuentos.setHorizontalHeaderLabels(['Nómina', 'Descuento', 'Valor', 'Estado', 'Editar', 'Eliminar'])
        self.tabla_descuentos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.tabla_descuentos)

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        self.actualizar_tabla_descuentos()

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

    def cargar_descuentos(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT DESCODIGO, DESDESCRIPCION FROM DESCUENTOS")
            descuentos = cursor.fetchall()
            cursor.close()
            connection.close()
            for descuento in descuentos:
                self.descuentos_menu.addItem(f"{descuento[0].strip()} - {descuento[1].strip()}")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar los descuentos: {error.message}")

    def cargar_valor_descuento(self):
        descodigo = self.descuentos_menu.currentText().split(" - ")[0].strip()
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT DESVALOR FROM DESCUENTOS WHERE DESCODIGO = :descodigo", {'descodigo': descodigo})
            desvalor = cursor.fetchone()[0]
            self.valor_descuento.setText(str(desvalor))

            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo cargar el valor del descuento: {error.message}")

    def finalizar_descuento(self):
        confirm = QMessageBox.question(self, "Confirmar Descuento", "¿Está seguro de que desea finalizar el descuento?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        try:
            nomcodigo = self.nomcodigo_display.currentText().strip()
            descodigo = self.descuentos_menu.currentText().split(" - ")[0].strip()
            valor = self.valor_descuento.text().strip()
            status = self.status_menu.currentText().strip().upper()

            if not nomcodigo or not descodigo or not valor:
                QMessageBox.critical(self, "Error", "Todos los campos son obligatorios.")
                return

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            # Insertar en DXN
            cursor.execute("""
                INSERT INTO DXN (DESCODIGO, NOMCODIGO, DXNVALOR, DXNSTATUS)
                VALUES (:1, :2, :3, :4)
            """, (descodigo, nomcodigo, valor, status))

            # Actualizar el total pagado en la nómina
            cursor.callproc("actualizar_nomtotalpagado", [nomcodigo])

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Descuento finalizado exitosamente.")
            self.actualizar_tabla_descuentos()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 1:  # Unique constraint violation
                QMessageBox.critical(self, "Error de Conexión", "El descuento ya existe para esta nómina.")
            else:
                QMessageBox.critical(self, "Error de Conexión", f"No se pudo finalizar el descuento: {error.message}")

    def actualizar_tabla_descuentos(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            nom_codigo = self.nomcodigo_display.currentText().strip()
            if nom_codigo:
                cursor.execute("""
                    SELECT DXN.NOMCODIGO, DESCUENTOS.DESCODIGO, DXN.DXNVALOR, DXN.DXNSTATUS
                    FROM DXN
                    JOIN DESCUENTOS ON DXN.DESCODIGO = DESCUENTOS.DESCODIGO
                    WHERE DXN.NOMCODIGO = :nom_codigo
                """, {'nom_codigo': nom_codigo})
            else:
                cursor.execute("""
                    SELECT DXN.NOMCODIGO, DESCUENTOS.DESCODIGO, DXN.DXNVALOR, DXN.DXNSTATUS
                    FROM DXN
                    JOIN DESCUENTOS ON DXN.DESCODIGO = DESCUENTOS.DESCODIGO
                """)
            descuentos = cursor.fetchall()
            cursor.close()
            connection.close()

            self.tabla_descuentos.setRowCount(len(descuentos))
            for row, descuento in enumerate(descuentos):
                self.tabla_descuentos.setItem(row, 0, QTableWidgetItem(descuento[0]))
                self.tabla_descuentos.setItem(row, 1, QTableWidgetItem(descuento[1]))
                self.tabla_descuentos.setItem(row, 2, QTableWidgetItem(str(descuento[2])))
                self.tabla_descuentos.setItem(row, 3, QTableWidgetItem(descuento[3]))

                # Añadir botón de editar
                btn_editar = QPushButton()
                btn_editar.setIcon(QIcon('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/editar.png'))
                btn_editar.clicked.connect(lambda _, d=descuento: self.editar_descuento(d))
                self.tabla_descuentos.setCellWidget(row, 4, btn_editar)

                # Añadir botón de eliminar
                btn_eliminar = QPushButton()
                btn_eliminar.setIcon(QIcon('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/borrar.png'))
                btn_eliminar.clicked.connect(lambda _, d=descuento: self.eliminar_descuento(d))
                self.tabla_descuentos.setCellWidget(row, 5, btn_eliminar)

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo actualizar la tabla de descuentos: {error.message}")

    def editar_descuento(self, descuento):
        nomcodigo, descodigo, valor, status = descuento

        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Descuento")

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
            confirm = QMessageBox.question(self, "Confirmar Edición", "¿Está seguro de que desea editar el descuento?", QMessageBox.Yes | QMessageBox.No)
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
                        UPDATE DXN
                        SET DXNVALOR = :1, DXNSTATUS = :2
                        WHERE NOMCODIGO = :3 AND DESCODIGO = :4
                    """, (nuevo_valor_float, nuevo_status, nomcodigo, descodigo))

                    cursor.callproc("actualizar_nomtotalpagado", [nomcodigo])

                    connection.commit()
                    cursor.close()
                    connection.close()

                    QMessageBox.information(self, "Éxito", "Descuento editado exitosamente.")
                    self.actualizar_tabla_descuentos()
                except ValueError as ve:
                    QMessageBox.critical(self, "Error de Valor", str(ve))
                except cx_Oracle.DatabaseError as e:
                    error, = e.args
                    QMessageBox.critical(self, "Error de Conexión", f"No se pudo editar el descuento: {error.message}")

    def eliminar_descuento(self, descuento):
        nomcodigo, descodigo, _, _ = descuento
        confirm = QMessageBox.question(self, "Confirmar Eliminación", "¿Está seguro de que desea eliminar el descuento?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE DXN
                SET DXNSTATUS = 'INA'
                WHERE NOMCODIGO = :1 AND DESCODIGO = :2
            """, (nomcodigo, descodigo))

            cursor.callproc("actualizar_nomtotalpagado", [nomcodigo])

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Éxito", "Descuento eliminado exitosamente.")
            self.actualizar_tabla_descuentos()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QMessageBox.critical(self, "Error de Conexión", f"No se pudo eliminar el descuento: {error.message}")

    def mostrar_todas_nominas(self):
        self.nomcodigo_display.setCurrentIndex(-1)
        self.actualizar_tabla_descuentos()

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
    gestionar_descuentos = GestionarDescuentos(parent=stacked_widget)
    stacked_widget.addWidget(gestionar_descuentos)
    stacked_widget.show()
    sys.exit(app.exec_())
