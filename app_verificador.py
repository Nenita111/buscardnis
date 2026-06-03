
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from docx import Document
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class AppVerificadorDNI:
    def __init__(self, root):
        self.root = root
        self.root.title("Verificador Local de DNIs")
        self.root.geometry("700x550")
        self.bd_dict = {}
        self.empresa_set = set()
        self.crear_interfaz()

    def configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

    def crear_interfaz(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_bd = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_bd, text=" BASE DE DATOS ")
        ttk.Button(self.tab_bd, text="📂 Cargar BD (Excel/PDF/Docx)", command=lambda: self.cargar_archivo('bd')).pack(pady=20)
        self.lbl_bd = ttk.Label(self.tab_bd, text="Registros: 0")
        self.lbl_bd.pack()

        self.tab_emp = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_emp, text=" DNIs EMPRESA ")
        ttk.Button(self.tab_emp, text="📂 Cargar Empresa", command=lambda: self.cargar_archivo('emp')).pack(pady=20)
        self.lbl_emp = ttk.Label(self.tab_emp, text="DNIs: 0")
        self.lbl_emp.pack()

        ttk.Button(self.root, text="🔍 BUSCAR COINCIDENCIAS", command=self.buscar).pack(pady=20)

    def normalizar_dni(self, texto):
        if not texto: return ""
        return re.sub(r'[^A-Z0-9]', '', str(texto).upper().strip())

    def extraer_dnis(self, texto):
        patron = r'\b[XYZxyz]?\d{7,8}[- ]?[A-Za-z]\b'
        return [self.normalizar_dni(d) for d in re.findall(patron, texto)]

    def cargar_archivo(self, destino):
        ruta = filedialog.askopenfilename()
        if not ruta: return
        try:
            ext = os.path.splitext(ruta)[1].lower()
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(ruta).fillna("")
                for val in df.iloc[:,0]:
                    dni = self.normalizar_dni(val)
                    if dni: self.bd_dict[dni] = {'dni': dni}
            elif ext == '.pdf':
                reader = PdfReader(ruta)
                for page in reader.pages:
                    for d in self.extraer_dnis(page.extract_text()):
                        if destino == 'bd': self.bd_dict[d] = {'dni': d}
                        else: self.empresa_set.add(d)
            
            self.lbl_bd.config(text=f"Registros: {len(self.bd_dict)}")
            self.lbl_emp.config(text=f"DNIs: {len(self.empresa_set)}")
            messagebox.showinfo("Éxito", "Archivo cargado")
        except Exception as e: messagebox.showerror("Error", str(e))

    def buscar(self):
        coincidencias = [self.bd_dict[d] for d in self.empresa_set if d in self.bd_dict]
        messagebox.showinfo("Resultado", f"Se encontraron {len(coincidencias)} coincidencias.")

if __name__ == '__main__':
    root = tk.Tk()
    app = AppVerificadorDNI(root)
    root.mainloop()
