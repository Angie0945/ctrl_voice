# =========================================================
# 🎤 INTERFACES MULTIMODALES PRO
# Control por Voz + MQTT + Diseño Mejorado
# =========================================================

import os
import time
import json
import paho.mqtt.client as paho
import streamlit as st
from PIL import Image
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Control por Voz MQTT",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------------- ESTILOS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #EDE7FF, #D6C8FF);
}

/* Título principal */
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #2E1065;
    margin-bottom: 0;
}

/* Subtítulo */
.sub-title {
    text-align: center;
    font-size: 20px;
    color: #4C1D95;
    margin-top: 0;
    margin-bottom: 25px;
}

/* Tarjetas */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Texto normal */
.big-text {
    text-align: center;
    font-size: 20px;
    color: #1F2937;
    font-weight: 500;
}

/* Resultado */
.result-box {
    background-color: white;
    padding: 15px;
    border-radius: 15px;
    border: 2px solid #8B5CF6;
    color: #111827;
    font-size: 22px;
    font-weight: bold;
    text-align: center;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #F3E8FF;
}
</style>
""", unsafe_allow_html=True)

# ---------------- MQTT ----------------
broker = "broker.mqttdashboard.com"
port = 1883

def on_publish(client, userdata, result):
    print("Dato publicado correctamente")

client1 = paho.Client("AngieVoiceApp")
client1.on_publish = on_publish

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🛠️ Panel de Ayuda")
    st.markdown("""
### 📌 Instrucciones:
1. Presiona **🎤 Escuchar**
2. Habla claramente  
3. La app enviará el comando al ESP32  

### 🗣️ Ejemplos:
- *enciende las luces* 💡  
- *apaga las luces* 🌙  
- *abre la puerta* 🚪  
- *cierra la puerta* 🔒  

### 🌐 Broker:
`broker.mqttdashboard.com`

### 📡 Topic:
`voice_ctrl`
""")

# ---------------- HEADER ----------------
st.markdown('<p class="main-title">🎙️ INTERFACES MULTIMODALES</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Control inteligente por voz + MQTT</p>', unsafe_allow_html=True)

# ---------------- IMAGEN ----------------
try:
    image = Image.open("voice_ctrl.jpg")
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.image(image, use_container_width=True)

except:
    st.info("📷 Agrega una imagen llamada 'voice_ctrl.jpg' para personalizar la interfaz.")

# ---------------- MENSAJE ----------------
st.markdown('<p class="big-text">🎤 Presiona el botón y da una orden por voz</p>', unsafe_allow_html=True)

# ---------------- BOTÓN DE VOZ ----------------
stt_button = Button(label="🎤 ESCUCHAR", width=250)

stt_button.js_on_event("button_click", CustomJS(code="""
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "es-ES";

    recognition.onstart = function() {
        document.dispatchEvent(new CustomEvent("LISTENING", {detail: "🎙️ Escuchando..."}));
    };

    recognition.onresult = function(e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }

        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    };

    recognition.onerror = function() {
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: "No se entendió el audio"}));
    };

    recognition.start();
"""))

# ---------------- EVENTOS ----------------
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT,LISTENING",
    key="listen",
    refresh_on_update=False,
    override_height=100,
    debounce_time=0
)

# ---------------- RESPUESTA ----------------
if result:

    if "LISTENING" in result:
        st.warning("🎙️ Escuchando... Habla ahora")

    if "GET_TEXT" in result:

        comando = result.get("GET_TEXT").strip()

        st.markdown(
            f'<div class="result-box">🗣️ Orden detectada: {comando}</div>',
            unsafe_allow_html=True
        )

        # Conectar y publicar
        try:
            client1.connect(broker, port)

            message = json.dumps({
                "Act1": comando.lower()
            })

            client1.publish("voice_ctrl", message)

            st.success("📡 Comando enviado correctamente al ESP32")

        except Exception as e:
            st.error(f"❌ Error MQTT: {e}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("💜 Diseñado para Interfaces Multimodales | Voz + ESP32 + MQTT")
