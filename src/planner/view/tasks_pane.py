# src/planner/view/tasks_pane.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTextEdit, QGroupBox, QVBoxLayout,
    QTabWidget, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QCheckBox
)
from PySide6.QtCore import Qt, Signal


class TaskTab(QWidget):
    """A single task tab UI (title, story, deliverables, notes)."""
    # Signals remain the same
    title_changed = Signal(str)
    user_story_changed = Signal(str)
    deliverable_added = Signal(str)
    deliverable_checked = Signal(int, bool)
    notes_changed = Signal(str)

    def __init__(self, task_data):
        super().__init__()
        layout = QVBoxLayout(self)

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
        self.deliverables_list = QListWidget()
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
        self.notes_text.setPlaceholderText("• Write notes here...")
        notes_layout.addWidget(self.notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        layout.addStretch()

        # Connect UI events
        self.title_box.textChanged.connect(self.title_changed)
        self.story_text.textChanged.connect(lambda: self.user_story_changed.emit(self.story_text.toPlainText()))
        self.deliverable_input.returnPressed.connect(self._on_add_deliverable)
        self.notes_text.textChanged.connect(lambda: self.notes_changed.emit(self.notes_text.toPlainText()))

        # Populate deliverables from loaded data
        self.populate_deliverables(task_data.deliverables)

    def populate_deliverables(self, deliverables):
        # Prevent signals from firing while populating
        self.deliverables_list.blockSignals(True)
        self.deliverables_list.clear()
        for d in deliverables:
            item = QListWidgetItem(d.description)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if d.complete else Qt.Unchecked)
            self.deliverables_list.addItem(item)
        self.deliverables_list.blockSignals(False)

        # Connect checkboxes
        self.deliverables_list.itemChanged.connect(self._on_deliverable_checked)

    def _on_add_deliverable(self):
        text = self.deliverable_input.text().strip()
        if text:
            self.deliverable_added.emit(text)
            self.deliverable_input.clear()

    def _on_deliverable_checked(self, item):
        idx = self.deliverables_list.row(item)
        checked = item.checkState() == Qt.Checked
        self.deliverable_checked.emit(idx, checked)

class TasksPane(QWidget):
    add_task_requested = Signal()
    remove_task_requested = Signal(int)
    # Forward sub-signals from active tab via presenter

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Tab widget with tabs at the bottom
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.South)
        layout.addWidget(self.tabs)

        # Buttons row
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.remove_button = QPushButton("Remove Task")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        self.add_button.clicked.connect(lambda: self.add_task_requested.emit())
        self.remove_button.clicked.connect(self._on_remove_clicked)

    def _on_remove_clicked(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self.remove_task_requested.emit(idx)

    def add_task_tab(self, task_data, index=None):
        tab = TaskTab(task_data)
        tab.populate_deliverables(task_data.deliverables)
        idx = self.tabs.addTab(tab, task_data.title)
        self.tabs.setCurrentIndex(idx)
        return tab

    def remove_task_tab(self, index):
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def update_tab_titles(self, tasks):
        for i, task in enumerate(tasks):
            self.tabs.setTabText(i, task.title)

