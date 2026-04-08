import re
from datetime import datetime, timedelta

from database.db import delete_events, get_events, insert_event, update_event

# Calendar agent manages event creation and schedule views.


class CalendarAgent:
    def handle(self, message: str) -> str:
        msg = message.lower()

        if self._is_delete_command(msg):
            print("[Calendar Agent] -> DELETE")
            ids = self._extract_ids(message)
            if not ids:
                return "Please provide valid IDs"
            print(f"[Calendar Agent] -> Deleting IDs: {ids}")
            removed = delete_events(ids)
            missing = [event_id for event_id in ids if event_id not in removed]
            if not removed:
                return self._format_not_found("Event", missing)
            response = self._format_removed("Event", removed)
            if missing:
                response += f"\nNot found: {', '.join(str(item) for item in missing)}"
            return response

        if self._is_complete_command(msg):
            print("[Calendar Agent] -> COMPLETE")
            event_id = self._extract_id(message)
            if event_id is None:
                return "Please provide an event id to mark complete."
            event = update_event(event_id, True)
            if not event:
                return "Event not found"
            return f"Event {event_id} marked as completed"

        if any(word in msg for word in ["show", "view", "list"]):
            events = get_events()
            if not events:
                return "No events available"
            lines = ["Events:"]
            for event in events:
                status = "Completed" if event["completed"] else "Pending"
                lines.append(f"{event['id']}. {event['description']} ({status})")
            return "\n".join(lines)

        if self._is_add_command(msg):
            print("[Calendar Agent] -> ADD")
            title = self._extract_title(message)
            when = self._parse_datetime(message)
            if not title:
                return "Please provide an event title."
            if not when:
                return "Please provide a time for the event (e.g., 10 AM)."
            event = insert_event(f"{title} at {when}")
            return f"Event added: {event['description']}"

        return "I can add events or view your schedule."

    def _extract_title(self, message: str) -> str:
        # Strip common command prefixes to keep just the event title.
        cleaned = re.sub(
            r"^(add\s+event|schedule|add|event|meeting)\s+",
            "",
            message,
            flags=re.I,
        ).strip()
        return cleaned

    def _parse_datetime(self, message: str) -> str | None:
        # Lightweight parsing for simple hackathon-friendly inputs.
        msg = message.lower()
        now = datetime.now()

        date = None
        if "tomorrow" in msg:
            date = now.date() + timedelta(days=1)
        elif "today" in msg:
            date = now.date()
        else:
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", msg)
            if date_match:
                try:
                    date = datetime.fromisoformat(date_match.group(1)).date()
                except ValueError:
                    return None

        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", msg)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            meridiem = time_match.group(3)
            if meridiem == "pm" and hour < 12:
                hour += 12
            if meridiem == "am" and hour == 12:
                hour = 0
        else:
            return None

        if date is None:
            date = now.date()

        dt = datetime.combine(date, datetime.min.time()).replace(hour=hour, minute=minute)
        return dt.isoformat(sep=" ", timespec="minutes")

    def _extract_id(self, message: str) -> int | None:
        match = re.search(r"(\d+)", message)
        return int(match.group(1)) if match else None

    def _extract_ids(self, message: str) -> list[int]:
        return [int(match) for match in re.findall(r"\d+", message)]

    def _is_complete_command(self, msg: str) -> bool:
        if not msg.startswith("mark event"):
            return False
        return bool(re.search(r"\bmark\s+event\s+\d+\s+(complete|completed|done)\b", msg))

    def _is_delete_command(self, msg: str) -> bool:
        return msg.startswith("remove event") or msg.startswith("delete event")

    def _is_add_command(self, msg: str) -> bool:
        if any(word in msg for word in ["remove", "delete", "mark"]):
            return False
        return any(word in msg for word in ["schedule", "meeting", "add event"])

    def _format_removed(self, label: str, ids: list[int]) -> str:
        if len(ids) == 1:
            return f"{label} {ids[0]} removed ✅"
        joined = ",".join(str(item) for item in ids)
        return f"{label}s {joined} removed ✅"

    def _format_not_found(self, label: str, ids: list[int]) -> str:
        if not ids:
            return "Event not found"
        if len(ids) == 1:
            return f"{label} {ids[0]} not found"
        joined = ",".join(str(item) for item in ids)
        return f"{label}s {joined} not found"
