# # =========================================================
# 🎙️ CONTROL POR VOZ MQTT - VERSIÓN PRO BONITA Y LEGIBLE
# Angie Style: Mejor contraste + interfaz limpia + sin espacios blancos feos
# =========================================================

import os
import streamlit as st
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# =========================================================
# CONFIGURACIÓN STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Control por Voz MQTT",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =========================================================
# ESTILOS VISUALES PRO
# =========================================================
st.markdown("""
<style>

/* Fondo general */
.stApp {
    background: linear-gradient(135deg, #d9c2ff, #f3e8ff);
    color: #1f1f1f;
}

/* Títulos */
.main-title {
    text-align:center;
    font-size:48px;
    font-weight:900;
    color:#2d1457;
    margin-bottom:0px;
}

.subtitle {
    text-align:center;
    font-size:20px;
    color:#4b2e83;
    margin-top:0px;
    margin-bottom:25px;
}

/* Caja principal */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    border-radius: 20px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #2d1457;
}

[data-testid="stSidebar"] * {
    color: white !important;
    font-weight: 600;
}

/* Botones */
.stButton>button {
    width: 100%;
    border-radius: 15px;
    background: linear-gradient(90deg, #6a0dad, #9b59b6);
    color: white;
    font-size: 20px;
    font-weight: bold;
    border: none;
    padding: 12px;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
    background: linear-gradient(90deg, #4b0082, #8e44ad);
}

/* Texto */
.big-text {
    text-align:center;
    font-size:22px;
    font-weight:bold;
    color:#2d1457;
}

/* Resultado */
.result-box {
    background-color:#ffffffcc;
    padding:20px;
    border-radius:20px;
    border: 3px solid #6a0dad;
    color:#1f1f1f;
    font-size:22px;
    font-weight:bold;
    text-align:center;
}

/* Elimina fondo blanco del componente Bokeh */
iframe {
    background: transparent !important;
}

/* Espaciado visual */
div[data-testid="stVerticalBlock"] > div:has(iframe) {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 auto !important;
    display: flex;
    justify-content: center;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# MQTT CONFIG
# =========================================================
broker = "broker.mqttdashboard.com"
port = 1883

def on_publish(client, userdata, result):
    print("Dato publicado correctamente")

client1 = paho.Client("GIT-HUBC")
client1.on_publish = on_publish

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("🛠️ Panel de Control")
    st.markdown("### 📌 Instrucciones")
    st.write("🎤 Presiona **ESCUCHAR**")
    st.write("🗣️ Di comandos como:")
    st.write("• enciende las luces")
    st.write("• apaga las luces")
    st.write("• abre la puerta")
    st.write("• cierra la puerta")
    st.markdown("---")
    st.success("🌐 Broker conectado: mqttdashboard")

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">🎙️ CONTROL POR VOZ MQTT</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Habla y controla tu ESP32 de forma inteligente ✨</div>', unsafe_allow_html=True)

# =========================================================
# IMAGEN
# =========================================================
try:
    image = Image.open("voice_ctrl.jpg")
    st.image(image, width=280)
except:
    st.info("🖼️ Agrega una imagen llamada voice_ctrl.jpg para personalizar.")

# =========================================================
# TEXTO
# =========================================================
st.markdown('<div class="big-text">🎤 Presiona el botón y habla claramente</div>', unsafe_allow_html=True)

# =========================================================
# BOTÓN BOKEH SIN ESPACIO FEO
# =========================================================
stt_button = Button(
    label="🎧 ESCUCHAR",
    width=250,
    height=60
)

stt_button.js_on_event("button_click", CustomJS(code="""
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-ES';

    recognition.onstart = function() {
        document.dispatchEvent(new CustomEvent("STATUS", {detail: "🎙️ Escuchando..."}));
    };

    recognition.onresult = function(e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }

        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    };

    recognition.onerror = function() {
        document.dispatchEvent(new CustomEvent("STATUS", {detail: "❌ Error de micrófono"}));
    };

    recognition.onend = function() {
        document.dispatchEvent(new CustomEvent("STATUS", {detail: "✅ Grabación finalizada"}));
    };

    recognition.start();
"""))

# =========================================================
# EVENTOS
# =========================================================
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT,STATUS",
    key="listen",
    refresh_on_update=False,
    override_height=80,
    debounce_time=0
)

# =========================================================
# RESPUESTA
# =========================================================
if result:

    if "STATUS" in result:
        st.info(result["STATUS"])

    if "GET_TEXT" in result:
        comando = result.get("GET_TEXT").strip().lower()

        st.markdown(
            f'<div class="result-box">🗣️ Comando detectado:<br><br>“{comando}”</div>',
            unsafe_allow_html=True
        )

        try:
            client1.connect(broker, port)

            message = json.dumps({
                "Act1": comando
            })

            client1.publish("voice_ctrl", message)

            st.success("📡 Comando enviado al ESP32 correctamente")

        except Exception as e:
            st.error(f"❌ Error enviando MQTT: {e}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("✨ Diseñado para Interfaces Multimodales | MQTT + Streamlit + ESP32")
