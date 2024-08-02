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
        margin-bottom: 10px;
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

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = None
        self.paused_time = None
        self.is_paused = False

    def start(self):
        self.start_time = time.time()
        self.is_paused = False

    def pause(self):
        if not self.is_paused:
            self.paused_time = time.time()
            self.is_paused = True

    def resume(self):
        if self.is_paused:
            self.start_time += time.time() - self.paused_time
            self.is_paused = False

    def get_remaining_time(self):
        if self.start_time is None:
            return self.duration
        if self.is_paused:
            elapsed = self.paused_time - self.start_time
        else:
            elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)

    def is_finished(self):
        return self.get_remaining_time() <= 0

class GameState:
    def __init__(self):
        self.game = LoteriaGame()
        self.timer = Timer(15)
        self.is_running = False

    def start_new_game(self):
        self.game.start_new_game()
        self.timer = Timer(self.timer.duration)
        self.is_running = False

    def start_game(self):
        if not self.is_running:
            self.is_running = True
            self.call_next_card()

    def call_next_card(self):
        card = self.game.call_next_card()
        if card:
            self.timer.start()
        else:
            self.is_running = False
        return card

    def update(self):
        if self.is_running and not self.timer.is_paused and self.timer.is_finished():
            self.call_next_card()

    def pause_game(self):
        self.timer.pause()

    def resume_game(self):
        self.timer.resume()

    def set_timer_duration(self, duration):
        self.timer.duration = duration
        if self.is_running and not self.timer.is_paused:
            self.timer.start()

def initialize_session_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = GameState()

def render_game_controls():
    game_state = st.session_state.game_state
    
    st.subheader("Controles del Juego")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reiniciar Juego"):
            game_state.start_new_game()
            st.rerun()
    
    with col2:
        if game_state.timer.is_paused:
            if st.button("▶️ Continuar"):
                game_state.resume_game()
                st.rerun()
        elif game_state.is_running:
            if st.button("⏸️ Pausar"):
                game_state.pause_game()
                st.rerun()

    with col3:
        if not game_state.is_running:
            if st.button("▶️ Comenzar"):
                game_state.start_game()
                st.rerun()

    st.subheader("Configuración")
    new_timer = st.slider("Tiempo por carta (segundos)", min_value=5, max_value=60, value=int(game_state.timer.duration), step=1)
    if new_timer != game_state.timer.duration:
        game_state.set_timer_duration(new_timer)

def render_current_card():
    game_state = st.session_state.game_state
    
    st.subheader("Carta Actual")
    if game_state.game.current_card:
        card = game_state.game.current_card
        st.image(card.image_path, caption=card.name, use_column_width=True)

        remaining_time = game_state.timer.get_remaining_time()
        st.progress(remaining_time / game_state.timer.duration)
        st.text(f"Tiempo restante: {remaining_time:.1f}s")

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

    # Update game state
    st.session_state.game_state.update()

    # Rerun the app to update the timer
    if st.session_state.game_state.is_running:
        time.sleep(0.1)
        st.rerun()

if __name__ == "__main__":
    main()
