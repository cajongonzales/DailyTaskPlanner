# src/planner/presenter/today_presenter.py
from daily_task_planner.model.task_model import TaskModel


class TodayPresenter:
    def __init__(self, view, model: TaskModel):
        self.view = view
        self.model = model

        # --- Connect view signals ---
        view.task_added.connect(self._on_task_added)
        view.task_changed.connect(self._on_task_changed)
        view.task_checked.connect(self._on_task_checked)
        view.task_reordered.connect(self._on_task_reordered)
        view.task_deleted.connect(self._on_task_deleted)

        view.meeting_added.connect(self._on_meeting_added)
        view.meeting_removed.connect(self._on_meeting_removed)
        view.notes_changed.connect(self._on_notes_changed)

        # Initial load
        self.refresh_view()

    # === TASK HANDLERS ===
    def _on_task_added(self, description: str):
        """Add a new task and refresh."""
        self.model.add_task(description)
        self.model.save()
        self.refresh_view()

    def _on_task_changed(self, index: int, text: str):
        """Update task text after editing."""
        self.model.update_task_description(index, text)
        self.model.save()
        self.refresh_view()

    def _on_task_checked(self, index: int, complete: bool):
        """Update completion state."""
        # Defensive: avoid crash from async checkbox race
        if 0 <= index < len(self.model.data.tasks):
            self.model.set_task_complete(index, complete)
            self.model.save()
            # No full refresh; only update checkboxes
            self.view.update_task_list(self.model.data.tasks)

    def _on_task_reordered(self, old_index: int, new_index: int):
        """Persist reordered tasks."""
        self.model.move_task(old_index, new_index)
        self.model.save()
        self.view.update_task_list(self.model.data.tasks)

    def _on_task_deleted(self, index: int):
        """Handle right-click delete."""
        if 0 <= index < len(self.model.data.tasks):
            self.model.remove_task(index)
            self.model.save()
            self.view.update_task_list(self.model.data.tasks)

    # === MEETING HANDLERS ===
    def _on_meeting_added(self, time: str, desc: str):
        self.model.add_meeting(time, desc)
        self.model.save()
        self.view.update_meetings(self.model.data.meetings)

    def _on_meeting_removed(self, index: int):
        self.model.remove_meeting(index)
        self.model.save()
        self.view.update_meetings(self.model.data.meetings)

    # === NOTES HANDLER ===
    def _on_notes_changed(self, text: str):
        self.model.set_notes(text)
        self.model.save()

    # === REFRESH ===
    def refresh_view(self):
        """Rebuild the entire view from model data."""
        self.view.update_task_list(self.model.data.tasks)
        self.view.update_meetings(self.model.data.meetings)
        self.view.update_notes(self.model.data.notes)
