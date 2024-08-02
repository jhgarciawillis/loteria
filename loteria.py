import streamlit as st
import random
from PIL import Image
import os
import pandas as pd
import time

# Configuración de la página
st.set_page_config(page_title="Juego de Lotería", layout="wide")

# Estilos CSS
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
        self.cards = self._load_cards()
        self.shuffle()

    def _load_cards(self):
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

    def draw_card(self):
        return self.cards.pop(0) if self.cards else None

class LoteriaGame:
    def __init__(self):
        self.deck = LoteriaDeck()
        self.current_card = None
        self.called_cards = []

    def start_new_game(self):
        self.deck = LoteriaDeck()
        self.current_card = None
        self.called_cards = []

    def call_next_card(self):
        card = self.deck.draw_card()
        if card:
            self.current_card = card
            self.called_cards.append(card)
        return card

class GameState:
    def __init__(self):
        self.game = LoteriaGame()
        self.timer = 15
        self.auto_call = False
        self.timer_start = None

    def start_new_game(self):
        self.game.start_new_game()
        self.timer_start = None

    def call_next_card(self):
        card = self.game.call_next_card()
        if card:
            self.timer_start = time.time()
        return card

    def should_auto_call(self):
        if not self.auto_call or self.timer_start is None:
            return False
        elapsed = time.time() - self.timer_start
        return elapsed >= self.timer

def initialize_session_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = GameState()

def render_game_controls():
    game_state = st.session_state.game_state
    
    st.subheader("Controles del Juego")
    if st.button("🔄 Iniciar Nuevo Juego"):
        game_state.start_new_game()
        st.rerun()

    st.subheader("Configuración")
    game_state.timer = st.slider("Tiempo por carta (segundos)", min_value=5, max_value=60, value=game_state.timer, step=1)
    game_state.auto_call = st.checkbox("Llamada automática", value=game_state.auto_call)

    if st.button("🎴 Llamar Siguiente Carta"):
        game_state.call_next_card()
        st.rerun()

def render_current_card():
    game_state = st.session_state.game_state
    
    st.subheader("Carta Actual")
    if game_state.game.current_card:
        card = game_state.game.current_card
        st.image(card.image_path, caption=card.name, use_column_width=True)

def render_called_cards():
    game_state = st.session_state.game_state
    
    st.subheader("Cartas Llamadas")
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    for card in game_state.game.called_cards:
        st.image(card.image_path, caption=card.name, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.title("🎭 Juego de Lotería")
    initialize_session_state()

    col1, col2 = st.columns([1, 2])

    with col1:
        render_game_controls()

    with col2:
        render_current_card()
        render_called_cards()

    # Check for auto-call
    if st.session_state.game_state.should_auto_call():
        st.session_state.game_state.call_next_card()
        st.rerun()

if __name__ == "__main__":
    main()
