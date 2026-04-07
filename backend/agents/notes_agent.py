import re

from backend.database.db import delete_notes, get_notes, insert_note

# Notes agent manages saving, listing, and summarizing notes.


class NotesAgent:
    def handle(self, message: str) -> str:
        msg = message.lower()

        if self._is_delete_command(msg):
            ids = self._extract_ids(message)
            if not ids:
                return "Please provide valid IDs"
            print(f"[Notes Agent] -> Deleting IDs: {ids}")
            removed = delete_notes(ids)
            missing = [note_id for note_id in ids if note_id not in removed]
            if not removed:
                return self._format_not_found("Note", missing)
            response = self._format_removed("Note", removed)
            if missing:
                response += f"\nNot found: {', '.join(str(item) for item in missing)}"
            return response

        if any(word in msg for word in ["list", "show", "view"]):
            notes = get_notes()
            if not notes:
                return "No notes saved."
            lines = ["Notes:"]
            for note in notes:
                lines.append(f"- {note['id']}: {note['content']}")
            return "\n".join(lines)

        if "save" in msg or "note" in msg:
            content = self._extract_content(message)
            if not content:
                return "Please provide note content."
            note = insert_note(content)
            return f"Note saved: {note['content']}"

        return "I can save, list, or summarize notes."

    def _extract_content(self, message: str) -> str:
        # Strip command prefixes so only note content remains.
        cleaned = re.sub(r"^(save\s+note|save|note)\s+", "", message, flags=re.I).strip()
        return cleaned

    def _is_delete_command(self, msg: str) -> bool:
        if not (msg.startswith("remove") or msg.startswith("delete")):
            return False
        return "note" in msg

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
