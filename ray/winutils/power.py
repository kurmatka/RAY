import subprocess

from ray.core.errors import CommandError

SHUTDOWN_DELAY_SECONDS = 10
ERROR_NO_SHUTDOWN_IN_PROGRESS = 1116


def _run_shutdown(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["shutdown", *args], capture_output=True, check=False)


def schedule_shutdown() -> None:
    result = _run_shutdown("/s", "/t", str(SHUTDOWN_DELAY_SECONDS))
    if result.returncode != 0:
        raise CommandError("Не удалось запланировать выключение")


def schedule_restart() -> None:
    result = _run_shutdown("/r", "/t", str(SHUTDOWN_DELAY_SECONDS))
    if result.returncode != 0:
        raise CommandError("Не удалось запланировать перезагрузку")


def cancel_scheduled_power_action() -> None:
    result = _run_shutdown("/a")
    if result.returncode == ERROR_NO_SHUTDOWN_IN_PROGRESS:
        raise CommandError("Выключение не запланировано")
    if result.returncode != 0:
        raise CommandError("Не удалось отменить выключение")
