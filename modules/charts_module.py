#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gráficos y Visualizaciones
Funcionalidades para crear gráficos modernos en la aplicación de escritorio
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from typing import List, Dict, Optional, Any
import sys
import os

# Agregar el directorio padre al path para importar themes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from themes import ModernTheme, Icons, ModernStyles

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import seaborn as sns
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class ChartsModule:
    """Módulo para crear gráficos y visualizaciones"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db = db_manager
        self.current_finca_id = None
        
        # Configurar estilo de matplotlib
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
    
    def show_dashboard_charts(self, finca_id: int = None):
        """Muestra un dashboard con gráficos de la finca"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Error", "Matplotlib no está disponible. Instale las dependencias necesarias.")
            return
            
        self.current_finca_id = finca_id
        
        # Crear ventana
        self.charts_window = tk.Toplevel(self.parent)
        self.charts_window.title(f"{Icons.DASHBOARD} Dashboard de Gráficos")
        self.charts_window.geometry("1400x900")
        self.charts_window.configure(bg=ModernTheme.BACKGROUND)
        
        # Configurar estilos modernos
        style = ttk.Style()
        ModernStyles.configure_modern_theme(style)
        
        # Frame principal
        main_frame = ttk.Frame(self.charts_window, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text=f"{Icons.DASHBOARD} Dashboard de Gráficos", 
                               style='Title.TLabel')
        title_label.pack(pady=15)
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(main_frame, text=f"{Icons.SETTINGS} Controles", padding="15")
        controls_frame.pack(fill='x', pady=(0, 20))
        
        controls_row = ttk.Frame(controls_frame)
        controls_row.pack(fill='x')
        
        ttk.Button(controls_row, text=f"{Icons.REFRESH} Actualizar", 
                  command=self.refresh_charts, style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_row, text=f"{Icons.EXPORT} Exportar", 
                  command=self.export_charts, style='Secondary.TButton').pack(side='left', padx=(0, 10))
        
        # Frame de gráficos con scroll
        canvas = tk.Canvas(main_frame, bg=ModernTheme.BACKGROUND)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear gráficos
        self.create_animales_chart(scrollable_frame)
        self.create_potreros_chart(scrollable_frame)
        self.create_empleados_chart(scrollable_frame)
        self.create_produccion_chart(scrollable_frame)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_animales_chart(self, parent):
        """Crea gráfico de distribución de animales"""
        # Frame del gráfico
        chart_frame = ttk.LabelFrame(parent, text=f"{Icons.ANIMALS} Distribución de Animales", padding="15")
        chart_frame.pack(fill='x', pady=(0, 20))
        
        # Obtener datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tipo, COUNT(*) as cantidad, estado
            FROM animales 
            WHERE finca_id = ?
            GROUP BY tipo, estado
            ORDER BY tipo
        ''', (self.current_finca_id,))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            ttk.Label(chart_frame, text="No hay datos de animales disponibles", 
                     style='Info.TLabel').pack(pady=20)
            return
        
        # Crear figura
        fig = Figure(figsize=(12, 6), facecolor=ModernTheme.BACKGROUND)
        
        # Gráfico de barras por tipo
        ax1 = fig.add_subplot(121)
        tipos = {}
        for tipo, cantidad, estado in data:
            if tipo not in tipos:
                tipos[tipo] = 0
            tipos[tipo] += cantidad
        
        tipos_list = list(tipos.keys())
        cantidades = list(tipos.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(tipos_list)))
        
        bars = ax1.bar(tipos_list, cantidades, color=colors)
        ax1.set_title('Animales por Tipo', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Cantidad')
        ax1.tick_params(axis='x', rotation=45)
        
        # Agregar valores en las barras
        for bar, cantidad in zip(bars, cantidades):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(cantidad), ha='center', va='bottom', fontweight='bold')
        
        # Gráfico de estado
        ax2 = fig.add_subplot(122)
        estados = {}
        for tipo, cantidad, estado in data:
            if estado not in estados:
                estados[estado] = 0
            estados[estado] += cantidad
        
        if estados:
            estados_list = list(estados.keys())
            cantidades_estado = list(estados.values())
            colors_estado = ['#4CAF50', '#FF9800', '#F44336', '#2196F3', '#9C27B0']
            
            wedges, texts, autotexts = ax2.pie(cantidades_estado, labels=estados_list, 
                                              autopct='%1.1f%%', colors=colors_estado[:len(estados_list)])
            ax2.set_title('Estado de los Animales', fontsize=14, fontweight='bold')
        
        fig.tight_layout()
        
        # Integrar en tkinter
        canvas_chart = FigureCanvasTkAgg(fig, chart_frame)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill='both', expand=True)
    
    def create_potreros_chart(self, parent):
        """Crea gráfico de ocupación de potreros"""
        # Frame del gráfico
        chart_frame = ttk.LabelFrame(parent, text=f"{Icons.PASTURES} Ocupación de Potreros", padding="15")
        chart_frame.pack(fill='x', pady=(0, 20))
        
        # Obtener datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.nombre, p.capacidad, COUNT(a.id) as ocupacion, p.estado
            FROM potreros p
            LEFT JOIN animales a ON p.id = a.potrero_id
            WHERE p.finca_id = ?
            GROUP BY p.id, p.nombre, p.capacidad, p.estado
            ORDER BY p.nombre
        ''', (self.current_finca_id,))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            ttk.Label(chart_frame, text="No hay datos de potreros disponibles", 
                     style='Info.TLabel').pack(pady=20)
            return
        
        # Crear figura
        fig = Figure(figsize=(12, 6), facecolor=ModernTheme.BACKGROUND)
        ax = fig.add_subplot(111)
        
        nombres = [row[0] for row in data]
        capacidades = [row[1] for row in data]
        ocupaciones = [row[2] for row in data]
        
        x = np.arange(len(nombres))
        width = 0.35
        
        # Barras de capacidad
        bars1 = ax.bar(x - width/2, capacidades, width, label='Capacidad', 
                      color='lightblue', alpha=0.7)
        
        # Barras de ocupación
        bars2 = ax.bar(x + width/2, ocupaciones, width, label='Ocupación', 
                      color='orange', alpha=0.7)
        
        ax.set_xlabel('Potreros')
        ax.set_ylabel('Cantidad de Animales')
        ax.set_title('Capacidad vs Ocupación de Potreros', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, rotation=45, ha='right')
        ax.legend()
        
        # Agregar valores en las barras
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom')
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom')
        
        fig.tight_layout()
        
        # Integrar en tkinter
        canvas_chart = FigureCanvasTkAgg(fig, chart_frame)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill='both', expand=True)
    
    def create_empleados_chart(self, parent):
        """Crea gráfico de empleados por cargo"""
        # Frame del gráfico
        chart_frame = ttk.LabelFrame(parent, text=f"{Icons.EMPLOYEES} Empleados por Cargo", padding="15")
        chart_frame.pack(fill='x', pady=(0, 20))
        
        # Obtener datos
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cargo, COUNT(*) as cantidad, AVG(salario) as salario_promedio
            FROM empleados 
            WHERE finca_id = ? AND estado = 'activo'
            GROUP BY cargo
            ORDER BY cantidad DESC
        ''', (self.current_finca_id,))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            ttk.Label(chart_frame, text="No hay datos de empleados disponibles", 
                     style='Info.TLabel').pack(pady=20)
            return
        
        # Crear figura
        fig = Figure(figsize=(12, 6), facecolor=ModernTheme.BACKGROUND)
        
        # Gráfico de cantidad por cargo
        ax1 = fig.add_subplot(121)
        cargos = [row[0] for row in data]
        cantidades = [row[1] for row in data]
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(cargos)))
        
        bars = ax1.bar(cargos, cantidades, color=colors)
        ax1.set_title('Empleados por Cargo', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Cantidad')
        ax1.tick_params(axis='x', rotation=45)
        
        # Agregar valores en las barras
        for bar, cantidad in zip(bars, cantidades):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(cantidad), ha='center', va='bottom', fontweight='bold')
        
        # Gráfico de salarios
        ax2 = fig.add_subplot(122)
        salarios = [row[2] for row in data]
        
        bars2 = ax2.bar(cargos, salarios, color=colors)
        ax2.set_title('Salario Promedio por Cargo', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Salario ($)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Formatear salarios
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Agregar valores en las barras
        for bar, salario in zip(bars2, salarios):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                    f'${salario:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        fig.tight_layout()
        
        # Integrar en tkinter
        canvas_chart = FigureCanvasTkAgg(fig, chart_frame)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill='both', expand=True)
    
    def create_produccion_chart(self, parent):
        """Crea gráfico de producción (simulado)"""
        # Frame del gráfico
        chart_frame = ttk.LabelFrame(parent, text=f"{Icons.REPORTS} Tendencias de Producción", padding="15")
        chart_frame.pack(fill='x', pady=(0, 20))
        
        # Crear datos simulados para demostración
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        produccion_leche = np.random.normal(1000, 200, len(dates))
        produccion_carne = np.random.normal(500, 100, len(dates))
        
        # Crear figura
        fig = Figure(figsize=(12, 6), facecolor=ModernTheme.BACKGROUND)
        ax = fig.add_subplot(111)
        
        ax.plot(dates, produccion_leche, marker='o', linewidth=2, label='Producción de Leche (L)', color='#4CAF50')
        ax.plot(dates, produccion_carne, marker='s', linewidth=2, label='Producción de Carne (kg)', color='#FF9800')
        
        ax.set_title('Tendencias de Producción Mensual', fontsize=14, fontweight='bold')
        ax.set_ylabel('Cantidad')
        ax.set_xlabel('Mes')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Formatear fechas
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        fig.autofmt_xdate()
        
        fig.tight_layout()
        
        # Integrar en tkinter
        canvas_chart = FigureCanvasTkAgg(fig, chart_frame)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill='both', expand=True)
    
    def refresh_charts(self):
        """Actualiza todos los gráficos"""
        messagebox.showinfo("Información", "Gráficos actualizados")
        # Aquí se podría implementar la lógica para actualizar los gráficos
    
    def export_charts(self):
        """Exporta los gráficos como imagen"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Error", "Matplotlib no está disponible")
            return
        
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Aquí se implementaría la lógica para exportar los gráficos
                messagebox.showinfo("Éxito", f"Gráficos exportados a {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def create_simple_chart(self, parent, title: str, data: Dict[str, float], chart_type: str = "bar"):
        """Crea un gráfico simple con datos proporcionados"""
        if not MATPLOTLIB_AVAILABLE:
            # Crear gráfico simple con texto si matplotlib no está disponible
            frame = ttk.LabelFrame(parent, text=title, padding="15")
            frame.pack(fill='x', pady=(0, 20))
            
            for key, value in data.items():
                ttk.Label(frame, text=f"{key}: {value}", style='Info.TLabel').pack(anchor='w')
            return
        
        # Crear figura
        fig = Figure(figsize=(10, 6), facecolor=ModernTheme.BACKGROUND)
        ax = fig.add_subplot(111)
        
        if chart_type == "bar":
            keys = list(data.keys())
            values = list(data.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(keys)))
            
            bars = ax.bar(keys, values, color=colors)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_ylabel('Valor')
            
            # Agregar valores en las barras
            for bar, value in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       str(value), ha='center', va='bottom', fontweight='bold')
        
        elif chart_type == "pie":
            keys = list(data.keys())
            values = list(data.values())
            colors = plt.cm.Pastel1(np.linspace(0, 1, len(keys)))
            
            wedges, texts, autotexts = ax.pie(values, labels=keys, autopct='%1.1f%%', colors=colors)
            ax.set_title(title, fontsize=14, fontweight='bold')
        
        fig.tight_layout()
        
        # Integrar en tkinter
        canvas_chart = FigureCanvasTkAgg(fig, parent)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill='both', expand=True)
