# src/planner/view/today_pane.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QLineEdit, QCheckBox, QTextEdit, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal


class TodayPane(QWidget):
    # Signals that will notify the presenter
    task_added = Signal(str)
    task_checked = Signal(int, bool)
    task_edited = Signal(int, str)
    task_reordered = Signal(int, int)
    meeting_added = Signal(str, str)
    notes_changed = Signal(str)

    def __init__(self, tasks):
        super().__init__()
        layout = QVBoxLayout(self)

        # --- Get Done Today ---
        tasks_group = QGroupBox("Get Done Today")
        tasks_layout = QVBoxLayout()
        self.task_list = QListWidget()
        self.task_input = QLineEdit()
        # Enable inline edit and drag/drop reordering
        self.task_list.setEditTriggers(QListWidget.DoubleClicked)
        self.task_list.setDragDropMode(QListWidget.InternalMove)
        self.task_list.setDefaultDropAction(Qt.MoveAction)
        self.task_input.setPlaceholderText("Add a new task and press Enter")
        self.populate_tasks(tasks)
        tasks_layout.addWidget(self.task_list)
        tasks_layout.addWidget(self.task_input)
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)

        # --- Meetings ---
        meetings_group = QGroupBox("Meetings")
        meetings_layout = QVBoxLayout()
        self.meetings_table = QTableWidget(0, 2)
        self.meetings_table.setHorizontalHeaderLabels(["Time", "Description"])
        self.meetings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        meetings_layout.addWidget(self.meetings_table)

        add_meeting_layout = QHBoxLayout()
        self.meeting_time_input = QLineEdit()
        self.meeting_time_input.setPlaceholderText("e.g. 10:30 AM")
        self.meeting_desc_input = QLineEdit()
        self.meeting_desc_input.setPlaceholderText("Meeting description")
        self.add_meeting_button = QPushButton("Add Meeting")
        add_meeting_layout.addWidget(self.meeting_time_input)
        add_meeting_layout.addWidget(self.meeting_desc_input)
        add_meeting_layout.addWidget(self.add_meeting_button)
        meetings_layout.addLayout(add_meeting_layout)

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

        # --- Connect UI events ---
        self.task_input.returnPressed.connect(self._on_task_entered)
        self.add_meeting_button.clicked.connect(self._on_meeting_added)
        self.notes_text.textChanged.connect(self._on_notes_changed)
        self.task_list.itemChanged.connect(self._on_task_checked)
        # --- Signals ---
        self.task_list.itemChanged.connect(self._on_task_changed)
        self.task_list.model().rowsMoved.connect(self._on_rows_moved)

    # === UI Event Handlers ===
    def _on_task_entered(self):
        text = self.task_input.text().strip()
        if text:
            self.task_added.emit(text)
            self.task_input.clear()

    def _on_meeting_added(self):
        time = self.meeting_time_input.text().strip()
        desc = self.meeting_desc_input.text().strip()
        if time and desc:
            self.meeting_added.emit(time, desc)
            self.meeting_time_input.clear()
            self.meeting_desc_input.clear()

    def _on_notes_changed(self):
        self.notes_changed.emit(self.notes_text.toPlainText())

    # === Presenter update methods ===
    def update_task_list(self, tasks):
        """
        Rebuild the QListWidget from the given tasks list.
        Block signals while populating to avoid spurious itemChanged events.
        """
        # Prevent itemChanged from firing while we set up the list
        self.task_list.blockSignals(True)
        try:
            self.task_list.clear()
            for task in tasks:
                item = QListWidgetItem(task.description)
                # make the item checkable
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                # set initial checked state
                item.setCheckState(Qt.Checked if task.complete else Qt.Unchecked)
                self.task_list.addItem(item)
        finally:
            # Always re-enable signals
            self.task_list.blockSignals(False)
    
    def _on_task_checked(self, item):
        """
        Called when a QListWidgetItem check state changes.
        Guard against invalid index and emit task_checked signal only for valid indexes.
        """
        try:
            index = self.task_list.row(item)
            if index < 0 or index >= self.task_list.count():
                # invalid index — ignore
                return
            checked = item.checkState() == Qt.Checked
            self.task_checked.emit(index, checked)
        except Exception:
            # Defensive: don't crash the whole app if something odd happens.
            # You may log here if you have logging configured.
            return

    def update_meetings(self, meetings):
        self.meetings_table.setRowCount(0)
        for meeting in meetings:
            row = self.meetings_table.rowCount()
            self.meetings_table.insertRow(row)
            self.meetings_table.setItem(row, 0, QTableWidgetItem(meeting.time))
            self.meetings_table.setItem(row, 1, QTableWidgetItem(meeting.description))

    def update_notes(self, text):
        if text != self.notes_text.toPlainText():
            self.notes_text.setPlainText(text)

    def populate_tasks(self, tasks):
        self.task_list.blockSignals(True)
        self.task_list.clear()
        for t in tasks:
            item = QListWidgetItem(t.description)
            item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.task_list.addItem(item)
        self.task_list.blockSignals(False)

    def _on_task_changed(self, item):
        index = self.task_list.row(item)
        new_text = item.text().strip()
        self.task_edited.emit(index, new_text)

    def _on_rows_moved(self, parent, start, end, destination, row):
        """
        Qt calls this after rows are dropped.
        - start: old index
        - row: new index (after drop)
        """
        if start != row and row <= self.task_list.count():
            # Adjust if the item was moved downward
            new_index = row if row < start else row - 1
            self.task_reordered.emit(start, new_index)

    def _create_task_item(self, task):
        """
        Helper to create a QListWidgetItem from a Task object,
        ensuring it’s checkable, editable, draggable, and selectable.
        """
        item = QListWidgetItem(task.description)
        item.setFlags(
            Qt.ItemIsUserCheckable
            | Qt.ItemIsEditable
            | Qt.ItemIsDragEnabled
            | Qt.ItemIsEnabled
            | Qt.ItemIsSelectable
        )
        item.setCheckState(Qt.Checked if task.complete else Qt.Unchecked)
        return item
    
    def populate_tasks(self, tasks):
        self.task_list.blockSignals(True)
        self.task_list.clear()
        for t in tasks:
            item = self._create_task_item(t)
            self.task_list.addItem(item)
        self.task_list.blockSignals(False)

    def update_task_list(self, tasks):
        """
        Rebuild the QListWidget from the given tasks list.
        Block signals while populating to avoid spurious itemChanged events.
        """
        self.task_list.blockSignals(True)
        try:
            self.task_list.clear()
            for task in tasks:
                item = self._create_task_item(task)
                self.task_list.addItem(item)
        finally:
            self.task_list.blockSignals(False)

    def _on_task_changed(self, item):
        index = self.task_list.row(item)
        new_text = item.text().strip()
        self.task_edited.emit(index, new_text)

    def _on_rows_moved(self, parent, start, end, destination, row):
        """
        Qt calls this after rows are dropped.
        - start: old index
        - row: new index (after drop)
        """
        if start != row and row <= self.task_list.count():
            # Adjust if the item was moved downward
            new_index = row if row < start else row - 1
            self.task_reordered.emit(start, new_index)
