# src/daily_task_planner/view/deliverables_list.py
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal


class DeliverablesList(QListWidget):
    """
    Custom QListWidget subclass that supports drag-drop reordering
    and emits the new order with the associated task index.
    """
    reordered = Signal(int, list)  # (task_index, new_order)

    def __init__(self, task_index=None, parent=None):
        super().__init__(parent)
        self._task_index = task_index
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def set_task_index(self, index: int):
        """Used by the parent tab to update which task this list belongs to."""
        self._task_index = index

    def dropEvent(self, event):
        super().dropEvent(event)
        if self._task_index is None:
            return

        # Build the new order of (description, checked)
        new_order = [
            (self.item(i).text(), self.item(i).checkState() == Qt.Checked)
            for i in range(self.count())
        ]
        self.reordered.emit(self._task_index, new_order)

    def populate(self, deliverables):
        """Populate the list safely from model data."""
        self.blockSignals(True)
        self.clear()
        for d in deliverables:
            item = QListWidgetItem(d.description)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            item.setCheckState(Qt.Checked if d.complete else Qt.Unchecked)
            self.addItem(item)
        self.blockSignals(False)
