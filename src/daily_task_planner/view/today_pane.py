from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QTextEdit, QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
import json
from pathlib import Path


class TodayPane(QWidget):
    # Signals for presenter
    task_added = Signal(str)
    task_checked = Signal(int, bool)
    task_edited = Signal(int, str)
    task_reordered = Signal(int, int)
    meeting_added = Signal(str, str)
    meeting_removed = Signal(int)
    notes_changed = Signal(str)

    STORAGE_PATH = Path.home() / ".daily_task_planner_meetings.json"

    def __init__(self, tasks):
        super().__init__()
        layout = QVBoxLayout(self)

        # --- Tasks ---
        tasks_group = QGroupBox("Get Done Today")
        tasks_layout = QVBoxLayout()
        self.task_list = QListWidget()
        self.task_input = QLineEdit()
        self.task_list.setEditTriggers(QListWidget.DoubleClicked)
        self.task_list.setDragDropMode(QListWidget.InternalMove)
        self.task_list.setDefaultDropAction(Qt.MoveAction)
        self.task_input.setPlaceholderText("Add a new task and press Enter")
        self._populate_tasks(tasks)
        tasks_layout.addWidget(self.task_list)
        tasks_layout.addWidget(self.task_input)
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)

        # --- Meetings ---
        meetings_group = QGroupBox("Meetings")
        meetings_layout = QVBoxLayout()

        # Table
        self.meetings_table = QTableWidget(0, 2)
        self.meetings_table.setHorizontalHeaderLabels(["Time", "Description"])
        self.meetings_table.setSortingEnabled(True)
        meetings_layout.addWidget(self.meetings_table)

        # Input row
        input_layout = QHBoxLayout()
        self.meeting_time_input = QLineEdit()
        self.meeting_time_input.setPlaceholderText("e.g. 10:30 AM")
        self.meeting_desc_input = QLineEdit()
        self.meeting_desc_input.setPlaceholderText("Meeting description")
        input_layout.addWidget(self.meeting_time_input, 1)
        input_layout.addWidget(self.meeting_desc_input, 2)
        meetings_layout.addLayout(input_layout)

        # Button row
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
        self.add_meeting_button.clicked.connect(self._on_meeting_added)
        self.remove_meeting_button.clicked.connect(self._on_remove_meeting_clicked)
        self.notes_text.textChanged.connect(self._on_notes_changed)
        self.task_list.itemChanged.connect(self._on_task_checked)
        self.task_list.itemChanged.connect(self._on_task_changed)
        self.task_list.model().rowsMoved.connect(self._on_rows_moved)

        # Load previous table column widths
        self.load_meetings_table_state()

    # === Task Methods ===
    def _populate_tasks(self, tasks):
        self.task_list.blockSignals(True)
        self.task_list.clear()
        for t in tasks:
            item = QListWidgetItem(t.description)
            item.setFlags(
                Qt.ItemIsUserCheckable
                | Qt.ItemIsEditable
                | Qt.ItemIsDragEnabled
                | Qt.ItemIsEnabled
                | Qt.ItemIsSelectable
            )
            item.setCheckState(Qt.Checked if t.complete else Qt.Unchecked)
            self.task_list.addItem(item)
        self.task_list.blockSignals(False)

    def _on_task_entered(self):
        text = self.task_input.text().strip()
        if text:
            self.task_added.emit(text)
            self.task_input.clear()

    def _on_task_checked(self, item):
        index = self.task_list.row(item)
        if 0 <= index < self.task_list.count():
            checked = item.checkState() == Qt.Checked
            self.task_checked.emit(index, checked)

    def _on_task_changed(self, item):
        index = self.task_list.row(item)
        new_text = item.text().strip()
        self.task_edited.emit(index, new_text)

    def _on_rows_moved(self, parent, start, end, destination, row):
        if start != row and row <= self.task_list.count():
            new_index = row if row < start else row - 1
            self.task_reordered.emit(start, new_index)

    # === Meetings Methods ===
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
        for meeting in meetings:
            row = self.meetings_table.rowCount()
            self.meetings_table.insertRow(row)
            self.meetings_table.setItem(row, 0, QTableWidgetItem(meeting.time))
            self.meetings_table.setItem(row, 1, QTableWidgetItem(meeting.description))

    # === Notes Methods ===
    def _on_notes_changed(self):
        self.notes_changed.emit(self.notes_text.toPlainText())

    def update_notes(self, text):
        if text != self.notes_text.toPlainText():
            self.notes_text.setPlainText(text)

    # === Persistence Methods ===
    def save_meetings_table_state(self):
        widths = [self.meetings_table.columnWidth(i) for i in range(self.meetings_table.columnCount())]
        try:
            with open(self.STORAGE_PATH, "w") as f:
                json.dump(widths, f)
        except Exception as e:
            print(f"[WARN] Could not save meetings table state: {e}")

    def load_meetings_table_state(self):
        if self.STORAGE_PATH.exists():
            try:
                with open(self.STORAGE_PATH, "r") as f:
                    widths = json.load(f)
                    for i, w in enumerate(widths):
                        if i < self.meetings_table.columnCount():
                            self.meetings_table.setColumnWidth(i, w)
            except Exception as e:
                print(f"[WARN] Could not load meetings table state: {e}")
    
    def update_task_list(self, tasks):
        """
        Rebuild the QListWidget from the given tasks list.
        Block signals while populating to avoid spurious itemChanged events.
        """
        self.task_list.blockSignals(True)
        try:
            self.task_list.clear()
            for task in tasks:
                item = QListWidgetItem(task.description)
                # make the item checkable, editable, draggable, selectable
                item.setFlags(
                    Qt.ItemIsUserCheckable
                    | Qt.ItemIsEditable
                    | Qt.ItemIsDragEnabled
                    | Qt.ItemIsEnabled
                    | Qt.ItemIsSelectable
                )
                # set initial checked state
                item.setCheckState(Qt.Checked if task.complete else Qt.Unchecked)
                self.task_list.addItem(item)
        finally:
            self.task_list.blockSignals(False)
