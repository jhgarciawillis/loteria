import streamlit as st
import random
from PIL import Image
import os
import pandas as pd

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
    st.set_page_config(page_title="Lotería Game", layout="wide")
    st.title("Lotería Game")

    if 'game' not in st.session_state:
        st.session_state.game = LoteriaGame()

    game = st.session_state.game

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("Start New Game"):
            game.start_new_game()
            st.rerun()

        if st.button("Call Next Card"):
            card = game.call_next_card()
            if card:
                st.image(card.image_path, caption=card.name, width=200)
            else:
                st.write("All cards have been called!")

    with col2:
        st.subheader("Called Cards")
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
