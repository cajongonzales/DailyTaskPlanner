# src/planner/presenter/today_presenter.py
from daily_task_planner.model.task_model import UnifiedModel


class TodayPresenter:
    def __init__(self, view, model: UnifiedModel):
        self.view = view
        self.model = model

        # Connect signals
        view.task_added.connect(self.add_task)
        view.task_changed.connect(self.edit_task)
        view.task_checked.connect(self.set_task_complete)
        view.task_reordered.connect(self.reorder_tasks)
        view.task_deleted.connect(self.delete_task)

        view.meeting_added.connect(self.add_meeting)
        view.meeting_removed.connect(self.remove_meeting)
        view.notes_changed.connect(self.update_notes)

        # Initial render
        self.refresh_view()

    # --- TODAY Tasks ---
    def add_task(self, description: str):
        self.model.add_today_task(description)
        self.refresh_view()

    def edit_task(self, index: int, new_text: str):
        if 0 <= index < len(self.model.today.tasks):
            self.model.today.tasks[index].description = new_text
            self.model.save()
            self.refresh_view()

    def set_task_complete(self, index: int, complete: bool):
        self.model.set_today_task_complete(index, complete)
        self.refresh_view()

    def reorder_tasks(self, old_index: int, new_index: int):    
        tasks = self.model.today.tasks
        if 0 <= old_index < len(tasks) and 0 <= new_index < len(tasks):
            task = tasks.pop(old_index)
            tasks.insert(new_index, task)
            self.model.save()
            self.refresh_view()

    def delete_task(self, index: int):
        self.model.remove_today_task(index)
        self.refresh_view()

    # --- Meetings ---
    def add_meeting(self, time: str, desc: str):
        self.model.add_meeting(time, desc)
        self.refresh_view()

    def remove_meeting(self, index: int):
        self.model.remove_meeting(index)
        self.refresh_view()

    # --- Notes ---
    def update_notes(self, text: str):
        self.model.set_today_notes(text)
        self.refresh_view()

    # --- Refresh ---
    def refresh_view(self):
        self.view.update_task_list(self.model.today.tasks)
        self.view.update_meetings(self.model.today.meetings)
        self.view.update_notes(self.model.today.notes)
