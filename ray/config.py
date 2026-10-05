import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
LOGS_DIR = PROJECT_ROOT / "logs"


@dataclass
class Config:
    wake_word: str = "рей"
    language: str = "ru"
    log_level: str = "INFO"
    sounds_enabled: bool = True
    microphone_index: int | None = None
    custom_commands: list = field(default_factory=list)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> "Config":
        if not path.exists():
            config = cls()
            config.save(path)
            return config
        with path.open(encoding="utf-8-sig") as file:
            data = json.load(file)
        known_names = {item.name for item in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in known_names})

    def save(self, path: Path = CONFIG_PATH) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(asdict(self), file, ensure_ascii=False, indent=2)
