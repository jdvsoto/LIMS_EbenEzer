import tkinter as tk
from tkinter import ttk, messagebox
from fpdf import FPDF
import sqlite3
import datetime
import os
from tkinter import Frame

# — Conexión SQLite —
conn = sqlite3.connect('laboratorio.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS resultados_heces (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    fecha TEXT,
    tipo TEXT,
    color TEXT,
    aspecto TEXT,
    ph TEXT,
    restos_alimenticios TEXT,
    moco TEXT,
    sangre TEXT,
    celulas_vegetales TEXT,
    jabones TEXT,
    almidones TEXT,
    grasas TEXT,
    levaduras TEXT,
    leucocitos TEXT,
    bacterias TEXT,
    eritrocitos TEXT,
    parasitos TEXT
)
''')
conn.commit()

class ExamenHecesFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.campos_macro = {}
        self.campos_micro = {}
        
        # Valores comunes para dropdowns
        self.valores_comunes = ['--------', 'Escaso', 'Regular', 'Abundante', 'Muy Abundante']
        
        # Configuración de secciones
        self.setup_macroscopico()
        self.setup_microscopico()
        
    def setup_macroscopico(self):
        frame_macro = ttk.LabelFrame(self, text="Examen Macroscópico")
        frame_macro.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
        
        # Color
        ttk.Label(frame_macro, text="Color:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.campos_macro['color'] = ttk.Combobox(frame_macro, values=['Café', 'Verde', 'Rojo', 'Amarillo'])
        self.campos_macro['color'].grid(row=0, column=1, padx=5, pady=2)
        
        # Aspecto
        ttk.Label(frame_macro, text="Aspecto:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.campos_macro['aspecto'] = ttk.Combobox(frame_macro, values=['Pastoso', 'Formado', 'Semi-Diarreico', 'Diarreico'])
        self.campos_macro['aspecto'].grid(row=1, column=1, padx=5, pady=2)
        
        # PH
        ttk.Label(frame_macro, text="PH:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.campos_macro['ph'] = ttk.Entry(frame_macro)
        self.campos_macro['ph'].grid(row=2, column=1, padx=5, pady=2)
        
        # Restos Alimenticios
        ttk.Label(frame_macro, text="Restos Alimenticios:").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.campos_macro['restos_alimenticios'] = ttk.Combobox(frame_macro, values=self.valores_comunes)
        self.campos_macro['restos_alimenticios'].grid(row=3, column=1, padx=5, pady=2)
        
        # Moco
        ttk.Label(frame_macro, text="Moco:").grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.campos_macro['moco'] = ttk.Combobox(frame_macro, values=self.valores_comunes)
        self.campos_macro['moco'].grid(row=4, column=1, padx=5, pady=2)
        
        # Sangre
        ttk.Label(frame_macro, text="Sangre:").grid(row=5, column=0, sticky='e', padx=5, pady=2)
        self.campos_macro['sangre'] = ttk.Combobox(frame_macro, values=self.valores_comunes)
        self.campos_macro['sangre'].grid(row=5, column=1, padx=5, pady=2)

    def setup_microscopico(self):
        frame_micro = ttk.LabelFrame(self, text="Examen Microscópico")
        frame_micro.grid(row=0, column=1, padx=10, pady=5, sticky='nsew')
        
        campos = [
            'Células Vegetales', 'Jabones', 'Almidones', 'Grasas', 
            'Levaduras', 'Leucocitos', 'Bacterias', 'Eritrocitos'
        ]
        
        for i, campo in enumerate(campos):
            ttk.Label(frame_micro, text=f"{campo}:").grid(row=i, column=0, sticky='e', padx=5, pady=2)
            campo_key = campo.lower().replace(' ', '_').replace('é', 'e')
            self.campos_micro[campo_key] = ttk.Combobox(frame_micro, values=self.valores_comunes)
            self.campos_micro[campo_key].grid(row=i, column=1, padx=5, pady=2)
        
        # Parásitos (con valores especiales)
        ttk.Label(frame_micro, text="Parásitos:").grid(row=len(campos), column=0, sticky='e', padx=5, pady=2)
        valores_parasitos = [
            'No se Observaron',
            'Entamoeba hitolytica ESCASO',
            'Entamoeba coli REGULAR',
            'TROFOZOITOS Trichomonas hominis ABUNDANTES',
            'Entamoeba coli ESCASO',
            'Entamoeba hitolytica ABUNDANTE',
            'Trichomonas hominis REGULAR',
            'Endolimax nana REGULAR',
            'Giardia lamblia REGULAR',
            'Entamoeba hitolytica REGULAR'
        ]
        self.campos_micro['parasitos'] = ttk.Combobox(frame_micro, values=valores_parasitos)
        self.campos_micro['parasitos'].grid(row=len(campos), column=1, padx=5, pady=2)

    def get_valores(self):
        valores = {}
        valores.update({k: v.get() for k, v in self.campos_macro.items()})
        valores.update({k: v.get() for k, v in self.campos_micro.items()})
        return valores

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Laboratorio Clínico "EBEN EZER"')
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Datos del paciente
        self.setup_datos_paciente(main_frame)
        
        # Frame para examen de heces (inicialmente oculto)
        self.frame_heces = ExamenHecesFrame(main_frame)
        
        # Botones
        self.setup_botones(main_frame)
        
        # Bind para cambios en tipo de prueba
        self.combo_tipo.bind('<<ComboboxSelected>>', self.on_tipo_changed)

    def setup_datos_paciente(self, parent):
        # Nombre
        ttk.Label(parent, text='Nombre:').grid(row=0, column=0, pady=2, sticky='e')
        self.entry_nombre = ttk.Entry(parent, width=40)
        self.entry_nombre.grid(row=0, column=1, columnspan=2, pady=2, sticky='w')

        # Fecha
        ttk.Label(parent, text='Fecha:').grid(row=1, column=0, pady=2, sticky='e')
        self.entry_fecha = ttk.Entry(parent)
        self.entry_fecha.grid(row=1, column=1, pady=2, sticky='w')
        self.entry_fecha.insert(0, datetime.date.today().strftime('%d/%m/%Y'))

        # Tipo de prueba
        ttk.Label(parent, text='Tipo de prueba:').grid(row=2, column=0, pady=2, sticky='e')
        self.combo_tipo = ttk.Combobox(parent, values=['HECES COMPLETA', 'VDRL', 'GLUC', 'EMB'])
        self.combo_tipo.grid(row=2, column=1, pady=2, sticky='w')
        self.combo_tipo.current(0)

    def setup_botones(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=10, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text='Guardar', command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Generar PDF', command=self.generar_pdf).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Imprimir', command=self.imprimir).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Salir', command=self.root.destroy).pack(side='left', padx=5)

    def on_tipo_changed(self, event=None):
        if self.combo_tipo.get() == 'HECES COMPLETA':
            self.frame_heces.grid(row=3, column=0, columnspan=3, pady=10)
        else:
            self.frame_heces.grid_remove()

    def guardar(self):
        if self.combo_tipo.get() == 'HECES COMPLETA':
            valores = self.frame_heces.get_valores()
            c.execute('''
                INSERT INTO resultados_heces (
                    nombre, fecha, tipo, color, aspecto, ph, restos_alimenticios,
                    moco, sangre, celulas_vegetales, jabones, almidones, grasas,
                    levaduras, leucocitos, bacterias, eritrocitos, parasitos
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.entry_nombre.get(),
                self.entry_fecha.get(),
                self.combo_tipo.get(),
                valores['color'],
                valores['aspecto'],
                valores['ph'],
                valores['restos_alimenticios'],
                valores['moco'],
                valores['sangre'],
                valores['celulas_vegetales'],
                valores['jabones'],
                valores['almidones'],
                valores.get('grasas', '--------'),
                valores['levaduras'],
                valores['leucocitos'],
                valores['bacterias'],
                valores['eritrocitos'],
                valores['parasitos']
            ))
            conn.commit()
            messagebox.showinfo('Éxito', 'Resultados guardados correctamente')

    def generar_pdf(self):
        if self.combo_tipo.get() == 'HECES COMPLETA':
            valores = self.frame_heces.get_valores()
            
            pdf = FPDF(format='A5')
            pdf.add_page()
            
            # Espacio para el encabezado
            pdf.ln(25)
            
            # Función helper para crear líneas con puntos
            def create_dotted_line(label, value):
                pdf.cell(20, 6, '', ln=0)  # Indentación reducida de 40 a 20
                label_width = pdf.get_string_width(label)
                dots_width = 60 - label_width  # Ancho total deseado menos el ancho del label
                num_dots = int(dots_width / pdf.get_string_width('.'))
                dots = '.' * num_dots
                pdf.cell(60, 6, f"{label}{dots}", ln=0)
                # Convertir el valor a mayúsculas
                value_str = str(value).upper() if value else '--------'
                pdf.cell(0, 6, value_str, ln=1)
            
            # Datos del paciente
            pdf.set_font('Times', 'B', 10.5)
            pdf.cell(25, 6, 'PACIENTE:', align='L')
            pdf.cell(3, 6, '', ln=0)  # Pequeño espacio
            pdf.cell(0, 6, self.entry_nombre.get().upper(), ln=1)
            
            pdf.cell(25, 6, 'FECHA:', align='L')
            pdf.cell(3, 6, '', ln=0)  # Pequeño espacio
            pdf.cell(40, 6, self.entry_fecha.get(), ln=0)
            pdf.cell(25, 6, 'EDAD:', align='L')
            pdf.cell(0, 6, '---- AÑOS', ln=1)
            
            pdf.ln(4)
            pdf.cell(0, 6, 'EXAMEN SOLICITADO: HECES COMPLETA', ln=1)
            
            pdf.ln(4)
            # Examen Macroscópico
            pdf.cell(0, 6, 'EXAMEN MACROSCOPICO:', ln=1)
            
            # Campos del examen macroscópico
            create_dotted_line('COLOR', valores['color'])
            create_dotted_line('ASPECTO', valores['aspecto'])
            create_dotted_line('PH', valores['ph'])
            create_dotted_line('RESTOS ALIMENTICIOS', valores['restos_alimenticios'])
            create_dotted_line('MOCO', valores['moco'])
            create_dotted_line('SANGRE', valores['sangre'])
            
            pdf.ln(4)
            # Examen Microscópico
            pdf.cell(0, 6, 'EXAMEN MICROSCOPICO:', ln=1)
            
            # Campos del examen microscópico
            create_dotted_line('CELULAS VEGETALES', valores['celulas_vegetales'])
            create_dotted_line('JABONES', valores['jabones'])
            create_dotted_line('ALMIDONES', valores['almidones'])
            create_dotted_line('GRASAS', valores.get('grasas', '--------'))
            create_dotted_line('LEVADURAS', valores['levaduras'])
            create_dotted_line('LEUCOCITOS', valores['leucocitos'])
            create_dotted_line('BACTERIAS', valores['bacterias'])
            create_dotted_line('ERITROCITOS', valores['eritrocitos'])
            create_dotted_line('PARASITOS', valores['parasitos'])
            
            # Espacio para firma
            pdf.ln(25)
            
            # Guardar PDF
            fname = f"reporte_{self.entry_nombre.get()}_HECES COMPLETA.pdf"
            pdf.output(fname)
            messagebox.showinfo('Éxito', f'PDF generado: {fname}')

    def imprimir(self):
        if self.combo_tipo.get() == 'HECES COMPLETA':
            self.generar_pdf()
            fname = f"reporte_{self.entry_nombre.get()}_HECES COMPLETA.pdf"
            if os.name == 'nt':  # Windows
                os.startfile(fname, "print")
            else:  # Linux/Mac
                os.system(f'lpr {fname}')

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    conn.close()

if __name__ == '__main__':
    main()
