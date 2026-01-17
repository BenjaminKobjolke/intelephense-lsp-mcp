"""Load and parse intelephense.json configuration file."""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def load_config_file(workspace_path: str) -> dict[str, Any] | None:
    """Load intelephense.json from workspace root.

    Args:
        workspace_path: Path to the project workspace root.

    Returns:
        Parsed JSON configuration or None if file doesn't exist or is invalid.
    """
    config_path = os.path.join(workspace_path, "intelephense.json")
    if not os.path.isfile(config_path):
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in {config_path}: {e}")
        return None
    except OSError as e:
        logger.warning(f"Could not read {config_path}: {e}")
        return None


def get_ignore_patterns(config: dict[str, Any] | None) -> list[str]:
    """Extract ignore patterns from config.

    Args:
        config: Parsed configuration dictionary or None.

    Returns:
        List of ignore patterns (glob patterns).
    """
    if config is None:
        return []

    patterns = config.get("ignore", [])
    if isinstance(patterns, list):
        return [p for p in patterns if isinstance(p, str)]
    return []
