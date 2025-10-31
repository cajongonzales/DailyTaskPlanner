# src/planner/presenter/tasks_presenter.py
from daily_task_planner.model.task_model import UnifiedModel, Deliverable


class TasksPresenter:
    def __init__(self, view, model: UnifiedModel):
        self.view = view
        self.model = model

        # Connect signals from view
        view.add_task_requested.connect(self.add_task)
        view.remove_task_requested.connect(self.remove_task)

        # Map task tab signals
        self._connect_existing_tabs()

    # --- Tasks ---
    def add_task(self):
        self.model.add_task()
        index = len(self.model.tasks) - 1
        tab = self.view.add_task_tab(self.model.tasks[index], index)
        self._connect_tab_signals(tab, index)

    def remove_task(self, index: int):
        self.model.remove_task(index)
        self.view.remove_task_tab(index)

    # --- Helpers ---
    def _connect_existing_tabs(self):
        for i, task in enumerate(self.model.tasks):
            tab = self.view.add_task_tab(task, i)
            self._connect_tab_signals(tab, i)

    def _connect_tab_signals(self, tab, index):
        tab._task_index = index  
        tab.title_changed.connect(lambda text: self.update_title(index, text))
        tab.user_story_changed.connect(lambda story: self.update_user_story(index, story))
        tab.deliverable_added.connect(lambda desc: self.add_deliverable(index, desc))
        tab.deliverable_checked.connect(lambda di, c: self.set_deliverable_complete(index, di, c))
        tab.notes_changed.connect(lambda notes: self.update_notes(index, notes))
        tab.deliverables_reordered.connect(lambda task_index, order: self.reorder_deliverables(task_index, order))
        tab.deliverable_deleted.connect(lambda di: self.remove_deliverable(index, di))

    # --- Task updates ---
    def update_title(self, index, title):
        self.model.update_task_title(index, title)

    def update_user_story(self, index, story):
        self.model.update_task_story(index, story)

    def update_notes(self, index, notes):
        self.model.update_task_notes(index, notes)

    # --- Deliverables ---
    def add_deliverable(self, task_index, desc):
        self.model.add_deliverable(task_index, desc)
        tab = self.view.tabs.widget(task_index)
        tab.populate_deliverables(self.model.tasks[task_index].deliverables)

    def set_deliverable_complete(self, task_index, deliverable_index, complete):
        self.model.set_deliverable_complete(task_index, deliverable_index, complete)

    def reorder_deliverables(self, task_index, new_order):
        self.model.reorder_deliverables(task_index, new_order)
        tab = self.view.tabs.widget(task_index)
        tab.populate_deliverables(self.model.tasks[task_index].deliverables)

    def remove_deliverable(self, task_index, deliverable_index):
        self.model.remove_deliverable(task_index, deliverable_index)
        tab = self.view.tabs.widget(task_index)
        tab.populate_deliverables(self.model.tasks[task_index].deliverables)
