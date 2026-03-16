#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestión de Animales
Funcionalidades para el manejo de animales en la aplicación de escritorio
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

class AnimalesModule:
    """Módulo para la gestión de animales"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.current_finca_id = None
    
    def show_animales_window(self, finca_id: int = None):
        """Muestra la ventana principal de gestión de animales"""
        self.current_finca_id = finca_id
        
        # Crear ventana
        self.animales_window = tk.Toplevel(self.parent)
        self.animales_window.title(f"{Icons.ANIMALS} Gestión de Animales")
        self.animales_window.geometry("1200x800")
        self.animales_window.configure(bg=ModernTheme.BACKGROUND)
        
        # Configurar estilos modernos
        style = ttk.Style()
        ModernStyles.configure_modern_theme(style)
        
        # Frame principal
        main_frame = ttk.Frame(self.animales_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Header con título y estadísticas
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título con icono
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left', padx=20, pady=15)
        
        title_label = ttk.Label(title_frame, text=f"{Icons.ANIMALS} Gestión de Animales", 
                               style='Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_frame, text="Administra el inventario de animales de tu finca", 
                                  style='Info.TLabel')
        subtitle_label.pack(anchor='w')
        
        # Estadísticas rápidas
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side='right', padx=20, pady=15)
        
        self.create_stats_cards(stats_frame)
        
        # Frame de botones con estilo moderno
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(0, 15))
        
        # Botones principales
        ttk.Button(buttons_frame, text=f"{Icons.ADD} Nuevo Animal", 
                  command=self.new_animal_dialog, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.EDIT} Editar", 
                  command=self.edit_animal, style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.DELETE} Eliminar", 
                  command=self.delete_animal, style='Danger.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.REPORTS} Historial", 
                  command=self.view_animal_history, style='Warning.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.REFRESH} Actualizar", 
                  command=self.refresh_animales_list, style='Success.TButton').pack(side='left', padx=(10, 0))
        
        # Frame de búsqueda moderno
        search_frame = ttk.LabelFrame(main_frame, text=f"{Icons.SEARCH} Búsqueda y Filtros", padding="15")
        search_frame.pack(fill='x', pady=(0, 15))
        
        # Primera fila de búsqueda
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_row1, text="Buscar:", style='Header.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_animales)
        search_entry = ttk.Entry(search_row1, textvariable=self.search_var, width=40, font=('Segoe UI', 10))
        search_entry.pack(side='left', padx=(10, 20))
        
        # Filtros
        ttk.Label(search_row1, text="Tipo:", style='Header.TLabel').pack(side='left')
        self.tipo_filter = ttk.Combobox(search_row1, values=['Todos', 'Vaca', 'Cochino', 'Caballo', 'Oveja', 'Cabra', 'Pollo', 'Pavo'], 
                                       state='readonly', width=15, font=('Segoe UI', 10))
        self.tipo_filter.set('Todos')
        self.tipo_filter.pack(side='left', padx=(10, 20))
        self.tipo_filter.bind('<<ComboboxSelected>>', self.filter_animales)
        
        # Filtro de estado
        ttk.Label(search_row1, text="Estado:", style='Header.TLabel').pack(side='left')
        self.estado_filter = ttk.Combobox(search_row1, values=['Todos', 'Activo', 'En Producción', 'Gestante', 'Enfermo', 'Vendido', 'Muerto'], 
                                         state='readonly', width=15, font=('Segoe UI', 10))
        self.estado_filter.set('Todos')
        self.estado_filter.pack(side='left', padx=(10, 0))
        self.estado_filter.bind('<<ComboboxSelected>>', self.filter_animales)
        
        # Lista de animales con estilo moderno
        list_frame = ttk.LabelFrame(main_frame, text=f"{Icons.ANIMALS} Lista de Animales", padding="15")
        list_frame.pack(expand=True, fill='both')
        
        # Treeview moderno
        columns = ('ID', 'Identificación', 'Nombre', 'Tipo', 'Raza', 'Sexo', 'Peso (kg)', 'Estado', 'Potrero')
        self.animales_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18, style='Modern.Treeview')
        
        # Configurar columnas con anchos apropiados
        column_widths = [50, 120, 120, 80, 100, 60, 80, 100, 120]
        for i, col in enumerate(columns):
            self.animales_tree.heading(col, text=col)
            self.animales_tree.column(col, width=column_widths[i], anchor='center')
        
        # Scrollbar moderno
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.animales_tree.yview)
        self.animales_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview y scrollbar
        self.animales_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Cargar datos
        self.refresh_animales_list()
    
    def create_stats_cards(self, parent):
        """Crea las tarjetas de estadísticas"""
        # Obtener estadísticas de la base de datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total de animales
        cursor.execute('SELECT COUNT(*) FROM animales WHERE finca_id = ?', (self.current_finca_id,))
        total_animales = cursor.fetchone()[0]
        
        # Animales por tipo
        cursor.execute('SELECT tipo, COUNT(*) FROM animales WHERE finca_id = ? GROUP BY tipo', (self.current_finca_id,))
        tipos = cursor.fetchall()
        
        # Animales activos
        cursor.execute('SELECT COUNT(*) FROM animales WHERE finca_id = ? AND estado = "Activo"', (self.current_finca_id,))
        activos = cursor.fetchone()[0]
        
        conn.close()
        
        # Crear tarjetas
        stats_data = [
            (f"{Icons.ANIMALS}", "Total", str(total_animales), ModernTheme.PRIMARY),
            (f"{Icons.ACTIVE}", "Activos", str(activos), ModernTheme.SUCCESS),
            (f"{Icons.COW}", "Vacas", str(sum(1 for t in tipos if t[0] == 'Vaca')), ModernTheme.INFO),
            (f"{Icons.PIG}", "Cerdos", str(sum(1 for t in tipos if t[0] == 'Cochino')), ModernTheme.WARNING)
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
    
    def refresh_animales_list(self):
        """Actualiza la lista de animales"""
        # Limpiar lista
        for item in self.animales_tree.get_children():
            self.animales_tree.delete(item)
        
        # Obtener animales de la base de datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT a.id, a.identificacion, a.nombre, a.tipo, a.raza, a.sexo, 
                   a.peso_actual, a.estado, p.nombre as potrero_nombre
            FROM animales a
            LEFT JOIN potreros p ON a.potrero_id = p.id
            WHERE a.finca_id = ?
            ORDER BY a.identificacion
        '''
        
        cursor.execute(query, (self.current_finca_id,))
        animales = cursor.fetchall()
        
        for animal in animales:
            self.animales_tree.insert('', 'end', values=animal)
        
        conn.close()
    
    def filter_animales(self, *args):
        """Filtra la lista de animales según los criterios de búsqueda"""
        search_text = self.search_var.get().lower()
        tipo_filter = self.tipo_filter.get()
        estado_filter = self.estado_filter.get()
        
        # Limpiar lista
        for item in self.animales_tree.get_children():
            self.animales_tree.delete(item)
        
        # Obtener animales filtrados
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT a.id, a.identificacion, a.nombre, a.tipo, a.raza, a.sexo, 
                   a.peso_actual, a.estado, p.nombre as potrero_nombre
            FROM animales a
            LEFT JOIN potreros p ON a.potrero_id = p.id
            WHERE a.finca_id = ?
        '''
        
        params = [self.current_finca_id]
        
        if search_text:
            query += ' AND (LOWER(a.identificacion) LIKE ? OR LOWER(a.nombre) LIKE ? OR LOWER(a.raza) LIKE ?)'
            search_param = f'%{search_text}%'
            params.extend([search_param, search_param, search_param])
        
        if tipo_filter != 'Todos':
            query += ' AND a.tipo = ?'
            params.append(tipo_filter)
        
        if estado_filter != 'Todos':
            query += ' AND a.estado = ?'
            params.append(estado_filter)
        
        query += ' ORDER BY a.identificacion'
        
        cursor.execute(query, params)
        animales = cursor.fetchall()
        
        for animal in animales:
            # Agregar iconos según el tipo de animal
            tipo_icon = self.get_animal_icon(animal[3])
            estado_icon = self.get_estado_icon(animal[7])
            
            # Crear valores con iconos
            values = list(animal)
            values[3] = f"{tipo_icon} {animal[3]}"  # Tipo con icono
            values[7] = f"{estado_icon} {animal[7]}"  # Estado con icono
            
            self.animales_tree.insert('', 'end', values=values)
        
        conn.close()
    
    def get_animal_icon(self, tipo):
        """Obtiene el icono correspondiente al tipo de animal"""
        icon_map = {
            'Vaca': Icons.COW,
            'Cochino': Icons.PIG,
            'Caballo': Icons.HORSE,
            'Oveja': Icons.SHEEP,
            'Cabra': Icons.GOAT,
            'Pollo': Icons.CHICKEN,
            'Pavo': Icons.TURKEY
        }
        return icon_map.get(tipo, Icons.ANIMALS)
    
    def get_estado_icon(self, estado):
        """Obtiene el icono correspondiente al estado del animal"""
        icon_map = {
            'Activo': Icons.ACTIVE,
            'En Producción': Icons.SUCCESS,
            'Gestante': Icons.INFO,
            'Enfermo': Icons.WARNING,
            'Vendido': Icons.INFO,
            'Muerto': Icons.INACTIVE
        }
        return icon_map.get(estado, Icons.ACTIVE)
    
    def new_animal_dialog(self):
        """Abre el diálogo para crear un nuevo animal"""
        dialog = AnimalDialog(self.animales_window, self.db, self.current_finca_id)
        self.animales_window.wait_window(dialog.dialog)
        self.refresh_animales_list()
    
    def edit_animal(self):
        """Edita el animal seleccionado"""
        selection = self.animales_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un animal para editar")
            return
        
        item = self.animales_tree.item(selection[0])
        animal_id = item['values'][0]
        
        dialog = AnimalDialog(self.animales_window, self.db, self.current_finca_id, animal_id)
        self.animales_window.wait_window(dialog.dialog)
        self.refresh_animales_list()
    
    def delete_animal(self):
        """Elimina el animal seleccionado"""
        selection = self.animales_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un animal para eliminar")
            return
        
        item = self.animales_tree.item(selection[0])
        animal_id = item['values'][0]
        identificacion = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el animal {identificacion}?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM animales WHERE id = ?', (animal_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Animal eliminado correctamente")
                self.refresh_animales_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar animal: {str(e)}")
            finally:
                conn.close()
    
    def view_animal_history(self):
        """Muestra el historial del animal seleccionado"""
        selection = self.animales_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un animal para ver su historial")
            return
        
        item = self.animales_tree.item(selection[0])
        animal_id = item['values'][0]
        
        # Crear ventana de historial
        history_window = tk.Toplevel(self.animales_window)
        history_window.title(f"Historial del Animal - {item['values'][1]}")
        history_window.geometry("800x600")
        
        # Aquí se implementaría la vista del historial
        ttk.Label(history_window, text="Historial del Animal", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        ttk.Label(history_window, text="Funcionalidad en desarrollo").pack(pady=20)

class AnimalDialog:
    """Diálogo para crear/editar animales"""
    
    def __init__(self, parent, db_manager, finca_id, animal_id=None):
        self.parent = parent
        self.db = db_manager
        self.finca_id = finca_id
        self.animal_id = animal_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{Icons.ADD if not animal_id else Icons.EDIT} {'Nuevo Animal' if not animal_id else 'Editar Animal'}")
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
        self.load_data() if animal_id else None
    
    def create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Header con título
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title = f"{Icons.ADD if not self.animal_id else Icons.EDIT} {'Nuevo Animal' if not self.animal_id else 'Editar Animal'}"
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
        form_frame = ttk.LabelFrame(scrollable_frame, text=f"{Icons.ANIMALS} Información del Animal", padding="20")
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Campos del formulario con mejor diseño
        row = 0
        
        # Identificación
        ttk.Label(form_frame, text=f"{Icons.INFO} Identificación *:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.identificacion_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.identificacion_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Nombre
        ttk.Label(form_frame, text=f"{Icons.USER} Nombre:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Tipo
        ttk.Label(form_frame, text=f"{Icons.ANIMALS} Tipo *:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(form_frame, textvariable=self.tipo_var, 
                                 values=['Vaca', 'Cochino', 'Caballo', 'Oveja', 'Cabra', 'Pollo', 'Pavo'],
                                 state='readonly', width=32, font=('Segoe UI', 10))
        tipo_combo.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Raza
        ttk.Label(form_frame, text=f"{Icons.INFO} Raza *:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.raza_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.raza_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Sexo
        ttk.Label(form_frame, text=f"{Icons.INFO} Sexo:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.sexo_var = tk.StringVar()
        sexo_combo = ttk.Combobox(form_frame, textvariable=self.sexo_var,
                                 values=['Macho', 'Hembra'],
                                 state='readonly', width=32, font=('Segoe UI', 10))
        sexo_combo.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Fecha de nacimiento
        ttk.Label(form_frame, text=f"{Icons.CALENDAR} Fecha Nacimiento *:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.fecha_nacimiento_var = tk.StringVar()
        fecha_entry = ttk.Entry(form_frame, textvariable=self.fecha_nacimiento_var, width=35, font=('Segoe UI', 10))
        fecha_entry.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        fecha_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        row += 1
        
        # Peso actual
        ttk.Label(form_frame, text=f"{Icons.WEIGHT} Peso Actual (kg) *:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.peso_actual_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.peso_actual_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Peso al nacer
        ttk.Label(form_frame, text=f"{Icons.WEIGHT} Peso al Nacer (kg):", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.peso_nacimiento_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.peso_nacimiento_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Estado
        ttk.Label(form_frame, text=f"{Icons.ACTIVE} Estado:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.estado_var = tk.StringVar()
        estado_combo = ttk.Combobox(form_frame, textvariable=self.estado_var,
                                   values=['Activo', 'En Producción', 'Gestante', 'Enfermo', 'Vendido', 'Muerto'],
                                   state='readonly', width=32, font=('Segoe UI', 10))
        estado_combo.set('Activo')
        estado_combo.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Potrero
        ttk.Label(form_frame, text=f"{Icons.PASTURES} Potrero:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.potrero_var = tk.StringVar()
        self.potrero_combo = ttk.Combobox(form_frame, textvariable=self.potrero_var, width=32, font=('Segoe UI', 10))
        self.potrero_combo.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        self.load_potreros()
        row += 1
        
        # Color y señas
        ttk.Label(form_frame, text=f"{Icons.INFO} Color/Señas:", style='Header.TLabel').grid(row=row, column=0, sticky='w', pady=8)
        self.color_señas_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.color_señas_var, width=35, font=('Segoe UI', 10)).grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Observaciones
        ttk.Label(form_frame, text=f"{Icons.INFO} Observaciones:", style='Header.TLabel').grid(row=row, column=0, sticky='nw', pady=8)
        self.observaciones_text = tk.Text(form_frame, width=35, height=4, font=('Segoe UI', 10))
        self.observaciones_text.grid(row=row, column=1, pady=8, padx=(15, 0), sticky='ew')
        row += 1
        
        # Configurar columnas para que se expandan
        form_frame.columnconfigure(1, weight=1)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones con estilo moderno
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        ttk.Button(buttons_frame, text=f"{Icons.SAVE} Guardar", command=self.save_animal, style='Primary.TButton').pack(side='right', padx=(10, 0))
        ttk.Button(buttons_frame, text=f"{Icons.CANCEL} Cancelar", command=self.dialog.destroy, style='Secondary.TButton').pack(side='right')
    
    def load_potreros(self):
        """Carga la lista de potreros"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, nombre FROM potreros WHERE finca_id = ? ORDER BY nombre', (self.finca_id,))
        potreros = cursor.fetchall()
        
        potrero_list = ['Sin asignar']
        potrero_dict = {'Sin asignar': None}
        
        for potrero in potreros:
            potrero_list.append(potrero[1])
            potrero_dict[potrero[1]] = potrero[0]
        
        self.potrero_combo['values'] = potrero_list
        self.potrero_dict = potrero_dict
        self.potrero_combo.set('Sin asignar')
        
        conn.close()
    
    def load_data(self):
        """Carga los datos del animal para edición"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT identificacion, nombre, tipo, raza, sexo, fecha_nacimiento,
                   peso_actual, peso_nacimiento, estado, potrero_id, color_señas, observaciones
            FROM animales WHERE id = ?
        ''', (self.animal_id,))
        
        animal = cursor.fetchone()
        
        if animal:
            self.identificacion_var.set(animal[0])
            self.nombre_var.set(animal[1] or '')
            self.tipo_var.set(animal[2])
            self.raza_var.set(animal[3])
            self.sexo_var.set(animal[4] or '')
            self.fecha_nacimiento_var.set(animal[5])
            self.peso_actual_var.set(str(animal[6]))
            self.peso_nacimiento_var.set(str(animal[7]) if animal[7] else '')
            self.estado_var.set(animal[8])
            
            # Buscar nombre del potrero
            if animal[9]:
                cursor.execute('SELECT nombre FROM potreros WHERE id = ?', (animal[9],))
                potrero_nombre = cursor.fetchone()
                if potrero_nombre:
                    self.potrero_var.set(potrero_nombre[0])
            
            self.color_señas_var.set(animal[10] or '')
            self.observaciones_text.insert('1.0', animal[11] or '')
        
        conn.close()
    
    def save_animal(self):
        """Guarda el animal en la base de datos"""
        # Validaciones
        if not self.identificacion_var.get().strip():
            messagebox.showerror("Error", "La identificación es obligatoria")
            return
        
        if not self.tipo_var.get():
            messagebox.showerror("Error", "El tipo es obligatorio")
            return
        
        if not self.raza_var.get().strip():
            messagebox.showerror("Error", "La raza es obligatoria")
            return
        
        if not self.fecha_nacimiento_var.get().strip():
            messagebox.showerror("Error", "La fecha de nacimiento es obligatoria")
            return
        
        try:
            peso_actual = float(self.peso_actual_var.get())
        except ValueError:
            messagebox.showerror("Error", "El peso actual debe ser un número válido")
            return
        
        peso_nacimiento = None
        if self.peso_nacimiento_var.get().strip():
            try:
                peso_nacimiento = float(self.peso_nacimiento_var.get())
            except ValueError:
                messagebox.showerror("Error", "El peso al nacer debe ser un número válido")
                return
        
        # Obtener ID del potrero
        potrero_id = self.potrero_dict.get(self.potrero_var.get())
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.animal_id:
                # Actualizar animal existente
                cursor.execute('''
                    UPDATE animales SET
                        identificacion = ?, nombre = ?, tipo = ?, raza = ?, sexo = ?,
                        fecha_nacimiento = ?, peso_actual = ?, peso_nacimiento = ?,
                        estado = ?, potrero_id = ?, color_señas = ?, observaciones = ?
                    WHERE id = ?
                ''', (
                    self.identificacion_var.get().strip(),
                    self.nombre_var.get().strip() or None,
                    self.tipo_var.get(),
                    self.raza_var.get().strip(),
                    self.sexo_var.get() or None,
                    self.fecha_nacimiento_var.get().strip(),
                    peso_actual,
                    peso_nacimiento,
                    self.estado_var.get(),
                    potrero_id,
                    self.color_señas_var.get().strip() or None,
                    self.observaciones_text.get('1.0', 'end-1c').strip() or None,
                    self.animal_id
                ))
            else:
                # Crear nuevo animal
                cursor.execute('''
                    INSERT INTO animales (
                        identificacion, nombre, tipo, raza, sexo, fecha_nacimiento,
                        peso_actual, peso_nacimiento, estado, potrero_id, color_señas,
                        observaciones, finca_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.identificacion_var.get().strip(),
                    self.nombre_var.get().strip() or None,
                    self.tipo_var.get(),
                    self.raza_var.get().strip(),
                    self.sexo_var.get() or None,
                    self.fecha_nacimiento_var.get().strip(),
                    peso_actual,
                    peso_nacimiento,
                    self.estado_var.get(),
                    potrero_id,
                    self.color_señas_var.get().strip() or None,
                    self.observaciones_text.get('1.0', 'end-1c').strip() or None,
                    self.finca_id
                ))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Animal guardado correctamente")
            self.dialog.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un animal con esa identificación")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar animal: {str(e)}")
        finally:
            conn.close()
