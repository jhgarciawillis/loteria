import streamlit as st
import random
from PIL import Image
import os
import pandas as pd
import time

# Set page configuration
st.set_page_config(page_title="Juego de Lotería", layout="wide")

# Set Spanish language
st.markdown("""
<style>
    .stButton>button {
        font-size: 20px;
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    .stImage {
        margin-bottom: 20px;
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

    game = st.session_state.game

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Controles del Juego")
        if st.button("🔄 Iniciar Nuevo Juego"):
            game.start_new_game()
            st.rerun()

        st.subheader("Temporizador")
        col_minus, col_timer, col_plus = st.columns([1,2,1])
        with col_minus:
            if st.button("-"):
                st.session_state.timer = max(5, st.session_state.timer - 5)
        with col_timer:
            st.session_state.timer = st.number_input("Segundos", min_value=5, value=st.session_state.timer, step=5)
        with col_plus:
            if st.button("+"):
                st.session_state.timer = min(60, st.session_state.timer + 5)

        if st.button("🎴 Llamar Siguiente Carta"):
            card = game.call_next_card()
            if card:
                st.session_state.current_card = card
                st.session_state.timer_start = time.time()
                st.rerun()
            else:
                st.write("¡Todas las cartas han sido llamadas!")

    with col2:
        st.subheader("Carta Actual")
        if hasattr(st.session_state, 'current_card'):
            card = st.session_state.current_card
            col_image, col_timer = st.columns([3,1])
            with col_image:
                st.image(card.image_path, caption=card.name, width=300)
            with col_timer:
                if hasattr(st.session_state, 'timer_start'):
                    elapsed = time.time() - st.session_state.timer_start
                    remaining = max(0, st.session_state.timer - elapsed)
                    st.metric("Tiempo", f"{remaining:.1f}s")
                    if remaining > 0:
                        st.empty().progress(remaining / st.session_state.timer)
                    else:
                        st.warning("¡Tiempo terminado!")

        st.subheader("Cartas Llamadas")
        called_cards_grid = st.empty()

    # Display called cards in a grid
    cols = 4
    rows = (len(game.called_cards) + cols - 1) // cols
    grid = [game.called_cards[i:i+cols] for i in range(0, len(game.called_cards), cols)]

    with called_cards_grid.container():
        for row in grid:
            cols = st.columns(4)
            for i, card in enumerate(row):
                with cols[i]:
                    st.image(card.image_path, caption=card.name, width=100)

if __name__ == "__main__":
    main()
