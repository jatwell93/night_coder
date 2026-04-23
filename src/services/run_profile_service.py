"""US1 execution profile checks."""

from __future__ import annotations

_VALID_PROFILES = frozenset({"offline", "online"})
_NETWORK_COMMAND_HINTS = (
    "curl ",
    "wget ",
    "http://",
    "https://",
    "ping ",
    "nc ",
    "nmap ",
    "ssh ",
)


def profile_allows_command(profile: str, command: str) -> bool:
    """Return whether a command is allowed under the named profile.

    Raises
    ------
    ValueError
        If profile is unknown.
    """
    if profile not in _VALID_PROFILES:
        msg = f"Unknown profile {profile!r}; expected one of {sorted(_VALID_PROFILES)}"
        raise ValueError(msg)
    if profile == "online":
        return True
    lowered = command.lower()
    return not any(hint in lowered for hint in _NETWORK_COMMAND_HINTS)
