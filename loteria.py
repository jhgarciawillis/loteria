import streamlit as st
import random
import os
import pandas as pd
import time
from PIL import Image

# Page configuration
st.set_page_config(page_title="Juego de Lotería", layout="wide")

# CSS styles
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
</style>
""", unsafe_allow_html=True)

class LoteriaCard:
    def __init__(self, name, image_path):
        self.name = name
        self.image_path = image_path

class LoteriaGame:
    def __init__(self):
        self.cards = self.load_cards()
        self.current_card = None
        self.called_cards = []
        self.timer = 15
        self.is_running = False
        self.last_call_time = None

    def load_cards(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'loteria.csv')
        images_dir = os.path.join(current_dir, 'imagenes')
        
        cards = []
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            image_path = os.path.join(images_dir, row['filename'])
            cards.append(LoteriaCard(row['label'], image_path))
        random.shuffle(cards)
        return cards

    def start_game(self):
        self.is_running = True
        self.call_next_card()

    def stop_game(self):
        self.is_running = False
        self.last_call_time = None

    def call_next_card(self):
        if self.cards:
            self.current_card = self.cards.pop(0)
            self.called_cards.append(self.current_card)
            self.last_call_time = time.time()
        else:
            self.stop_game()

    def reset_game(self):
        self.__init__()

    def update(self):
        if self.is_running and self.last_call_time:
            elapsed_time = time.time() - self.last_call_time
            if elapsed_time >= self.timer:
                self.call_next_card()

def initialize_session_state():
    if 'game' not in st.session_state:
        st.session_state.game = LoteriaGame()

def render_game_controls():
    game = st.session_state.game
    
    st.subheader("Controles del Juego")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reiniciar Juego"):
            game.reset_game()
            st.rerun()
    
    with col2:
        if game.is_running:
            if st.button("⏸️ Pausar"):
                game.stop_game()
                st.rerun()
        else:
            if st.button("▶️ Comenzar"):
                game.start_game()
                st.rerun()

    with col3:
        game.timer = st.number_input("Tiempo por carta (segundos)", min_value=5, max_value=60, value=game.timer, step=1)

def render_current_card():
    game = st.session_state.game
    
    st.subheader("Carta Actual")
    if game.current_card:
        st.image(game.current_card.image_path, caption=game.current_card.name, use_column_width=True)
        
        if game.is_running and game.last_call_time:
            elapsed_time = time.time() - game.last_call_time
            remaining_time = max(0, game.timer - elapsed_time)
            st.progress(remaining_time / game.timer)
            st.text(f"Tiempo restante: {remaining_time:.1f}s")

def render_called_cards():
    game = st.session_state.game
    
    st.subheader("Cartas Llamadas")
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    for card in game.called_cards[:-1]:  # Exclude the current card
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
    st.session_state.game.update()

    # Rerun the app to update the UI
    if st.session_state.game.is_running:
        time.sleep(0.1)
        st.rerun()

if __name__ == "__main__":
    main()
