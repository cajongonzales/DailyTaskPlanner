# src/daily_task_planner/view/tasks_pane.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTabWidget,
    QPushButton, QLineEdit, QTextEdit, QMenu, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from daily_task_planner.view.deliverables_list import DeliverablesList


class TaskTab(QWidget):
    """A single task tab UI (title, story, deliverables, notes)."""
    title_changed = Signal(str)
    user_story_changed = Signal(str)
    deliverable_added = Signal(str)
    deliverable_changed = Signal(int, str)
    deliverable_checked = Signal(int, bool)
    deliverable_deleted = Signal(int)
    deliverables_reordered = Signal(int, list)
    notes_changed = Signal(str)

    def __init__(self, task_data, task_index=None):
        super().__init__()
        layout = QVBoxLayout(self)
        self._task_index = task_index
        self._editing_index = None

        # --- Title ---
        self.title_box = QLineEdit(task_data.title)
        self.title_box.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title_box)

        # --- User Story ---
        story_group = QGroupBox("User Story")
        story_layout = QVBoxLayout()
        self.story_text = QTextEdit(task_data.user_story)
        story_layout.addWidget(self.story_text)
        story_group.setLayout(story_layout)
        layout.addWidget(story_group)

        # --- Deliverables ---
        deliverables_group = QGroupBox("Deliverables")
        deliverables_layout = QVBoxLayout()

        self.deliverables_list = DeliverablesList(task_index=self._task_index)
        self.deliverables_list.reordered.connect(self.deliverables_reordered)

        self.deliverable_input = QLineEdit()
        self.deliverable_input.setPlaceholderText("Add a new deliverable and press Enter")

        deliverables_layout.addWidget(self.deliverables_list)
        deliverables_layout.addWidget(self.deliverable_input)
        deliverables_group.setLayout(deliverables_layout)
        layout.addWidget(deliverables_group)

        # --- Notes ---
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout()
        self.notes_text = QTextEdit(task_data.notes)
        notes_layout.addWidget(self.notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        layout.addStretch()

        # Connect signals
        self.title_box.textChanged.connect(self.title_changed)
        self.story_text.textChanged.connect(lambda: self.user_story_changed.emit(self.story_text.toPlainText()))
        self.notes_text.textChanged.connect(lambda: self.notes_changed.emit(self.notes_text.toPlainText()))
        self.deliverable_input.returnPressed.connect(self._on_add_deliverable)

        self.deliverables_list.itemChanged.connect(self._on_deliverable_checked)
        self.deliverables_list.itemDoubleClicked.connect(self._on_edit_deliverable)
        self.deliverables_list.itemChanged.connect(self._on_deliverable_changed)
        self.deliverables_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.deliverables_list.customContextMenuRequested.connect(self._on_deliverable_context_menu)

        self.populate_deliverables(task_data.deliverables)

    def populate_deliverables(self, deliverables):
        self.deliverables_list.populate(deliverables)

    def _on_add_deliverable(self):
        text = self.deliverable_input.text().strip()
        if text:
            self.deliverable_added.emit(text)
            self.deliverable_input.clear()

    def _on_deliverable_checked(self, item):
        idx = self.deliverables_list.row(item)
        checked = item.checkState() == Qt.Checked
        self.deliverable_checked.emit(idx, checked)

    def _on_edit_deliverable(self, item):
        self._editing_index = self.deliverables_list.row(item)
        self.deliverables_list.editItem(item)

    def _on_deliverable_changed(self, item):
        idx = self.deliverables_list.row(item)
        if idx == self._editing_index:
            self.deliverable_changed.emit(idx, item.text())
            self._editing_index = None

    def _on_deliverable_context_menu(self, pos):
        item = self.deliverables_list.itemAt(pos)
        if item is None:
            return
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.deliverables_list.mapToGlobal(pos))
        if action == delete_action:
            index = self.deliverables_list.row(item)
            self.deliverable_deleted.emit(index)


class TasksPane(QWidget):
    """Container for multiple TaskTabs as tabs."""
    add_task_requested = Signal()
    remove_task_requested = Signal(int)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.South)
        layout.addWidget(self.tabs)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.remove_button = QPushButton("Remove Task")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        self.add_button.clicked.connect(lambda: self.add_task_requested.emit())
        self.remove_button.clicked.connect(self._on_remove_clicked)

    def add_task_tab(self, task_data, index=None):
        tab = TaskTab(task_data, task_index=index)
        idx = self.tabs.addTab(tab, task_data.title)
        self.tabs.setCurrentIndex(idx)
        tab.title_changed.connect(lambda new_title, t=tab: self._on_tab_title_changed(t, new_title))
        return tab

    def remove_task_tab(self, index):
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def update_tab_titles(self, tasks):
        for i, task in enumerate(tasks):
            self.tabs.setTabText(i, task.title)

    def _on_remove_clicked(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self.remove_task_requested.emit(idx)
        
    def _on_tab_title_changed(self, tab, new_title):
        index = self.tabs.indexOf(tab)
        if index != -1:
            self.tabs.setTabText(index, new_title)