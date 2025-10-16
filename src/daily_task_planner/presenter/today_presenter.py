# src/planner/presenter/today_presenter.py
from daily_task_planner.model.task_model import TaskModel


class TodayPresenter:
    def __init__(self, view, model: TaskModel):
        self.view = view
        self.model = model

        # Connect signals
        view.task_added.connect(self.add_task)
        view.task_checked.connect(self.set_task_complete)
        view.meeting_added.connect(self.add_meeting)
        view.notes_changed.connect(self.update_notes)

        # Initial render
        self.refresh_view()

    def add_task(self, description: str):
        self.model.add_task(description)
        self.refresh_view()

    def set_task_complete(self, index: int, complete: bool):
        self.model.set_task_complete(index, complete)
        self.refresh_view()

    def add_meeting(self, time: str, desc: str):
        self.model.add_meeting(time, desc)
        self.refresh_view()

    def update_notes(self, text: str):
        self.model.set_notes(text)

    def refresh_view(self):
        self.view.update_task_list(self.model.data.tasks)
        self.view.update_meetings(self.model.data.meetings)
        self.view.update_notes(self.model.data.notes)
