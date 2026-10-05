import os
import subprocess

from ray.core.registry import command
from ray.winutils.launcher import launch_first_existing


CHROME_PATHS = (
    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
    r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
)

DISCORD_UPDATER_PATHS = (
    r"%LocalAppData%\Discord\Update.exe",
)

TELEGRAM_PATHS = (
    r"%AppData%\Telegram Desktop\Telegram.exe",
    r"%LocalAppData%\Telegram Desktop\Telegram.exe",
    r"%ProgramFiles%\Telegram Desktop\Telegram.exe",
)

STEAM_PATHS = (
    r"%ProgramFiles(x86)%\Steam\steam.exe",
    r"%ProgramFiles%\Steam\steam.exe",
)


@command(
    "открой chrome",
    "запусти chrome",
    "открой браузер",
    "открой хром",
    "запусти хром",
    "открой гугл хром",
)
def open_chrome() -> str:
    launch_first_existing("Chrome", CHROME_PATHS)
    return "Открываю Chrome"


@command(
    "открой discord",
    "запусти discord",
    "открой дискорд",
    "запусти дискорд",
    "открой дискомфорт",
    "запусти дискомфорт",
    "открой ди корда",
    "запусти ди корда",
    "открой ди скоро",
    "запусти ди скоро",
    "открой дез корда",
    "запусти дез корда",
    "открой дис корд",
    "запусти дис корд",
)
def open_discord() -> str:
    launch_first_existing(
        "Discord",
        DISCORD_UPDATER_PATHS,
        args=("--processStart", "Discord.exe"),
    )
    return "Открываю Discord"


@command(
    "открой telegram",
    "запусти telegram",
    "открой телеграм",
    "запусти телеграм",
    "открой телеграмм",
    "запусти телеграмм",
)
def open_telegram() -> str:
    launch_first_existing("Telegram", TELEGRAM_PATHS)
    return "Открываю Telegram"


@command(
    "открой steam",
    "запусти steam",
    "открой стим",
    "запусти стим",
)
def open_steam() -> str:
    launch_first_existing("Steam", STEAM_PATHS)
    return "Открываю Steam"


@command(
    "открой проводник",
    "запусти проводник",
)
def open_explorer() -> str:
    subprocess.Popen(["explorer"])
    return "Открываю проводник"


@command(
    "открой диспетчер задач",
    "запусти диспетчер задач",
)
def open_task_manager() -> str:
    os.startfile("taskmgr")
    return "Открываю диспетчер задач"


@command(
    "открой настройки",
    "открой настройки windows",
    "запусти настройки",
)
def open_settings() -> str:
    os.startfile("ms-settings:")
    return "Открываю настройки"