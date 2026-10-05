from ray.core.registry import command
from ray.winutils import power


@command(
    "выключи компьютер", "выключи комп", "выруби компьютер",
    dangerous=True,
    confirm_prompt="Точно выключить компьютер?",
)
def shutdown_computer() -> str:
    power.schedule_shutdown()
    return f"Выключаю компьютер через {power.SHUTDOWN_DELAY_SECONDS} секунд"


@command(
    "перезагрузи компьютер", "перезагрузи комп", "перезагрузка",
    dangerous=True,
    confirm_prompt="Точно перезагрузить компьютер?",
)
def restart_computer() -> str:
    power.schedule_restart()
    return f"Перезагружаю компьютер через {power.SHUTDOWN_DELAY_SECONDS} секунд"


@command(
    "отмени выключение", "отмени перезагрузку", "отмени выключение компьютера",
    "отмена выключения",
)
def cancel_power_action() -> str:
    power.cancel_scheduled_power_action()
    return "Выключение отменено"
