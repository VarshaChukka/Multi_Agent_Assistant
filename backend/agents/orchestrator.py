import logging
from typing import List

from backend.agents.task_agent import TaskAgent
from backend.agents.calendar_agent import CalendarAgent
from backend.agents.notes_agent import NotesAgent
from backend.models.schemas import Intent

logger = logging.getLogger("orchestrator")

# Orchestrator routes intents to specialized agents and combines results.


def call_llm_placeholder(prompt: str) -> str:
    # Placeholder for future LLM integration.
    return "LLM integration placeholder"


class Orchestrator:
    def __init__(self) -> None:
        self.task_agent = TaskAgent()
        self.calendar_agent = CalendarAgent()
        self.notes_agent = NotesAgent()
        self._pending_confirmation: str | None = None

    def handle_message(self, message: str) -> str:
        # Detect intents and route to specialized agents.
        cleaned = message.strip()
        if not cleaned:
            return "Sorry, I didn't understand."

        if self._pending_confirmation:
            return self._handle_confirmation(cleaned)

        if self._is_help_request(cleaned):
            return self._help_message()

        if "plan my day" in cleaned.lower():
            logger.info("Using multi-agent plan")
            print("[Orchestrator] -> Plan Day workflow triggered")
            return self._plan_day()

        if self._is_remove_completed_request(cleaned):
            self._pending_confirmation = "remove_completed_tasks"
            return "Are you sure you want to delete all completed tasks? (yes/no)"

        responses: List[str] = []
        matched_any = False

        for clause in self._split_clauses(cleaned):
            target = self._route_clause(clause)
            if not target:
                continue
            matched_any = True
            if target == Intent.TASK:
                logger.info("Using TaskAgent")
                print(f"[Orchestrator] -> Task Agent called with: \"{clause}\"")
                responses.append(self.task_agent.handle(clause))
            elif target == Intent.CALENDAR:
                logger.info("Using CalendarAgent")
                print(f"[Orchestrator] -> Calendar Agent called with: \"{clause}\"")
                responses.append(self.calendar_agent.handle(clause))
            elif target == Intent.NOTES:
                logger.info("Using NotesAgent")
                print(f"[Orchestrator] -> Notes Agent called with: \"{clause}\"")
                responses.append(self.notes_agent.handle(clause))

        combined = "\n".join(r for r in responses if r)
        if not matched_any or not combined:
            return "Sorry, I didn't understand."
        return combined

    def _plan_day(self) -> str:
        # Multi-step workflow: combine tasks, schedule, and notes summary.
        task_summary = self.task_agent.handle("list tasks")
        calendar_summary = self.calendar_agent.handle("view schedule")
        notes_summary = self.notes_agent.handle("summarize notes")
        return "\n".join(["Plan for today:", task_summary, calendar_summary, notes_summary])

    def _detect_intents(self, message: str) -> List[Intent]:
        msg = message.lower()
        intents: List[Intent] = []

        if any(word in msg for word in ["task", "todo", "complete", "done"]):
            intents.append(Intent.TASK)

        if any(word in msg for word in ["event", "calendar", "schedule", "meeting"]):
            intents.append(Intent.CALENDAR)

        if any(word in msg for word in ["note", "notes", "summarize", "summary"]):
            intents.append(Intent.NOTES)

        unique = []
        for intent in intents:
            if intent not in unique:
                unique.append(intent)
        return unique

    def _split_clauses(self, message: str) -> List[str]:
        parts = [part.strip() for part in message.split(" and ")]
        return [part for part in parts if part]

    def _route_clause(self, clause: str) -> Intent | None:
        msg = clause.lower()
        if any(word in msg for word in ["note", "notes"]):
            return Intent.NOTES
        if any(word in msg for word in ["schedule", "meeting", "event", "calendar"]):
            return Intent.CALENDAR
        if any(word in msg for word in ["task", "todo", "study", "finish", "complete project"]):
            return Intent.TASK
        return None

    def _is_help_request(self, message: str) -> bool:
        msg = message.lower()
        return msg in ["help", "how to use", "commands", "guide"]

    def _is_remove_completed_request(self, message: str) -> bool:
        msg = message.lower()
        return msg in ["remove completed tasks", "delete completed tasks"]

    def _handle_confirmation(self, message: str) -> str:
        msg = message.lower()
        if msg in ["yes", "y"]:
            if self._pending_confirmation == "remove_completed_tasks":
                self._pending_confirmation = None
                return self.task_agent.remove_completed_tasks()
        if msg in ["no", "n"]:
            self._pending_confirmation = None
            return "Operation cancelled"
        return "Please reply with 'yes' or 'no'."

    def _help_message(self) -> str:
        return (
            "Here is a quick guide to what I can do:\n\n"
            "📝 TASKS:\n"
            "Add tasks:\n"
            "- add task buy milk\n"
            "- I need to study AI\n\n"
            "View tasks:\n"
            "- show tasks\n"
            "- what are my tasks\n\n"
            "Mark complete:\n"
            "- mark task 1 complete\n\n"
            "Remove completed tasks:\n"
            "- remove completed tasks\n\n"
            "📅 CALENDAR:\n"
            "Add events:\n"
            "- schedule meeting tomorrow at 10 AM\n"
            "- I have a meeting at 5 PM\n\n"
            "Mark complete:\n"
            "- mark event 1 complete\n\n"
            "View events:\n"
            "- show events\n"
            "- what is my schedule\n\n"
            "🧠 NOTES:\n"
            "Add notes:\n"
            "- note AI is powerful\n"
            "- save this: revise ML\n\n"
            "View notes:\n"
            "- show notes\n"
            "- what are my notes\n\n"
            "Tip: You can speak naturally (e.g., \"I need to finish my project and schedule a meeting\")"
        )
