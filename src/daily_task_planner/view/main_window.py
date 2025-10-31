from PySide6.QtWidgets import QMainWindow, QSplitter 
from PySide6.QtCore import Qt, QEvent, QTimer 
import json 
from pathlib import Path

class MainWindow(QMainWindow):
    STORAGE_PATH = Path.home() / ".daily_task_planner_window.json"

    def __init__(self, today_presenter, tasks_presenter):
        super().__init__()
        self.setWindowTitle("Daily Task Planner")

        # --- Splitter setup ---
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(today_presenter.view)
        self.splitter.addWidget(tasks_presenter.view)
        self.setCentralWidget(self.splitter)

        # --- Connect signals ---
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
        self._cached_splitter_sizes = []

        # --- Load window state ---
        self._load_window_state()

        # Ensure initial splitter sizes are applied after show
        QTimer.singleShot(0, self._apply_splitter_sizes)

    # Apply cached splitter sizes
    def _apply_splitter_sizes(self):
        if self._cached_splitter_sizes:
            self.splitter.setSizes(self._cached_splitter_sizes)

    # Splitter moved
    def _on_splitter_moved(self, pos, index):
        self._cached_splitter_sizes = self.splitter.sizes()
        self._save_window_state()

    # Close event
    def closeEvent(self, event):
        self._cached_splitter_sizes = self.splitter.sizes()
        self._save_window_state()
        super().closeEvent(event)

    # Persistence
    def _save_window_state(self):
        payload = {
            "width": self.width(),
            "height": self.height(),
            "splitter_sizes": self._cached_splitter_sizes or [self.splitter.width()//3, 2*self.splitter.width()//3],
        }
        try:
            with open(self.STORAGE_PATH, "w") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"[WARN] Could not save window state: {e}")

    def _load_window_state(self):
        if not self.STORAGE_PATH.exists():
            return
        try:
            with open(self.STORAGE_PATH, "r") as f:
                payload = json.load(f)
            self.resize(payload.get("width", 1200), payload.get("height", 700))
            self._cached_splitter_sizes = payload.get("splitter_sizes", [])
        except Exception as e:
            print(f"[WARN] Could not load window state: {e}")
