# src/planner/main.py
from PySide6.QtWidgets import QApplication
import sys

from daily_task_planner.model.task_model import TaskModel, TasksModel
from daily_task_planner.view.today_pane import TodayPane
from daily_task_planner.view.tasks_pane import TasksPane
from daily_task_planner.presenter.today_presenter import TodayPresenter
from daily_task_planner.presenter.tasks_presenter import TasksPresenter
from daily_task_planner.view.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    today_model = TaskModel()
    today_model.load()
    today_view = TodayPane()
    today_presenter = TodayPresenter(today_view, today_model)

    tasks_model = TasksModel()
    tasks_view = TasksPane()
    tasks_presenter = TasksPresenter(tasks_view, tasks_model)

    window = MainWindow(today_presenter, tasks_presenter)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
