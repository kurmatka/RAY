from datetime import datetime

import mss

from ray.config import PROJECT_ROOT
from ray.core.errors import CommandError
from ray.core.registry import command
from ray.winutils import window

SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"


@command("заблокируй компьютер", "заблокируй экран", "заблокируй")
def lock_computer() -> str:
    window.lock_workstation()
    return "Блокирую компьютер"


@command("сверни окно", "сверни активное окно", "сверни")
def minimize_window() -> str:
    if not window.minimize_active_window():
        raise CommandError("Нет активного окна")
    return "Окно свёрнуто"


@command("закрой окно", "закрой активное окно", "закрой программу")
def close_window() -> str:
    if not window.close_active_window():
        raise CommandError("Нет активного окна")
    return "Закрываю окно"


@command("сделай скриншот", "сделай снимок экрана", "скриншот")
def take_screenshot() -> str:
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    path = SCREENSHOTS_DIR / f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"
    with mss.mss() as screen:
        screen.shot(mon=1, output=str(path))
    return "Скриншот сохранён"


# ============================================================
# ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ
# ============================================================

import subprocess
from datetime import datetime


@command(
    "открой калькулятор",
    "запусти калькулятор",
)
def open_calculator() -> str:
    subprocess.Popen(["calc.exe"])
    return "Открываю калькулятор"


@command(
    "открой блокнот",
    "запусти блокнот",
)
def open_notepad() -> str:
    subprocess.Popen(["notepad.exe"])
    return "Открываю блокнот"


@command(
    "открой paint",
    "открой пейнт",
    "запусти paint",
)
def open_paint() -> str:
    subprocess.Popen(["mspaint.exe"])
    return "Открываю Paint"


@command(
    "открой командную строку",
    "запусти командную строку",
)
def open_cmd() -> str:
    subprocess.Popen(["cmd.exe"])
    return "Открываю командную строку"


@command(
    "открой powershell",
    "запусти powershell",
)
def open_powershell() -> str:
    subprocess.Popen(["powershell.exe"])
    return "Открываю PowerShell"


@command(
    "который час",
    "сколько времени",
    "скажи время",
)
def current_time() -> str:
    now = datetime.now()
    return f"Сейчас {now.strftime('%H:%M')}"


@command(
    "какая сегодня дата",
    "скажи дату",
    "какое сегодня число",
)
def current_date() -> str:
    now = datetime.now()
    return f"Сегодня {now.strftime('%d.%m.%Y')}"
