import os
import subprocess
import ctypes
from datetime import datetime

from ray.core.registry import command


# =========================
# ПАПКИ
# =========================

@command(
    "открой рабочий стол",
    "открой десктоп",
)
def open_desktop() -> str:
    os.startfile(os.path.join(os.path.expanduser("~"), "Desktop"))
    return "Открываю рабочий стол"


@command(
    "открой документы",
)
def open_documents() -> str:
    os.startfile(os.path.join(os.path.expanduser("~"), "Documents"))
    return "Открываю документы"


@command(
    "открой загрузки",
    "открой загрузки файлов",
)
def open_downloads() -> str:
    os.startfile(os.path.join(os.path.expanduser("~"), "Downloads"))
    return "Открываю загрузки"


@command(
    "открой картинки",
    "открой изображения",
)
def open_pictures() -> str:
    os.startfile(os.path.join(os.path.expanduser("~"), "Pictures"))
    return "Открываю картинки"


@command(
    "открой музыку",
)
def open_music() -> str:
    os.startfile(os.path.join(os.path.expanduser("~"), "Music"))
    return "Открываю музыку"


@command(
    "открой видео",
)
def open_videos() -> str:
    os.startfile(os.path.join(os.path.expanduser("~"), "Videos"))
    return "Открываю видео"


# =========================
# СТАНДАРТНЫЕ ПРОГРАММЫ
# =========================

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
    "открой командную строку windows",
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


# =========================
# УПРАВЛЕНИЕ WINDOWS
# =========================

@command(
    "покажи рабочий стол",
    "сверни все окна",
)
def show_desktop() -> str:
    subprocess.Popen(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "(New-Object -ComObject Shell.Application).MinimizeAll()",
        ]
    )
    return "Показываю рабочий стол"


@command(
    "заблокируй компьютер",
    dangerous=True,
    confirm_prompt="Заблокировать компьютер?",
)
def lock_computer() -> str:
    ctypes.windll.user32.LockWorkStation()
    return "Компьютер заблокирован"


@command(
    "выключи компьютер",
    dangerous=True,
    confirm_prompt="Выключить компьютер?",
)
def shutdown_computer() -> str:
    subprocess.Popen(["shutdown", "/s", "/t", "5"])
    return "Компьютер будет выключен через 5 секунд"


@command(
    "перезагрузи компьютер",
    "перезапусти компьютер",
    dangerous=True,
    confirm_prompt="Перезагрузить компьютер?",
)
def restart_computer() -> str:
    subprocess.Popen(["shutdown", "/r", "/t", "5"])
    return "Компьютер будет перезагружен через 5 секунд"


# =========================
# ВРЕМЯ И ДАТА
# =========================

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


# =========================
# ИНФОРМАЦИЯ О СИСТЕМЕ
# =========================

@command(
    "какая система",
    "какая операционная система",
    "какая у меня виндовс",
)
def system_info() -> str:
    return f"У тебя Windows {os.sys.getwindowsversion().major}"


@command(
    "какой процессор",
    "какой у меня процессор",
)
def cpu_info() -> str:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "(Get-CimInstance Win32_Processor).Name",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    cpu = result.stdout.strip()

    if not cpu:
        return "Не удалось определить процессор"

    return f"Твой процессор: {cpu}"


@command(
    "сколько оперативной памяти",
    "сколько у меня оперативной памяти",
)
def ram_info() -> str:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    ram = result.stdout.strip()

    if not ram:
        return "Не удалось определить оперативную память"

    return f"У тебя {ram} гигабайт оперативной памяти"