# 🎮 PyArcade Studio

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-PyTest%20%7C%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

A modular, desktop-based game collection and interactive story engine built with **Python 3**, **PyQt5**, and **Minimax AI**. Designed with clean architecture, strict typing, and high test coverage.

---

## ✨ Features

- **🤖 Tic-Tac-Toe with Minimax AI** — Unbeatable AI opponent with Alpha-Beta pruning across 3 difficulty levels.
- **📜 Branching Text Adventure Engine** — Interactive story system driven by custom JSON schemas with inventory & decision nodes.
- **🔤 Multilingual Hangman** — Support for English, French, Spanish, and Persian word lists.
- **🔀 Word Scramble & Number Guessing** — Classic mental agility mini-games.
- **🎨 Modern Dark UI** — Custom Catppuccin-inspired QSS dark theme built with PyQt5.
- **📊 Persistence & Analytics** — Local JSON-backed statistics and win/loss tracking.

---

## 🏗️ Architecture & Project Structure

The project strictly follows Separation of Concerns (SoC) and Object-Oriented principles:

```
.
├── data/              # Game resources (story JSONs, multilingual word lists)
├── src/
│   ├── ai/            # Minimax algorithm & decision trees
│   ├── core/          # Game logic decoupled from UI
│   ├── models/        # Dataclasses & type definitions
│   ├── ui/            # PyQt5 UI components & custom QSS styles
│   └── utils/         # Persistence & statistics tracking
├── tests/             # Unit and integration tests (PyTest)
└── main.py            # Application entry point
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher

### Installation & Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/PyArcadeStudio.git
   cd PyArcadeStudio
   ```

2. **Set up virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 🧪 Testing

Run unit and integration tests with coverage report:

```bash
pytest --cov=src tests/
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more details.
