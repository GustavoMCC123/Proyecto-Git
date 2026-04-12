# recordar subir sus cambios al repositorio de git
import tkinter as tk
from tkinter import messagebox

# Diccionario global de señas
MENSAJES = {
    "A": "Puño cerrado con el pulgar al costado",
    "B": "Mano abierta con dedos juntos",
    "C": "Forma de la letra C con la mano"
}

# Función que simula mostrar la seña
def mostrar_sena(letra):
    mensaje = MENSAJES.get(letra, "Seña no disponible")
    messagebox.showinfo(f"Seña {letra}", mensaje)

# Efecto hover en botones
def on_enter(e):
    e.widget.config(bg="#d1e7ff")

def on_leave(e):
    e.widget.config(bg="SystemButtonFace")

# Crear ventana
ventana = tk.Tk()
ventana.title("Lenguaje de Señas - Demo")
ventana.geometry("320x240")
ventana.config(bg="#f0f0f0")

# Frame contenedor
frame = tk.Frame(ventana, bg="#f0f0f0")
frame.pack(expand=True)

# Título
titulo = tk.Label(
    frame,
    text="Aprende Señas Básicas",
    font=("Arial", 14, "bold"),
    bg="#f0f0f0"
)
titulo.pack(pady=10)

# Crear botones dinámicamente
for letra in MENSAJES.keys():
    btn = tk.Button(
        frame,
        text=letra,
        width=12,
        font=("Arial", 11),
        command=lambda l=letra: mostrar_sena(l)
    )
    btn.pack(pady=5)

    # Eventos hover
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# Ejecutar aplicación
ventana.mainloop()