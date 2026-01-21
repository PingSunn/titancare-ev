"""
Model mapping loader for llms.txt configuration.
Provides easy model alias resolution for LiteLLM integration.
"""

from pathlib import Path
from functools import lru_cache


def load_model_mapping(path: str | Path = "llms.txt") -> dict[str, str]:
    """
    Load model aliases from llms.txt file.

    Args:
        path: Path to the llms.txt configuration file.

    Returns:
        Dictionary mapping aliases to full model identifiers.

    Example llms.txt format:
        # Comment line
        gpt4o=gpt-4o
        gemini-flash=litellm/gemini/gemini-2.0-flash
    """
    mapping: dict[str, str] = {}
    filepath = Path(path)

    if not filepath.exists():
        raise FileNotFoundError(f"Model mapping file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Parse alias=model format
            if "=" not in line:
                raise ValueError(
                    f"Invalid format at line {line_num}: expected 'alias=model', got '{line}'"
                )

            alias, model = line.split("=", 1)
            alias = alias.strip()
            model = model.strip()

            if not alias or not model:
                raise ValueError(
                    f"Invalid format at line {line_num}: empty alias or model"
                )

            mapping[alias] = model

    return mapping


def get_model(alias: str, mapping: dict[str, str]) -> str:
    """
    Get full model identifier from alias.

    Args:
        alias: Model alias to resolve.
        mapping: Dictionary of alias to model mappings.

    Returns:
        Full model identifier, or the alias itself if not found
        (falls back to 'default' if available).
    """
    if alias in mapping:
        return mapping[alias]

    # Try default fallback
    if "default" in mapping:
        return mapping["default"]

    # Return alias as-is (might be a full model name already)
    return alias


class ModelRegistry:
    """
    Registry for managing model aliases and instances.
    Singleton pattern for application-wide model configuration.
    """

    _instance: "ModelRegistry | None" = None
    _mapping: dict[str, str]

    def __new__(cls, config_path: str | Path = "llms.txt") -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._mapping = load_model_mapping(config_path)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None

    @property
    def mapping(self) -> dict[str, str]:
        """Get the model mapping dictionary."""
        return self._mapping

    def get(self, alias: str) -> str:
        """Get model identifier by alias."""
        return get_model(alias, self._mapping)

    def list_aliases(self) -> list[str]:
        """List all available model aliases."""
        return [k for k in self._mapping.keys() if k != "default"]

    def get_default(self) -> str:
        """Get the default model identifier."""
        return self._mapping.get("default", "gpt-4o")


@lru_cache
def get_model_registry(config_path: str = "llms.txt") -> ModelRegistry:
    """Get or create the model registry singleton."""
    return ModelRegistry(config_path)
