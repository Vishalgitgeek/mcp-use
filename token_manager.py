"""Token management for storing and retrieving OAuth tokens."""
import json
from pathlib import Path
from typing import Optional, List
from config import TOKENS_DIR


def get_token_file(email: str) -> Path:
    """Get the token file path for an email."""
    return TOKENS_DIR / f"{email}.json"


def save_tokens(email: str, tokens: dict) -> None:
    """Save OAuth tokens for a user."""
    token_file = get_token_file(email)
    token_data = {
        "email": email,
        "tokens": tokens
    }
    with open(token_file, "w") as f:
        json.dump(token_data, f, indent=2)


def load_tokens(email: str) -> Optional[dict]:
    """Load OAuth tokens for a user."""
    token_file = get_token_file(email)
    if not token_file.exists():
        return None
    
    try:
        with open(token_file, "r") as f:
            data = json.load(f)
            return data.get("tokens")
    except (json.JSONDecodeError, IOError):
        return None


def get_connected_accounts() -> List[str]:
    """Get list of all connected account emails."""
    accounts = []
    for token_file in TOKENS_DIR.glob("*.json"):
        try:
            with open(token_file, "r") as f:
                data = json.load(f)
                email = data.get("email")
                if email:
                    accounts.append(email)
        except (json.JSONDecodeError, IOError):
            continue
    return sorted(accounts)


def delete_tokens(email: str) -> bool:
    """Delete tokens for a user. Returns True if deleted, False if not found."""
    token_file = get_token_file(email)
    if token_file.exists():
        token_file.unlink()
        return True
    return False

