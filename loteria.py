import streamlit as st
import random
from PIL import Image
import os
import pandas as pd
import time

# Configuración de la página
st.set_page_config(page_title="Juego de Lotería", layout="wide")

# Estilos CSS para mejorar la apariencia y la compatibilidad responsive
st.markdown("""
<style>
    .stButton>button {
        font-size: 1.2rem;
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    .stImage {
        margin-bottom: 1rem;
    }
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 1rem;
    }
    .card-item {
        text-align: center;
    }
    .card-item img {
        max-width: 100%;
        height: auto;
    }
    @media (max-width: 768px) {
        .stButton>button {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

class LoteriaCard:
    def __init__(self, name, image_path):
        self.name = name
        self.image_path = image_path

class LoteriaDeck:
    def __init__(self):
        self.cards = self.load_cards()
        self.shuffle()

    def load_cards(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'loteria.csv')
        images_dir = os.path.join(current_dir, 'imagenes')
        
        cards = []
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            image_path = os.path.join(images_dir, row['filename'])
            cards.append(LoteriaCard(row['label'], image_path))
        return cards

    def shuffle(self):
        random.shuffle(self.cards)

class LoteriaGame:
    def __init__(self):
        self.deck = LoteriaDeck()
        self.current_card = None
        self.called_cards = []

    def start_new_game(self):
        self.deck.shuffle()
        self.current_card = None
        self.called_cards = []

    def call_next_card(self):
        if len(self.called_cards) < len(self.deck.cards):
            self.current_card = self.deck.cards[len(self.called_cards)]
            self.called_cards.append(self.current_card)
            return self.current_card
        return None

def main():
    st.title("🎭 Juego de Lotería")

    if 'game' not in st.session_state:
        st.session_state.game = LoteriaGame()
    if 'timer' not in st.session_state:
        st.session_state.timer = 15
    if 'auto_call' not in st.session_state:
        st.session_state.auto_call = False

    game = st.session_state.game

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Controles del Juego")
        if st.button("🔄 Iniciar Nuevo Juego"):
            game.start_new_game()
            st.session_state.current_card = None
            st.session_state.timer_start = None
            st.rerun()

        st.subheader("Configuración")
        st.session_state.timer = st.slider("Tiempo por carta (segundos)", min_value=5, max_value=60, value=st.session_state.timer, step=5)
        st.session_state.auto_call = st.checkbox("Llamada automática", value=st.session_state.auto_call)

        if st.button("🎴 Llamar Siguiente Carta"):
            call_next_card()

    with col2:
        st.subheader("Carta Actual")
        if st.session_state.current_card:
            card = st.session_state.current_card
            col_image, col_timer = st.columns([3,1])
            with col_image:
                st.image(card.image_path, caption=card.name, use_column_width=True)
            with col_timer:
                if st.session_state.timer_start:
                    elapsed = time.time() - st.session_state.timer_start
                    remaining = max(0, st.session_state.timer - elapsed)
                    st.metric("Tiempo", f"{remaining:.1f}s")
                    if remaining > 0:
                        st.progress(remaining / st.session_state.timer)
                    else:
                        st.warning("¡Tiempo terminado!")
                        if st.session_state.auto_call:
                            call_next_card()

        st.subheader("Cartas Llamadas")
        display_called_cards()

def call_next_card():
    card = st.session_state.game.call_next_card()
    if card:
        st.session_state.current_card = card
        st.session_state.timer_start = time.time()
        st.rerun()
    else:
        st.write("¡Todas las cartas han sido llamadas!")

def display_called_cards():
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    for card in st.session_state.game.called_cards:
        st.markdown(f'''
        <div class="card-item">
            <img src="data:image/png;base64,{base64_image(card.image_path)}" alt="{card.name}">
            <p>{card.name}</p>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

if __name__ == "__main__":
    main()
