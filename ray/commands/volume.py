import re

from ray.core.registry import command, command_pattern
from ray.winutils import audio

VOLUME_STEP_PERCENT = 10


@command("сделай громче", "увеличь громкость", "прибавь громкость", "громче")
def volume_up() -> str:
    percent = audio.set_volume_percent(audio.get_volume_percent() + VOLUME_STEP_PERCENT)
    return f"Громкость {percent} процентов"


@command("сделай тише", "уменьши громкость", "убавь громкость", "тише")
def volume_down() -> str:
    percent = audio.set_volume_percent(audio.get_volume_percent() - VOLUME_STEP_PERCENT)
    return f"Громкость {percent} процентов"


@command("выключи звук", "отключи звук", "без звука")
def mute() -> str:
    audio.set_muted(True)
    return "Звук выключен"


@command("включи звук", "верни звук")
def unmute() -> str:
    audio.set_muted(False)
    return "Звук включён"


@command_pattern(r"(?:сделай |поставь |установи )?громкость (?:на )?(\d{1,3})(?: процент\w*)?")
def set_volume(match: re.Match) -> str:
    percent = audio.set_volume_percent(int(match.group(1)))
    return f"Громкость {percent} процентов"
