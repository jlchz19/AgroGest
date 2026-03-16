#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestión de Empleados
Funcionalidades para el manejo de empleados en la aplicación de escritorio
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import sqlite3
from typing import List, Dict, Optional, Any
import sys
import os

# Agregar el directorio padre al path para importar themes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from themes import ModernTheme, Icons, ModernStyles

class EmpleadosModule:
    """Módulo para la gestión de empleados"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.current_finca_id = None
    
    def show_empleados_window(self, finca_id: int = None):
        """Muestra la ventana principal de gestión de empleados"""
        self.current_finca_id = finca_id
        
        # Crear ventana
        self.empleados_window = tk.Toplevel(self.parent)
        self.empleados_window.title(f"{Icons.EMPLOYEES} Gestión de Empleados")
        self.empleados_window.geometry("1200x800")
        self.empleados_window.configure(bg=ModernTheme.BACKGROUND)
        
        # Configurar estilos modernos
        style = ttk.Style()
        ModernStyles.configure_modern_theme(style)
        
        # Frame principal
        main_frame = ttk.Frame(self.empleados_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Header con título y estadísticas
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título con icono
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left', padx=20, pady=15)
        
        title_label = ttk.Label(title_frame, text=f"{Icons.EMPLOYEES} Gestión de Empleados", 
                               style='Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_frame, text="Administra el personal de tu finca", 
                                  style='Info.TLabel')
        subtitle_label.pack(anchor='w')
        
        # Estadísticas rápidas
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side='right', padx=20, pady=15)
        
        self.create_empleados_stats_cards(stats_frame)
        
        # Frame de botones con estilo moderno
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(0, 15))
        
        # Botones principales
        ttk.Button(buttons_frame, text=f"{Icons.ADD} Nuevo Empleado", 
                  command=self.new_empleado_dialog, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.EDIT} Editar", 
                  command=self.edit_empleado, style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.DELETE} Eliminar", 
                  command=self.delete_empleado, style='Danger.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.INFO} Detalles", 
                  command=self.view_empleado_details, style='Warning.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.REFRESH} Actualizar", 
                  command=self.refresh_empleados_list, style='Success.TButton').pack(side='left', padx=(10, 0))
        
        # Frame de búsqueda moderno
        search_frame = ttk.LabelFrame(main_frame, text=f"{Icons.SEARCH} Búsqueda y Filtros", padding="15")
        search_frame.pack(fill='x', pady=(0, 15))
        
        # Primera fila de búsqueda
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_row1, text="Buscar:", style='Header.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_empleados)
        search_entry = ttk.Entry(search_row1, textvariable=self.search_var, width=40, font=('Segoe UI', 10))
        search_entry.pack(side='left', padx=(10, 20))
        
        # Filtros
        ttk.Label(search_row1, text="Cargo:", style='Header.TLabel').pack(side='left')
        self.cargo_filter = ttk.Combobox(search_row1, 
                                        values=['Todos', 'Veterinario', 'Vaquero', 'Porquero', 'Administrador', 'Otro'], 
                                        state='readonly', width=15, font=('Segoe UI', 10))
        self.cargo_filter.set('Todos')
        self.cargo_filter.pack(side='left', padx=(10, 20))
        self.cargo_filter.bind('<<ComboboxSelected>>', self.filter_empleados)
        
        ttk.Label(search_row1, text="Estado:", style='Header.TLabel').pack(side='left')
        self.estado_filter = ttk.Combobox(search_row1, values=['Todos', 'Activo', 'Inactivo'], 
                                         state='readonly', width=15, font=('Segoe UI', 10))
        self.estado_filter.set('Todos')
        self.estado_filter.pack(side='left', padx=(10, 0))
        self.estado_filter.bind('<<ComboboxSelected>>', self.filter_empleados)
        
        # Lista de empleados con estilo moderno
        list_frame = ttk.LabelFrame(main_frame, text=f"{Icons.EMPLOYEES} Lista de Empleados", padding="15")
        list_frame.pack(expand=True, fill='both')
        
        # Treeview moderno
        columns = ('ID', 'Cédula', 'Nombre', 'Apellido', 'Cargo', 'Teléfono', 'Salario', 'Estado', 'Antigüedad')
        self.empleados_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18, style='Modern.Treeview')
        
        # Configurar columnas con anchos apropiados
        column_widths = [50, 100, 120, 120, 120, 100, 100, 80, 80]
        for i, col in enumerate(columns):
            self.empleados_tree.heading(col, text=col)
            self.empleados_tree.column(col, width=column_widths[i], anchor='center')
        
        # Scrollbar moderno
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.empleados_tree.yview)
        self.empleados_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview y scrollbar
        self.empleados_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Cargar datos
        self.refresh_empleados_list()
    
    def create_empleados_stats_cards(self, parent):
        """Crea las tarjetas de estadísticas de empleados"""
        # Obtener estadísticas de la base de datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total de empleados
        cursor.execute('SELECT COUNT(*) FROM empleados WHERE finca_id = ?', (self.current_finca_id,))
        total_empleados = cursor.fetchone()[0]
        
        # Empleados activos
        cursor.execute('SELECT COUNT(*) FROM empleados WHERE finca_id = ? AND estado = "activo"', (self.current_finca_id,))
        activos = cursor.fetchone()[0]
        
        # Empleados por cargo
        cursor.execute('SELECT cargo, COUNT(*) FROM empleados WHERE finca_id = ? GROUP BY cargo', (self.current_finca_id,))
        cargos = cursor.fetchall()
        
        # Salario promedio
        cursor.execute('SELECT AVG(salario) FROM empleados WHERE finca_id = ? AND estado = "activo"', (self.current_finca_id,))
        salario_promedio = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Crear tarjetas
        stats_data = [
            (f"{Icons.EMPLOYEES}", "Total", str(total_empleados), ModernTheme.PRIMARY),
            (f"{Icons.ACTIVE}", "Activos", str(activos), ModernTheme.SUCCESS),
            (f"{Icons.USER}", "Veterinarios", str(sum(1 for c in cargos if c[0] == 'Veterinario')), ModernTheme.INFO),
            (f"{Icons.INFO}", "Salario Prom.", f"${salario_promedio:,.0f}", ModernTheme.WARNING)
        ]
        
        for i, (icon, label, value, color) in enumerate(stats_data):
            card = ttk.Frame(parent, style='Card.TFrame')
            card.pack(side='left', padx=10, fill='both', expand=True)
            
            # Icono
            icon_label = ttk.Label(card, text=icon, font=('Segoe UI', 24))
            icon_label.pack(pady=(10, 5))
            
            # Valor
            value_label = ttk.Label(card, text=value, font=('Segoe UI', 20, 'bold'), 
                                   foreground=color)
            value_label.pack()
            
            # Etiqueta
            label_label = ttk.Label(card, text=label, style='Info.TLabel')
            label_label.pack(pady=(0, 10))
    
    def refresh_empleados_list(self):
        """Actualiza la lista de empleados"""
        # Limpiar lista
        for item in self.empleados_tree.get_children():
            self.empleados_tree.delete(item)
        
        # Obtener empleados de la base de datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, cedula, nombre, apellido, cargo, telefono, salario, estado,
                   ROUND((julianday('now') - julianday(fecha_contratacion)) / 365.25, 1) as antiguedad
            FROM empleados
            WHERE finca_id = ?
            ORDER BY nombre, apellido
        '''
        
        cursor.execute(query, (self.current_finca_id,))
        empleados = cursor.fetchall()
        
        for empleado in empleados:
            self.empleados_tree.insert('', 'end', values=empleado)
        
        conn.close()
    
    def filter_empleados(self, *args):
        """Filtra la lista de empleados según los criterios de búsqueda"""
        search_text = self.search_var.get().lower()
        cargo_filter = self.cargo_filter.get()
        estado_filter = self.estado_filter.get()
        
        # Limpiar lista
        for item in self.empleados_tree.get_children():
            self.empleados_tree.delete(item)
        
        # Obtener empleados filtrados
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, cedula, nombre, apellido, cargo, telefono, salario, estado,
                   ROUND((julianday('now') - julianday(fecha_contratacion)) / 365.25, 1) as antiguedad
            FROM empleados
            WHERE finca_id = ?
        '''
        
        params = [self.current_finca_id]
        
        if search_text:
            query += ' AND (LOWER(nombre) LIKE ? OR LOWER(apellido) LIKE ? OR LOWER(cedula) LIKE ?)'
            search_param = f'%{search_text}%'
            params.extend([search_param, search_param, search_param])
        
        if cargo_filter != 'Todos':
            if cargo_filter == 'Otro':
                query += ' AND cargo NOT IN (?, ?, ?, ?)'
                params.extend(['Veterinario', 'Vaquero', 'Porquero', 'Administrador'])
            else:
                query += ' AND cargo = ?'
                params.append(cargo_filter)
        
        if estado_filter != 'Todos':
            query += ' AND estado = ?'
            params.append(estado_filter.lower())
        
        query += ' ORDER BY nombre, apellido'
        
        cursor.execute(query, params)
        empleados = cursor.fetchall()
        
        for empleado in empleados:
            # Agregar iconos según el cargo y estado
            cargo_icon = self.get_cargo_icon(empleado[4])
            estado_icon = self.get_estado_icon(empleado[7])
            
            # Crear valores con iconos
            values = list(empleado)
            values[4] = f"{cargo_icon} {empleado[4]}"  # Cargo con icono
            values[7] = f"{estado_icon} {empleado[7]}"  # Estado con icono
            values[6] = f"${empleado[6]:,.0f}"  # Formatear salario
            
            self.empleados_tree.insert('', 'end', values=values)
        
        conn.close()
    
    def get_cargo_icon(self, cargo):
        """Obtiene el icono correspondiente al cargo del empleado"""
        icon_map = {
            'Veterinario': Icons.USER,
            'Vaquero': Icons.ANIMALS,
            'Porquero': Icons.PIG,
            'Administrador': Icons.SETTINGS
        }
        return icon_map.get(cargo, Icons.USER)
    
    def get_estado_icon(self, estado):
        """Obtiene el icono correspondiente al estado del empleado"""
        icon_map = {
            'Activo': Icons.ACTIVE,
            'Inactivo': Icons.INACTIVE
        }
        return icon_map.get(estado, Icons.ACTIVE)
    
    def new_empleado_dialog(self):
        """Abre el diálogo para crear un nuevo empleado"""
        dialog = EmpleadoDialog(self.empleados_window, self.db, self.current_finca_id)
        self.empleados_window.wait_window(dialog.dialog)
        self.refresh_empleados_list()
    
    def edit_empleado(self):
        """Edita el empleado seleccionado"""
        selection = self.empleados_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado para editar")
            return
        
        item = self.empleados_tree.item(selection[0])
        empleado_id = item['values'][0]
        
        dialog = EmpleadoDialog(self.empleados_window, self.db, self.current_finca_id, empleado_id)
        self.empleados_window.wait_window(dialog.dialog)
        self.refresh_empleados_list()
    
    def delete_empleado(self):
        """Elimina el empleado seleccionado"""
        selection = self.empleados_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado para eliminar")
            return
        
        item = self.empleados_tree.item(selection[0])
        empleado_id = item['values'][0]
        nombre = f"{item['values'][2]} {item['values'][3]}"
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al empleado {nombre}?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM empleados WHERE id = ?', (empleado_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Empleado eliminado correctamente")
                self.refresh_empleados_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar empleado: {str(e)}")
            finally:
                conn.close()
    
    def view_empleado_details(self):
        """Muestra los detalles del empleado seleccionado"""
        selection = self.empleados_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado para ver sus detalles")
            return
        
        item = self.empleados_tree.item(selection[0])
        empleado_id = item['values'][0]
        
        # Crear ventana de detalles
        details_window = tk.Toplevel(self.empleados_window)
        details_window.title(f"Detalles del Empleado - {item['values'][2]} {item['values'][3]}")
        details_window.geometry("500x400")
        
        # Obtener información detallada del empleado
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cedula, nombre, apellido, telefono, direccion, cargo, 
                   fecha_contratacion, salario, estado,
                   ROUND((julianday('now') - julianday(fecha_contratacion)) / 365.25, 1) as antiguedad
            FROM empleados
            WHERE id = ?
        ''', (empleado_id,))
        
        empleado_info = cursor.fetchall()
        conn.close()
        
        if not empleado_info:
            messagebox.showerror("Error", "No se encontró información del empleado")
            return
        
        empleado = empleado_info[0]
        
        # Frame principal
        main_frame = ttk.Frame(details_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Información del empleado
        info_frame = ttk.LabelFrame(main_frame, text="Información del Empleado", padding="10")
        info_frame.pack(fill='x', pady=(0, 20))
        
        info_text = f"""
Cédula: {empleado[0]}
Nombre: {empleado[1]} {empleado[2]}
Teléfono: {empleado[3]}
Dirección: {empleado[4]}
Cargo: {empleado[5]}
Fecha de Contratación: {empleado[6]}
Salario: ${empleado[7]:,.2f}
Estado: {empleado[8]}
Antigüedad: {empleado[9]} años
        """
        
        ttk.Label(info_frame, text=info_text.strip(), justify='left').pack(anchor='w')
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=details_window.destroy).pack(pady=20)

class EmpleadoDialog:
    """Diálogo para crear/editar empleados"""
    
    def __init__(self, parent, db_manager, finca_id, empleado_id=None):
        self.parent = parent
        self.db = db_manager
        self.finca_id = finca_id
        self.empleado_id = empleado_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Empleado" if not empleado_id else "Editar Empleado")
        self.dialog.geometry("450x600")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.load_data() if empleado_id else None
    
    def create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title = "Nuevo Empleado" if not self.empleado_id else "Editar Empleado"
        ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Frame de formulario
        form_frame = ttk.LabelFrame(main_frame, text="Información del Empleado", padding="10")
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Cédula
        ttk.Label(form_frame, text="Cédula *:").grid(row=0, column=0, sticky='w', pady=5)
        self.cedula_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.cedula_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Nombre
        ttk.Label(form_frame, text="Nombre *:").grid(row=1, column=0, sticky='w', pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Apellido
        ttk.Label(form_frame, text="Apellido *:").grid(row=2, column=0, sticky='w', pady=5)
        self.apellido_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.apellido_var, width=30).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Teléfono
        ttk.Label(form_frame, text="Teléfono *:").grid(row=3, column=0, sticky='w', pady=5)
        self.telefono_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.telefono_var, width=30).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Dirección
        ttk.Label(form_frame, text="Dirección *:").grid(row=4, column=0, sticky='w', pady=5)
        self.direccion_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.direccion_var, width=30).grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Cargo
        ttk.Label(form_frame, text="Cargo *:").grid(row=5, column=0, sticky='w', pady=5)
        self.cargo_var = tk.StringVar()
        cargo_combo = ttk.Combobox(form_frame, textvariable=self.cargo_var,
                                  values=['Veterinario', 'Vaquero', 'Porquero', 'Administrador', 'Otro'],
                                  state='readonly', width=27)
        cargo_combo.grid(row=5, column=1, pady=5, padx=(10, 0))
        
        # Cargo personalizado
        ttk.Label(form_frame, text="Cargo personalizado:").grid(row=6, column=0, sticky='w', pady=5)
        self.cargo_custom_var = tk.StringVar()
        self.cargo_custom_entry = ttk.Entry(form_frame, textvariable=self.cargo_custom_var, width=30)
        self.cargo_custom_entry.grid(row=6, column=1, pady=5, padx=(10, 0))
        
        # Fecha de contratación
        ttk.Label(form_frame, text="Fecha Contratación *:").grid(row=7, column=0, sticky='w', pady=5)
        self.fecha_contratacion_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.fecha_contratacion_var, width=30).grid(row=7, column=1, pady=5, padx=(10, 0))
        
        # Salario
        ttk.Label(form_frame, text="Salario *:").grid(row=8, column=0, sticky='w', pady=5)
        self.salario_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.salario_var, width=30).grid(row=8, column=1, pady=5, padx=(10, 0))
        
        # Estado
        ttk.Label(form_frame, text="Estado:").grid(row=9, column=0, sticky='w', pady=5)
        self.estado_var = tk.StringVar()
        estado_combo = ttk.Combobox(form_frame, textvariable=self.estado_var,
                                   values=['Activo', 'Inactivo'],
                                   state='readonly', width=27)
        estado_combo.set('Activo')
        estado_combo.grid(row=9, column=1, pady=5, padx=(10, 0))
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        ttk.Button(buttons_frame, text="Guardar", command=self.save_empleado).pack(side='right', padx=(10, 0))
        ttk.Button(buttons_frame, text="Cancelar", command=self.dialog.destroy).pack(side='right')
    
    def load_data(self):
        """Carga los datos del empleado para edición"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cedula, nombre, apellido, telefono, direccion, cargo, 
                   fecha_contratacion, salario, estado
            FROM empleados WHERE id = ?
        ''', (self.empleado_id,))
        
        empleado = cursor.fetchone()
        
        if empleado:
            self.cedula_var.set(empleado[0])
            self.nombre_var.set(empleado[1])
            self.apellido_var.set(empleado[2])
            self.telefono_var.set(empleado[3])
            self.direccion_var.set(empleado[4])
            
            # Verificar si el cargo está en la lista predefinida
            cargos_predefinidos = ['Veterinario', 'Vaquero', 'Porquero', 'Administrador']
            if empleado[5] in cargos_predefinidos:
                self.cargo_var.set(empleado[5])
            else:
                self.cargo_var.set('Otro')
                self.cargo_custom_var.set(empleado[5])
            
            self.fecha_contratacion_var.set(empleado[6])
            self.salario_var.set(str(empleado[7]))
            self.estado_var.set(empleado[8])
        
        conn.close()
    
    def save_empleado(self):
        """Guarda el empleado en la base de datos"""
        # Validaciones
        if not self.cedula_var.get().strip():
            messagebox.showerror("Error", "La cédula es obligatoria")
            return
        
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        if not self.apellido_var.get().strip():
            messagebox.showerror("Error", "El apellido es obligatorio")
            return
        
        if not self.telefono_var.get().strip():
            messagebox.showerror("Error", "El teléfono es obligatorio")
            return
        
        if not self.direccion_var.get().strip():
            messagebox.showerror("Error", "La dirección es obligatoria")
            return
        
        if not self.cargo_var.get():
            messagebox.showerror("Error", "El cargo es obligatorio")
            return
        
        if not self.fecha_contratacion_var.get().strip():
            messagebox.showerror("Error", "La fecha de contratación es obligatoria")
            return
        
        try:
            salario = float(self.salario_var.get())
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido")
            return
        
        # Determinar cargo final
        if self.cargo_var.get() == 'Otro':
            if not self.cargo_custom_var.get().strip():
                messagebox.showerror("Error", "Debe especificar el cargo personalizado")
                return
            cargo_final = self.cargo_custom_var.get().strip()
        else:
            cargo_final = self.cargo_var.get()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.empleado_id:
                # Actualizar empleado existente
                cursor.execute('''
                    UPDATE empleados SET
                        cedula = ?, nombre = ?, apellido = ?, telefono = ?, direccion = ?,
                        cargo = ?, fecha_contratacion = ?, salario = ?, estado = ?
                    WHERE id = ?
                ''', (
                    self.cedula_var.get().strip(),
                    self.nombre_var.get().strip(),
                    self.apellido_var.get().strip(),
                    self.telefono_var.get().strip(),
                    self.direccion_var.get().strip(),
                    cargo_final,
                    self.fecha_contratacion_var.get().strip(),
                    salario,
                    self.estado_var.get().lower(),
                    self.empleado_id
                ))
            else:
                # Crear nuevo empleado
                cursor.execute('''
                    INSERT INTO empleados (
                        cedula, nombre, apellido, telefono, direccion, cargo,
                        fecha_contratacion, salario, estado, finca_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.cedula_var.get().strip(),
                    self.nombre_var.get().strip(),
                    self.apellido_var.get().strip(),
                    self.telefono_var.get().strip(),
                    self.direccion_var.get().strip(),
                    cargo_final,
                    self.fecha_contratacion_var.get().strip(),
                    salario,
                    self.estado_var.get().lower(),
                    self.finca_id
                ))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Empleado guardado correctamente")
            self.dialog.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un empleado con esa cédula")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar empleado: {str(e)}")
        finally:
            conn.close()
