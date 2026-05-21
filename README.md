# AI Puzzle Solver 🧩

A Streamlit-based puzzle solving app that can read puzzles from text input or from uploaded images using OCR, then solve them step by step with a polished visual interface.

## Features

- **Sudoku Solver**
  - Accepts a 9×9 grid as text input
  - Supports image upload with OCR extraction
  - Shows the original board and the solved board

- **Maze Solver**
  - Accepts maze input using:
    - `S` = start
    - `E` = end
    - `#` = wall
    - `.` = open path
  - Uses BFS to find a path
  - Displays step-by-step path visualization

- **8 Puzzle Solver**
  - Accepts a 3×3 puzzle with `0` as the blank tile
  - Uses A* search with Manhattan distance
  - Shows the solution path and move-by-move animation

- **OCR Input**
  - Image preprocessing improves OCR accuracy before reading the puzzle text
  - Uses `pytesseract` and Pillow for image handling

- **Modern UI**
  - Custom CSS styling
  - Animated background
  - Card-style puzzle boards and step counters

## Tech Stack

- **Python**
- **Streamlit**
- **Pillow**
- **pytesseract**
- **NumPy**
- **collections / heapq** for search algorithms

## Project Structure

```text
.
├── app.py
├── README.md
├── package.json / server files (if used in your setup)
└── requirements / pyproject config
```

## Requirements

- Python 3.11+
- Streamlit
- Pillow
- pytesseract
- NumPy
- Tesseract OCR installed on your system

> Note: `pytesseract` is only the Python wrapper. The Tesseract engine must be installed separately.

## Installation

```bash
git clone <your-repo-url>
cd <your-project-folder>
pip install -r requirements.txt
```

If you are using the provided project config, install the Python dependencies from the environment or add them manually.

### Install Tesseract OCR

Make sure Tesseract is installed on your machine:

- **Windows:** install from the official Tesseract installer
- **macOS:** `brew install tesseract`
- **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`

## Running the App

Start the Streamlit app with:

```bash
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

If you are using the Node wrapper shown in your project, you can also run the launcher script that starts Streamlit for you.

## How to Use

### Sudoku
1. Choose **Sudoku** from the dropdown.
2. Upload a Sudoku image or paste the board as text.
3. Use dots `.` for empty cells.
4. Click **Solve**.

### Maze
1. Choose **Maze**.
2. Upload a maze image or paste the maze as text.
3. Use:
   - `S` for start
   - `E` for end
   - `#` for walls
   - `.` for paths
4. Click **Solve** to view the solution and step-by-step route.

### 8 Puzzle
1. Choose **8 Puzzle**.
2. Upload a puzzle image or enter the tiles as text.
3. Use `0` for the empty space.
4. Click **Solve** to see the sequence of moves.

## Notes

- Sudoku solving uses backtracking.
- Maze solving uses breadth-first search.
- 8 Puzzle solving uses A* search.
- The interface includes animated step views and manual step sliders for better understanding.

## Troubleshooting

- If OCR does not work, check that Tesseract is installed and available in your PATH.
- If the app fails to start, verify that Streamlit and all Python packages are installed.
- For image inputs, clearer images with higher contrast usually give better OCR results.

## License

Add your preferred license here.

Contribution by Lakshmi E.
Contribution by Nagaveni H S.
