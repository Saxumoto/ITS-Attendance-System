import os

# --- PATHS ---
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
DB_PATH = os.path.join(DATA_DIR, "StudentDatabase.db")

# Ensure required directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# --- UI CONFIGURATION ---
APP_TITLE = "ITS Command Center"
THEME_COLOR = "#E0A638"  # Gold color for ITS
DEFAULT_APPEARANCE = "Light"
DEFAULT_COLOR_THEME = "blue"

# --- SCANNED AUDIO CONFIG ---
SUCCESS_FREQ = 1000  # Hz
SUCCESS_DURATION = 200  # ms
ERROR_FREQ = 400  # Hz
ERROR_DURATION = 500  # ms
