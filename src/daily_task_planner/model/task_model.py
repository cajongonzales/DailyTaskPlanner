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

# -----------------------------
# Unified Model
# -----------------------------
class UnifiedModel:
    """
    Single model for Today Pane + Tasks Pane
    Handles persistence of all tasks, deliverables, meetings, and notes
    """

    def __init__(self):
        self.today = TodayData()
        self.tasks: List[TaskDetail] = []
        self.storage_path = Path.home() / ".daily_task_planner.json"
        self.load()

    # --- TODAY Pane Methods ---
    def add_today_task(self, description: str):
        self.today.tasks.append(Task(description))
        self.save()

    def set_today_task_complete(self, index: int, complete: bool):
        if 0 <= index < len(self.today.tasks):
            self.today.tasks[index].complete = complete
            self.save()

    def remove_today_task(self, index: int):
        if 0 <= index < len(self.today.tasks):
            del self.today.tasks[index]
            self.save()

    def reorder_today_tasks(self, new_order: List[tuple[str, bool]]):
        """
        Reorder today's tasks using a list of (description, complete) tuples.
        Preserves existing Task objects if they match.
        """
        old_tasks = self.today.tasks.copy()
        reordered = []
        for desc, complete in new_order:
            for t in old_tasks:
                if t.description == desc and t.complete == complete and t not in reordered:
                    reordered.append(t)
                    break
            else:
                reordered.append(Task(desc, complete))
        self.today.tasks = reordered
        self.save()

    def add_meeting(self, time: str, description: str):
        self.today.meetings.append(Meeting(time, description))
        self.save()

    def remove_meeting(self, index: int):
        if 0 <= index < len(self.today.meetings):
            del self.today.meetings[index]
            self.save()

    def set_today_notes(self, text: str):
        self.today.notes = text
        self.save()

    # --- TASKS Pane Methods ---
    def add_task(self):
        self.tasks.append(TaskDetail())
        self.save()

    def remove_task(self, index: int):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save()

    def update_task_title(self, index: int, title: str):
        if 0 <= index < len(self.tasks):
            self.tasks[index].title = title
            self.save()

    def update_task_story(self, index: int, story: str):
        if 0 <= index < len(self.tasks):
            self.tasks[index].user_story = story
            self.save()

    def add_deliverable(self, task_index: int, description: str):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index].deliverables.append(Deliverable(description))
            self.save()

    def set_deliverable_complete(self, task_index: int, deliverable_index: int, complete: bool):
        if 0 <= task_index < len(self.tasks):
            deliverables = self.tasks[task_index].deliverables
            if 0 <= deliverable_index < len(deliverables):
                deliverables[deliverable_index].complete = complete
                self.save()

    def reorder_deliverables(self, task_index: int, new_order: List[tuple[str, bool]]):
        if 0 <= task_index < len(self.tasks):
            task = self.tasks[task_index]
            old_deliverables = self.tasks[task_index].deliverables.copy()
            reordered = []
            for desc, complete in new_order:
                for d in old_deliverables:
                    if d.description == desc and d.complete == complete and d not in reordered:
                        reordered.append(d)
                        break
                else:
                    reordered.append(Deliverable(desc, complete))
            task.deliverables = reordered
            self.save()

    def remove_deliverable(self, task_index: int, deliverable_index: int):
        if 0 <= task_index < len(self.tasks):
            deliverables = self.tasks[task_index].deliverables
            if 0 <= deliverable_index < len(deliverables):
                del deliverables[deliverable_index]
                self.save()

    def update_task_notes(self, index: int, notes: str):
        if 0 <= index < len(self.tasks):
            self.tasks[index].notes = notes
            self.save()

    # --- Persistence ---
    def save(self):
        payload = {
            "today": {
                "tasks": [asdict(t) for t in self.today.tasks],
                "meetings": [asdict(m) for m in self.today.meetings],
                "notes": self.today.notes,
            },
            "tasks": [t.to_dict() for t in self.tasks],
        }
        try:
            self.storage_path.parent.mkdir(exist_ok=True, parents=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"[WARN] Could not save data: {e}")

    def load(self):
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            # TODAY pane
            self.today.tasks = [Task(**t) for t in payload.get("today", {}).get("tasks", [])]
            self.today.meetings = [Meeting(**m) for m in payload.get("today", {}).get("meetings", [])]
            self.today.notes = payload.get("today", {}).get("notes", "")

            # TASKS pane
            self.tasks = [TaskDetail.from_dict(t) for t in payload.get("tasks", [])]
        except Exception as e:
            print(f"[WARN] Could not load data: {e}")
