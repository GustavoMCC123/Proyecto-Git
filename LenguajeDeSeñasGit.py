#recordar subir sus cambios al repositorio de git
import tkinter as tk
from tkinter import messagebox

# Función que simula mostrar la seña
def mostrar_sena(letra):
    mensajes = {
        "A": "Seña A: Puño cerrado con el pulgar al costado",
        "B": "Seña B: Mano abierta con dedos juntos",
        "C": "Seña C: Forma de la letra C con la mano"
    }
    messagebox.showinfo("Lenguaje de Señas", mensajes[letra])

# Crear ventana
ventana = tk.Tk()
ventana.title("Lenguaje de Señas - Demo")
ventana.geometry("300x200")

# Título
titulo = tk.Label(ventana, text="Aprende Señas Básicas", font=("Arial", 14))
titulo.pack(pady=10)

# Botones
btn_a = tk.Button(ventana, text="A", width=10, command=lambda: mostrar_sena("A"))
btn_a.pack(pady=5)

btn_b = tk.Button(ventana, text="B", width=10, command=lambda: mostrar_sena("B"))
btn_b.pack(pady=5)

btn_c = tk.Button(ventana, text="C", width=10, command=lambda: mostrar_sena("C"))
btn_c.pack(pady=5)

# Ejecutar
ventana.mainloop()