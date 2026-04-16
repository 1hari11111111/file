"""
State Management Helper
Simple in-memory state store for multi-step admin conversations.
state format: { user_id: { "state": str, "data": dict } }
"""

_user_states: dict = {}


def set_state(user_id: int, state: str, data: dict = None):
    """Set the current state (and optional data) for a user."""
    _user_states[user_id] = {"state": state, "data": data or {}}


def get_state(user_id: int) -> dict | None:
    """Return the current state dict for a user, or None if not set."""
    return _user_states.get(user_id)


def clear_state(user_id: int):
    """Clear the state for a user."""
    _user_states.pop(user_id, None)


def update_data(user_id: int, key: str, value):
    """Update a single key in the state data without changing state name."""
    if user_id in _user_states:
        _user_states[user_id]["data"][key] = value
