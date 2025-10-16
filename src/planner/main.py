# src/planner/main.py
from PySide6.QtWidgets import QApplication
import sys

from planner.model.task_model import TaskModel, TasksModel
from planner.view.today_pane import TodayPane
from planner.view.tasks_pane import TasksPane
from planner.presenter.today_presenter import TodayPresenter
from planner.presenter.tasks_presenter import TasksPresenter
from planner.view.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    today_model = TaskModel()
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
