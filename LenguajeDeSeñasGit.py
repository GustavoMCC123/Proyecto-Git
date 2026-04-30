# recordar subir sus cambios al repositorio de git
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # 🔥 NUEVO Agregar imagenes

# ==============================
# DICCIONARIO DE SEÑAS (A - Z)
# ==============================
MENSAJES = {
    "A": "Puño cerrado con el pulgar al costado",
    "B": "Mano abierta con dedos juntos",
    "C": "Forma de la letra C con la mano",
    "D": "Índice levantado, demás dedos juntos",
    "E": "Dedos doblados hacia la palma",
    "F": "Pulgar e índice formando un círculo",
    "G": "Mano horizontal con índice apuntando",
    "H": "Índice y medio extendidos horizontalmente",
    "I": "Meñique levantado",
    "J": "Movimiento en forma de J con el meñique",
    "K": "Índice y medio en forma de V con pulgar",
    "L": "Pulgar e índice formando una L",
    "M": "Tres dedos sobre el pulgar",
    "N": "Dos dedos sobre el pulgar",
    "O": "Forma de círculo con los dedos",
    "P": "Como K pero hacia abajo",
    "Q": "Como G pero hacia abajo",
    "R": "Índice y medio cruzados",
    "S": "Puño cerrado",
    "T": "Pulgar entre índice y medio",
    "U": "Índice y medio juntos hacia arriba",
    "V": "Índice y medio separados (paz)",
    "W": "Tres dedos extendidos",
    "X": "Índice doblado en forma de gancho",
    "Y": "Pulgar y meñique extendidos",
    "Z": "Movimiento en forma de Z con el dedo",
    "CH": "Mano en forma de C con los dedos juntos",
    "Ñ": "Mano en forma de Ñ con los dedos juntos",
}


# ==============================
# RUTA DE IMÁGENES   imagenes
# ==============================
IMAGENES = {
    "A": "imagenes/A.png",
    "B": "imagenes/B.png",
    "C": "imagenes/C.png",
    "CH": "imagenes/CH.png",
    "D": "imagenes/D.png",
    "E": "imagenes/E.png",
    "F": "imagenes/F.png",
    "G": "imagenes/G.png",
    "H": "imagenes/H.png",
    "I": "imagenes/I.png",
    "J": "imagenes/J.png",
    "K": "imagenes/K.png",
    "L": "imagenes/L.png",
    "M": "imagenes/M.png",
    "N": "imagenes/N.png",
    "Ñ": "imagenes/Ñ.png",
    "O": "imagenes/O.png",
    "P": "imagenes/P.png",
    "Q": "imagenes/Q.png",
    "R": "imagenes/R.png",
    "S": "imagenes/S.png",
    "T": "imagenes/T.png",
    "U": "imagenes/U.png",
    "V": "imagenes/V.png",
    "W": "imagenes/W.png",
    "X": "imagenes/X.png",
    "Y": "imagenes/Y.png",
    "Z": "imagenes/Z.png"
}


# ==============================
# FUNCIONES
# ==============================

def mostrar_sena(letra):
    mensaje = MENSAJES.get(letra, "Seña no disponible")


    #  Nueva ventana
    ventana_img = tk.Toplevel()
    ventana_img.title(f"Seña {letra}")
    ventana_img.geometry("300x300")

    label = tk.Label(ventana_img, text=mensaje, font=("Arial", 10))
    label.pack(pady=10)

    #  Mostrar imagen si existe
    if letra in IMAGENES:
        try:
            img = Image.open(IMAGENES[letra])
            img = img.resize((200, 200))
            foto = ImageTk.PhotoImage(img)

            panel = tk.Label(ventana_img, image=foto)
            panel.image = foto          # importante para que no se borre
            panel.pack()
        except:
            tk.Label(ventana_img, text="No se pudo cargar la imagen").pack()
    else:
        tk.Label(ventana_img, text="Imagen no disponible").pack()




def buscar_sena():
    letra = entrada.get().upper()
    if letra in MENSAJES:
        mostrar_sena(letra)
    else:
        messagebox.showerror("Error", "Letra no válida")


def on_enter(e):
    e.widget.config(bg="#a6d4ff")

def on_leave(e):
    e.widget.config(bg="#e0e0e0")



# ==============================
# INTERFAZ
# ==============================

ventana = tk.Tk()
ventana.title("Lenguaje de Señas - A-Z")
ventana.geometry("500x500")
ventana.config(bg="#f5f7fa")

# Título
titulo = tk.Label(
    ventana,
    text="Aprende el Abecedario en Señas",
    font=("Arial", 16, "bold"),
    bg="#f5f7fa",
    fg="#333"
)
titulo.pack(pady=10)

# Buscador
frame_busqueda = tk.Frame(ventana, bg="#f5f7fa")
frame_busqueda.pack(pady=10)

entrada = tk.Entry(frame_busqueda, width=5, font=("Arial", 14))
entrada.pack(side="left", padx=5)

btn_buscar = tk.Button(
    frame_busqueda,
    text="Buscar",
    command=buscar_sena,
    bg="#4CAF50",
    fg="white"
)
btn_buscar.pack(side="left")

# Frame de botones
frame_botones = tk.Frame(ventana, bg="#f5f7fa")
frame_botones.pack()

# Crear botones en grid (mejor presentación)
fila = 0
columna = 0

for letra in MENSAJES.keys():
    btn = tk.Button(
        frame_botones,
        text=letra,
        width=5,
        height=2,
        font=("Arial", 12, "bold"),
        bg="#e0e0e0",
        command=lambda l=letra: mostrar_sena(l)
    )
    btn.grid(row=fila, column=columna, padx=5, pady=5)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    columna += 1
    if columna == 6:
        columna = 0
        fila += 1

# Footer
footer = tk.Label(
    ventana,
    text="Proyecto de Lenguaje de Señas - Python Tkinter",
    font=("Arial", 9),
    bg="#f5f7fa",
    fg="#777"
)
footer.pack(pady=10)

ventana.mainloop()