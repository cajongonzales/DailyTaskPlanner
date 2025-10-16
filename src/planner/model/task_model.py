# src/planner/model/task_model.py
from dataclasses import dataclass, field, asdict
from typing import List
import json
from pathlib import Path


# -----------------------------
# TODAY pane models
# -----------------------------

@dataclass
class Task:
    description: str
    complete: bool = False


@dataclass
class Meeting:
    time: str
    description: str


@dataclass
class TodayData:
    tasks: List[Task] = field(default_factory=list)
    meetings: List[Meeting] = field(default_factory=list)
    notes: str = ""


class TaskModel:
    """Stores and manipulates today's data."""

    def __init__(self):
        self.data = TodayData()

    # --- Tasks ---
    def add_task(self, description: str):
        self.data.tasks.append(Task(description))

    def set_task_complete(self, index: int, complete: bool):
        if 0 <= index < len(self.data.tasks):
            self.data.tasks[index].complete = complete

    def remove_task(self, index: int):
        if 0 <= index < len(self.data.tasks):
            del self.data.tasks[index]

    # --- Meetings ---
    def add_meeting(self, time: str, description: str):
        self.data.meetings.append(Meeting(time, description))

    def remove_meeting(self, index: int):
        if 0 <= index < len(self.data.meetings):
            del self.data.meetings[index]

    # --- Notes ---
    def set_notes(self, text: str):
        self.data.notes = text

    def get_notes(self) -> str:
        return self.data.notes


# -----------------------------
# TASKS pane models
# -----------------------------

@dataclass
class Deliverable:
    description: str
    complete: bool = False


@dataclass
class TaskDetail:
    title: str = "New Task"
    user_story: str = (
        "As a [type of user], I want to [perform some action] "
        "so that [I can achieve a benefit]."
    )
    deliverables: List[Deliverable] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "user_story": self.user_story,
            "deliverables": [asdict(d) for d in self.deliverables],
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "TaskDetail":
        return TaskDetail(
            title=data.get("title", "New Task"),
            user_story=data.get("user_story", ""),
            deliverables=[Deliverable(**d) for d in data.get("deliverables", [])],
            notes=data.get("notes", ""),
        )


class TasksModel:
    """Stores and manages a list of detailed tasks (for the TASKS pane)."""

    def __init__(self):
        self.tasks: List[TaskDetail] = []
        self._data_file = Path.home() / ".daily_task_planner" / "tasks.json"
        self.load()  

    # --- Task management ---
    def add_task(self):
        self.tasks.append(TaskDetail())
        self.save()  

    def remove_task(self, index: int):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save()

    def update_title(self, index: int, title: str):
        if 0 <= index < len(self.tasks):
            self.tasks[index].title = title
            self.save()

    def update_user_story(self, index: int, story: str):
        if 0 <= index < len(self.tasks):
            self.tasks[index].user_story = story
            self.save()

    def add_deliverable(self, index: int, description: str):
        if 0 <= index < len(self.tasks):
            self.tasks[index].deliverables.append(Deliverable(description))
            self.save()

    def set_deliverable_complete(
        self, task_index: int, deliverable_index: int, complete: bool
    ):
        if 0 <= task_index < len(self.tasks):
            deliverables = self.tasks[task_index].deliverables
            if 0 <= deliverable_index < len(deliverables):
                deliverables[deliverable_index].complete = complete
                self.save()

    def update_notes(self, index: int, notes: str):
        if 0 <= index < len(self.tasks):
            self.tasks[index].notes = notes
            self.save()

    def load(self):
        """Load tasks from JSON file."""
        if not self._data_file.exists():
            self.tasks = []
            return

        try:
            with open(self._data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tasks = [TaskDetail.from_dict(item) for item in data]
        except Exception:
            # Defensive: if file corrupt, reset tasks
            self.tasks = []

    def save(self):
        """Save tasks to JSON file."""
        try:
            self._data_file.parent.mkdir(exist_ok=True)
            with open(self._data_file, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in self.tasks], f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
