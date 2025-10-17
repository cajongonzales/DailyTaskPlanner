from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
import json
from pathlib import Path

class MainWindow(QMainWindow):
    STORAGE_PATH = Path.home() / ".daily_task_planner_window.json"

    def __init__(self, today_presenter, tasks_presenter):
        super().__init__()
        self.setWindowTitle("Daily Task Planner")
        self.resize(1200, 700)
        self._load_window_state()

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(today_presenter.view, 1)
        layout.addWidget(tasks_presenter.view, 2)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        self._save_window_state()
        # Save the meetings table widths as well
        if hasattr(self.centralWidget().layout().itemAt(0).widget(), "save_meetings_table_state"):
            self.centralWidget().layout().itemAt(0).widget().save_meetings_table_state()
        super().closeEvent(event)

    def _save_window_state(self):
        payload = {"width": self.width(), "height": self.height()}
        try:
            with open(self.STORAGE_PATH, "w") as f:
                json.dump(payload, f)
        except Exception as e:
            print(f"[WARN] Could not save window size: {e}")

    def _load_window_state(self):
        if self.STORAGE_PATH.exists():
            try:
                with open(self.STORAGE_PATH, "r") as f:
                    payload = json.load(f)
                    self.resize(payload.get("width", 1200), payload.get("height", 700))
            except Exception as e:
                print(f"[WARN] Could not load window size: {e}")
