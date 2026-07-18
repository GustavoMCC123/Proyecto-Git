import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
from PIL import Image
import os


from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime



# ---------- Configuración de SQLAlchemy ----------
Base = declarative_base()


class Mensaje(Base):
    __tablename__ = 'mensajes'  # <- Doble guion bajo
    id = Column(Integer, primary_key=True)
    texto = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Base de datos SQLite (local, en archivo)
engine = create_engine('sqlite:///mensajes.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Crear tabla si no existe
Base.metadata.create_all(engine)

# ===== CONFIGURACIÓN INICIAL =====
st.set_page_config(
    page_title="Comunicador de Señas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ESTILOS CSS =====
st.markdown("""
<style>
.sidebar .sidebar-content {
    background-color: #f0f2f6;
    padding: 1rem;
}
.img-container {
    border: 2px solid #4f8bf9;
    border-radius: 10px;
    padding: 10px;
    background: white;
    margin-bottom: 1rem;
}
.letter-badge {
    background: #4f8bf9;
    color: white;
    padding: 3px 10px;
    border-radius: 50px;
    font-size: 0.9rem;
    display: inline-block;
    margin: 3px;
}
.camera-frame {
    border: 3px solid #4f8bf9;
    border-radius: 10px;
    padding: 5px;
}
.message-box {
    background-color: #f0f8ff;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ===== INTERFAZ PRINCIPAL =====
st.title(" Comunicador de Lenguaje de Señas")
st.markdown("""
<div class="message-box">
    <b>Instrucciones:</b> Muestra tu mano frente a la cámara para formar letras en lenguaje de señas.
</div>
""", unsafe_allow_html=True)

# ===== BARRA LATERAL =====
with st.sidebar:
    st.header("Referencia de Señas", divider='blue')
    
    # Imagen del abecedario
    with st.container():
        st.markdown('<div class="img-container">', unsafe_allow_html=True)
        try:
            img = Image.open("imagenes/abecedario.png")
            st.image(img, use_container_width=True)
        except:
            st.warning("Coloca 'abecedario.png' en esta carpeta")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Guía de gestos
    with st.expander("Cómo hacer cada letra"):
        st.markdown("""
        <div style="column-count: 2;">
            <span class='letter-badge'>A</span> Mano cerrada<br>
            <span class='letter-badge'>B</span> Mano abierta<br>
            <span class='letter-badge'>C</span> Forma de C<br>
            <span class='letter-badge'>D</span> Índice arriba<br>
            <span class='letter-badge'>E</span> Mano cerrada con pulgar<br>
            <span class='letter-badge'>F</span> OK invertido<br>
            <span class='letter-badge'>G</span> Índice a un lado<br>
            <span class='letter-badge'>H</span> Índice+medio<br>
            <span class='letter-badge'>I</span> Meñique arriba<br>
            <span class='letter-badge'>J</span> Meñique con movimiento<br>
            <span class='letter-badge'>K</span> Índice+medio cruzados<br>
            <span class='letter-badge'>L</span> Índice+pulgar<br>
            <span class='letter-badge'>M</span> 3 dedos abajo<br>
            <span class='letter-badge'>N</span> 2 dedos cruzados<br>
            <span class='letter-badge'>O</span> Círculo con dedos<br>
            <span class='letter-badge'>P</span> Pinza<br>
            <span class='letter-badge'>Q</span> Índice abajo<br>
            <span class='letter-badge'>R</span> Medio arriba<br>
            <span class='letter-badge'>S</span> Puño cerrado<br>
            <span class='letter-badge'>T</span> Índice con pulgar<br>
            <span class='letter-badge'>U</span> Índice+medio juntos<br>
            <span class='letter-badge'>V</span> Índice+medio separados<br>
            <span class='letter-badge'>W</span> 3 dedos extendidos<br>
            <span class='letter-badge'>X</span> Índice curvado<br>
            <span class='letter-badge'>Y</span> Pulgar+meñique<br>
            <span class='letter-badge'>Z</span> Movimiento de Z<br>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("*Gestos Especiales*")
    st.markdown("- <span class='letter-badge'>✊</span> Puño cerrado:", unsafe_allow_html=True)
    st.markdown("- <span class='letter-badge'>🖐️</span> Mano abierta:", unsafe_allow_html=True)
    st.markdown("- <span class='letter-badge'>🤟</span> I love you:", unsafe_allow_html=True)

# ===== MODELO DE DETECCIÓN =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=1, min_detection_confidence=0.8, min_tracking_confidence=0.8, max_num_hands=1)

# ===== FUNCIONES AUXILIARES =====
def distancia(p1, p2): return np.linalg.norm(np.array(p1) - np.array(p2))
def dedo_extendido(px, id_dedo): return px(id_dedo)[1] < px(id_dedo-2)[1]
def pulgar_cruzado(px): return px(4)[0] < px(2)[0]

# ===== DETECCIÓN COMPLETA A-Z =====
def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def detectar_gesto(landmarks, width, height):
    def px(id): return (int(landmarks.landmark[id].x * width), int(landmarks.landmark[id].y * height))
    
    # Coordenadas clave
    index_tip, index_pip = px(8), px(6)
    middle_tip, middle_pip = px(12), px(10)
    ring_tip, ring_pip = px(16), px(14)
    pinky_tip, pinky_pip = px(20), px(18)
    thumb_tip, thumb_ip, thumb_mcp = px(4), px(3), px(2)
    palm_center = px(0)  # Landmark 0 = centro de la palma

    # ================== LETRA A ==================
    distancia_anulartip_cero = distancia(palm_center, ring_tip)
    if all(tip[1] > pip[1] for tip, pip in [  # "all" todos deben cumplir la condicion
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip)
    ]) and thumb_tip[1] < thumb_ip[1] and 30<distancia_anulartip_cero<60:
        #st.write("Distancia entre tip anular y cero:", distancia_anulartip_cero)
        return "A"

    # ================== LETRA B ==================
    distancia_horizontal = abs(index_tip[0] - thumb_tip[0])
    distancia_tipIndice_tipMenique = distancia(pinky_tip,index_tip)
    if all(tip[1] < pip[1] for tip, pip in [ 
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip)
    ]) and thumb_tip[1] < thumb_ip[1] and 10<distancia_horizontal<35 and 50< distancia_tipIndice_tipMenique < 100:
        #st.write("Distancia entre pulgar e índice:", distancia_tipIndice_tipMenique)
        return "B"

    # ================== LETRA C ==================
    dist_thumb_index = distancia(thumb_tip, index_tip)
    dist_middle_ring = distancia(middle_tip, ring_tip)
    dedos_curvados = sum(tip[1] > pip[1] for tip, pip in [ # "sum" cuenta 
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip),
        (thumb_tip, thumb_ip)
    ]) >= 2  # Al menos 2 dedos un poco levantados

    if all(tip[1] > pip[1] for tip, pip in [  # "all" todos deben cumplir la condicion
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip),
        (thumb_tip, thumb_ip)]) and 50 < dist_thumb_index < 70 and dist_middle_ring < 40 and dedos_curvados:
        return "C"

    # ================== LETRA D ==================
    if distancia(thumb_tip, middle_tip) < 30  and index_tip[1] < index_pip[1] and all(tip[0] > pip[0] for tip, pip in [
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip)
    ]):
        return "D"

    # ================== LETRA E ==================
    distancia_tipPulgar_cero=distancia(thumb_tip, palm_center)
    if all(abs(tip[1] - pip[1]) < 30 for tip, pip in [
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip)
    ]) and thumb_tip[0] < index_tip[0] and thumb_tip[0] < thumb_ip[0] and 80 < distancia_tipPulgar_cero < 150:
        #st.write("Distancia:", distancia_tipPulgar_cero)
        return "E"


    # ================== LETRA F ==================
    if (distancia(thumb_tip, index_tip) < 30 and
        all(tip[1] < pip[1] for tip, pip in [
            (middle_tip, middle_pip), 
            (ring_tip, ring_pip), 
            (pinky_tip, pinky_pip)]) and index_tip > index_pip):
        return "F"
    
     #================== LETRA G ==================
    dist_tipPulgar_tipIndice = distancia(index_tip,thumb_tip)
    if (index_tip[1] < index_pip[1] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (ring_tip, ring_pip),
            (pinky_tip, pinky_pip),
            (middle_tip, middle_pip)]) and  
            thumb_tip[0] > thumb_ip[0] and
            thumb_tip[0] > index_tip[0] and 40< dist_tipPulgar_tipIndice <70):
        #st.write("Distancia:", dist_tipPulgar_tipIndice)
        return "G"
    
    # ================== LETRA I ==================
    distancia_tipPulgar_tipMenique = distancia(pinky_tip,thumb_tip)
    if (pinky_tip[1] < pinky_pip[1] and
        all(tip[1] > pip[1] for tip, pip in [
            (index_tip, index_pip), 
            (middle_tip, middle_pip), 
            (ring_tip, ring_pip)]) and  thumb_tip[1] < thumb_ip[1]) and 100< distancia_tipPulgar_tipMenique <200:
        #st.write("Distancia:", distancia_tipPulgar_tipMenique)
        return "I"
    
    # ================== LETRA J ==================
    distancia_tipIndice_tipMenique2 = distancia(pinky_tip,middle_tip)
    if (pinky_tip[1] < pinky_pip[1] and 
        index_tip[1] < index_pip[1] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (middle_tip, middle_pip), 
            (ring_tip, ring_pip)]) and  thumb_tip[1] < thumb_ip[1] and 100 < distancia_tipIndice_tipMenique2 < 200):
        #st.write("Distancia:", distancia_tipIndice_tipMenique2)
        return "J"
    
     # ================== LETRA K ==================
    dist_tipIndice_tipMedio = distancia(middle_tip, index_tip)
    if (index_tip[1] < index_pip[1] and
        middle_tip[1] < middle_pip[1] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (ring_tip, ring_pip),
            (pinky_tip, pinky_pip)]) and  
            thumb_tip[1] < thumb_ip[1] and 
            10<distancia_horizontal<35 and
            30< dist_tipIndice_tipMedio <60):
        #st.write("Distancia:", dist_tipIndice_tipMedio)
        return "K"
        # ================== LETRA L ==================
    if (index_tip[1] < index_pip[1] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (ring_tip, ring_pip),
            (pinky_tip, pinky_pip),
            (middle_tip, middle_pip)]) and  
            thumb_tip[0] > thumb_ip[0] and
            thumb_tip[0] > index_tip[0] and distancia_anulartip_cero < 60):
        #st.write("Distancia:", dist_tipIndice_tipMedio)
        return "L"
    # ================== LETRA M ==================
    if all(tip[1] > pip[1] for tip, pip in [  # "all" todos deben cumplir la condicion
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (thumb_tip, thumb_ip)
    ]) and pinky_tip[1] < pinky_pip[1]:    
        return "M" 
     # ================== LETRA N ==================             
    if all(tip[1] > pip[1] for tip, pip in [  # "all" todos deben cumplir la condicion
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (thumb_tip, thumb_ip)
    ]) and pinky_tip[1] < pinky_pip[1] and ring_tip[1] < ring_pip[1]:    
        return "N"
    # ================== LETRA O ==================
    if all(tip[0] > pip[0] for tip, pip in [
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip),
        (thumb_tip, thumb_ip)
    ]) and distancia(thumb_tip, index_tip) < 30:
        return "O"

# ================== LETRA P ==================
    if all(tip[0] < pip[0] for tip, pip in [  # "all" todos deben cumplir la condicion
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip)
    ]) and thumb_tip[0] > thumb_ip[0] and index_tip[0] > index_pip[0] and middle_tip[0] > middle_pip[0]:
        #st.write("Distancia: ", dist_tipPulgar_tipIndice)
        return "P"
    
    # ================== LETRA R ==================
    #dist_tipIndice_tipMedio_cruzados = distancia(middle_tip, index_tip)
    if (index_tip[1] < index_pip[1] and
        middle_tip[1] < middle_pip[1] and
        thumb_tip[1] < thumb_ip[1] and 

        index_tip[0] < middle_tip[0] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (ring_tip, ring_pip),
            (pinky_tip, pinky_pip)])):
        #st.write("Distancia:", dist_tipIndice_tipMedio)
        return "R"
    
    # ================== LETRA T ==================
    #dist_tipPulgar_tipIndice = distancia(index_tip,thumb_tip)
    if all(tip[0] < pip[0] for tip, pip in [  # "all" todos deben cumplir la condicion
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip)
    ]) and thumb_tip[1] < thumb_ip[1] and index_tip[0] > thumb_tip[0] and 140<dist_tipPulgar_tipIndice < 180:
        #st.write("Distancia: ", dist_tipPulgar_tipIndice)
        return "T"

    # ================== LETRA U ==================
    dist_tipIndice_tipMedio_juntos = distancia(middle_tip, index_tip)
    if (index_tip[1] < index_pip[1] and
        middle_tip[1] < middle_pip[1] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (ring_tip, ring_pip),
            (pinky_tip, pinky_pip)]) and  thumb_tip[1] < thumb_ip[1] and 
            thumb_tip[0] < middle_tip[0] and 
            dist_tipIndice_tipMedio_juntos < 30):
        #st.write("Distancia:", dist_tipIndice_tipMedio)
        return "U"
    # ================== LETRA V ==================
    dist_tipIndice_tipMedio = distancia(middle_tip, index_tip)
    if (index_tip[1] < index_pip[1] and
        middle_tip[1] < middle_pip[1] and
        thumb_tip[1] < thumb_ip[1] and
        index_tip[0] > thumb_tip[0] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (ring_tip, ring_pip),
            (pinky_tip, pinky_pip)]) and   40< dist_tipIndice_tipMedio <60):
        #st.write("Distancia:", dist_tipIndice_tipMedio)
        return "V"   
    
    # ================== LETRA S ==================
    dist_tipIndice_tipPulgar = distancia(thumb_tip, middle_pip)
    if (index_tip[1] < index_pip[1] and
        middle_tip[1] > middle_pip[1] and
        thumb_tip[1] < thumb_ip[1] and
        index_tip[0] > thumb_tip[0] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (ring_tip, ring_pip),
            (pinky_tip, pinky_pip)]) and dist_tipIndice_tipPulgar < 30 ):
        #st.write("Distancia:", dist_tipIndice_tipMedio)
        return "S"  

    # ================== LETRA W ==================
    # dist_tipIndice_tipMedio = distancia(middle_tip, index_tip)
    if (index_tip[1] < index_pip[1] and
        middle_tip[1] < middle_pip[1] and
        thumb_tip[1] < thumb_ip[1] and
        ring_tip[1] < ring_pip[1] and 

        index_tip[0] > thumb_tip[0] and
        all(tip[1] > pip[1] for tip, pip in [ 
            (pinky_tip, pinky_pip)]) ):
        #st.write("Distancia:", dist_tipIndice_tipMedio)
        return "W"    


    # ================== LETRA _ ==================
    #distancia_tipIndice_tipMenique = distancia(pinky_tip,thumb_tip)
    if all(tip[1] < pip[1] for tip, pip in [ 
        (index_tip, index_pip),
        (middle_tip, middle_pip),
        (ring_tip, ring_pip),
        (pinky_tip, pinky_pip)
    ]) and thumb_tip[1] < thumb_ip[1]:
        #st.write("Distancia:", distancia_tipIndice_tipMenique)
        return "_"

    # ================== LETRA J ==================
    # Requiere detección de movimiento del meñique (trayectoria curva)
    # Este bloque es un marcador para agregar detección por trayectoria más adelante.
    # Por ahora, puedes dejarlo así:
    # if trayectoria_del_meñique_forma_curva():
    #     return "J"
    




# ===== INTERFAZ DE USUARIO =====
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Cámara en Tiempo Real")
    run = st.checkbox("Iniciar Cámara", True)
    frame_placeholder = st.empty()

with col2:
    st.subheader("Mensaje Construido")
    if "mensaje" not in st.session_state:
        st.session_state.mensaje = []
    
    mensaje_display = st.empty()
    mensaje_display.markdown(
        f"<div style='min-height: 100px; border: 1px solid #eee; padding: 10px; border-radius: 5px;'><b>{' '.join(st.session_state.mensaje)}</b></div>",
        unsafe_allow_html=True
    )

    if st.button("Borrar Todo", use_container_width=True):
        st.session_state.mensaje = []
        mensaje_display.markdown("<div style='min-height: 100px; border: 1px solid #eee; padding: 10px; border-radius: 5px;'></div>", unsafe_allow_html=True)

    # Botón para guardar mensaje en la base de datos
    if st.button("Guardar mensaje", use_container_width=True):
        mensaje_final = ''.join(st.session_state.mensaje).strip()
        if mensaje_final:
            nuevo = Mensaje(texto=mensaje_final)
            session.add(nuevo)
            session.commit()
            st.success("Mensaje guardado en la base de datos")
        else:
            st.warning("No hay mensaje para guardar")

    st.markdown("---")
    st.subheader("Última Detección")
    gesto_display = st.markdown("*Esperando...*")

    # Mostrar últimos mensajes guardados
    st.markdown("---")
    st.subheader("Historial de mensajes guardados")
    mensajes_guardados = session.query(Mensaje).order_by(Mensaje.timestamp.desc()).limit(5).all()
    for m in mensajes_guardados:
        st.markdown(f"-  {m.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: *{m.texto}*")

# ===== BUCLE PRINCIPAL =====
if run:
    cap = cv2.VideoCapture(0)
    ultimo_gesto = None
    ultimo_tiempo = 0

    while run:
        ret, frame = cap.read()
        if not ret:
            st.error("Error al acceder a la cámara.")
            break

        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        h, w = image.shape[:2]
        gesto = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image, hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style())
                gesto = detectar_gesto(hand_landmarks, w, h)

        ahora = time.time()
        if gesto and (ahora - ultimo_tiempo >1.8):
        ##if gesto and (ahora - ultimo_tiempo > 2.5 or gesto != ultimo_gesto):
            if gesto == "BORRAR" and st.session_state.mensaje:
                st.session_state.mensaje.pop()
            elif gesto == "BORRAR_TODO":
                st.session_state.mensaje = []
            elif gesto == "ESPACIO":
                st.session_state.mensaje.append(" ")
            elif len(gesto) == 1:
                st.session_state.mensaje.append(gesto)
            mensaje_display.markdown(
                f"<div style='min-height: 100px; border: 1px solid #eee; padding: 10px; border-radius: 5px;'><b>{' '.join(st.session_state.mensaje)}</b></div>",
                unsafe_allow_html=True)
            gesto_display.markdown(f"*{gesto}*")
            ultimo_gesto = gesto
            ultimo_tiempo = ahora

        cv2.putText(image, f"Mensaje: {' '.join(st.session_state.mensaje)}",
                    (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        frame_placeholder.image(image, channels="RGB")
    cap.release()
else:
    st.info("Activa la cámara para comenzar")
detectar_gesto