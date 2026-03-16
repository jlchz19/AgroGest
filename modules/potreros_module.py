#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestión de Potreros
Funcionalidades para el manejo de potreros en la aplicación de escritorio
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from typing import List, Dict, Optional, Any
import sys
import os

# Agregar el directorio padre al path para importar themes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from themes import ModernTheme, Icons, ModernStyles

class PotrerosModule:
    """Módulo para la gestión de potreros"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.current_finca_id = None
    
    def show_potreros_window(self, finca_id: int = None):
        """Muestra la ventana principal de gestión de potreros"""
        self.current_finca_id = finca_id
        
        # Crear ventana
        self.potreros_window = tk.Toplevel(self.parent)
        self.potreros_window.title(f"{Icons.PASTURES} Gestión de Potreros")
        self.potreros_window.geometry("1200x800")
        self.potreros_window.configure(bg=ModernTheme.BACKGROUND)
        
        # Configurar estilos modernos
        style = ttk.Style()
        ModernStyles.configure_modern_theme(style)
        
        # Frame principal
        main_frame = ttk.Frame(self.potreros_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Header con título y estadísticas
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título con icono
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left', padx=20, pady=15)
        
        title_label = ttk.Label(title_frame, text=f"{Icons.PASTURES} Gestión de Potreros", 
                               style='Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_frame, text="Administra los potreros y su ocupación", 
                                  style='Info.TLabel')
        subtitle_label.pack(anchor='w')
        
        # Estadísticas rápidas
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side='right', padx=20, pady=15)
        
        self.create_potreros_stats_cards(stats_frame)
        
        # Frame de botones con estilo moderno
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(0, 15))
        
        # Botones principales
        ttk.Button(buttons_frame, text=f"{Icons.ADD} Nuevo Potrero", 
                  command=self.new_potrero_dialog, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.EDIT} Editar", 
                  command=self.edit_potrero, style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.DELETE} Eliminar", 
                  command=self.delete_potrero, style='Danger.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.INFO} Detalles", 
                  command=self.view_potrero_details, style='Warning.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(buttons_frame, text=f"{Icons.REFRESH} Actualizar", 
                  command=self.refresh_potreros_list, style='Success.TButton').pack(side='left', padx=(10, 0))
        
        # Frame de búsqueda moderno
        search_frame = ttk.LabelFrame(main_frame, text=f"{Icons.SEARCH} Búsqueda y Filtros", padding="15")
        search_frame.pack(fill='x', pady=(0, 15))
        
        # Primera fila de búsqueda
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_row1, text="Buscar:", style='Header.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_potreros)
        search_entry = ttk.Entry(search_row1, textvariable=self.search_var, width=40, font=('Segoe UI', 10))
        search_entry.pack(side='left', padx=(10, 20))
        
        # Filtros
        ttk.Label(search_row1, text="Estado:", style='Header.TLabel').pack(side='left')
        self.estado_filter = ttk.Combobox(search_row1, values=['Todos', 'Disponible', 'Ocupado', 'Mantenimiento'], 
                                         state='readonly', width=15, font=('Segoe UI', 10))
        self.estado_filter.set('Todos')
        self.estado_filter.pack(side='left', padx=(10, 20))
        self.estado_filter.bind('<<ComboboxSelected>>', self.filter_potreros)
        
        # Filtro de función
        ttk.Label(search_row1, text="Función:", style='Header.TLabel').pack(side='left')
        self.funcion_filter = ttk.Combobox(search_row1, values=['Todas', 'Cría', 'Engorde', 'Lechería', 'Reproducción', 'Aislamiento'], 
                                          state='readonly', width=15, font=('Segoe UI', 10))
        self.funcion_filter.set('Todas')
        self.funcion_filter.pack(side='left', padx=(10, 0))
        self.funcion_filter.bind('<<ComboboxSelected>>', self.filter_potreros)
        
        # Lista de potreros con estilo moderno
        list_frame = ttk.LabelFrame(main_frame, text=f"{Icons.PASTURES} Lista de Potreros", padding="15")
        list_frame.pack(expand=True, fill='both')
        
        # Treeview moderno
        columns = ('ID', 'Nombre', 'Área (ha)', 'Capacidad', 'Ocupación', 'Estado', 'Función')
        self.potreros_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18, style='Modern.Treeview')
        
        # Configurar columnas con anchos apropiados
        column_widths = [50, 150, 80, 80, 100, 120, 120]
        for i, col in enumerate(columns):
            self.potreros_tree.heading(col, text=col)
            self.potreros_tree.column(col, width=column_widths[i], anchor='center')
        
        # Scrollbar moderno
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.potreros_tree.yview)
        self.potreros_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview y scrollbar
        self.potreros_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Cargar datos
        self.refresh_potreros_list()
    
    def create_potreros_stats_cards(self, parent):
        """Crea las tarjetas de estadísticas de potreros"""
        # Obtener estadísticas de la base de datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total de potreros
        cursor.execute('SELECT COUNT(*) FROM potreros WHERE finca_id = ?', (self.current_finca_id,))
        total_potreros = cursor.fetchone()[0]
        
        # Potreros disponibles
        cursor.execute('SELECT COUNT(*) FROM potreros WHERE finca_id = ? AND estado = "Disponible"', (self.current_finca_id,))
        disponibles = cursor.fetchone()[0]
        
        # Potreros ocupados
        cursor.execute('SELECT COUNT(*) FROM potreros WHERE finca_id = ? AND estado = "Ocupado"', (self.current_finca_id,))
        ocupados = cursor.fetchone()[0]
        
        # Área total
        cursor.execute('SELECT SUM(area) FROM potreros WHERE finca_id = ?', (self.current_finca_id,))
        area_total = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Crear tarjetas
        stats_data = [
            (f"{Icons.PASTURES}", "Total", str(total_potreros), ModernTheme.PRIMARY),
            (f"{Icons.ACTIVE}", "Disponibles", str(disponibles), ModernTheme.SUCCESS),
            (f"{Icons.WARNING}", "Ocupados", str(ocupados), ModernTheme.WARNING),
            (f"{Icons.INFO}", "Área Total", f"{area_total:.1f} ha", ModernTheme.INFO)
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
    
    def refresh_potreros_list(self):
        """Actualiza la lista de potreros"""
        # Limpiar lista
        for item in self.potreros_tree.get_children():
            self.potreros_tree.delete(item)
        
        # Obtener potreros de la base de datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT p.id, p.nombre, p.area, p.capacidad, p.estado, p.funcion,
                   COUNT(a.id) as ocupacion
            FROM potreros p
            LEFT JOIN animales a ON p.id = a.potrero_id
            WHERE p.finca_id = ?
            GROUP BY p.id, p.nombre, p.area, p.capacidad, p.estado, p.funcion
            ORDER BY p.nombre
        '''
        
        cursor.execute(query, (self.current_finca_id,))
        potreros = cursor.fetchall()
        
        for potrero in potreros:
            ocupacion = f"{potrero[6]}/{potrero[3]}"
            self.potreros_tree.insert('', 'end', values=(
                potrero[0], potrero[1], potrero[2], potrero[3], 
                ocupacion, potrero[4], potrero[5]
            ))
        
        conn.close()
    
    def filter_potreros(self, *args):
        """Filtra la lista de potreros según los criterios de búsqueda"""
        search_text = self.search_var.get().lower()
        estado_filter = self.estado_filter.get()
        funcion_filter = self.funcion_filter.get()
        
        # Limpiar lista
        for item in self.potreros_tree.get_children():
            self.potreros_tree.delete(item)
        
        # Obtener potreros filtrados
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT p.id, p.nombre, p.area, p.capacidad, p.estado, p.funcion,
                   COUNT(a.id) as ocupacion
            FROM potreros p
            LEFT JOIN animales a ON p.id = a.potrero_id
            WHERE p.finca_id = ?
        '''
        
        params = [self.current_finca_id]
        
        if search_text:
            query += ' AND (LOWER(p.nombre) LIKE ? OR LOWER(p.funcion) LIKE ?)'
            search_param = f'%{search_text}%'
            params.extend([search_param, search_param])
        
        if estado_filter != 'Todos':
            query += ' AND p.estado = ?'
            params.append(estado_filter)
        
        if funcion_filter != 'Todas':
            query += ' AND p.funcion = ?'
            params.append(funcion_filter)
        
        query += '''
            GROUP BY p.id, p.nombre, p.area, p.capacidad, p.estado, p.funcion
            ORDER BY p.nombre
        '''
        
        cursor.execute(query, params)
        potreros = cursor.fetchall()
        
        for potrero in potreros:
            ocupacion = f"{potrero[6]}/{potrero[3]}"
            
            # Agregar iconos según el estado
            estado_icon = self.get_estado_icon(potrero[4])
            funcion_icon = self.get_funcion_icon(potrero[5])
            
            # Crear valores con iconos
            values = [
                potrero[0],  # ID
                potrero[1],  # Nombre
                f"{potrero[2]:.1f}",  # Área
                str(potrero[3]),  # Capacidad
                ocupacion,  # Ocupación
                f"{estado_icon} {potrero[4]}",  # Estado con icono
                f"{funcion_icon} {potrero[5]}"  # Función con icono
            ]
            
            self.potreros_tree.insert('', 'end', values=values)
        
        conn.close()
    
    def get_estado_icon(self, estado):
        """Obtiene el icono correspondiente al estado del potrero"""
        icon_map = {
            'Disponible': Icons.ACTIVE,
            'Ocupado': Icons.WARNING,
            'Mantenimiento': Icons.ERROR
        }
        return icon_map.get(estado, Icons.ACTIVE)
    
    def get_funcion_icon(self, funcion):
        """Obtiene el icono correspondiente a la función del potrero"""
        icon_map = {
            'Cría': Icons.ANIMALS,
            'Engorde': Icons.WEIGHT,
            'Lechería': Icons.COW,
            'Reproducción': Icons.ANIMALS,
            'Aislamiento': Icons.WARNING
        }
        return icon_map.get(funcion, Icons.PASTURES)
    
    def new_potrero_dialog(self):
        """Abre el diálogo para crear un nuevo potrero"""
        dialog = PotreroDialog(self.potreros_window, self.db, self.current_finca_id)
        self.potreros_window.wait_window(dialog.dialog)
        self.refresh_potreros_list()
    
    def edit_potrero(self):
        """Edita el potrero seleccionado"""
        selection = self.potreros_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un potrero para editar")
            return
        
        item = self.potreros_tree.item(selection[0])
        potrero_id = item['values'][0]
        
        dialog = PotreroDialog(self.potreros_window, self.db, self.current_finca_id, potrero_id)
        self.potreros_window.wait_window(dialog.dialog)
        self.refresh_potreros_list()
    
    def delete_potrero(self):
        """Elimina el potrero seleccionado"""
        selection = self.potreros_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un potrero para eliminar")
            return
        
        item = self.potreros_tree.item(selection[0])
        potrero_id = item['values'][0]
        nombre = item['values'][1]
        
        # Verificar si hay animales en el potrero
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM animales WHERE potrero_id = ?', (potrero_id,))
        animal_count = cursor.fetchone()[0]
        
        if animal_count > 0:
            messagebox.showerror("Error", f"No se puede eliminar el potrero '{nombre}' porque tiene {animal_count} animal(es) asignado(s)")
            conn.close()
            return
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el potrero '{nombre}'?"):
            try:
                cursor.execute('DELETE FROM potreros WHERE id = ?', (potrero_id,))
                conn.commit()
                messagebox.showinfo("Éxito", "Potrero eliminado correctamente")
                self.refresh_potreros_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar potrero: {str(e)}")
            finally:
                conn.close()
    
    def view_potrero_details(self):
        """Muestra los detalles del potrero seleccionado"""
        selection = self.potreros_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor seleccione un potrero para ver sus detalles")
            return
        
        item = self.potreros_tree.item(selection[0])
        potrero_id = item['values'][0]
        
        # Crear ventana de detalles
        details_window = tk.Toplevel(self.potreros_window)
        details_window.title(f"Detalles del Potrero - {item['values'][1]}")
        details_window.geometry("600x500")
        
        # Obtener información detallada del potrero
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.nombre, p.area, p.capacidad, p.estado, p.funcion, p.fecha_creacion,
                   COUNT(a.id) as ocupacion
            FROM potreros p
            LEFT JOIN animales a ON p.id = a.potrero_id
            WHERE p.id = ?
            GROUP BY p.id
        ''', (potrero_id,))
        
        potrero_info = cursor.fetchone()
        
        # Obtener animales en el potrero
        cursor.execute('''
            SELECT identificacion, nombre, tipo, raza, peso_actual, estado
            FROM animales
            WHERE potrero_id = ?
            ORDER BY identificacion
        ''', (potrero_id,))
        
        animales = cursor.fetchall()
        conn.close()
        
        # Frame principal
        main_frame = ttk.Frame(details_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Información del potrero
        info_frame = ttk.LabelFrame(main_frame, text="Información del Potrero", padding="10")
        info_frame.pack(fill='x', pady=(0, 20))
        
        info_text = f"""
Nombre: {potrero_info[0]}
Área: {potrero_info[1]} hectáreas
Capacidad: {potrero_info[2]} animales
Ocupación: {potrero_info[6]}/{potrero_info[2]} animales
Estado: {potrero_info[3]}
Función: {potrero_info[4]}
Fecha de Creación: {potrero_info[5]}
        """
        
        ttk.Label(info_frame, text=info_text.strip(), justify='left').pack(anchor='w')
        
        # Lista de animales
        animales_frame = ttk.LabelFrame(main_frame, text="Animales en el Potrero", padding="10")
        animales_frame.pack(expand=True, fill='both')
        
        if animales:
            columns = ('Identificación', 'Nombre', 'Tipo', 'Raza', 'Peso', 'Estado')
            animales_tree = ttk.Treeview(animales_frame, columns=columns, show='headings', height=10)
            
            for col in columns:
                animales_tree.heading(col, text=col)
                animales_tree.column(col, width=100)
            
            for animal in animales:
                animales_tree.insert('', 'end', values=animal)
            
            scrollbar = ttk.Scrollbar(animales_frame, orient='vertical', command=animales_tree.yview)
            animales_tree.configure(yscrollcommand=scrollbar.set)
            
            animales_tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
        else:
            ttk.Label(animales_frame, text="No hay animales en este potrero").pack(pady=20)

class PotreroDialog:
    """Diálogo para crear/editar potreros"""
    
    def __init__(self, parent, db_manager, finca_id, potrero_id=None):
        self.parent = parent
        self.db = db_manager
        self.finca_id = finca_id
        self.potrero_id = potrero_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Potrero" if not potrero_id else "Editar Potrero")
        self.dialog.geometry("400x500")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.load_data() if potrero_id else None
    
    def create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Título
        title = "Nuevo Potrero" if not self.potrero_id else "Editar Potrero"
        ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Frame de formulario
        form_frame = ttk.LabelFrame(main_frame, text="Información del Potrero", padding="10")
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Nombre
        ttk.Label(form_frame, text="Nombre *:").grid(row=0, column=0, sticky='w', pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nombre_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Área
        ttk.Label(form_frame, text="Área (hectáreas) *:").grid(row=1, column=0, sticky='w', pady=5)
        self.area_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.area_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Capacidad
        ttk.Label(form_frame, text="Capacidad (animales) *:").grid(row=2, column=0, sticky='w', pady=5)
        self.capacidad_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.capacidad_var, width=30).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Estado
        ttk.Label(form_frame, text="Estado:").grid(row=3, column=0, sticky='w', pady=5)
        self.estado_var = tk.StringVar()
        estado_combo = ttk.Combobox(form_frame, textvariable=self.estado_var,
                                   values=['Disponible', 'Ocupado', 'Mantenimiento'],
                                   state='readonly', width=27)
        estado_combo.set('Disponible')
        estado_combo.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Función
        ttk.Label(form_frame, text="Función *:").grid(row=4, column=0, sticky='w', pady=5)
        self.funcion_var = tk.StringVar()
        funcion_combo = ttk.Combobox(form_frame, textvariable=self.funcion_var,
                                    values=['Cría', 'Engorde', 'Lechería', 'Reproducción', 'Aislamiento', 'Otra'],
                                    state='readonly', width=27)
        funcion_combo.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Función personalizada
        ttk.Label(form_frame, text="Función personalizada:").grid(row=5, column=0, sticky='w', pady=5)
        self.funcion_custom_var = tk.StringVar()
        self.funcion_custom_entry = ttk.Entry(form_frame, textvariable=self.funcion_custom_var, width=30)
        self.funcion_custom_entry.grid(row=5, column=1, pady=5, padx=(10, 0))
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=20)
        
        ttk.Button(buttons_frame, text="Guardar", command=self.save_potrero).pack(side='right', padx=(10, 0))
        ttk.Button(buttons_frame, text="Cancelar", command=self.dialog.destroy).pack(side='right')
    
    def load_data(self):
        """Carga los datos del potrero para edición"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT nombre, area, capacidad, estado, funcion
            FROM potreros WHERE id = ?
        ''', (self.potrero_id,))
        
        potrero = cursor.fetchone()
        
        if potrero:
            self.nombre_var.set(potrero[0])
            self.area_var.set(str(potrero[1]))
            self.capacidad_var.set(str(potrero[2]))
            self.estado_var.set(potrero[3])
            
            # Verificar si la función está en la lista predefinida
            funciones_predefinidas = ['Cría', 'Engorde', 'Lechería', 'Reproducción', 'Aislamiento']
            if potrero[4] in funciones_predefinidas:
                self.funcion_var.set(potrero[4])
            else:
                self.funcion_var.set('Otra')
                self.funcion_custom_var.set(potrero[4])
        
        conn.close()
    
    def save_potrero(self):
        """Guarda el potrero en la base de datos"""
        # Validaciones
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        try:
            area = float(self.area_var.get())
        except ValueError:
            messagebox.showerror("Error", "El área debe ser un número válido")
            return
        
        try:
            capacidad = int(self.capacidad_var.get())
        except ValueError:
            messagebox.showerror("Error", "La capacidad debe ser un número entero válido")
            return
        
        if not self.funcion_var.get():
            messagebox.showerror("Error", "La función es obligatoria")
            return
        
        # Determinar función final
        if self.funcion_var.get() == 'Otra':
            if not self.funcion_custom_var.get().strip():
                messagebox.showerror("Error", "Debe especificar la función personalizada")
                return
            funcion_final = self.funcion_custom_var.get().strip()
        else:
            funcion_final = self.funcion_var.get()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.potrero_id:
                # Actualizar potrero existente
                cursor.execute('''
                    UPDATE potreros SET
                        nombre = ?, area = ?, capacidad = ?, estado = ?, funcion = ?
                    WHERE id = ?
                ''', (
                    self.nombre_var.get().strip(),
                    area,
                    capacidad,
                    self.estado_var.get(),
                    funcion_final,
                    self.potrero_id
                ))
            else:
                # Crear nuevo potrero
                cursor.execute('''
                    INSERT INTO potreros (nombre, area, capacidad, estado, funcion, finca_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    self.nombre_var.get().strip(),
                    area,
                    capacidad,
                    self.estado_var.get(),
                    funcion_final,
                    self.finca_id
                ))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Potrero guardado correctamente")
            self.dialog.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un potrero con ese nombre")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar potrero: {str(e)}")
        finally:
            conn.close()
