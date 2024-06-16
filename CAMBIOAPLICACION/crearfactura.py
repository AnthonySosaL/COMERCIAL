# -*- coding: 1252 -*-
import sys
import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
import cx_Oracle
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class CrearFactura(QtWidgets.QWidget):
    def __init__(self, parent=None, window_stack=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.window_stack = window_stack if window_stack is not None else []
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Generar Factura')

        # Establecer fondo de pantalla
        self.background_label = QtWidgets.QLabel(self)
        self.background_pixmap = QtGui.QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1280, 790)

        layout = QtWidgets.QHBoxLayout()

        left_layout = QtWidgets.QVBoxLayout()
        right_layout = QtWidgets.QVBoxLayout()

        # Limitar el ancho máximo del layout izquierdo
        left_layout_widget = QtWidgets.QWidget()
        left_layout_widget.setLayout(left_layout)
        left_layout_widget.setMaximumWidth(420)

        # Left Layout - Generar Factura
        self.facnumero_label = QtWidgets.QLabel('Número de Factura')
        self.facnumero_input = QtWidgets.QLineEdit()
        self.facnumero_input.setReadOnly(True)
        left_layout.addWidget(self.facnumero_label)
        left_layout.addWidget(self.facnumero_input)

        self.facfecha_label = QtWidgets.QLabel('Fecha')
        self.facfecha_input = QtWidgets.QLineEdit()
        self.facfecha_input.setReadOnly(True)
        left_layout.addWidget(self.facfecha_label)
        left_layout.addWidget(self.facfecha_input)

        self.facdescuento_label = QtWidgets.QLabel('Descuento')
        self.facdescuento_input = QtWidgets.QLineEdit()
        left_layout.addWidget(self.facdescuento_label)
        left_layout.addWidget(self.facdescuento_input)

        self.cliente_label = QtWidgets.QLabel('Código de Cliente')
        self.clientes_menu = QtWidgets.QComboBox()
        left_layout.addWidget(self.cliente_label)
        left_layout.addWidget(self.clientes_menu)

        self.formapago_label = QtWidgets.QLabel('Forma de Pago')
        self.formapago_menu = QtWidgets.QComboBox()
        self.formapago_menu.addItems(['Efectivo', 'Crédito', 'Débito', 'Transferencia'])
        left_layout.addWidget(self.formapago_label)
        left_layout.addWidget(self.formapago_menu)

        self.generar_btn = QtWidgets.QPushButton('Generar Factura', self)
        self.generar_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.generar_btn.clicked.connect(self.generar_factura)
        left_layout.addWidget(self.generar_btn)

        self.volver_btn = QtWidgets.QPushButton('Salir', self)
        self.volver_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.volver_btn.clicked.connect(self.volver_al_inicio)
        left_layout.addWidget(self.volver_btn)

        # Right Layout - Agregar Producto a Factura
        self.factura_label = QtWidgets.QLabel('Número de Factura para Agregar Productos')
        self.factura_input = QtWidgets.QLineEdit()
        right_layout.addWidget(self.factura_label)
        right_layout.addWidget(self.factura_input)

        self.seleccionar_btn = QtWidgets.QPushButton('Seleccionar Factura', self)
        self.seleccionar_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.seleccionar_btn.clicked.connect(self.seleccionar_factura)
        right_layout.addWidget(self.seleccionar_btn)

        self.productos_label = QtWidgets.QLabel('Productos de la Factura')
        self.productos_table = QtWidgets.QTableWidget()
        self.productos_table.setColumnCount(12)  # Añadir columnas adicionales
        self.productos_table.setHorizontalHeaderLabels(["Imagen", "Código", "Descripción", "Cantidad", "Valor", "Subtotal", "IVA 0%", "IVA 8%", "IVA 15%", "Total", "Eliminar", "Editar"])
        self.productos_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        right_layout.addWidget(self.productos_label)
        right_layout.addWidget(self.productos_table)

        self.agregar_producto_btn = QtWidgets.QPushButton('Agregar Producto a Factura', self)
        self.agregar_producto_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.agregar_producto_btn.clicked.connect(self.agregar_producto_a_factura)
        right_layout.addWidget(self.agregar_producto_btn)

        # Añadir campos de resumen de factura
        self.resumen_label = QtWidgets.QLabel('Resumen de Factura')
        self.subtotal_label = QtWidgets.QLabel('Subtotal: ')
        self.iva_8_label = QtWidgets.QLabel('IVA 8%: ')
        self.iva_15_label = QtWidgets.QLabel('IVA 15%: ')
        self.total_label = QtWidgets.QLabel('Total: ')
        right_layout.addWidget(self.resumen_label)
        right_layout.addWidget(self.subtotal_label)
        right_layout.addWidget(self.iva_8_label)
        right_layout.addWidget(self.iva_15_label)
        right_layout.addWidget(self.total_label)

        self.generar_factura_btn = QtWidgets.QPushButton('Generar Factura Definitiva', self)
        self.generar_factura_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.generar_factura_btn.clicked.connect(self.generar_factura_definitiva)
        right_layout.addWidget(self.generar_factura_btn)

        layout.addWidget(left_layout_widget)
        layout.addLayout(right_layout)

        self.setLayout(layout)
        self.cargar_clientes()
        self.actualizar_numero_factura()
        self.actualizar_fecha_actual()

    def actualizar_fecha_actual(self):
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        self.facfecha_input.setText(fecha_actual)

    def volver_al_inicio(self):
        if self.window_stack:
            ultima_ventana = self.window_stack.pop()
            self.parent_widget.setCurrentWidget(ultima_ventana)
        else:
            self.parent_widget.setCurrentIndex(0)  # Asumiendo que la primera pantalla es el índice 0

    def generar_factura(self):
        try:
            facnumero = self.facnumero_input.text()
            cliente_seleccionado = self.clientes_menu.currentText()
            clicodigo = cliente_seleccionado.split(" - ")[0]
            facfecha = self.facfecha_input.text()
            facdescuento = self.facdescuento_input.text()
            facformapago = self.formapago_menu.currentText()
            facstatus = "Creada"

            facfecha_oracle = datetime.strptime(facfecha, '%Y-%m-%d').strftime('%d-%b-%Y')

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO FACTURAS (FACNUMERO, CLICODIGO, FACFECHA, FACSUBTOTAL, FACDESCUENTO, FACIVA, FACICE, FACFORMAPAGO, FACSTATUS)
                VALUES (:1, :2, TO_DATE(:3, 'DD-MON-YYYY'), 0, :4, 0, 0, :5, :6)
            """, (facnumero, clicodigo, facfecha_oracle, facdescuento, facformapago, facstatus))
            connection.commit()
            cursor.close()
            connection.close()
            QtWidgets.QMessageBox.information(self, 'Éxito', 'Factura generada exitosamente.')
            self.actualizar_numero_factura()

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo generar la factura: {error.message}')

    def actualizar_numero_factura(self):
        nuevo_numero = self.generar_numero_factura()
        self.facnumero_input.setReadOnly(False)
        self.facnumero_input.setText(nuevo_numero)
        self.facnumero_input.setReadOnly(True)

    def seleccionar_factura(self):
        facnumero = self.factura_input.text().strip()

        # Verificar si la factura existe y su estado
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
        
            # Verificar si la factura existe
            cursor.execute("""
                SELECT FACSTATUS 
                FROM FACTURAS 
                WHERE TRIM(FACNUMERO) = :1
            """, (facnumero,))
            factura = cursor.fetchone()
        
            if factura is None:
                QtWidgets.QMessageBox.warning(self, 'Advertencia', 'No existe la factura seleccionada.')
                return
        
            # Verificar el estado de la factura
            facstatus = factura[0].strip()
            if facstatus in ["Pagada", "Entregada", "Cancelada"]:
                QtWidgets.QMessageBox.warning(self, 'Advertencia', f'La factura {facnumero} tiene un estado de "{facstatus}" y no se puede modificar.')
                self.cargar_productos(facnumero, editable=False)
            else:
                self.cargar_productos(facnumero, editable=True)
        
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo verificar la factura: {error.message}')


    def agregar_producto_a_factura(self):
        facnumero = self.factura_input.text().strip()

        # Verificar si la factura tiene un estado que permite agregar productos
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT FACSTATUS 
                FROM FACTURAS 
                WHERE TRIM(FACNUMERO) = :1
            """, (facnumero,))
            factura = cursor.fetchone()

            if factura is None:
                QtWidgets.QMessageBox.warning(self, 'Advertencia', 'No existe la factura seleccionada.')
                return

            facstatus = factura[0].strip()
            if facstatus in ["Pagada", "Entregada", "Cancelada"]:
                QtWidgets.QMessageBox.warning(self, 'Advertencia', f'La factura {facnumero} tiene un estado de "{facstatus}" y no se pueden agregar productos.')
                return
        
            producto_window = ProductoWindow(facnumero, self)
            producto_window.exec_()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo verificar la factura: {error.message}')


    def cargar_clientes(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT CLICODIGO, CLINOMBRE FROM CLIENTES")
            clientes = cursor.fetchall()
            for cliente in clientes:
                self.clientes_menu.addItem(f"{cliente[0]} - {cliente[1]}")
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo cargar los clientes: {error.message}')

    def cargar_productos(self, facnumero, editable=True):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("""
                SELECT PXF.PROCODIGO, P.PRODESCRIPCION, PXF.PXFCANTIDAD, PXF.PXFVALOR, PXF.PXFSUBTOTAL, P.FOTO_PATH, PXF.PXFIVA
                FROM PXF 
                JOIN PRODUCTOS P ON PXF.PROCODIGO = P.PROCODIGO 
                WHERE TRIM(PXF.FACNUMERO) = :1
            """, (facnumero,))
            productos = cursor.fetchall()
            self.productos_table.setRowCount(0)
            for row_num, producto in enumerate(productos):
                self.productos_table.insertRow(row_num)
                for col_num, data in enumerate(producto):
                    if col_num == 5:  # Si es la columna de la imagen
                        item = QtWidgets.QTableWidgetItem()
                        if data:  # Si hay una ruta de imagen
                            pixmap = QtGui.QPixmap(data)
                        else:  # Si no hay ruta de imagen, usar imagen por defecto
                            pixmap = QtGui.QPixmap('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/apoyo.png')
                        icon = QtGui.QIcon(pixmap)
                        item.setIcon(icon)
                        self.productos_table.setItem(row_num, 0, item)
                    else:
                        self.productos_table.setItem(row_num, col_num + 1, QtWidgets.QTableWidgetItem(str(data)))

                # Calcular IVA y Total
                pxf_iva = float(producto[6])
                pxf_subtotal = float(producto[4])
                pxf_total_0 = pxf_total_8 = pxf_total_15 = 0.0
                if pxf_iva == 0.0:
                    pxf_total_0 = pxf_subtotal * 0.00
                elif pxf_iva == 8.0:
                    pxf_total_8 = pxf_subtotal * 0.08
                elif pxf_iva == 15.0:
                    pxf_total_15 = pxf_subtotal * 0.15

                pxf_total = pxf_total_0 + pxf_total_8 + pxf_total_15

                self.productos_table.setItem(row_num, 6, QtWidgets.QTableWidgetItem(str(pxf_total_0)))
                self.productos_table.setItem(row_num, 7, QtWidgets.QTableWidgetItem(str(pxf_total_8)))
                self.productos_table.setItem(row_num, 8, QtWidgets.QTableWidgetItem(str(pxf_total_15)))
                self.productos_table.setItem(row_num, 9, QtWidgets.QTableWidgetItem(str(pxf_total)))

                if editable:
                    # Añadir botón de eliminar
                    eliminar_btn = QtWidgets.QPushButton(self)
                    eliminar_pixmap = QtGui.QPixmap('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/borrar.png')
                    eliminar_icon = QtGui.QIcon(eliminar_pixmap.scaled(24, 24))
                    eliminar_btn.setIcon(eliminar_icon)
                    eliminar_btn.clicked.connect(lambda ch, row=row_num, procodigo=producto[0]: self.eliminar_producto(row, facnumero, procodigo))
                    self.productos_table.setCellWidget(row_num, 10, eliminar_btn)

                    # Añadir botón de editar
                    editar_btn = QtWidgets.QPushButton(self)
                    editar_pixmap = QtGui.QPixmap('C:/Users/antho/Music/PROYECTO3.3/PROYECTO3.3/editar.png')
                    editar_icon = QtGui.QIcon(editar_pixmap.scaled(24, 24))
                    editar_btn.setIcon(editar_icon)
                    editar_btn.clicked.connect(lambda ch, row=row_num, producto=producto: self.editar_producto(row, producto))
                    self.productos_table.setCellWidget(row_num, 11, editar_btn)
                else:
                    # Deshabilitar edición y eliminación si la factura no es editable
                    self.productos_table.setCellWidget(row_num, 10, QtWidgets.QWidget())
                    self.productos_table.setCellWidget(row_num, 11, QtWidgets.QWidget())

            self.productos_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            cursor.close()
            connection.close()

            # Actualizar los totales en el resumen
            self.actualizar_resumen()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo cargar los productos: {error.message}')

    def eliminar_producto(self, row, facnumero, procodigo):
        facnumero = facnumero.strip()
        procodigo = procodigo.strip()
        reply = QtWidgets.QMessageBox.question(self, 'Confirmar Eliminación',
                                               f'¿Está seguro de que desea eliminar el producto {procodigo} de la factura {facnumero}?',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
                cursor = connection.cursor()
            
                cursor.execute("DELETE FROM PXF WHERE TRIM(FACNUMERO) = :1 AND TRIM(PROCODIGO) = :2", (facnumero, procodigo))
                connection.commit()

                cursor.close()
                connection.close()
                QtWidgets.QMessageBox.information(self, 'Éxito', 'Producto eliminado de la factura exitosamente.')
                self.cargar_productos(facnumero)
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo eliminar el producto: {error.message}')


    def editar_producto(self, row, producto):
        facnumero = self.factura_input.text()
        procodigo = producto[0]
        cantidad = producto[2]
        valor = producto[3]
        iva = producto[6]

        editar_window = EditarProductoWindow(facnumero, procodigo, cantidad, valor, iva, self)
        editar_window.exec_()

    def actualizar_numero_factura(self):
        nuevo_numero = self.generar_numero_factura()
        self.facnumero_input.setReadOnly(False)
        self.facnumero_input.setText(nuevo_numero)
        self.facnumero_input.setReadOnly(True)

    def generar_numero_factura(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT FACNUMERO FROM FACTURAS")
            facturas = cursor.fetchall()
            max_num = 0
            for fac in facturas:
                num = int(fac[0].split('-')[1])
                if num > max_num:
                    max_num = num
            nuevo_numero = max_num + 1
            fac_numero_generado = f"FAC-{nuevo_numero:03d}"
            cursor.close()
            connection.close()
            return fac_numero_generado
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo generar el número de factura: {error.message}')
            return "FAC-001"

    def actualizar_resumen(self):
        subtotal = 0.0
        iva_8 = 0.0
        iva_15 = 0.0
        total = 0.0

        for row in range(self.productos_table.rowCount()):
            subtotal += float(self.productos_table.item(row, 5).text())
            iva_8 += float(self.productos_table.item(row, 7).text())
            iva_15 += float(self.productos_table.item(row, 8).text())
        total = subtotal + iva_8 + iva_15

        self.subtotal_label.setText(f'Subtotal: {subtotal:.2f}')
        self.iva_8_label.setText(f'IVA 8%: {iva_8:.2f}')
        self.iva_15_label.setText(f'IVA 15%: {iva_15:.2f}')
        self.total_label.setText(f'Total: {total:.2f}')

    def generar_factura_definitiva(self):
        try:
            facnumero = self.factura_input.text().strip()
            print(facnumero)
            # Conectar a la base de datos
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            # Recuperar datos de la factura
            cursor.execute("""
                SELECT 
                    F.FACNUMERO, F.FACFECHA, F.FACDESCUENTO, F.FACFORMAPAGO, 
                    C.CLINOMBRE, C.CLIIDENTIFICACION, C.CLIDIRECCION, C.CLITELEFONO, C.CLIEMAIL
                FROM FACTURAS F
                JOIN CLIENTES C ON F.CLICODIGO = C.CLICODIGO
                WHERE TRIM(F.FACNUMERO) = :1
            """, (facnumero,))
            factura = cursor.fetchone()

            facfecha = factura[1].strftime('%Y-%m-%d')
            facdescuento = float(factura[2])
            facformapago = factura[3]
            clinombre = factura[4]
            cliidentificacion = factura[5]
            clidireccion = factura[6]
            clitelefono = factura[7]
            cliemail = factura[8]

            # Recuperar productos de la factura
            cursor.execute("""
                SELECT 
                    P.PROCODIGO, P.PRODESCRIPCION, PXF.PXFCANTIDAD, PXF.PXFVALOR, PXF.PXFSUBTOTAL, PXF.PXFIVA 
                FROM PXF
                JOIN PRODUCTOS P ON PXF.PROCODIGO = P.PROCODIGO
                WHERE TRIM(PXF.FACNUMERO) = :1
            """, (facnumero,))
            productos = cursor.fetchall()

            # Crear PDF
            pdf_path = f"C:/Users/antho/Downloads/{facnumero}.pdf"
            doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4), rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            elements = []

            styles = getSampleStyleSheet()
            title_style = styles['Title']
            body_style = styles['BodyText']
            title = Paragraph(f"Factura #{facnumero}", title_style)

            cliente_info = [
                f"Número de Factura: {facnumero}",
                f"Cliente: {clinombre}",
                f"Identificación: {cliidentificacion}",
                f"Dirección: {clidireccion}",
                f"Teléfono: {clitelefono}",
                f"Email: {cliemail}",                
                f"Fecha: {facfecha}",
                f"Forma de Pago: {facformapago}"
            ]

            elements.append(title)
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("<br/>".join(cliente_info), body_style))
            elements.append(Spacer(1, 24))

            # Agregar la tabla de productos
            data = [["Código", "Descripción", "Cantidad", "Valor", "Subtotal", "IVA 0%", "IVA 8%", "IVA 15%", "Total"]]

            total_items = 0
            for producto in productos:
                codigo = producto[0]
                descripcion = producto[1]
                cantidad = float(producto[2])
                valor = float(producto[3])
                subtotal = float(producto[4])
                iva_0 = 0 if producto[5] == 0.0 else ""
                iva_8 = round(subtotal * 0.08, 2) if producto[5] == 8.0 else ""
                iva_15 = round(subtotal * 0.15, 2) if producto[5] == 15.0 else ""
                total = round(subtotal + (iva_0 if iva_0 != "" else 0) + (iva_8 if iva_8 != "" else 0) + (iva_15 if iva_15 != "" else 0), 2)

                data.append([codigo, descripcion, cantidad, valor, subtotal, iva_0, iva_8, iva_15, total])
                total_items += 1

            # Agregar fila de total de ítems
            data.append(["Total Ítems", total_items, "", "", "", "", "", "", ""])

            table = Table(data, colWidths=[3*cm, 10*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 24))

            # Calcular los totales y el descuento
            subtotal = sum([float(p[4]) for p in productos])
            iva_8 = sum([round(float(p[4]) * 0.08, 2) for p in productos if float(p[5]) == 8.0])
            iva_15 = sum([round(float(p[4]) * 0.15, 2) for p in productos if float(p[5]) == 15.0])
            total = subtotal + iva_8 + iva_15

            descuento_valor = subtotal * (facdescuento / 100)
            total_con_descuento = total - descuento_valor
            print(facdescuento)
            resumen_data = [
                ["Subtotal:", f"{subtotal:.2f}"],
                ["IVA 8%:", f"{iva_8:.2f}"],
                ["IVA 15%:", f"{iva_15:.2f}"],
                ["Descuento:", f"{facdescuento:.2f}"],
                ["Total:", f"{total_con_descuento:.2f}"]
            ]

            resumen_table = Table(resumen_data, colWidths=[3*cm, 3*cm])
            resumen_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            # Agregar el recuadro de firma
            firma_data = [
                ["Firma:"],
                [""]
            ]
            firma_table = Table(firma_data, colWidths=[6*cm])
            firma_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM')
            ]))

            # Organizar las tablas en una disposición de dos columnas
            table_data = [
                [firma_table, resumen_table]
            ]
            combined_table = Table(table_data, colWidths=[7*cm, 6*cm])
            combined_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))

            elements.append(combined_table)

            doc.build(elements)
            QtWidgets.QMessageBox.information(self, 'Éxito', f'Factura generada y guardada como {pdf_path}.')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', f'No se pudo generar la factura definitiva: {str(e)}')
        finally:
            cursor.close()
            connection.close()



class ProductoWindow(QtWidgets.QDialog):
    def __init__(self, facnumero, parent):
        super().__init__(parent)
        self.facnumero = facnumero
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Agregar Producto a Factura')

        # Establecer fondo de pantalla
        self.background_label = QtWidgets.QLabel(self)
        self.background_pixmap = QtGui.QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 400, 300)

        layout = QtWidgets.QVBoxLayout()

        self.producto_label = QtWidgets.QLabel('Código de Producto')
        self.productos_menu = QtWidgets.QComboBox()
        self.cargar_productos()
        layout.addWidget(self.producto_label)
        layout.addWidget(self.productos_menu)

        self.cantidad_label = QtWidgets.QLabel('Cantidad')
        self.cantidad_input = QtWidgets.QLineEdit()
        layout.addWidget(self.cantidad_label)
        layout.addWidget(self.cantidad_input)

        self.valor_label = QtWidgets.QLabel('Valor')
        self.valor_input = QtWidgets.QLineEdit()
        self.valor_input.setReadOnly(True)
        layout.addWidget(self.valor_label)
        layout.addWidget(self.valor_input)

        self.iva_label = QtWidgets.QLabel('IVA')
        self.iva_menu = QtWidgets.QComboBox()
        self.iva_menu.addItems(['0%', '8%', '15%'])
        layout.addWidget(self.iva_label)
        layout.addWidget(self.iva_menu)

        self.agregar_btn = QtWidgets.QPushButton('Agregar Producto', self)
        self.agregar_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.agregar_btn.clicked.connect(self.on_agregar_producto)
        layout.addWidget(self.agregar_btn)

        self.setLayout(layout)
        self.productos_menu.currentIndexChanged.connect(self.on_producto_change)

    def on_producto_change(self):
        self.cargar_valor_producto(self.productos_menu.currentText(), self.valor_input)

    def on_agregar_producto(self):
        self.agregar_producto(self.facnumero, self.productos_menu.currentText(), self.cantidad_input.text(), self.valor_input.text(), self.iva_menu.currentText())

    def cargar_productos(self):
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            cursor.execute("SELECT PROCODIGO, PRODESCRIPCION FROM PRODUCTOS")
            productos = cursor.fetchall()
            for producto in productos:
                self.productos_menu.addItem(f"{producto[0]} - {producto[1]}")
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo cargar los productos: {error.message}')

    def cargar_valor_producto(self, selected_producto, valor_input):
        procodigo = selected_producto.split(' - ')[0].strip()
        try:
            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()
            sql_query = "SELECT PROPRECIOUM FROM PRODUCTOS WHERE TRIM(PROCODIGO) = :1"
            cursor.execute(sql_query, {'1': procodigo})
            producto = cursor.fetchone()
            if producto:
                valor_input.setReadOnly(False)
                valor_input.setText(str(producto[0]))
                valor_input.setReadOnly(True)
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', 'No se encontraron datos del producto.')
            cursor.close()
            connection.close()
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo obtener el valor del producto: {error.message}')

    def agregar_producto(self, facnumero, procodigo, cantidad, valor, iva):
        try:
            procodigo = procodigo.split(' - ')[0].strip()
            pxf_cantidad = float(cantidad)  # Convertir a float
            pxf_valor = float(valor)  # Convertir a float

            if iva == '0%':
                pxf_iva = 0.0
            elif iva == '8%':
                pxf_iva = 8.0
            elif iva == '15%':
                pxf_iva = 15.0
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', 'IVA no válido.')
                return

            if pxf_cantidad <= 0 or pxf_valor <= 0:
                QtWidgets.QMessageBox.critical(self, 'Error', 'La cantidad y el valor deben ser mayores que cero.')
                return

            pxf_subtotal = pxf_cantidad * pxf_valor
            pxf_status = "ACT"

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            # Verificar si se puede agregar el producto sin que el saldo final sea negativo
            cursor.execute("""
                SELECT PROSALDOFINAL 
                FROM PRODUCTOS 
                WHERE TRIM(PROCODIGO) = :1
            """, (procodigo,))
            saldo_final = cursor.fetchone()[0]

            if saldo_final < pxf_cantidad:
                QtWidgets.QMessageBox.critical(self, 'Error', 'No se puede agregar el producto porque no hay suficiente stock.')
                cursor.close()
                connection.close()
                return

            cursor.execute("""
                INSERT INTO PXF (FACNUMERO, PROCODIGO, PXFCANTIDAD, PXFVALOR, PXFSUBTOTAL, PXFIVA, PXFSTATUS)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (facnumero, procodigo, pxf_cantidad, pxf_valor, pxf_subtotal, pxf_iva, pxf_status))
            connection.commit()
            cursor.close()
            connection.close()
            QtWidgets.QMessageBox.information(self, 'Éxito', 'Producto agregado a la factura exitosamente.')
            self.parent.cargar_productos(facnumero)
            self.close()
        except ValueError as ve:
            QtWidgets.QMessageBox.critical(self, 'Error de Valor', f'Error al convertir a float: {ve}')
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo agregar el producto a la factura: {error.message}')



class EditarProductoWindow(QtWidgets.QDialog):
    def __init__(self, facnumero, procodigo, cantidad, valor, iva, parent):
        super().__init__(parent)
        self.facnumero = facnumero
        self.procodigo = procodigo
        self.cantidad = cantidad
        self.valor = valor
        self.iva = iva
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 400, 300)
        self.setWindowTitle('Editar Producto en Factura')

        # Establecer fondo de pantalla
        self.background_label = QtWidgets.QLabel(self)
        self.background_pixmap = QtGui.QPixmap('C:/Users/antho/Downloads/fondo4.png')
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 400, 300)

        layout = QtWidgets.QVBoxLayout()

        self.producto_label = QtWidgets.QLabel(f'Producto: {self.procodigo}')
        layout.addWidget(self.producto_label)

        self.cantidad_label = QtWidgets.QLabel('Cantidad')
        self.cantidad_input = QtWidgets.QLineEdit()
        self.cantidad_input.setText(str(self.cantidad))
        layout.addWidget(self.cantidad_label)
        layout.addWidget(self.cantidad_input)

        self.valor_label = QtWidgets.QLabel('Valor')
        self.valor_input = QtWidgets.QLineEdit()
        self.valor_input.setText(str(self.valor))
        self.valor_input.setReadOnly(True)
        layout.addWidget(self.valor_label)
        layout.addWidget(self.valor_input)

        self.iva_label = QtWidgets.QLabel('IVA')
        self.iva_menu = QtWidgets.QComboBox()
        self.iva_menu.addItems(['0%', '8%', '15%'])
        if self.iva == 0.0:
            self.iva_menu.setCurrentText('0%')
        elif self.iva == 8.0:
            self.iva_menu.setCurrentText('8%')
        elif self.iva == 15.0:
            self.iva_menu.setCurrentText('15%')
        layout.addWidget(self.iva_label)
        layout.addWidget(self.iva_menu)

        self.guardar_btn = QtWidgets.QPushButton('Guardar Cambios', self)
        self.guardar_btn.setStyleSheet("background-color: #001f3f; color: white;")
        self.guardar_btn.clicked.connect(self.on_guardar_cambios)
        layout.addWidget(self.guardar_btn)

        self.setLayout(layout)

    def on_guardar_cambios(self):
        try:
            nueva_cantidad_text = self.cantidad_input.text()
            if not nueva_cantidad_text.isdigit() or int(nueva_cantidad_text) <= 0:
                QtWidgets.QMessageBox.critical(self, 'Error', 'La cantidad debe ser un número entero positivo.')
                return

            nueva_cantidad = int(nueva_cantidad_text)
            nuevo_iva_text = self.iva_menu.currentText()
            if nuevo_iva_text == '0%':
                nuevo_iva = 0.0
            elif nuevo_iva_text == '8%':
                nuevo_iva = 8.0
            elif nuevo_iva_text == '15%':
                nuevo_iva = 15.0
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', 'IVA no válido.')
                return

            nuevo_subtotal = nueva_cantidad * self.valor

            connection = cx_Oracle.connect(os.environ['DB_USERNAME'], os.environ['DB_PASSWORD'], "localhost/comercial")
            cursor = connection.cursor()

            # Verificar si se puede actualizar el producto sin que el saldo final sea negativo
            cursor.execute("""
                SELECT PROSALDOFINAL 
                FROM PRODUCTOS 
                WHERE TRIM(PROCODIGO) = :1
            """, (self.procodigo.strip(),))
            saldo_final = cursor.fetchone()[0]

            if saldo_final - (nueva_cantidad - self.cantidad) < 0:
                QtWidgets.QMessageBox.critical(self, 'Error', 'No se puede actualizar el producto porque no hay suficiente stock.')
                cursor.close()
                connection.close()
                return

            cursor.execute("""
                UPDATE PXF
                SET PXFCANTIDAD = :1, PXFIVA = :2, PXFSUBTOTAL = :3
                WHERE TRIM(FACNUMERO) = :4 AND TRIM(PROCODIGO) = :5
            """, (nueva_cantidad, nuevo_iva, nuevo_subtotal, self.facnumero.strip(), self.procodigo.strip()))

            connection.commit()
            cursor.close()
            connection.close()
            QtWidgets.QMessageBox.information(self, 'Éxito', 'Producto actualizado exitosamente.')
            self.parent.cargar_productos(self.facnumero)
            self.close()
        except ValueError as ve:
            QtWidgets.QMessageBox.critical(self, 'Error de Valor', f'Error al convertir a float: {ve}')
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            QtWidgets.QMessageBox.critical(self, 'Error de Conexión', f'No se pudo actualizar el producto: {error.message}')



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = CrearFactura()
    ex.show()
    sys.exit(app.exec_())
