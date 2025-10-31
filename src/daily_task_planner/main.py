# src/daily_task_planner/main.py
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter
from daily_task_planner.view.today_pane import TodayPane
from daily_task_planner.view.tasks_pane import TasksPane
from daily_task_planner.presenter.today_presenter import TodayPresenter
from daily_task_planner.presenter.tasks_presenter import TasksPresenter
from daily_task_planner.model.task_model import UnifiedModel
import sys

def main():
    app = QApplication(sys.argv)

    # --- Unified model ---
    model = UnifiedModel()

    # --- Views ---
    today_view = TodayPane(model.today.tasks)
    tasks_view = TasksPane()

    # --- Presenters ---
    today_presenter = TodayPresenter(today_view, model)
    tasks_presenter = TasksPresenter(tasks_view, model)

    # --- Main window ---
    window = QMainWindow()
    splitter = QSplitter()
    splitter.addWidget(today_view)
    splitter.addWidget(tasks_view)
    window.setCentralWidget(splitter)
    window.resize(1200, 700)
    window.show()

    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
