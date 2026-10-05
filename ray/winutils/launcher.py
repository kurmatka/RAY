import os
import subprocess
from collections.abc import Iterable, Sequence
from pathlib import Path

from ray.core.errors import CommandError


def launch_first_existing(
    app_name: str, candidates: Iterable[str], args: Sequence[str] = ()
) -> None:
    """Запускает первую найденную программу из списка возможных путей."""
    for template in candidates:
        path = Path(os.path.expandvars(template))
        if path.exists():
            subprocess.Popen([str(path), *args])
            return
    raise CommandError(f"Не нашёл {app_name} на этом компьютере")
