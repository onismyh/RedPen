"""Validation helpers for edit JSON payloads."""
from __future__ import annotations

from collections.abc import Sequence

from .revision_writer import ParagraphEdit, TextChange


class EditValidationError(ValueError):
    """Raised when an edit payload does not match the expected shape."""


def _expect_mapping(value: object, context: str) -> dict:
    if not isinstance(value, dict):
        raise EditValidationError(f"{context} must be an object, got {type(value).__name__}.")
    return value


def _expect_string(value: object, context: str, *, allow_empty: bool = True) -> str:
    if not isinstance(value, str):
        raise EditValidationError(f"{context} must be a string, got {type(value).__name__}.")
    if not allow_empty and not value:
        raise EditValidationError(f"{context} must not be empty.")
    return value


def _expect_int(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EditValidationError(f"{context} must be an integer, got {type(value).__name__}.")
    return value


def parse_edit_payload(data: object) -> list[ParagraphEdit]:
    """Validate and normalize raw edit payloads into ParagraphEdit objects."""
    if not isinstance(data, list):
        raise EditValidationError(f"Top-level edits payload must be a list, got {type(data).__name__}.")

    edits: list[ParagraphEdit] = []
    for item_index, raw_item in enumerate(data):
        item = _expect_mapping(raw_item, f"Edit item #{item_index}")
        paragraph_index = _expect_int(item.get("paragraph_index"), f"Edit item #{item_index}.paragraph_index")

        raw_changes = item.get("changes")
        if not isinstance(raw_changes, list):
            raise EditValidationError(
                f"Edit item #{item_index}.changes must be a list, got {type(raw_changes).__name__}."
            )

        changes: list[TextChange] = []
        for change_index, raw_change in enumerate(raw_changes):
            change = _expect_mapping(raw_change, f"Edit item #{item_index}.changes[{change_index}]")
            original = _expect_string(
                change.get("original"),
                f"Edit item #{item_index}.changes[{change_index}].original",
                allow_empty=False,
            )
            revised = _expect_string(
                change.get("revised"),
                f"Edit item #{item_index}.changes[{change_index}].revised",
            )
            reason = change.get("reason", "")
            if reason is None:
                reason = ""
            reason = _expect_string(reason, f"Edit item #{item_index}.changes[{change_index}].reason")

            if original == revised:
                continue

            changes.append(TextChange(original=original, revised=revised, reason=reason))

        if changes:
            edits.append(ParagraphEdit(paragraph_index=paragraph_index, changes=changes))

    return edits


def paragraph_edits_to_payload(edits: Sequence[ParagraphEdit]) -> list[dict]:
    """Convert normalized ParagraphEdit objects back into JSON-serializable payloads."""
    payload: list[dict] = []
    for edit in edits:
        payload.append(
            {
                "paragraph_index": edit.paragraph_index,
                "changes": [
                    {
                        "original": change.original,
                        "revised": change.revised,
                        "reason": change.reason,
                    }
                    for change in edit.changes
                ],
            }
        )
    return payload
