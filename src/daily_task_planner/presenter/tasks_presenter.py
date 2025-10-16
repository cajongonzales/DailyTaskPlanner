# src/planner/presenter/tasks_presenter.py
from daily_task_planner.model.task_model import TasksModel


class TasksPresenter:
    def __init__(self, view, model: TasksModel):
        self.view = view
        self.model = model

        view.add_task_requested.connect(self.add_task)
        view.remove_task_requested.connect(self.remove_task)
        
        for index, task in enumerate(self.model.tasks):
            tab = self.view.add_task_tab(task, index)
            self._connect_tab_signals(tab, index)

    def add_task(self):
        self.model.add_task()
        index = len(self.model.tasks) - 1
        task = self.model.tasks[index]
        tab = self.view.add_task_tab(task, index)
        self._connect_tab_signals(tab, index)

    def remove_task(self, index):
        self.model.remove_task(index)
        self.view.remove_task_tab(index)

    def _connect_tab_signals(self, tab, index):
        tab.title_changed.connect(lambda text: self._update_title(index, text))
        tab.user_story_changed.connect(lambda story: self._update_user_story(index, story))
        tab.deliverable_added.connect(lambda desc: self._add_deliverable(index, desc))
        tab.deliverable_checked.connect(lambda di, c: self._set_deliverable_complete(index, di, c))
        tab.notes_changed.connect(lambda notes: self._update_notes(index, notes))

    def _update_title(self, index, title):
        self.model.update_title(index, title)
        self.view.update_tab_titles(self.model.tasks)

    def _update_user_story(self, index, story):
        self.model.update_user_story(index, story)

    def _add_deliverable(self, index, desc):
        self.model.add_deliverable(index, desc)
        tab = self.view.tabs.widget(index)
        tab.populate_deliverables(self.model.tasks[index].deliverables)

    def _set_deliverable_complete(self, index, deliverable_index, complete):
        self.model.set_deliverable_complete(index, deliverable_index, complete)

    def _update_notes(self, index, notes):
        self.model.update_notes(index, notes)
