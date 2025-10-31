import sys
from PySide6.QtWidgets import QApplication
from daily_task_planner.view.main_window import MainWindow
from daily_task_planner.presenter.today_presenter import TodayPresenter
from daily_task_planner.presenter.tasks_presenter import TasksPresenter
from daily_task_planner.view.tasks_pane import TasksPane
from daily_task_planner.view.today_pane import TodayPane
from daily_task_planner.model.task_model import UnifiedModel


def main():
    """Entry point for the Daily Task Planner application."""
    app = QApplication(sys.argv)

    model = UnifiedModel()
    today_pane = TodayPane(model.today.tasks)
    tasks_pane = TasksPane()

    today_presenter = TodayPresenter(today_pane, model)
    tasks_presenter = TasksPresenter(tasks_pane, model)

    window = MainWindow(today_presenter, tasks_presenter)
    window.show()

    # --- Run the app ---
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
