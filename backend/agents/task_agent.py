import re

from backend.database.db import (
    delete_completed_tasks,
    delete_tasks,
    get_tasks,
    insert_task,
    update_task,
)

# Task agent handles task creation, listing, and completion.


class TaskAgent:
    def handle(self, message: str) -> str:
        msg = message.lower()

        if self._is_delete_command(msg):
            ids = self._extract_ids(message)
            if not ids:
                return "Please provide valid IDs"
            print(f"[Task Agent] -> Deleting IDs: {ids}")
            removed = delete_tasks(ids)
            missing = [task_id for task_id in ids if task_id not in removed]
            if not removed:
                return self._format_not_found("Task", missing)
            response = self._format_removed("Task", removed)
            if missing:
                response += f"\nNot found: {', '.join(str(item) for item in missing)}"
            return response

        if any(word in msg for word in ["list", "show", "view"]):
            tasks = get_tasks()
            if not tasks:
                return "No tasks yet."
            lines = ["Tasks:"]
            for task in tasks:
                status = "done" if task["completed"] else "open"
                lines.append(f"{task['id']}. {task['description']} ({status})")
            return "\n".join(lines)

        if self._is_complete_command(msg):
            task_id = self._extract_id(message)
            if task_id is None:
                return "Please provide a task id to mark complete."
            task = update_task(task_id, True)
            if task:
                return f"Marked task {task_id} complete."
            return f"Task {task_id} not found."

        if "add" in msg or "task" in msg:
            title = self._extract_title(message)
            if not title:
                return "Please provide a task title."
            task = insert_task(title)
            return f"Added task {task['id']}: {task['description']}"

        return "I can add, list, or complete tasks."

    def _extract_id(self, message: str) -> int | None:
        match = re.search(r"(\d+)", message)
        return int(match.group(1)) if match else None

    def _extract_title(self, message: str) -> str:
        # Strip common command prefixes to keep just the task title.
        cleaned = re.sub(r"^(add\s+task|add|task)\s+", "", message, flags=re.I).strip()
        return cleaned

    def _is_complete_command(self, msg: str) -> bool:
        return bool(re.search(r"\bmark\s+task\s+\d+\s+complete\b", msg))

    def remove_completed_tasks(self) -> str:
        removed = delete_completed_tasks()
        if removed == 0:
            return "No completed tasks to remove"
        return "All completed tasks removed ✅"

    def _is_delete_command(self, msg: str) -> bool:
        if not (msg.startswith("remove") or msg.startswith("delete")):
            return False
        return "task" in msg

    def _extract_ids(self, message: str) -> list[int]:
        return [int(match) for match in re.findall(r"\d+", message)]

    def _format_removed(self, label: str, ids: list[int]) -> str:
        if len(ids) == 1:
            return f"{label} {ids[0]} removed ✅"
        joined = ",".join(str(item) for item in ids)
        return f"{label}s {joined} removed ✅"

    def _format_not_found(self, label: str, ids: list[int]) -> str:
        if not ids:
            return f"{label} not found"
        if len(ids) == 1:
            return f"{label} {ids[0]} not found"
        joined = ",".join(str(item) for item in ids)
        return f"{label}s {joined} not found"
