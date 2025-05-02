import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow
import random
import time

# --- Game Classes ---
class SnakeAndLadderBoard:
    def __init__(self, end_square=30):
        self.ladders = {3: 22, 5: 8, 11: 26, 20: 29}
        self.snakes = {27: 1, 21: 9, 17: 4, 19: 7}
        self.end_square = end_square

    def check_snake_or_ladder(self, position):
        if position in self.ladders:
            return 'ladder', self.ladders[position]
        elif position in self.snakes:
            return 'snake', self.snakes[position]
        return None, position


class SnakeAndLadderNPC:
    def __init__(self, name="NPC"):
        self.name = name
        self.state = "Idle"
        self.position = 0
        self.dice_roll = 0
        self.has_won = False
        self.color = (random.random(), random.random(), random.random())

    def take_turn(self, board):
        if self.has_won:
            return
        self.state = "Rolling"
        self.dice_roll = random.randint(1, 6)
        self.state = "Moving"
        self.position += self.dice_roll
        if self.position > board.end_square:
            self.position = board.end_square

        kind, new_position = board.check_snake_or_ladder(self.position)
        if kind == 'ladder':
            self.position = new_position
        elif kind == 'snake':
            self.position = new_position

        if self.position == board.end_square:
            self.has_won = True


def draw_board(board, npcs, current_npc_index):
    fig, ax = plt.subplots(figsize=(6, 6))
    cols = 6
    rows = 6
    size = board.end_square

    # Draw grid and numbers
    for i in range(1, size + 1):
        x = (i - 1) % cols
        y = (i - 1) // cols
        if (y % 2) == 1:
            x = cols - 1 - x
        rect = Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=1, edgecolor='black', facecolor='lightyellow')
        ax.add_patch(rect)
        ax.text(x, y, str(i), ha='center', va='center', fontsize=9)

    # Draw ladders
    for start, end in board.ladders.items():
        sx, sy = (start - 1) % cols, (start - 1) // cols
        ex, ey = (end - 1) % cols, (end - 1) // cols
        if sy % 2: sx = cols - 1 - sx
        if ey % 2: ex = cols - 1 - ex
        ax.add_patch(FancyArrow(sx, sy, ex - sx, ey - sy, width=0.05, head_width=0.3, color='green', alpha=0.7))

    # Draw snakes
    for start, end in board.snakes.items():
        sx, sy = (start - 1) % cols, (start - 1) // cols
        ex, ey = (end - 1) % cols, (end - 1) // cols
        if sy % 2: sx = cols - 1 - sx
        if ey % 2: ex = cols - 1 - ex
        ax.add_patch(FancyArrow(sx, sy, ex - sx, ey - sy, width=0.05, head_width=0.3, color='red', alpha=0.7))

    # Draw players
    for npc in npcs:
        if npc.position > 0:
            x = (npc.position - 1) % cols
            y = (npc.position - 1) // cols
            if (y % 2) == 1:
                x = cols - 1 - x
            ax.add_patch(Circle((x, y), 0.25, color=npc.color))
            ax.text(x, y - 0.35, npc.name, ha='center', va='center', fontsize=8)

    # Highlight current player
    current_npc = npcs[current_npc_index]
    if current_npc.position > 0:
        x = (current_npc.position - 1) % cols
        y = (current_npc.position - 1) // cols
        if (y % 2) == 1:
            x = cols - 1 - x
        ax.add_patch(Circle((x, y), 0.35, color=current_npc.color, alpha=0.3))

    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(-1.5, rows - 0.5)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# --- Streamlit UI ---
st.set_page_config(page_title="Snake & Ladder Game", layout="centered")
st.title("🎲 Snake & Ladder Game with NPCs")

# Initialize game state
if "board" not in st.session_state:
    st.session_state.board = SnakeAndLadderBoard()
    st.session_state.npcs = [SnakeAndLadderNPC(name) for name in ["Alice", "Bob", "Charlie"]]
    st.session_state.current_index = 0
    st.session_state.winner = None

# Game logic
if not st.session_state.winner:
    current_npc = st.session_state.npcs[st.session_state.current_index]
    st.subheader(f"🌀 It's **{current_npc.name}**'s turn!")
    
    if st.button("🎯 Roll Dice"):
        current_npc.take_turn(st.session_state.board)
        if current_npc.has_won:
            st.session_state.winner = current_npc.name
        else:
            st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.npcs)

# Draw game board
fig = draw_board(st.session_state.board, st.session_state.npcs, st.session_state.current_index)
st.pyplot(fig)

# Winner message
if st.session_state.winner:
    st.success(f"🏆 **{st.session_state.winner}** has won the game!")
    if st.button("🔄 Restart Game"):
        st.session_state.clear()
        st.experimental_rerun()
