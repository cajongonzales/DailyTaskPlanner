from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QMenu, QTextEdit, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, Signal
import json
from pathlib import Path


class TodayPane(QWidget):
    # Signals for Presenter
    task_added = Signal(str)
    task_changed = Signal(int, str)
    task_checked = Signal(int, bool)
    task_reordered = Signal(int, int)  # emits list of (description, checked)
    task_deleted = Signal(int)
    meeting_added = Signal(str, str)
    meeting_removed = Signal(int)
    notes_changed = Signal(str)

    STORAGE_PATH = Path.home() / ".daily_task_planner_meetings.json"

    def __init__(self, tasks):
        super().__init__()
        layout = QVBoxLayout(self)

        # --- Tasks ---
        tasks_group = QGroupBox("Tasks For Today")
        tasks_layout = QVBoxLayout()

        self.task_list = QListWidget()
        self.task_list.setDragDropMode(QListWidget.InternalMove)
        self.task_list.setDefaultDropAction(Qt.MoveAction)
        self.task_list.setSelectionMode(QListWidget.SingleSelection)
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self._on_task_context_menu)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a new task and press Enter")

        tasks_layout.addWidget(self.task_list)
        tasks_layout.addWidget(self.task_input)
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)

        # --- Meetings ---
        meetings_group = QGroupBox("Meetings")
        meetings_layout = QVBoxLayout()
        self.meetings_table = QTableWidget(0, 2)
        self.meetings_table.setHorizontalHeaderLabels(["Time", "Description"])
        self.meetings_table.setSortingEnabled(True)
        meetings_layout.addWidget(self.meetings_table)

        input_layout = QHBoxLayout()
        self.meeting_time_input = QLineEdit()
        self.meeting_time_input.setPlaceholderText("e.g. 10:30 AM")
        self.meeting_desc_input = QLineEdit()
        self.meeting_desc_input.setPlaceholderText("Meeting description")
        input_layout.addWidget(self.meeting_time_input, 1)
        input_layout.addWidget(self.meeting_desc_input, 2)
        meetings_layout.addLayout(input_layout)

        button_layout = QHBoxLayout()
        self.add_meeting_button = QPushButton("Add Meeting")
        self.remove_meeting_button = QPushButton("Remove Meeting")
        button_layout.addWidget(self.add_meeting_button)
        button_layout.addWidget(self.remove_meeting_button)
        meetings_layout.addLayout(button_layout)

        meetings_group.setLayout(meetings_layout)
        layout.addWidget(meetings_group)

        # --- Notes ---
        notes_group = QGroupBox("General Notes")
        notes_layout = QVBoxLayout()
        self.notes_text = QTextEdit()
        notes_layout.addWidget(self.notes_text)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        layout.addStretch()

        # --- Signals ---
        self.task_input.returnPressed.connect(self._on_task_entered)
        self.task_list.itemDoubleClicked.connect(self._on_edit_task)
        self.task_list.itemChanged.connect(self._on_task_changed)
        self.task_list.model().rowsMoved.connect(self._on_rows_moved)
        self.add_meeting_button.clicked.connect(self._on_meeting_added)
        self.remove_meeting_button.clicked.connect(self._on_remove_meeting_clicked)
        self.notes_text.textChanged.connect(self._on_notes_changed)

        # Internal tracking
        self._editing_index = None

        # Populate tasks initially
        self._populate_tasks(tasks)

    # === Tasks ===
    def _populate_tasks(self, tasks):
        self.task_list.blockSignals(True)
        self.task_list.clear()
        for task in tasks:
            item = QListWidgetItem(task.description)
            item.setFlags(
                item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled
            )
            item.setCheckState(Qt.Checked if task.complete else Qt.Unchecked)
            self.task_list.addItem(item)
        self.task_list.blockSignals(False)

    def _on_task_entered(self):
        text = self.task_input.text().strip()
        if text:
            self.task_added.emit(text)
            self.task_input.clear()

    def _on_task_checked(self, item):
        try:
            index = self.task_list.row(item)
            if index < 0 or index >= self.task_list.count():
                return
            checked = item.checkState() == Qt.Checked
            self.task_checked.emit(index, checked)
        except RuntimeError:
            return

    def _on_edit_task(self, item):
        self._editing_index = self.task_list.row(item)
        self.task_list.editItem(item)

    def _on_task_changed(self, item: QListWidgetItem):
        idx = self.task_list.row(item)
        if idx == self._editing_index:
            self.task_changed.emit(idx, item.text())
            self._editing_index = None
        else:
            # Detect checkbox changes
            checked = item.checkState() == Qt.Checked
            self.task_checked.emit(idx, checked)   
    """
    def _on_rows_moved(self, parent, start, end, destination, row):
        # Emit full new order like deliverables
        new_order = [
            (self.task_list.item(i).text(), self.task_list.item(i).checkState() == Qt.Checked)
            for i in range(self.task_list.count())
        ]
        self.task_reordered.emit(new_order)
    """
    def _on_rows_moved(self, parent, start, end, destination, row):
        if start != row and row <= self.task_list.count():
            new_index = row if row < start else row - 1
            self.task_reordered.emit(start, new_index)

    def _on_task_context_menu(self, pos):
        item = self.task_list.itemAt(pos)
        if item is None:
            return
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.task_list.mapToGlobal(pos))
        if action == delete_action:
            index = self.task_list.row(item)
            self.task_deleted.emit(index)

    # === Meetings ===
    def _on_meeting_added(self):
        time = self.meeting_time_input.text().strip()
        desc = self.meeting_desc_input.text().strip()
        if time and desc:
            self.meeting_added.emit(time, desc)
            self.meeting_time_input.clear()
            self.meeting_desc_input.clear()

    def _on_remove_meeting_clicked(self):
        row = self.meetings_table.currentRow()
        if row >= 0:
            self.meeting_removed.emit(row)

    def update_meetings(self, meetings):
        self.meetings_table.setRowCount(0)
        for m in meetings:
            row = self.meetings_table.rowCount()
            self.meetings_table.insertRow(row)
            self.meetings_table.setItem(row, 0, QTableWidgetItem(m.time))
            self.meetings_table.setItem(row, 1, QTableWidgetItem(m.description))

    # === Notes ===
    def _on_notes_changed(self):
        self.notes_changed.emit(self.notes_text.toPlainText())

    def update_task_list(self, tasks):
        self._populate_tasks(tasks)

    def update_notes(self, text):
        if text != self.notes_text.toPlainText():
            self.notes_text.setPlainText(text)
