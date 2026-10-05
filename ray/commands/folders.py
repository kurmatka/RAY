import os

from ray.core.registry import command


@command("открой загрузки", "открой папку загрузки")
def open_downloads() -> str:
    os.startfile("shell:Downloads")
    return "Открываю Загрузки"


@command("открой рабочий стол", "открой папку рабочий стол")
def open_desktop() -> str:
    os.startfile("shell:Desktop")
    return "Открываю Рабочий стол"


@command("открой документы", "открой папку документы")
def open_documents() -> str:
    os.startfile("shell:Personal")
    return "Открываю Документы"
