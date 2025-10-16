# src/planner/view/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from planner.view.today_pane import TodayPane
from planner.view.tasks_pane import TasksPane


class MainWindow(QMainWindow):
    def __init__(self, today_presenter, tasks_presenter):
        super().__init__()
        self.setWindowTitle("Daily Task Planner")
        self.resize(1200, 700)

        container = QWidget()
        layout = QHBoxLayout(container)

        layout.addWidget(today_presenter.view, 1)
        layout.addWidget(tasks_presenter.view, 2)

        self.setCentralWidget(container)
