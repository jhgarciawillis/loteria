import streamlit as st
import random
from PIL import Image
import io
from loteriabackend import LoteriaCard, LoteriaDeck

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
            st.experimental_rerun()

        if st.button("Call Next Card"):
            card = game.call_next_card()
            if card:
                img = Image.open(io.BytesIO(card.image))
                st.image(img, caption=card.name, width=200)
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
                    img = Image.open(io.BytesIO(card.image))
                    st.image(img, caption=card.name, width=100)

if __name__ == "__main__":
    main()
