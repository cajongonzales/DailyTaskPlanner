# src/planner/view/today_pane.py
from PySide6.QtCore import Qt, Signal, QPoint, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QLineEdit, QMenu, QLabel, QPushButton, QTextEdit, QGroupBox
)

class TodayPane(QWidget):
    # --- Signals for presenter ---
    task_added = Signal(str)
    task_changed = Signal(int, str)
    task_checked = Signal(int, bool)
    task_reordered = Signal(list)
    task_deleted = Signal(int)

    meeting_added = Signal(str, str)
    meeting_removed = Signal(int)
    notes_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # === TASKS SECTION ===
        task_group = QGroupBox("Tasks For Today")
        task_layout = QVBoxLayout()
        self.task_list = QListWidget()
        # Make drag and drop
        self.task_list.setDragDropMode(QListWidget.InternalMove)
        self.task_list.setDefaultDropAction(Qt.MoveAction)
        self.task_list.setSelectionMode(QListWidget.SingleSelection)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a task...")
        layout.addWidget(self.task_list)
        layout.addWidget(self.task_input)
        task_group.setLayout(task_layout)
        self.task_list.keyPressEvent = self._on_task_key 
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self._on_task_context_menu)
        layout.addWidget(task_group)
        
        # === MEETINGS SECTION ===
        layout.addWidget(QLabel("Meetings"))
        self.meeting_input = QLineEdit()
        self.meeting_input.setPlaceholderText("Add meeting (e.g., 9:00 AM - Team sync)")
        layout.addWidget(self.meeting_input)
        self.meeting_list = QListWidget()
        layout.addWidget(self.meeting_list)

        # === NOTES SECTION ===
        layout.addWidget(QLabel("Notes"))
        self.notes_text = QTextEdit()
        layout.addWidget(self.notes_text)

        # --- Connect signals ---
        self.task_input.returnPressed.connect(self._on_add_task)
        self.task_list.itemChanged.connect(self._on_task_changed)
        self.task_list.customContextMenuRequested.connect(self._on_task_context_menu)
        #self.task_list.model().rowsMoved.connect(self._on_reordered)

        self.meeting_input.returnPressed.connect(self._on_add_meeting)
        self.meeting_list.customContextMenuRequested.connect(self._on_meeting_context_menu)
        self.meeting_list.setContextMenuPolicy(Qt.CustomContextMenu)

        self.notes_text.textChanged.connect(self._on_notes_changed)

        self.task_list.itemDoubleClicked.connect(self._on_edit_task)
        self.task_list.itemChanged.connect(self._on_task_changed)

        self._editing_index = None
        # For later use when making multiple today tabs
        #self.populate_tasks(task_data.deliverables)

    # === TASK HANDLERS ===
    def _on_add_task(self):
        text = self.task_input.text().strip()
        if text:
            self.task_added.emit(text)
            self.task_input.clear()

    def _on_edit_task(self,item):
        self._editing_index = self.task_list.row(item)
        self.task_list.editItem(item)

    def _on_task_changed(self, item: QListWidgetItem):
        idx = self.task_list.row(item)
        if idx == self._editing_index:
            self.task_changed.emit(idx, item.text())
            self._editing_index = None  
    
    def _on_task_key(self,event):
        if event.key() == Qt.Key_Delete:
            item = self.task_list.currentItem()
            if item:
                idx = self.task_list.row(item)
                self.task_deleted.emit(idx)
        else:
            # default behavior
            super(QListWidget, self.task_list).keyPressEvent(event)

    # Override drop event to detect reordering
    def dropEvent(self, event):
        super().dropEvent(event)

        # After the drop finishes, rebuild the order list
        new_order = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            new_order.append((item.text(), item.checkState() == Qt.Checked))

        # Emit a signal to presenter
        self.task_reordered.emit(new_order)

    def _on_task_context_menu(self, pos: QPoint):
        item = self.task_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.task_list.mapToGlobal(pos))
        if action == delete_action:
            index = self.task_list.row(item)
            self.task_deleted.emit(index)

    # === MEETING HANDLERS ===

    def _on_add_meeting(self):
        text = self.meeting_input.text().strip()
        if not text:
            return
        self.meeting_added.emit("", text)
        self.meeting_input.clear()

    def _on_meeting_context_menu(self, pos: QPoint):
        item = self.meeting_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Meeting")
        action = menu.exec(self.meeting_list.mapToGlobal(pos))
        if action == delete_action:
            index = self.meeting_list.row(item)
            self.meeting_removed.emit(index)

    def _on_notes_changed(self):
        self.notes_changed.emit(self.notes_text.toPlainText())

    # === UPDATE METHODS (from Presenter) ===

    def update_task_list(self, tasks):
        """Mirror deliverables behavior — stable, safe, persistent UI update."""
        self.task_list.blockSignals(True)
        try:
            self.task_list.clear()
            for task in tasks:
                item = QListWidgetItem(task.description)
                item.setFlags(
                    item.flags()
                    | Qt.ItemIsUserCheckable
                    | Qt.ItemIsEditable
                    | Qt.ItemIsEnabled
                    | Qt.ItemIsSelectable
                )
                item.setCheckState(Qt.Checked if task.complete else Qt.Unchecked)
                self.task_list.addItem(item)
        finally:
            self.task_list.blockSignals(False)

    def update_meetings(self, meetings):
        self.meeting_list.clear()
        for meeting in meetings:
            self.meeting_list.addItem(f"{meeting.time} - {meeting.description}")

    def update_notes(self, text):
        self.notes_text.blockSignals(True)
        self.notes_text.setPlainText(text or "")
        self.notes_text.blockSignals(False)
