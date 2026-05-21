import streamlit as st
import collections
import heapq
from PIL import Image, ImageEnhance
import pytesseract
import io
import numpy as np

st.set_page_config(page_title="AI Puzzle Solver", page_icon="🧩", layout="wide")

# Custom CSS for impressive background and styling
st.markdown("""
<style>
    * { margin: 0; padding: 0; }
    html, body { height: 100%; width: 100%; }
    body {
        background: #0a0a0a;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    body::before {
        content: '';
        position: fixed; top: -50%; right: -10%;
        width: 600px; height: 600px;
        background: radial-gradient(circle, rgba(255,107,107,0.4) 0%, transparent 70%);
        border-radius: 50%;
        animation: float 8s ease-in-out infinite;
        z-index: 0; pointer-events: none;
    }
    body::after {
        content: '';
        position: fixed; bottom: -30%; left: -5%;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(35,165,213,0.4) 0%, transparent 70%);
        border-radius: 50%;
        animation: float 10s ease-in-out infinite reverse;
        z-index: 0; pointer-events: none;
    }
    @keyframes float {
        0%, 100% { transform: translate(0,0); }
        25%       { transform: translate(30px,-30px); }
        50%       { transform: translate(-20px,30px); }
        75%       { transform: translate(30px,20px); }
    }
    .stApp::before {
        content: '';
        position: fixed; top: 20%; left: 10%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(35,213,171,0.25) 0%, transparent 70%);
        border-radius: 50%;
        animation: float 12s ease-in-out infinite;
        z-index: 0; pointer-events: none;
    }
    .stApp::after {
        content: '';
        position: fixed; bottom: 10%; right: 5%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(238,119,82,0.3) 0%, transparent 70%);
        border-radius: 50%;
        animation: float 14s ease-in-out infinite reverse;
        z-index: 0; pointer-events: none;
    }
    .main {
        background: rgba(255,255,255,0.85) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 25px !important;
        padding: 40px !important;
        box-shadow: 0 30px 60px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.6) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        position: relative; z-index: 1;
    }
    .main::before {
        content: '';
        position: absolute; top:-2px; left:-2px; right:-2px; bottom:-2px;
        background: linear-gradient(135deg, rgba(255,107,107,0.1), rgba(35,165,213,0.1), rgba(35,213,171,0.1));
        border-radius: 25px; z-index: -1;
        animation: glow 3s ease-in-out infinite;
    }
    @keyframes glow {
        0%, 100% { opacity: 0.5; }
        50%       { opacity: 1; }
    }
    h1 {
        background: linear-gradient(135deg, #ee7752 0%, #e73c7e 25%, #23a6d5 50%, #23d5ab 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5em !important; margin-bottom: 15px;
        font-weight: 800 !important; letter-spacing: -1px;
    }
    h3 {
        background: linear-gradient(135deg, #e73c7e 0%, #23a6d5 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; font-weight: 700 !important; margin-bottom: 20px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #ee7752 0%, #e73c7e 50%, #23a6d5 100%) !important;
        color: white !important; border: none !important;
        padding: 14px 45px !important; border-radius: 50px !important;
        font-weight: 700 !important; font-size: 1.1em !important;
        box-shadow: 0 8px 25px rgba(238,119,82,0.35) !important;
        transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
    }
    .stButton > button:hover { transform: translateY(-3px) !important; }
    .stButton > button:active { transform: translateY(-1px) !important; }
    .step-counter {
        background: linear-gradient(135deg, #e73c7e 0%, #23a6d5 100%);
        color: white; padding: 8px 16px; border-radius: 50px;
        font-weight: bold; text-align: center; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI Puzzle Solver 🧩")
st.write("Select a puzzle type, upload an image, and watch the step-by-step solution!")

puzzle_type = st.selectbox("Select Puzzle Type", ["Sudoku", "Maze", "8 Puzzle"])

# ── Image preprocessing ──────────────────────────────────────────────────────
def preprocess_image_for_ocr(image):
    img_gray = image.convert('L')
    img_contrast = ImageEnhance.Contrast(img_gray).enhance(2.0)
    img_bright   = ImageEnhance.Brightness(img_contrast).enhance(1.2)
    return img_bright

def extract_text_from_image(image):
    try:
        processed_img = preprocess_image_for_ocr(image)
        return pytesseract.image_to_string(processed_img).strip()
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return None

# ── Display helpers ───────────────────────────────────────────────────────────
def display_sudoku_board(board, title="Board", highlight_cell=None, original_board=None):
    html = f'<h3 style="text-align:center;">{title}</h3>'
    html += '<div style="display:flex;justify-content:center;">'
    html += '<div style="display:inline-block;border:4px solid #e73c7e;background:linear-gradient(135deg,#f5f7ff 0%,#f0e6ff 100%);border-radius:12px;padding:10px;box-shadow:0 15px 40px rgba(231,60,126,0.25);">'
    for i in range(9):
        if i % 3 == 0 and i != 0:
            html += '<div style="height:4px;background:linear-gradient(90deg,#e73c7e 0%,#ee7752 100%);"></div>'
        row_html = '<div style="display:flex;">'
        for j in range(9):
            if j % 3 == 0 and j != 0:
                row_html += '<div style="width:4px;background:linear-gradient(180deg,#e73c7e 0%,#ee7752 100%);"></div>'
            value = board[i][j]
            is_highlighted = highlight_cell and (i, j) == highlight_cell
            is_original    = original_board and original_board[i][j] != 0
            if is_highlighted:
                bg, tc = 'linear-gradient(135deg,#e73c7e 0%,#ee7752 100%)', 'white'
            elif is_original:
                bg, tc = '#e8f0ff', '#2c3e50'
            else:
                bg, tc = ('#ffffff' if value != 0 else '#f9f9f9'), ('#23d5ab' if value != 0 else '#e0e0e0')
            display_val = str(value) if value != 0 else ''
            row_html += f'<div style="width:44px;height:44px;display:flex;align-items:center;justify-content:center;border:1px solid #e0e0e0;font-size:20px;font-weight:bold;background:{bg};color:{tc};">{display_val}</div>'
        row_html += '</div>'
        html += row_html
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def display_maze_board(maze_str, title="Maze", highlight_step=None):
    lines = maze_str.strip().split('\n')
    html  = f'<h3 style="text-align:center;">{title}</h3>'
    html += '<div style="display:flex;justify-content:center;">'
    html += '<div style="display:inline-block;background:linear-gradient(135deg,#f5f7ff 0%,#f0e6ff 100%);padding:12px;border-radius:12px;box-shadow:0 15px 40px rgba(231,60,126,0.25);">'
    cell_colors = {'#':'#2c3e50','S':'#23d5ab','E':'#ee7752','.':'#ffffff','*':'#f1c40f','X':'#9b59b6'}
    symbol_map  = {'S':'⭐','E':'🏁','#':'█','*':'✓','.':'','X':'●'}
    for r, line in enumerate(lines):
        row_html = '<div style="display:flex;gap:3px;">'
        for c, char in enumerate(line):
            is_highlighted = highlight_step and (r, c) == highlight_step
            color      = '#e73c7e' if is_highlighted else cell_colors.get(char, '#fff')
            text_color = 'white'   if char in ['#','S','E'] or is_highlighted else 'black'
            symbol     = symbol_map.get(char, char)
            row_html  += f'<div style="width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:2px solid #ddd;font-size:16px;font-weight:bold;background-color:{color};color:{text_color};border-radius:6px;">{symbol}</div>'
        row_html += '</div>'
        html     += row_html
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def display_8puzzle_board(puzzle_state, title="8 Puzzle", highlight_moved=None):
    html  = f'<h3 style="text-align:center;">{title}</h3>'
    html += '<div style="display:flex;justify-content:center;">'
    html += '<div style="display:inline-block;border:4px solid #23a6d5;background:linear-gradient(135deg,#f5f7ff 0%,#f0e6ff 100%);border-radius:12px;padding:10px;box-shadow:0 15px 40px rgba(35,166,213,0.25);">'
    for i in range(3):
        row_html = '<div style="display:flex;">'
        for j in range(3):
            idx          = i * 3 + j
            value        = puzzle_state[idx]
            display_val  = str(value) if value != 0 else ''
            is_highlighted = highlight_moved and idx == highlight_moved
            bg = ('linear-gradient(135deg,#e73c7e 0%,#ee7752 100%)' if is_highlighted
                  else ('linear-gradient(135deg,#23a6d5 0%,#23d5ab 100%)' if value != 0 else '#f9f9f9'))
            tc = 'white' if (value != 0 or is_highlighted) else '#e0e0e0'
            row_html += f'<div style="width:70px;height:70px;display:flex;align-items:center;justify-content:center;border:2px solid #ddd;font-size:28px;font-weight:bold;background:{bg};color:{tc};border-radius:10px;">{display_val}</div>'
        row_html += '</div>'
        html     += row_html
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

# ── Solvers ───────────────────────────────────────────────────────────────────
def solve_sudoku(board_str):
    lines  = board_str.strip().split('\n')
    values = [int(c) if c.isdigit() else (0 if c == '.' else None)
              for line in lines for c in line if c.isdigit() or c == '.']
    if len(values) != 81:
        return None, None
    board          = [values[i:i+9] for i in range(0, 81, 9)]
    original_board = [row[:] for row in board]

    def is_valid(bo, num, pos):
        if any(bo[pos[0]][i] == num and pos[1] != i for i in range(9)): return False
        if any(bo[i][pos[1]] == num and pos[0] != i for i in range(9)): return False
        bx, by = pos[1]//3, pos[0]//3
        return all(bo[by*3+i][bx*3+j] != num or (by*3+i, bx*3+j) == pos
                   for i in range(3) for j in range(3))

    def find_empty(bo):
        return next(((i,j) for i in range(9) for j in range(9) if bo[i][j]==0), None)

    def solve(bo):
        pos = find_empty(bo)
        if not pos: return True
        for n in range(1, 10):
            if is_valid(bo, n, pos):
                bo[pos[0]][pos[1]] = n
                if solve(bo): return True
                bo[pos[0]][pos[1]] = 0
        return False

    return (original_board, board) if solve(board) else (original_board, None)


def solve_sudoku_with_steps(board_str):
    lines  = board_str.strip().split('\n')
    values = [int(c) if c.isdigit() else (0 if c == '.' else None)
              for line in lines for c in line if c.isdigit() or c == '.']
    if len(values) != 81:
        return None, None, None
    board          = [values[i:i+9] for i in range(0, 81, 9)]
    original_board = [row[:] for row in board]
    steps          = []

    def is_valid(bo, num, pos):
        if any(bo[pos[0]][i] == num and pos[1] != i for i in range(9)): return False
        if any(bo[i][pos[1]] == num and pos[0] != i for i in range(9)): return False
        bx, by = pos[1]//3, pos[0]//3
        return all(bo[by*3+i][bx*3+j] != num or (by*3+i, bx*3+j) == pos
                   for i in range(3) for j in range(3))

    def find_empty(bo):
        return next(((i,j) for i in range(9) for j in range(9) if bo[i][j]==0), None)

    def solve(bo):
        pos = find_empty(bo)
        if not pos: return True
        for n in range(1, 10):
            if is_valid(bo, n, pos):
                bo[pos[0]][pos[1]] = n
                steps.append(([r[:] for r in bo], pos))
                if solve(bo): return True
                bo[pos[0]][pos[1]] = 0
        return False

    return (original_board, steps, len(steps)) if solve(board) else (original_board, None, None)


def solve_maze_with_steps(maze_str):
    grid  = [list(line) for line in maze_str.strip().split('\n')]
    start = next(((r,c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c]=='S'), None)
    end   = next(((r,c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c]=='E'), None)
    if not start or not end:
        return None, None, None

    queue   = collections.deque([(start, [start])])
    visited = set()
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end:
            steps = []
            for step_idx, pos in enumerate(path):
                step_grid = [row[:] for row in grid]
                for pr, pc in path[:step_idx+1]:
                    if step_grid[pr][pc] not in ('S', 'E'):
                        step_grid[pr][pc] = '*'
                steps.append((step_grid, pos))
            return grid, steps, len(path)
        if (r, c) in visited: continue
        visited.add((r, c))
        for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<len(grid) and 0<=nc<len(grid[0]) and grid[nr][nc]!='#' and (nr,nc) not in visited:
                queue.append(((nr,nc), path+[(nr,nc)]))
    return None, None, None


def solve_8_puzzle_with_steps(puzzle_str):
    nums = [int(x) for x in puzzle_str.replace('\n',' ').split() if x.isdigit()]
    if len(nums) != 9: return None, None, None
    start_state = tuple(nums)
    goal_state  = (1,2,3,4,5,6,7,8,0)

    def manhattan(state):
        return sum(abs(i//3 - (v-1)//3) + abs(i%3 - (v-1)%3)
                   for i, v in enumerate(state) if v != 0)

    pq      = [(manhattan(start_state), 0, start_state, [])]
    visited = set()
    while pq:
        _, moves, current, path = heapq.heappop(pq)
        if current == goal_state:
            return list(start_state), moves, path + [current]
        if current in visited: continue
        visited.add(current)
        idx      = current.index(0)
        row, col = idx//3, idx%3
        for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr, nc = row+dr, col+dc
            if 0<=nr<3 and 0<=nc<3:
                new_idx  = nr*3+nc
                lst      = list(current)
                lst[idx], lst[new_idx] = lst[new_idx], lst[idx]
                ns = tuple(lst)
                if ns not in visited:
                    heapq.heappush(pq, (moves+1+manhattan(ns), moves+1, ns, path+[current]))
    return None, None, None

# ── Input UI ──────────────────────────────────────────────────────────────────
if puzzle_type == "Sudoku":
    st.info("📸 Upload an image (JPG/PNG) OR enter text (dots '.' for empty cells)")
    col_img, col_text = st.columns([1, 2])
    puzzle_input = ""
    with col_img:
        st.write("**Upload Image:**")
        uploaded_file = st.file_uploader("Choose an image", type=["jpg","jpeg","png"], key="sudoku_img")
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            with st.spinner("Reading image with OCR..."):
                puzzle_input = extract_text_from_image(image)
                if puzzle_input: st.success("✅ Image processed!")
    with col_text:
        st.write("**Or Enter Text:**")
        default_sudoku = "53..7....\n6..195...\n.98....6.\n8...6...3\n4..8.3..1\n7...2...6\n.6....28.\n...419..5\n....8..79"
        if not puzzle_input:
            puzzle_input = st.text_area("Input", default_sudoku, height=150, key="sudoku_input")
    if puzzle_input:
        col1, col2 = st.columns(2)
        with col1:
            lines  = puzzle_input.strip().split('\n')
            values = [int(c) if c.isdigit() else 0 for line in lines for c in line if c.isdigit() or c=='.']
            if len(values) == 81:
                display_sudoku_board([values[i:i+9] for i in range(0,81,9)], "Input Board")

elif puzzle_type == "Maze":
    st.info("📸 Upload an image of a maze OR enter text (S=start, E=end, #=wall, .=path)")
    col_img, col_text = st.columns([1, 2])
    puzzle_input = ""
    with col_img:
        st.write("**Upload Image:**")
        uploaded_file = st.file_uploader("Choose an image", type=["jpg","jpeg","png"], key="maze_img")
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Maze Image", use_column_width=True)
            with st.spinner("Reading maze from image..."):
                puzzle_input = extract_text_from_image(image)
                if puzzle_input: st.success("✅ Maze image processed!")
    with col_text:
        st.write("**Or Enter Text:**")
        default_maze = "S#...\n.#.#.\n.....\n.#.##\n...E."
        if not puzzle_input:
            puzzle_input = st.text_area("Input", default_maze, height=150, key="maze_input")
    if puzzle_input:
        display_maze_board(puzzle_input, "Input Maze")

elif puzzle_type == "8 Puzzle":
    st.info("📸 Upload an image of a puzzle OR enter text (numbers 0–8, 0=empty)")
    col_img, col_text = st.columns([1, 2])
    puzzle_input = ""
    with col_img:
        st.write("**Upload Image:**")
        uploaded_file = st.file_uploader("Choose an image", type=["jpg","jpeg","png"], key="8puzzle_img")
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Puzzle Image", use_column_width=True)
            with st.spinner("Reading puzzle from image..."):
                puzzle_input = extract_text_from_image(image)
                if puzzle_input: st.success("✅ Puzzle image processed!")
    with col_text:
        st.write("**Or Enter Text:**")
        default_8puz = "1 2 3\n4 5 6\n0 7 8"
        if not puzzle_input:
            puzzle_input = st.text_area("Input", default_8puz, height=150, key="8puzzle_input")
    if puzzle_input:
        try:
            nums = [int(x) for x in puzzle_input.replace('\n',' ').split() if x.isdigit()]
            if len(nums) == 9:
                display_8puzzle_board(nums, "Input Puzzle")
        except: pass

# ── Solve button & results ────────────────────────────────────────────────────
if st.button("Solve", key="solve_btn"):
    with st.spinner("Solving..."):

        if puzzle_type == "Sudoku":
            original, result = solve_sudoku(puzzle_input)
            if result is None:
                st.error("Error: Invalid input or no solution found.")
            else:
                st.success("✨ Sudoku Solved!")
                col1, col2 = st.columns(2)
                with col1: display_sudoku_board(original, "Original")
                with col2: display_sudoku_board(result,   "Solution")

        elif puzzle_type == "Maze":
            original, steps, path_length = solve_maze_with_steps(puzzle_input)
            if steps is None:
                st.error("Error: Invalid maze or no solution found.")
            else:
                st.success(f"✨ Maze Solved in {path_length} steps!")
                final_grid = original
                for step_grid, _ in steps: final_grid = step_grid
                display_maze_board("\n".join("".join(r) for r in final_grid), "Complete Solution")

                st.subheader("📍 Step-by-Step Solution")
                tab1, tab2 = st.tabs(["Animated View", "Manual Steps"])
                with tab1:
                    speed = st.slider("Animation Speed", 0.1, 1.0, 0.5, 0.1)
                    if st.button("Play Animation"):
                        import time
                        pb = st.progress(0)
                        for idx, (step_grid, pos) in enumerate(steps):
                            st.markdown(f"<div class='step-counter'>Step {idx+1} / {len(steps)}</div>", unsafe_allow_html=True)
                            display_maze_board("\n".join("".join(r) for r in step_grid), f"Position: {pos}")
                            pb.progress((idx+1)/len(steps))
                            time.sleep(2.0 - speed*2)
                with tab2:
                    sel = st.slider("Select Step", 0, len(steps)-1, 0)
                    step_grid, pos = steps[sel]
                    st.markdown(f"<div class='step-counter'>Step {sel+1} / {len(steps)} — Position: {pos}</div>", unsafe_allow_html=True)
                    display_maze_board("\n".join("".join(r) for r in step_grid), "Maze State")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Current Step", sel+1)
                    c2.metric("Total Steps",  len(steps))
                    c3.metric("Progress",     f"{(sel+1)/len(steps)*100:.1f}%")

        elif puzzle_type == "8 Puzzle":
            start, moves, path = solve_8_puzzle_with_steps(puzzle_input)
            if start is None:
                st.error("Error: Invalid input or no solution found.")
            else:
                st.success(f"✨ 8 Puzzle Solved in {moves} moves!")
                col1, col2 = st.columns(2)
                with col1: display_8puzzle_board(start,          "Starting State")
                with col2: display_8puzzle_board(list(path[-1]), "Final State")

                st.subheader("📍 Step-by-Step Solution")
                tab1, tab2 = st.tabs(["Animated View", "Manual Steps"])
                with tab1:
                    speed = st.slider("Animation Speed", 0.1, 1.0, 0.5, 0.1, key="8puzzle_speed")
                    if st.button("Play Animation", key="8puzzle_play"):
                        import time
                        pb = st.progress(0)
                        for idx, state in enumerate(path):
                            st.markdown(f"<div class='step-counter'>Move {idx} / {len(path)-1}</div>", unsafe_allow_html=True)
                            display_8puzzle_board(list(state))
                            pb.progress((idx+1)/len(path))
                            time.sleep(2.0 - speed*2)
                with tab2:
                    sel = st.slider("Select Move", 0, len(path)-1, 0, key="8puzzle_step")
                    st.markdown(f"<div class='step-counter'>Move {sel} / {len(path)-1}</div>", unsafe_allow_html=True)
                    display_8puzzle_board(list(path[sel]))
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Current Move", sel)
                    c2.metric("Total Moves",  len(path)-1)
                    c3.metric("Progress",     f"{(sel+1)/len(path)*100:.1f}%")