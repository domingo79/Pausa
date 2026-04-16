import streamlit as st
import time
import base64

# --- CONFIG ---
st.set_page_config(page_title="Timer Pausa", page_icon="⌛", layout="centered")

# --- STILI ---
st.markdown("""
<style>
.timer-overlay {
    position: fixed;
    top: 430px;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    z-index: 1000;
    pointer-events: none;
}
.big-timer {
    font-size: 4rem;
    font-weight: bold;
    text-shadow: 2px 2px 12px rgba(0,0,0,0.6);
    line-height: 1;
}
.sub-text {
    font-size: 1rem;
    color: #ccc;
    margin-top: 0.3rem;
}
.message {
    font-size: 5rem;
    font-weight: bold;
    color: #FF3B3B;
}
</style>
""", unsafe_allow_html=True)

# --- AUDIO ---


def play_sound(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)


# --- SESSION STATE ---
if "running" not in st.session_state:
    st.session_state.running = False
if "paused" not in st.session_state:
    st.session_state.paused = False
if "time_left" not in st.session_state:
    st.session_state.time_left = 0

# --- TITOLO ---
st.markdown("<h1 style='text-align: center;'>⌛ Scegli la durata della pausa!</h1>",
            unsafe_allow_html=True)


# --- INPUT ---
col_a, col_b = st.columns([2, 1])
with col_a:
    option = st.selectbox("Durata pausa:", ("5 minuti",
                          "10 minuti", "Personalizzato"))
with col_b:
    if option == "5 minuti":
        minutes = 5
    elif option == "10 minuti":
        minutes = 10
    else:
        minutes = st.number_input(
            "Minuti:", min_value=1, max_value=60, value=5)

# --- SVEGLIA (immagine statica) ---
st.image("sveglia.png", use_container_width=True)

# --- TIMER PLACEHOLDER (sovrapposto via CSS) ---
timer_placeholder = st.empty()


def show_timer(text, color="#888", sub=""):
    sub_html = f'<div class="sub-text">{sub}</div>' if sub else ""
    timer_placeholder.markdown(f"""
    <div class="timer-overlay">
        <div class="big-timer" style="color:{color};">{text}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


# Stato iniziale
if not st.session_state.running:
    timer_placeholder.markdown(
        '<div class="timer-overlay" style="visibility:hidden;">00:00</div>', unsafe_allow_html=True)

# --- PROGRESS BAR ---
progress_bar = st.progress(0)

# --- BOTTONI ---
col1, col2, col3 = st.columns(3)
with col1:
    start = st.button("▶️ Start")
with col2:
    pause_btn = st.button("⏸️ Pausa / Riprendi")
with col3:
    reset_btn = st.button("🔄 Reset")

if start:
    st.session_state.running = True
    st.session_state.paused = False
    st.session_state.time_left = int(minutes * 60)

if pause_btn and st.session_state.running:
    st.session_state.paused = not st.session_state.paused

if reset_btn:
    st.session_state.running = False
    st.session_state.paused = False
    st.session_state.time_left = 0
    timer_placeholder.markdown(
        '<div class="timer-overlay" style="visibility:hidden;">00:00</div>', unsafe_allow_html=True)
    progress_bar.progress(0)

# --- LOOP TIMER ---
if st.session_state.running:
    total = int(minutes * 60)

    while st.session_state.time_left >= 0:
        mins = st.session_state.time_left // 60
        secs = st.session_state.time_left % 60
        remaining = st.session_state.time_left / total if total > 0 else 0

        color = "#00FF9C" if remaining > 0.6 else "#FFA500" if remaining > 0.3 else "#FF3B3B"

        if not st.session_state.paused:
            show_timer(f"{mins:02d}:{secs:02d}", color=color)
            progress_bar.progress((total - st.session_state.time_left) / total)
            time.sleep(1)
            st.session_state.time_left -= 1
        else:
            show_timer(f"{mins:02d}:{secs:02d}", color=color, sub="⏸ In pausa")
            time.sleep(0.2)

        if st.session_state.time_left < 0:
            break

    # --- FINE ---
    timer_placeholder.markdown("""
    <div class="timer-overlay">
        <div class="message">🔔 PAUSA FINITA!</div>
        <div class="sub-text">Tornate in aula</div>
    </div>
    """, unsafe_allow_html=True)
    progress_bar.progress(1.0)
    play_sound("alarm.mp3")
    st.session_state.running = False
