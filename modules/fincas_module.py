#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestión de Fincas
Funcionalidades para el manejo de fincas en la aplicación de escritorio
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import sqlite3
from typing import List, Dict, Optional, Any
import sys
import os

# Agregar el directorio padre al path para importar themes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from themes import ModernTheme, Icons, ModernStyles

class FincasModule:
    """Módulo para la gestión de fincas"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.current_user_id = None
    
    def show_fincas_window(self, user_id: int = None):
        """Muestra la ventana principal de gestión de fincas"""
        self.current_user_id = user_id
        
        # Crear ventana
        self.fincas_window = tk.Toplevel(self.parent)
        self.fincas_window.title(f"{Icons.HOME} Gestión de Fincas")
        self.fincas_window.geometry("1200x800")
        self.fincas_window.configure(bg=ModernTheme.BACKGROUND)
        
        # Configurar estilos modernos
        style = ttk.Style()
        ModernStyles.configure_modern_theme(style)
        
        # Frame principal
        main_frame = ttk.Frame(self.fincas_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Header con título y estadísticas
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título con icono
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left', padx=20, pady=15)
        
        title_label = ttk.Label(title_frame, text=f"{Icons.HOME} Gestión de Fincas", 
                               style='Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_frame, text="Administra las fincas de tu sistema", 
                                  style='Info.TLabel')
        subtitle_label.pack(anchor='w')
        
        # Estadísticas rápidas
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side='right', padx=20, pady=15)
        
        self.create_fincas_stats_cards(stats_frame)
        
        # Frame de botones con estilo moderno
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(0, 15))
        
        # Botones principales
        ttk.Button(buttons_frame, text=f"{Icons.ADD} Nueva Finca", 
                  command=self.new_finca_dialog, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.EDIT} Editar", 
                  command=self.edit_finca, style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.DELETE} Eliminar", 
                  command=self.delete_finca, style='Danger.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.INFO} Detalles", 
                  command=self.view_finca_details, style='Warning.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.REFRESH} Actualizar", 
                  command=self.refresh_fincas_list, style='Success.TButton').pack(side='left', padx=(10, 0))
        
        # Frame de búsqueda moderno
        search_frame = ttk.LabelFrame(main_frame, text=f"{Icons.SEARCH} Búsqueda y Filtros", padding="15")
        search_frame.pack(fill='x', pady=(0, 15))
        
        # Primera fila de búsqueda
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_row1, text="Buscar:", style='Header.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_fincas)
        search_entry = ttk.Entry(search_row1, textvariable=self.search_var, width=40, font=('Segoe UI', 10))
        search_entry.pack(side='left', padx=(10, 20))
        
        # Filtros
        ttk.Label(search_row1, text="Tipo Producción:", style='Header.TLabel').pack(side='left')
        self.tipo_filter = ttk.Combobox(search_row1, 
                                       values=['Todos', 'Ganado Bovino', 'Ganado Porcino', 'Avicultura', 'Mixto'], 
                                       state='readonly', width=15, font=('Segoe UI', 10))
        self.tipo_filter.set('Todos')
        self.tipo_filter.pack(side='left', padx=(10, 20))
        self.tipo_filter.bind('<<ComboboxSelected>>', self.filter_fincas)
        
        # Lista de fincas con estilo moderno
        list_frame = ttk.LabelFrame(main_frame, text=f"{Icons.HOME} Lista de Fincas", padding="15")
        list_frame.pack(expand=True, fill='both')
        
        # Treeview moderno
        columns = ('ID', 'Nombre', 'Dirección', 'Extensión (ha)', 'Tipo Producción', 'Propietario', 'Teléfono', 'Fecha Fundación')
        self.fincas_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18, style='Modern.Treeview')
        
        # Configurar columnas con anchos apropiados
        column_widths = [50, 150, 200, 100, 120, 120, 100, 120]
        for i, col in enumerate(columns):
            self.fincas_tree.heading(col, text=col)
            self.fincas_tree.column(col, width=column_widths[i], anchor='center')
        
        # Scrollbar moderno
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.fincas_tree.yview)
        self.fincas_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview y scrollbar
        self.fincas_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Cargar datos
        self.refresh_fincas_list()
    
    def create_fincas_stats_cards(self, parent):
        """Crea las tarjetas de estadísticas de fincas"""
        # Obtener estadísticas de la base de datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total de fincas
        cursor.execute('SELECT COUNT(*) FROM fincas WHERE usuario_id = ?', (self.current_user_id,))
        total_fincas = cursor.fetchone()[0]
        
        # Fincas por tipo de producción
        cursor.execute('SELECT tipo_produccion, COUNT(*) FROM fincas WHERE usuario_id = ? GROUP BY tipo_produccion', (self.current_user_id,))
        tipos = cursor.fetchall()
        
        # Extensión total
        cursor.execute('SELECT SUM(extension) FROM fincas WHERE usuario_id = ?', (self.current_user_id,))
        extension_total = cursor.fetchone()[0] or 0
        
        # Fincas con más de 100 hectáreas
        cursor.execute('SELECT COUNT(*) FROM fincas WHERE usuario_id = ? AND extension > 100', (self.current_user_id,))
        fincas_grandes = cursor.fetchone()[0]
        
        conn.close()
        
        # Crear tarjetas
        stats_data = [
            (f"{Icons.HOME}", "Total", str(total_fincas), ModernTheme.PRIMARY),
            (f"{Icons.ANIMALS}", "Bovino", str(sum(1 for t in tipos if 'Bovino' in t[0])), ModernTheme.SUCCESS),
            (f"{Icons.INFO}", "Extensión Total", f"{extension_total:.1f} ha", ModernTheme.INFO),
            (f"{Icons.WARNING}", "Grandes (>100ha)", str(fincas_grandes), ModernTheme.WARNING)
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
    
    def refresh_fincas_list(self):
        """Actualiza la lista de fincas"""
        # Limpiar lista
        for item in self.fincas_tree.get_children():
            self.fincas_tree.delete(item)
        
        # Obtener fincas de la base de datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, nombre, direccion, extension, tipo_produccion, propietario, telefono, fecha_fundacion
            FROM fincas
            WHERE usuario_id = ?
            ORDER BY nombre
        '''
        
        cursor.execute(query, (self.current_user_id,))
        fincas = cursor.fetchall()
        
        for finca in fincas:
            # Agregar iconos según el tipo de producción
            tipo_icon = self.get_tipo_icon(finca[4])
            
            # Crear valores con iconos
            values = list(finca)
            values[3] = f"{finca[3]:.1f}" if finca[3] else "0.0"  # Formatear extensión
            values[4] = f"{tipo_icon} {finca[4]}" if finca[4] else f"{tipo_icon} No especificado"  # Tipo con icono
            
            self.fincas_tree.insert('', 'end', values=values)
        
        conn.close()
    
    def filter_fincas(self, *args):
        """Filtra la lista de fincas según los criterios de búsqueda"""
        search_text = self.search_var.get().lower()
        tipo_filter = self.tipo_filter.get()
        
        # Limpiar lista
        for item in self.fincas_tree.get_children():
            self.fincas_tree.delete(item)
        
        # Obtener fincas filtradas
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, nombre, direccion, extension, tipo_produccion, propietario, telefono, fecha_fundacion
            FROM fincas
            WHERE usuario_id = ?
        '''
        
        params = [self.current_user_id]
        
        if search_text:
            query += ' AND (LOWER(nombre) LIKE ? OR LOWER(direccion) LIKE ? OR LOWER(propietario) LIKE ?)'
            search_param = f'%{search_text}%'
            params.extend([search_param, search_param, search_param])
        
        if tipo_filter != 'Todos':
            query += ' AND tipo_produccion LIKE ?'
            params.append(f'%{tipo_filter}%')
        
        query += ' ORDER BY nombre'
        
        cursor.execute(query, params)
        fincas = cursor.fetchall()
        
        for finca in fincas:
            # Agregar iconos según el tipo de producción
            tipo_icon = self.get_tipo_icon(finca[4])
            
            # Crear valores con iconos
            values = list(finca)
            values[3] = f"{finca[3]:.1f}" if finca[3] else "0.0"  # Formatear extensión
            values[4] = f"{tipo_icon} {finca[4]}" if finca[4] else f"{tipo_icon} No especificado"  # Tipo con icono
            
            self.fincas_tree.insert('', 'end', values=values)
        
        conn.close()
    
    def get_tipo_icon(self, tipo):
        """Obtiene el icono correspondiente al tipo de producción"""
        if not tipo:
            return Icons.INFO
        
        tipo_lower = tipo.lower()
        if 'bovino' in tipo_lower:
            return Icons.COW
        elif 'porcino' in tipo_lower:
            return Icons.PIG
        elif 'avicultura' in tipo_lower or 'pollo' in tipo_lower:
            return Icons.CHICKEN
        elif 'mixto' in tipo_lower:
            return Icons.ANIMALS
        else:
            return Icons.HOME
    
    def new_finca_dialog(self):
        """Abre el diálogo para crear una nueva finca"""
        dialog = FincaDialog(self.fincas_window, self.db, self.current_user_id)
        self.fincas_window.wait_window(dialog.dialog)
        self.refresh_fincas_list()
    
    def edit_finca(self):
        """Edita la finca seleccionada"""
        selection = self.fincas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione una finca para editar")
            return
        
        item = self.fincas_tree.item(selection[0])
        finca_id = item['values'][0]
        
        dialog = FincaDialog(self.fincas_window, self.db, self.current_user_id, finca_id)
        self.fincas_window.wait_window(dialog.dialog)
        self.refresh_fincas_list()
    
    def delete_finca(self):
        """Elimina la finca seleccionada"""
        selection = self.fincas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione una finca para eliminar")
            return
        
        item = self.fincas_tree.item(selection[0])
        finca_id = item['values'][0]
        nombre = item['values'][1]
        
        # Verificar si hay datos relacionados
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Verificar animales
        cursor.execute('SELECT COUNT(*) FROM animales WHERE finca_id = ?', (finca_id,))
        animales_count = cursor.fetchone()[0]
        
        # Verificar potreros
        cursor.execute('SELECT COUNT(*) FROM potreros WHERE finca_id = ?', (finca_id,))
        potreros_count = cursor.fetchone()[0]
        
        # Verificar empleados
        cursor.execute('SELECT COUNT(*) FROM empleados WHERE finca_id = ?', (finca_id,))
        empleados_count = cursor.fetchone()[0]
        
        conn.close()
        
        if animales_count > 0 or potreros_count > 0 or empleados_count > 0:
            messagebox.showerror("Error", 
                f"No se puede eliminar la finca '{nombre}' porque tiene datos relacionados:\n"
                f"- {animales_count} animal(es)\n"
                f"- {potreros_count} potrero(s)\n"
                f"- {empleados_count} empleado(s)")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la finca '{nombre}'?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM fincas WHERE id = ?', (finca_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Finca eliminada correctamente")
                self.refresh_fincas_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar finca: {str(e)}")
            finally:
                conn.close()
    
    def view_finca_details(self):
        """Muestra los detalles de la finca seleccionada"""
        selection = self.fincas_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione una finca para ver sus detalles")
            return
        
        item = self.fincas_tree.item(selection[0])
        finca_id = item['values'][0]
        
        # Crear ventana de detalles
        details_window = tk.Toplevel(self.fincas_window)
        details_window.title(f"Detalles de la Finca - {item['values'][1]}")
        details_window.geometry("700x600")
        details_window.configure(bg=ModernTheme.BACKGROUND)
        
        # Configurar estilos
        style = ttk.Style()
        ModernStyles.configure_modern_theme(style)
        
        # Obtener información detallada de la finca
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT nombre, direccion, extension, tipo_produccion, propietario, 
                   telefono, email, fecha_fundacion, descripcion, ubicacion
            FROM fincas
            WHERE id = ?
        ''', (finca_id,))
        
        finca_info = cursor.fetchone()
        
        # Obtener estadísticas de la finca
        cursor.execute('SELECT COUNT(*) FROM animales WHERE finca_id = ?', (finca_id,))
        total_animales = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM potreros WHERE finca_id = ?', (finca_id,))
        total_potreros = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM empleados WHERE finca_id = ?', (finca_id,))
        total_empleados = cursor.fetchone()[0]
        
        conn.close()
        
        if not finca_info:
            messagebox.showerror("Error", "No se encontró información de la finca")
            return
        
        # Frame principal
        main_frame = ttk.Frame(details_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text=f"{Icons.HOME} {finca_info[0]}", 
                               style='Title.TLabel')
        title_label.pack(pady=15)
        
        # Información de la finca
        info_frame = ttk.LabelFrame(main_frame, text=f"{Icons.INFO} Información General", padding="15")
        info_frame.pack(fill='x', pady=(0, 20))
        
        info_text = f"""
Dirección: {finca_info[1]}
Extensión: {finca_info[2]:.1f} hectáreas
Tipo de Producción: {finca_info[3] or 'No especificado'}
Propietario: {finca_info[4] or 'No especificado'}
Teléfono: {finca_info[5] or 'No especificado'}
Email: {finca_info[6] or 'No especificado'}
Fecha de Fundación: {finca_info[7] or 'No especificado'}
Ubicación: {finca_info[9] or 'No especificado'}
        """
        
        ttk.Label(info_frame, text=info_text.strip(), justify='left', style='Info.TLabel').pack(anchor='w')
        
        # Descripción
        if finca_info[8]:
            desc_frame = ttk.LabelFrame(main_frame, text=f"{Icons.INFO} Descripción", padding="15")
            desc_frame.pack(fill='x', pady=(0, 20))
            
            desc_text = tk.Text(desc_frame, height=4, wrap='word', font=('Segoe UI', 10))
            desc_text.pack(fill='x')
            desc_text.insert('1.0', finca_info[8])
            desc_text.config(state='disabled')
        
        # Estadísticas
        stats_frame = ttk.LabelFrame(main_frame, text=f"{Icons.DASHBOARD} Estadísticas", padding="15")
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stats_text = f"""
Total de Animales: {total_animales}
Total de Potreros: {total_potreros}
Total de Empleados: {total_empleados}
        """
        
        ttk.Label(stats_frame, text=stats_text.strip(), justify='left', style='Info.TLabel').pack(anchor='w')
        
        # Botón cerrar
        ttk.Button(main_frame, text=f"{Icons.CANCEL} Cerrar", command=details_window.destroy, 
                  style='Secondary.TButton').pack(pady=20)

class FincaDialog:
    """Diálogo para crear/editar fincas"""
    
    def __init__(self, parent, db_manager, user_id, finca_id=None):
        self.parent = parent
        self.db = db_manager
        self.user_id = user_id
        self.finca_id = finca_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{Icons.ADD if not finca_id else Icons.EDIT} {'Nueva Finca' if not finca_id else 'Editar Finca'}")
        self.dialog.geometry("600x700")
        self.dialog.configure(bg=ModernTheme.BACKGROUND)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configurar estilos modernos
        style = ttk.Style()
        ModernStyles.configure_modern_theme(style)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.load_data() if finca_id else None
    
    def create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Header con título
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title = f"{Icons.ADD if not self.finca_id else Icons.EDIT} {'Nueva Finca' if not self.finca_id else 'Editar Finca'}"
        ttk.Label(header_frame, text=title, style='Title.TLabel').pack(pady=15)
        
        # Frame de formulario con scroll
        canvas = tk.Canvas(main_frame, bg=ModernTheme.BACKGROUND)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame de formulario
        form_frame = ttk.LabelFrame(scrollable_frame, text=f"{Icons.HOME} Información de la Finca", padding="20")
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Campos del formulario con mejor diseño
        row = 0
        
        # Nombre
        ttk.Label(form_frame, text=f"{Icons.INFO} Nombre *:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Dirección
        ttk.Label(form_frame, text=f"{Icons.INFO} Dirección *:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.direccion_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.direccion_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Extensión
        ttk.Label(form_frame, text=f"{Icons.INFO} Extensión (hectáreas) *:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.extension_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.extension_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Tipo de producción
        ttk.Label(form_frame, text=f"{Icons.ANIMALS} Tipo de Producción:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.tipo_produccion_var = tk.StringVar()
        tipo_combo = ttk.Combobox(form_frame, textvariable=self.tipo_produccion_var, 
                                 values=['Ganado Bovino', 'Ganado Porcino', 'Avicultura', 'Mixto', 'Otro'],
                                 state='readonly', width=32, font=('Segoe UI', 10))
        tipo_combo.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Propietario
        ttk.Label(form_frame, text=f"{Icons.USER} Propietario:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.propietario_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.propietario_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Teléfono
        ttk.Label(form_frame, text=f"{Icons.INFO} Teléfono:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.telefono_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.telefono_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Email
        ttk.Label(form_frame, text=f"{Icons.INFO} Email:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Fecha de fundación
        ttk.Label(form_frame, text=f"{Icons.CALENDAR} Fecha de Fundación:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.fecha_fundacion_var = tk.StringVar()
        fecha_entry = ttk.Entry(form_frame, textvariable=self.fecha_fundacion_var, width=35, font=('Segoe UI', 10))
        fecha_entry.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        fecha_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        row += 1
        
        # Ubicación
        ttk.Label(form_frame, text=f"{Icons.INFO} Ubicación:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.ubicacion_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ubicacion_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Descripción
        ttk.Label(form_frame, text=f"{Icons.INFO} Descripción:", style='Header.TLabel').grid(row=row, column=0, sticky='nw', pady=8)
        self.descripcion_text = tk.Text(form_frame, width=35, height=4, font=('Segoe UI', 10))
        self.descripcion_text.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Configurar columnas para que se expandan
        form_frame.columnconfigure(1, weight=1)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones con estilo moderno
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        ttk.Button(buttons_frame, text=f"{Icons.SAVE} Guardar", command=self.save_finca, style='Primary.TButton').pack(side='right', padx=(10, 0))
        ttk.Button(buttons_frame, text=f"{Icons.CANCEL} Cancelar", command=self.dialog.destroy, style='Secondary.TButton').pack(side='right')
    
    def load_data(self):
        """Carga los datos de la finca para edición"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT nombre, direccion, extension, tipo_produccion, propietario, 
                   telefono, email, fecha_fundacion, descripcion, ubicacion
            FROM fincas WHERE id = ?
        ''', (self.finca_id,))
        
        finca = cursor.fetchone()
        
        if finca:
            self.nombre_var.set(finca[0])
            self.direccion_var.set(finca[1])
            self.extension_var.set(str(finca[2]) if finca[2] else '')
            self.tipo_produccion_var.set(finca[3] or '')
            self.propietario_var.set(finca[4] or '')
            self.telefono_var.set(finca[5] or '')
            self.email_var.set(finca[6] or '')
            self.fecha_fundacion_var.set(finca[7] or '')
            self.ubicacion_var.set(finca[9] or '')
            self.descripcion_text.insert('1.0', finca[8] or '')
        
        conn.close()
    
    def save_finca(self):
        """Guarda la finca en la base de datos"""
        # Validaciones
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        if not self.direccion_var.get().strip():
            messagebox.showerror("Error", "La dirección es obligatoria")
            return
        
        try:
            extension = float(self.extension_var.get()) if self.extension_var.get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Error", "La extensión debe ser un número válido")
            return
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.finca_id:
                # Actualizar finca existente
                cursor.execute('''
                    UPDATE fincas SET
                        nombre = ?, direccion = ?, extension = ?, tipo_produccion = ?, 
                        propietario = ?, telefono = ?, email = ?, fecha_fundacion = ?, 
                        descripcion = ?, ubicacion = ?
                    WHERE id = ?
                ''', (
                    self.nombre_var.get().strip(),
                    self.direccion_var.get().strip(),
                    extension,
                    self.tipo_produccion_var.get() or None,
                    self.propietario_var.get().strip() or None,
                    self.telefono_var.get().strip() or None,
                    self.email_var.get().strip() or None,
                    self.fecha_fundacion_var.get().strip() or None,
                    self.descripcion_text.get('1.0', 'end-1c').strip() or None,
                    self.ubicacion_var.get().strip() or None,
                    self.finca_id
                ))
            else:
                # Crear nueva finca
                cursor.execute('''
                    INSERT INTO fincas (
                        nombre, direccion, extension, tipo_produccion, propietario,
                        telefono, email, fecha_fundacion, descripcion, ubicacion, usuario_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.nombre_var.get().strip(),
                    self.direccion_var.get().strip(),
                    extension,
                    self.tipo_produccion_var.get() or None,
                    self.propietario_var.get().strip() or None,
                    self.telefono_var.get().strip() or None,
                    self.email_var.get().strip() or None,
                    self.fecha_fundacion_var.get().strip() or None,
                    self.descripcion_text.get('1.0', 'end-1c').strip() or None,
                    self.ubicacion_var.get().strip() or None,
                    self.user_id
                ))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Finca guardada correctamente")
            self.dialog.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe una finca con ese nombre")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar finca: {str(e)}")
        finally:
            conn.close()
