import re
import webbrowser

from ray.core.registry import command, command_pattern


@command(
    "открой youtube",
    "открой ютуб",
    "запусти youtube",
    "запусти ютуб",
)
def open_youtube() -> str:
    webbrowser.open("https://www.youtube.com")
    return "Открываю YouTube"


@command(
    "открой google",
    "открой гугл",
    "запусти google",
    "запусти гугл",
)
def open_google() -> str:
    webbrowser.open("https://www.google.com")
    return "Открываю Google"


@command(
    "открой github",
    "открой гитхаб",
    "запусти github",
    "запусти гитхаб",
)
def open_github() -> str:
    webbrowser.open("https://github.com")
    return "Открываю GitHub"


@command_pattern(
    r"(?:открой|запусти) сайт "
    r"(?P<domain>[a-zа-я0-9-]+) "
    r"(?:точка|\.) "
    r"(?P<tld>[a-zа-я]{2,})"
)
def open_website(match: re.Match) -> str:
    domain = match.group("domain")
    tld = match.group("tld")

    url = f"https://{domain}.{tld}"

    webbrowser.open(url)

    return f"Открываю {domain}.{tld}"