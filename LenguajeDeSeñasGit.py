import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import math

# ----------------------------
# CONFIGURACIÓN DE MEDIAPIPE
# ----------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# ----------------------------
# MENSAJES DE LAS LETRAS
# ----------------------------
MENSAJES = {
    "A": "Puño cerrado con el pulgar al costado",
    "B": "Mano abierta con dedos juntos",
    "C": "Forma de la letra C con la mano",
    "D": "Índice levantado",
    "E": "Dedos doblados",
    "F": "Pulgar e índice formando círculo",
    "G": "Mano horizontal",
    "H": "Dos dedos horizontales",
    "I": "Meñique levantado",
    "J": "Movimiento en forma de J",
    "K": "Forma de V con los dedos",
    "L": "Forma de la letra L",
    "M": "Tres dedos sobre el pulgar",
    "N": "Dos dedos sobre el pulgar",
    "Ñ": "Movimiento de Ñ",
    "O": "Forma de círculo",
    "P": "Como K hacia abajo",
    "Q": "Como G hacia abajo",
    "R": "Dedos cruzados",
    "S": "Puño cerrado",
    "T": "Pulgar entre dedos",
    "U": "Dos dedos juntos",
    "V": "Símbolo de paz",
    "W": "Tres dedos arriba",
    "X": "Gancho con índice",
    "Y": "Pulgar y meñique arriba",
    "Z": "Movimiento en forma de Z"
}

# ----------------------------
# FUNCIONES MATEMÁTICAS Y DE DETECCIÓN
# ----------------------------

def calcular_distancia(p1, p2):
    """Calcula la distancia entre dos puntos (landmarks)"""
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def predecir_letra(hand_landmarks):
    """
    Motor lógico que evalúa el estado de los 5 dedos (0 = Doblado, 1 = Estirado)
    y calcula distancias para adivinar la letra estática.
    """
    dedos_estado = []
    
    # 1. Evaluar el Pulgar (es diferente a los demás dedos, evaluamos en el eje X)
    # Comparamos la punta (4) con la articulación base (2)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[2].x:
        dedos_estado.append(1) # Pulgar extendido (asumiendo mano derecha)
    else:
        dedos_estado.append(0) # Pulgar cerrado

    # 2. Evaluar Índice, Medio, Anular y Meñique (evaluamos en el eje Y)
    puntas = [8, 12, 16, 20]
    articulaciones = [6, 10, 14, 18]

    for punta, art in zip(puntas, articulaciones):
        # Si la punta está más arriba (menor valor en Y) que la articulación
        if hand_landmarks.landmark[punta].y < hand_landmarks.landmark[art].y:
            dedos_estado.append(1) # Dedo estirado
        else:
            dedos_estado.append(0) # Dedo doblado

    # 3. Lógica de Diccionario según los dedos estirados [Pulgar, Índice, Medio, Anular, Meñique]
    if dedos_estado == [0, 1, 0, 0, 0]:
        return "D"
    elif dedos_estado == [0, 0, 0, 0, 1]:
        return "I"
    elif dedos_estado == [1, 1, 0, 0, 0]:
        return "L"
    elif dedos_estado == [1, 0, 0, 0, 1]:
        return "Y"
    elif dedos_estado == [0, 1, 1, 1, 0]:
        return "W"
    elif dedos_estado == [1, 1, 1, 1, 1] or dedos_estado == [0, 1, 1, 1, 1]:
        return "B" # Mano completamente abierta
    elif dedos_estado == [0, 0, 0, 0, 0] or dedos_estado == [1, 0, 0, 0, 0]:
        return "A / E / S" # Muy similares solo con coordenadas Y
    
    # 4. Diferenciar entre U y V (ambas tienen Índice y Medio levantados)
    elif dedos_estado == [0, 1, 1, 0, 0] or dedos_estado == [1, 1, 1, 0, 0]:
        distancia_indice_medio = calcular_distancia(
            hand_landmarks.landmark[8], 
            hand_landmarks.landmark[12]
        )
        if distancia_indice_medio > 0.05: # Si hay separación entre las puntas
            return "V"
        else:
            return "U"
            
    # Para letras más complejas como la C o la O que forman curvas
    distancia_pulgar_indice = calcular_distancia(
        hand_landmarks.landmark[4], 
        hand_landmarks.landmark[8]
    )
    if dedos_estado == [0, 0, 0, 0, 0] and distancia_pulgar_indice < 0.05:
        return "O" # Si están formando un círculo cerrado

    return "Buscando..."

# ----------------------------
# VENTANA
# ----------------------------
ventana = tk.Tk()
ventana.title("Lenguaje de Señas")
ventana.geometry("700x700")
ventana.config(bg="white")

# ----------------------------
# TITULO
# ----------------------------
titulo = tk.Label(
    ventana,
    text="Sistema de Lenguaje de Señas",
    font=("Arial", 22, "bold"),
    bg="white"
)
titulo.pack(pady=20)

# ----------------------------
# CAMARA
# ----------------------------
lbl_camara = tk.Label(ventana)
lbl_camara.pack()

# abrir cámara
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# ----------------------------
# FUNCION CAMARA MODIFICADA
# ----------------------------
def actualizar_camara():
    ret, frame = cap.read()

    if ret:
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar con MediaPipe
        resultados = hands.process(frame_rgb)
        letra_detectada = "Buscando..."

        if resultados.multi_hand_landmarks:
            for hand_landmarks in resultados.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                letra_detectada = predecir_letra(hand_landmarks)

        # Volver a RGB para Tkinter
        frame_procesado = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Dibujar la letra detectada en el recuadro del video
        cv2.putText(frame_procesado, f"Detectando: {letra_detectada}", (10, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        img = Image.fromarray(frame_procesado)
        img = img.resize((500, 350))
        imgtk = ImageTk.PhotoImage(image=img)

        lbl_camara.imgtk = imgtk
        lbl_camara.configure(image=imgtk)

    lbl_camara.after(10, actualizar_camara)

# ----------------------------
# MOSTRAR MENSAJE
# ----------------------------
def mostrar_letra(letra):
    mensaje = MENSAJES.get(
        letra,
        "No disponible"
    )
    messagebox.showinfo(
        f"Letra {letra}",
        mensaje
    )

# ----------------------------
# BOTONES
# ----------------------------
frame_botones = tk.Frame(
    ventana,
    bg="white"
)
frame_botones.pack(pady=20)

letras = [
    "A","B","C","D","E","F",
    "G","H","I","J","K","L",
    "M","N","Ñ","O","P","Q",
    "R","S","T","U","V","W",
    "X","Y","Z"
]

fila = 0
columna = 0

for letra in letras:
    btn = tk.Button(
        frame_botones,
        text=letra,
        width=5,
        height=2,
        font=("Arial", 12, "bold"),
        command=lambda l=letra: mostrar_letra(l)
    )
    btn.grid(
        row=fila,
        column=columna,
        padx=5,
        pady=5
    )
    
    columna += 1
    if columna == 6:
        columna = 0
        fila += 1

# ----------------------------
# CERRAR
# ----------------------------
def cerrar():
    cap.release()
    ventana.destroy()

ventana.protocol(
    "WM_DELETE_WINDOW",
    cerrar
)

# iniciar cámara
actualizar_camara()

# ejecutar
ventana.mainloop()