import logging
import math
import threading
import time
import tkinter as tk
from datetime import datetime

from ray import commands  # noqa: F401
from ray.config import Config
from ray.core.command_processor import CommandProcessor
from ray.core.registry import registry
from ray.core.tts import TextToSpeech
from ray.core.voice import VoiceRecognizer
from ray.logging_setup import setup_logging


logger = logging.getLogger("ray.ui")

MODEL_PATH = "models/vosk-model-small-ru-0.22"


# ============================================================
# COLORS
# ============================================================

BG = "#02050c"
SIDEBAR = "#050914"
PANEL = "#07111f"
PANEL_2 = "#091628"

CYAN = "#32d9ff"
BLUE = "#557cff"
PURPLE = "#a66cff"
MAGENTA = "#d85cff"
GREEN = "#20e6a0"
RED = "#ff5577"

TEXT = "#eef5ff"
MUTED = "#8296b8"
DIM = "#465978"
BORDER = "#17345d"


class RayUI:

    def __init__(self, root):

        self.root = root

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.root.title("RAY")
        self.root.geometry("1450x900")
        self.root.minsize(1150, 720)
        self.root.configure(bg=BG)

        self.root.overrideredirect(True)

        self.window_x = 0
        self.window_y = 0
        self.is_maximized = False
        self.normal_geometry = "1450x900"

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.running = False
        self.processing = False
        self.closing = False

        self.voice_thread = None

        self.history = []
        self.nav_buttons = {}

        # ----------------------------------------------------
        # RAY ENGINE
        # ----------------------------------------------------

        config = Config.load()

        setup_logging(
            config.log_level
        )

        self.processor = CommandProcessor(
            registry
        )

        self.recognizer = VoiceRecognizer(
            MODEL_PATH
        )

        self.speaker = TextToSpeech()

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.build_layout()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close,
        )

        self.animate()
        self.update_clock()
        self.root.after(500, self.start_ray)

    # ========================================================
    # BUILD
    # ========================================================

    def build_layout(self):

        self.root.grid_rowconfigure(
            1,
            weight=1,
        )

        self.root.grid_columnconfigure(
            0,
            weight=1,
        )

        self.create_titlebar()
        self.create_main_area()

    # ========================================================
    # TITLEBAR
    # ========================================================

    def create_titlebar(self):

        self.titlebar = tk.Frame(
            self.root,
            bg="#030711",
            height=42,
        )

        self.titlebar.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self.titlebar.grid_propagate(
            False
        )

        # LEFT

        left = tk.Frame(
            self.titlebar,
            bg="#030711",
        )

        left.pack(
            side="left",
            fill="y",
        )

        self.drag_widgets = [
            self.titlebar,
            left,
        ]

        logo = tk.Label(
            left,
            text="✦",
            bg="#030711",
            fg=CYAN,
            font=("Segoe UI Symbol", 17),
        )

        logo.pack(
            side="left",
            padx=(15, 8),
        )

        name = tk.Label(
            left,
            text="RAY",
            bg="#030711",
            fg=TEXT,
            font=("Segoe UI", 9, "bold"),
        )

        name.pack(
            side="left"
        )

        subtitle = tk.Label(
            left,
            text="VOICE INTELLIGENCE",
            bg="#030711",
            fg=DIM,
            font=("Segoe UI", 7),
        )

        subtitle.pack(
            side="left",
            padx=12,
        )

        self.drag_widgets.extend([
            logo,
            name,
            subtitle,
        ])

        # RIGHT

        controls = tk.Frame(
            self.titlebar,
            bg="#030711",
        )

        controls.pack(
            side="right",
            fill="y",
        )

        # MINIMIZE

        minimize = tk.Label(
            controls,
            text="—",
            bg="#030711",
            fg=MUTED,
            font=("Segoe UI", 12),
            width=5,
            cursor="hand2",
        )

        minimize.pack(
            side="left",
            fill="y",
        )

        minimize.bind(
            "<Button-1>",
            lambda event: self.minimize_window(),
        )

        # MAXIMIZE

        maximize = tk.Label(
            controls,
            text="□",
            bg="#030711",
            fg=MUTED,
            font=("Segoe UI", 11),
            width=5,
            cursor="hand2",
        )

        maximize.pack(
            side="left",
            fill="y",
        )

        maximize.bind(
            "<Button-1>",
            lambda event: self.toggle_maximize(),
        )

        # CLOSE

        close = tk.Label(
            controls,
            text="×",
            bg="#030711",
            fg=MUTED,
            font=("Segoe UI", 16),
            width=5,
            cursor="hand2",
        )

        close.pack(
            side="left",
            fill="y",
        )

        close.bind(
            "<Enter>",
            lambda event: close.configure(
                bg=RED,
                fg=TEXT,
            ),
        )

        close.bind(
            "<Leave>",
            lambda event: close.configure(
                bg="#030711",
                fg=MUTED,
            ),
        )

        close.bind(
            "<Button-1>",
            lambda event: self.close(),
        )

        # DRAG

        for widget in self.drag_widgets:

            widget.bind(
                "<Button-1>",
                self.start_move,
            )

            widget.bind(
                "<B1-Motion>",
                self.do_move,
            )

    # ========================================================
    # WINDOW CONTROL
    # ========================================================

    def start_move(self, event):

        self.window_x = event.x_root
        self.window_y = event.y_root

        self.start_geometry = (
            self.root.geometry()
        )

    def do_move(self, event):

        if self.is_maximized:
            return

        dx = event.x_root - self.window_x
        dy = event.y_root - self.window_y

        geometry = self.root.geometry()

        try:

            size, x, y = geometry.split(
                "+"
            )

            new_x = int(x) + dx
            new_y = int(y) + dy

            self.root.geometry(
                f"{size}+{new_x}+{new_y}"
            )

            self.window_x = event.x_root
            self.window_y = event.y_root

        except ValueError:
            pass

    def minimize_window(self):

        self.root.overrideredirect(
            False
        )

        self.root.iconify()

        self.root.after(
            200,
            lambda: self.root.overrideredirect(
                True
            ),
        )

    def toggle_maximize(self):

        if not self.is_maximized:

            self.normal_geometry = (
                self.root.geometry()
            )

            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()

            self.root.geometry(
                f"{width}x{height}+0+0"
            )

            self.is_maximized = True

        else:

            self.root.geometry(
                self.normal_geometry
            )

            self.is_maximized = False

    # ========================================================
    # MAIN AREA
    # ========================================================

    def create_main_area(self):

        self.main_area = tk.Frame(
            self.root,
            bg=BG,
        )

        self.main_area.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        self.main_area.grid_columnconfigure(
            1,
            weight=1,
        )

        self.main_area.grid_rowconfigure(
            0,
            weight=1,
        )

        self.create_sidebar()
        self.create_center()
        self.create_right_panel()

        self.create_pages()

    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):

        sidebar = tk.Frame(
            self.main_area,
            bg=SIDEBAR,
            width=250,
        )

        sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        sidebar.grid_propagate(
            False
        )

        # LOGO

        logo = tk.Frame(
            sidebar,
            bg=SIDEBAR,
        )

        logo.pack(
            fill="x",
            padx=25,
            pady=(25, 10),
        )

        tk.Label(
            logo,
            text="✦",
            bg=SIDEBAR,
            fg=CYAN,
            font=("Segoe UI Symbol", 30),
        ).pack(
            side="left"
        )

        text_frame = tk.Frame(
            logo,
            bg=SIDEBAR,
        )

        text_frame.pack(
            side="left",
            padx=10,
        )

        tk.Label(
            text_frame,
            text="RAY",
            bg=SIDEBAR,
            fg=TEXT,
            font=("Segoe UI", 27, "bold"),
        ).pack(
            anchor="w"
        )

        tk.Label(
            text_frame,
            text="Voice Intelligence",
            bg=SIDEBAR,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(
            anchor="w"
        )

        # NAVIGATION

        navigation = tk.Frame(
            sidebar,
            bg=SIDEBAR,
        )

        navigation.pack(
            fill="x",
            padx=15,
            pady=30,
        )

        self.nav_buttons["home"] = self.nav_button(
            navigation,
            "◉",
            "Главная",
            "home",
            True,
        )

        self.nav_buttons["commands"] = self.nav_button(
            navigation,
            "ϟ",
            "Команды",
            "commands",
        )

        self.nav_buttons["apps"] = self.nav_button(
            navigation,
            "▦",
            "Приложения",
            "apps",
        )

        self.nav_buttons["settings"] = self.nav_button(
            navigation,
            "⚙",
            "Настройки",
            "settings",
        )

        # STATUS

        status = tk.Frame(
            sidebar,
            bg="#06101c",
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        status.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=18,
        )

        row = tk.Frame(
            status,
            bg="#06101c",
        )

        row.pack(
            fill="x",
            padx=12,
            pady=(12, 3),
        )

        self.online_dot = tk.Label(
            row,
            text="●",
            bg="#06101c",
            fg=GREEN,
            font=("Segoe UI", 11),
        )

        self.online_dot.pack(
            side="left"
        )

        self.online_text = tk.Label(
            row,
            text="Рей онлайн",
            bg="#06101c",
            fg=TEXT,
            font=("Segoe UI", 9, "bold"),
        )

        self.online_text.pack(
            side="left",
            padx=7,
        )

        self.sidebar_status = tk.Label(
            status,
            text="Готов слушать твой голос",
            bg="#06101c",
            fg=MUTED,
            font=("Segoe UI", 8),
        )

        self.sidebar_status.pack(
            anchor="w",
            padx=12,
            pady=(0, 13),
        )

    def nav_button(
        self,
        parent,
        icon,
        text,
        page,
        active=False,
    ):

        bg = (
            "#17277a"
            if active
            else SIDEBAR
        )

        border = (
            "#675cff"
            if active
            else SIDEBAR
        )

        button = tk.Frame(
            parent,
            bg=bg,
            highlightbackground=border,
            highlightthickness=1,
            cursor="hand2",
        )

        button.pack(
            fill="x",
            pady=4,
        )

        icon_label = tk.Label(
            button,
            text=icon,
            bg=bg,
            fg=CYAN if active else MUTED,
            font=("Segoe UI Symbol", 17),
        )

        icon_label.pack(
            side="left",
            padx=(15, 12),
            pady=9,
        )

        text_label = tk.Label(
            button,
            text=text,
            bg=bg,
            fg=TEXT if active else MUTED,
            font=(
                "Segoe UI",
                9,
                "bold" if active else "normal",
            ),
        )

        text_label.pack(
            side="left",
            pady=9,
        )

        def click(event=None):
            self.show_page(page)

        button.bind(
            "<Button-1>",
            click,
        )

        icon_label.bind(
            "<Button-1>",
            click,
        )

        text_label.bind(
            "<Button-1>",
            click,
        )

        return button

    # ========================================================
    # CENTER
    # ========================================================

    def create_center(self):

        center = tk.Frame(
            self.main_area,
            bg=BG,
        )

        center.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        center.grid_columnconfigure(
            0,
            weight=1,
        )

        center.grid_rowconfigure(
            1,
            weight=1,
        )

        # TOP

        top = tk.Frame(
            center,
            bg=BG,
            height=60,
        )

        top.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
        )

        top.grid_propagate(False)

        self.system_status = tk.Label(
            top,
            text="● SYSTEM ONLINE",
            bg=BG,
            fg=GREEN,
            font=("Segoe UI", 8, "bold"),
        )

        self.system_status.pack(
            side="left",
            pady=20,
        )

        self.clock = tk.Label(
            top,
            text="",
            bg=BG,
            fg=MUTED,
            font=("Consolas", 8),
        )

        self.clock.pack(
            side="right",
            pady=20,
        )

        # CONTENT

        content = tk.Frame(
            center,
            bg=BG,
        )

        content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=30,
        )

        tk.Label(
            content,
            text="Привет! Я",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 26, "bold"),
        ).pack(
            pady=(15, 0),
        )

        tk.Label(
            content,
            text="Рей",
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 40, "bold"),
        ).pack()

        tk.Label(
            content,
            text="Говори команду, и я помогу",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(
            pady=(0, 4),
        )

        # CORE

        self.canvas = tk.Canvas(
            content,
            width=500,
            height=300,
            bg=BG,
            highlightthickness=0,
        )

        self.canvas.pack()

        self.animation_time = 0

        # STATE

        state = tk.Frame(
            content,
            bg=BG,
        )

        state.pack(
            pady=(0, 7),
        )

        self.state_dot = tk.Label(
            state,
            text="●",
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 11),
        )

        self.state_dot.pack(
            side="left"
        )

        self.state_text = tk.Label(
            state,
            text="Готов",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 9, "bold"),
        )

        self.state_text.pack(
            side="left",
            padx=7,
        )

        # SUGGESTION

        suggestion = tk.Frame(
            content,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        suggestion.pack(
            fill="x",
            padx=25,
            pady=5,
        )

        tk.Label(
            suggestion,
            text="ϟ",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI Symbol", 17),
        ).pack(
            side="left",
            padx=(15, 10),
            pady=8,
        )

        tk.Label(
            suggestion,
            text="«Открой YouTube»  ·  «Открой Discord»  ·  «Открой GitHub»",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(
            side="left",
            pady=8,
        )

        # CONTROL

        control = tk.Frame(
            content,
            bg=PANEL_2,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        control.pack(
            fill="x",
            padx=10,
            pady=12,
        )

        tk.Label(
            control,
            text="ϟ",
            bg=PANEL_2,
            fg=CYAN,
            font=("Segoe UI Symbol", 22),
        ).pack(
            side="left",
            padx=(18, 12),
            pady=10,
        )

        info = tk.Frame(
            control,
            bg=PANEL_2,
        )

        info.pack(
            side="left",
            pady=9,
        )

        tk.Label(
            info,
            text="Голосовое управление",
            bg=PANEL_2,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(
            anchor="w"
        )

        tk.Label(
            info,
            text="Скажи «Рэй» и затем команду",
            bg=PANEL_2,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(
            anchor="w"
        )

        self.start_button = tk.Button(
            control,
            text="●",
            command=self.toggle,
            bg="#17185f",
            fg=CYAN,
            activebackground="#28258b",
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            font=("Segoe UI", 21),
            width=3,
            cursor="hand2",
        )

        self.start_button.pack(
            side="right",
            padx=14,
            pady=9,
        )

        # LOG

        log_panel = tk.Frame(
            content,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        log_panel.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10),
        )

        tk.Label(
            log_panel,
            text="LIVE LOG",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 8, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=(9, 3),
        )

        self.log = tk.Text(
            log_panel,
            bg=PANEL,
            fg=MUTED,
            font=("Consolas", 8),
            relief="flat",
            bd=0,
            height=3,
            state="disabled",
            wrap="word",
        )

        self.log.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 8),
        )

    # ========================================================
    # RIGHT PANEL
    # ========================================================

    def create_right_panel(self):

        right = tk.Frame(
            self.main_area,
            bg=BG,
            width=350,
        )

        right.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=(0, 18),
        )

        right.grid_propagate(False)

        header = tk.Frame(
            right,
            bg=BG,
            height=45,
        )

        header.pack(
            fill="x",
        )

        tk.Label(
            header,
            text="RAY CONTROL",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(
            side="left",
            pady=14,
        )

        # HISTORY

        history = tk.Frame(
            right,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        history.pack(
            fill="x",
            pady=5,
        )

        tk.Label(
            history,
            text="◷  Последние команды",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=(13, 8),
        )

        self.history_box = tk.Frame(
            history,
            bg=PANEL,
        )

        self.history_box.pack(
            fill="x",
            padx=10,
            pady=(0, 9),
        )

        # POPULAR

        popular = tk.Frame(
            right,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        popular.pack(
            fill="x",
            pady=5,
        )

        tk.Label(
            popular,
            text="☆  Популярные команды",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=(13, 8),
        )

        grid = tk.Frame(
            popular,
            bg=PANEL,
        )

        grid.pack(
            fill="x",
            padx=10,
            pady=(0, 9),
        )

        buttons = [
            ("▶", "YouTube", "открой ютуб"),
            ("G", "Google", "открой гугл"),
            ("●", "GitHub", "открой гитхаб"),
            ("D", "Discord", "открой discord"),
            ("T", "Telegram", "открой telegram"),
            ("S", "Steam", "открой steam"),
        ]

        for i, (
            icon,
            name,
            command,
        ) in enumerate(buttons):

            row = i // 3
            column = i % 3

            grid.grid_columnconfigure(
                column,
                weight=1,
            )

            cell = tk.Frame(
                grid,
                bg="#08162a",
                highlightbackground=BORDER,
                highlightthickness=1,
                cursor="hand2",
            )

            cell.grid(
                row=row,
                column=column,
                padx=3,
                pady=3,
                sticky="nsew",
            )

            icon_label = tk.Label(
                cell,
                text=icon,
                bg="#08162a",
                fg=CYAN if i < 3 else PURPLE,
                font=("Segoe UI", 16, "bold"),
            )

            icon_label.pack(
                pady=(7, 1)
            )

            name_label = tk.Label(
                cell,
                text=name,
                bg="#08162a",
                fg=TEXT,
                font=("Segoe UI", 7),
            )

            name_label.pack(
                pady=(0, 7)
            )

            def launch(
                event=None,
                cmd=command,
            ):

                self.run_command(cmd)

            cell.bind(
                "<Button-1>",
                launch,
            )

            icon_label.bind(
                "<Button-1>",
                launch,
            )

            name_label.bind(
                "<Button-1>",
                launch,
            )

        # SYSTEM

        system = tk.Frame(
            right,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        system.pack(
            fill="x",
            pady=5,
        )

        tk.Label(
            system,
            text="ϟ  Система",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=(13, 8),
        )

        self.meter(
            system,
            "♩",
            "Микрофон",
            85,
            CYAN,
        )

        self.meter(
            system,
            "◎",
            "Интернет",
            68,
            BLUE,
        )

        self.meter(
            system,
            "◖",
            "Громкость",
            78,
            PURPLE,
        )

        # TIP

        tip = tk.Frame(
            right,
            bg="#0a1128",
            highlightbackground="#302774",
            highlightthickness=1,
        )

        tip.pack(
            fill="x",
            pady=5,
        )

        tk.Label(
            tip,
            text="NEURAL TIP",
            bg="#0a1128",
            fg=PURPLE,
            font=("Segoe UI", 8, "bold"),
        ).pack(
            anchor="w",
            padx=15,
            pady=(12, 4),
        )

        tk.Label(
            tip,
            text=(
                "Скажи «Рэй», затем команду.\n\n"
                "Например:\n"
                "«Рэй, открой YouTube»"
            ),
            bg="#0a1128",
            fg=MUTED,
            font=("Segoe UI", 8),
            justify="left",
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 12),
        )

    def meter(
        self,
        parent,
        icon,
        name,
        value,
        color,
    ):

        row = tk.Frame(
            parent,
            bg=PANEL,
        )

        row.pack(
            fill="x",
            padx=15,
            pady=4,
        )

        tk.Label(
            row,
            text=icon,
            bg=PANEL,
            fg=color,
            font=("Segoe UI Symbol", 11),
        ).pack(
            side="left"
        )

        tk.Label(
            row,
            text=name,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(
            side="left",
            padx=7,
        )

        background = tk.Frame(
            row,
            bg="#101d32",
            width=105,
            height=6,
        )

        background.pack(
            side="right"
        )

        background.pack_propagate(False)

        tk.Frame(
            background,
            bg=color,
            width=value,
            height=6,
        ).pack(
            side="left"
        )

    # ========================================================
    # PAGES
    # ========================================================

    def create_pages(self):

        self.page_layer = tk.Frame(
            self.main_area,
            bg=BG,
        )

        self.page_layer.place(
            relx=0.0,
            rely=0.0,
            relwidth=1.0,
            relheight=1.0,
        )

        self.page_layer.place_forget()

    def clear_page_layer(self):

        for widget in (
            self.page_layer.winfo_children()
        ):

            widget.destroy()

    def show_page(self, page):

        if page == "home":

            self.page_layer.place_forget()

            self.set_nav_colors(
                "home"
            )

            return

        self.page_layer.place(
            relx=0.0,
            rely=0.0,
            relwidth=1.0,
            relheight=1.0,
        )

        self.clear_page_layer()

        if page == "commands":
            self.create_commands_page()

        elif page == "apps":
            self.create_apps_page()

        elif page == "settings":
            self.create_settings_page()

        self.set_nav_colors(
            page
        )

    def set_nav_colors(
        self,
        active_page,
    ):

        for name, button in (
            self.nav_buttons.items()
        ):

            active = (
                name == active_page
            )

            bg = (
                "#17277a"
                if active
                else SIDEBAR
            )

            border = (
                "#675cff"
                if active
                else SIDEBAR
            )

            button.configure(
                bg=bg,
                highlightbackground=border,
            )

            children = (
                button.winfo_children()
            )

            for index, child in enumerate(
                children
            ):

                child.configure(
                    bg=bg,
                    fg=(
                        CYAN
                        if index == 0 and active
                        else (
                            TEXT
                            if active
                            else MUTED
                        )
                    ),
                )

    # ========================================================
    # COMMANDS PAGE
    # ========================================================

    def create_commands_page(self):

        page = tk.Frame(
            self.page_layer,
            bg=BG,
        )

        page.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=35,
        )

        tk.Label(
            page,
            text="КОМАНДЫ",
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 30, "bold"),
        ).pack(
            anchor="w"
        )

        tk.Label(
            page,
            text="Команды, которые Рей понимает прямо сейчас",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(
            anchor="w",
            pady=(3, 25),
        )

        cards = tk.Frame(
            page,
            bg=BG,
        )

        cards.pack(
            fill="both",
            expand=True,
        )

        categories = [
            (
                "БРАУЗЕР",
                [
                    "открой YouTube",
                    "открой Google",
                    "открой GitHub",
                    "открой сайт wikipedia.org",
                ],
            ),
            (
                "ПРИЛОЖЕНИЯ",
                [
                    "открой Chrome",
                    "открой Discord",
                    "открой Telegram",
                    "открой Steam",
                ],
            ),
            (
                "WINDOWS",
                [
                    "открой проводник",
                    "открой настройки",
                    "открой диспетчер задач",
                ],
            ),
        ]

        for column, (
            title,
            items,
        ) in enumerate(categories):

            cards.grid_columnconfigure(
                column,
                weight=1,
            )

            card = tk.Frame(
                cards,
                bg=PANEL,
                highlightbackground=BORDER,
                highlightthickness=1,
            )

            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=7,
            )

            tk.Label(
                card,
                text=title,
                bg=PANEL,
                fg=PURPLE,
                font=("Segoe UI", 9, "bold"),
            ).pack(
                anchor="w",
                padx=18,
                pady=(18, 12),
            )

            for command in items:

                row = tk.Frame(
                    card,
                    bg="#081528",
                    highlightbackground=BORDER,
                    highlightthickness=1,
                    cursor="hand2",
                )

                row.pack(
                    fill="x",
                    padx=12,
                    pady=4,
                )

                tk.Label(
                    row,
                    text="›",
                    bg="#081528",
                    fg=CYAN,
                    font=("Segoe UI", 13, "bold"),
                ).pack(
                    side="left",
                    padx=(10, 7),
                    pady=8,
                )

                label = tk.Label(
                    row,
                    text=command,
                    bg="#081528",
                    fg=TEXT,
                    font=("Segoe UI", 8),
                )

                label.pack(
                    side="left",
                    pady=8,
                )

    # ========================================================
    # APPLICATIONS PAGE
    # ========================================================

    def create_apps_page(self):

        page = tk.Frame(
            self.page_layer,
            bg=BG,
        )

        page.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=35,
        )

        tk.Label(
            page,
            text="ПРИЛОЖЕНИЯ",
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 30, "bold"),
        ).pack(
            anchor="w"
        )

        tk.Label(
            page,
            text="Запускай приложения одним нажатием",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(
            anchor="w",
            pady=(3, 25),
        )

        grid = tk.Frame(
            page,
            bg=BG,
        )

        grid.pack(
            fill="both",
            expand=True,
        )

        apps = [
            ("▶", "YouTube", "открой ютуб", CYAN),
            ("G", "Google", "открой гугл", BLUE),
            ("◈", "GitHub", "открой гитхаб", PURPLE),
            ("D", "Discord", "открой discord", MAGENTA),
            ("T", "Telegram", "открой telegram", CYAN),
            ("S", "Steam", "открой steam", BLUE),
            ("▣", "Проводник", "открой проводник", GREEN),
            ("⚙", "Настройки", "открой настройки", PURPLE),
        ]

        for index, (
            icon,
            name,
            command,
            color,
        ) in enumerate(apps):

            row = index // 4
            column = index % 4

            grid.grid_columnconfigure(
                column,
                weight=1,
            )

            card = tk.Frame(
                grid,
                bg=PANEL,
                highlightbackground=BORDER,
                highlightthickness=1,
                cursor="hand2",
            )

            card.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=6,
                pady=6,
            )

            icon_label = tk.Label(
                card,
                text=icon,
                bg=PANEL,
                fg=color,
                font=("Segoe UI", 25, "bold"),
            )

            icon_label.pack(
                pady=(25, 8)
            )

            name_label = tk.Label(
                card,
                text=name,
                bg=PANEL,
                fg=TEXT,
                font=("Segoe UI", 10, "bold"),
            )

            name_label.pack(
                pady=(0, 22)
            )

            def launch(
                event=None,
                cmd=command,
            ):

                self.run_command(
                    cmd
                )

            card.bind(
                "<Button-1>",
                launch,
            )

            icon_label.bind(
                "<Button-1>",
                launch,
            )

            name_label.bind(
                "<Button-1>",
                launch,
            )

    # ========================================================
    # SETTINGS
    # ========================================================

    def create_settings_page(self):

        page = tk.Frame(
            self.page_layer,
            bg=BG,
        )

        page.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=35,
        )

        tk.Label(
            page,
            text="НАСТРОЙКИ",
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 30, "bold"),
        ).pack(
            anchor="w"
        )

        tk.Label(
            page,
            text="Конфигурация голосового ассистента",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(
            anchor="w",
            pady=(3, 25),
        )

        card = tk.Frame(
            page,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        card.pack(
            fill="x",
        )

        self.setting_row(
            card,
            "Голосовой движок",
            "Vosk",
            GREEN,
        )

        self.setting_row(
            card,
            "Язык",
            "Русский",
            CYAN,
        )

        self.setting_row(
            card,
            "Синтез речи",
            "Windows TTS",
            PURPLE,
        )

        self.setting_row(
            card,
            "Микрофон",
            "G435 Wireless Gaming",
            GREEN,
        )

        self.setting_row(
            card,
            "Модель",
            "vosk-model-small-ru-0.22",
            BLUE,
        )

        control = tk.Frame(
            page,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        control.pack(
            fill="x",
            pady=18,
        )

        tk.Label(
            control,
            text="УПРАВЛЕНИЕ",
            bg=PANEL,
            fg=PURPLE,
            font=("Segoe UI", 9, "bold"),
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 10),
        )

        tk.Button(
            control,
            text="ЗАПУСТИТЬ РЕЯ",
            command=self.start_ray,
            bg="#16245c",
            fg=CYAN,
            activebackground="#263b8a",
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=20,
            pady=10,
        ).pack(
            side="left",
            padx=18,
            pady=(0, 18),
        )

        tk.Button(
            control,
            text="ОСТАНОВИТЬ",
            command=self.stop_ray,
            bg="#351629",
            fg=RED,
            activebackground="#54213a",
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=20,
            pady=10,
        ).pack(
            side="left",
            pady=(0, 18),
        )

    def setting_row(
        self,
        parent,
        name,
        value,
        color,
    ):

        row = tk.Frame(
            parent,
            bg="#081528",
            highlightbackground=BORDER,
            highlightthickness=1,
        )

        row.pack(
            fill="x",
            padx=12,
            pady=4,
        )

        tk.Label(
            row,
            text=name,
            bg="#081528",
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(
            side="left",
            padx=14,
            pady=11,
        )

        tk.Label(
            row,
            text=value,
            bg="#081528",
            fg=color,
            font=("Consolas", 8, "bold"),
        ).pack(
            side="right",
            padx=14,
            pady=11,
        )

    # ========================================================
    # ANIMATION
    # ========================================================

    def animate(self):

        if self.closing:
            return

        self.animation_time += 0.08

        self.canvas.delete(
            "all"
        )

        cx = 250
        cy = 135

        pulse = (
            math.sin(
                self.animation_time
            ) + 1
        ) / 2

        # OUTER RINGS

        for radius, color, width in [
            (120 + pulse * 8, "#102653", 2),
            (98 + pulse * 6, "#173c7c", 2),
            (76 + pulse * 4, "#2d5bd1", 3),
        ]:

            self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                outline=color,
                width=width,
            )

        # CORE

        self.canvas.create_oval(
            cx - 58,
            cy - 58,
            cx + 58,
            cy + 58,
            fill="#07162c",
            outline=CYAN,
            width=3,
        )

        self.canvas.create_oval(
            cx - 40,
            cy - 40,
            cx + 40,
            cy + 40,
            fill="#0a1f40",
            outline=PURPLE,
            width=2,
        )

        # EYES

        self.canvas.create_oval(
            cx - 25,
            cy - 18,
            cx - 10,
            cy - 3,
            fill=CYAN,
            outline="",
        )

        self.canvas.create_oval(
            cx + 10,
            cy - 18,
            cx + 25,
            cy - 3,
            fill=CYAN,
            outline="",
        )

        # MOUTH

        self.canvas.create_arc(
            cx - 18,
            cy - 3,
            cx + 18,
            cy + 25,
            start=205,
            extent=130,
            style="arc",
            outline=PURPLE,
            width=3,
        )

        # WAVES

        for index, color in enumerate(
            [CYAN, PURPLE, MAGENTA]
        ):

            points = []

            for x in range(
                20,
                481,
                5,
            ):

                amplitude = (
                    10
                    if self.running
                    else 3
                )

                y = (
                    cy
                    + 125
                    + math.sin(
                        x * 0.055
                        + self.animation_time
                        + index
                    )
                    * amplitude
                )

                points.extend(
                    [x, y]
                )

            self.canvas.create_line(
                *points,
                fill=color,
                width=(
                    2
                    if index == 1
                    else 1
                ),
                smooth=True,
            )

        self.root.after(
            40,
            self.animate,
        )

    # ========================================================
    # VOICE
    # ========================================================

    def toggle(self):

        if self.running:
            self.stop_ray()
        else:
            self.start_ray()

    def start_ray(self):

        if self.running:
            return

        self.running = True

        self.start_button.configure(
            text="■",
            fg=RED,
        )

        self.set_state(
            "Ожидание «Рей»...",
            CYAN,
        )

        self.set_online(
            True
        )

        self.log_message(
            "SYSTEM",
            "Рей запущен. Жду ключевое слово «Рей»",
        )

        self.voice_thread = threading.Thread(
            target=self.voice_loop,
            daemon=True,
        )

        self.voice_thread.start()

    def stop_ray(self):

        self.running = False

        self.start_button.configure(
            text="●",
            fg=CYAN,
        )

        self.set_state(
            "Остановлен",
            RED,
        )

        self.set_online(
            False
        )

        self.log_message(
            "SYSTEM",
            "Рей остановлен",
        )

    def voice_loop(self):

        while self.running:

            try:

                # ------------------------------------------------
                # 1. РЕЖИМ ОЖИДАНИЯ
                # ------------------------------------------------

                self.ui_state(
                    "Ожидание «Рей»...",
                    CYAN,
                )

                text = self.recognizer.listen_once(
                    timeout=1
                )

                if not text:
                    continue

                text = text.strip()

                self.ui_log(
                    "heard",
                    text,
                )

                lower = text.lower()
                words = lower.split()

                # ------------------------------------------------
                # 2. ПРОВЕРЯЕМ КЛЮЧЕВОЕ СЛОВО
                # ------------------------------------------------

                if (
                    "рей" not in words
                    and "рэй" not in words
                ):
                    continue

                self.ui_state(
                    "Рей активирован",
                    GREEN,
                )

                self.ui_log(
                    "wake",
                    "Ключевое слово распознано",
                )

                # ------------------------------------------------
                # 3. ДОСТАЁМ КОМАНДУ ПОСЛЕ «РЕЙ»
                # ------------------------------------------------

                command = ""

                if "рей" in words:

                    index = words.index("рей")

                    command = " ".join(
                        words[index + 1:]
                    ).strip()

                elif "рэй" in words:

                    index = words.index("рэй")

                    command = " ".join(
                        words[index + 1:]
                    ).strip()

                # ------------------------------------------------
                # 4. ЕСЛИ КОМАНДЫ НЕТ — ЖДЁМ ЕЁ
                # ------------------------------------------------

                if not command:

                    self.ui_state(
                        "Жду команду...",
                        GREEN,
                    )

                    self.ui_log(
                        "dialog",
                        "Рей активирован. Жду команду...",
                    )

                    command = self.recognizer.listen_once(
                        timeout=10
                    )

                    if not command:

                        self.ui_log(
                            "dialog",
                            "Время ожидания истекло",
                        )

                        continue

                    command = command.strip()

                    self.ui_log(
                        "command",
                        command,
                    )

                # ------------------------------------------------
                # 5. КОМАНДА
                # ------------------------------------------------

                command_lower = command.lower().strip()

                # Выход из диалога
                if command_lower in {
                    "выход",
                    "выйди",
                    "пока",
                    "отмена",
                    "отменить",
                }:

                    self.ui_log(
                        "dialog",
                        "Диалог отменён",
                    )

                    self.ui_state(
                        "Ожидание «Рей»...",
                        CYAN,
                    )

                    continue

                # ------------------------------------------------
                # 6. ВЫПОЛНЯЕМ
                # ------------------------------------------------

                self.execute_command(
                    command
                )

                # Даём TTS полностью закончить.
                # В это время Рей не слушает микрофон,
                # чтобы не поймать собственный голос.
                time.sleep(
                    1.5
                )

                if self.running:

                    self.ui_state(
                        "Ожидание «Рей»...",
                        CYAN,
                    )

            except Exception as error:

                logger.exception(
                    "Voice loop error"
                )

                self.ui_log(
                    "ERROR",
                    str(error),
                )

                self.ui_state(
                    "Ошибка голосового модуля",
                    RED,
                )

                time.sleep(
                    1
                )

    # ========================================================
    # COMMAND EXECUTION
    # ========================================================

    def execute_command(
        self,
        command,
    ):

        if self.processing:
            return

        self.processing = True

        try:

            self.ui_state(
                "Выполняю...",
                PURPLE,
            )

            self.ui_log(
                "command",
                command,
            )

            result = self.processor.process(
                command
            )

            self.ui_log(
                result.status.value,
                result.message,
            )

            self.add_history(
                command,
                result.message,
                result.status.value,
            )

            self.ui_state(
                result.message,
                GREEN,
            )

            if result.message:

                self.speaker.speak(
                    result.message
                )

        except Exception as error:

            logger.exception(
                "Command error"
            )

            self.ui_log(
                "ERROR",
                str(error),
            )

            self.ui_state(
                "Ошибка",
                RED,
            )

        finally:

            self.processing = False

    def run_command(
        self,
        command,
    ):

        threading.Thread(
            target=self.execute_command,
            args=(command,),
            daemon=True,
        ).start()

    # ========================================================
    # HISTORY
    # ========================================================

    def add_history(
        self,
        command,
        response,
        status,
    ):

        self.history.insert(
            0,
            (
                command,
                response,
                status,
            ),
        )

        self.history = self.history[:5]

        self.root.after(
            0,
            self.refresh_history,
        )

    def refresh_history(self):

        for widget in (
            self.history_box.winfo_children()
        ):

            widget.destroy()

        for (
            command,
            response,
            status,
        ) in self.history:

            row = tk.Frame(
                self.history_box,
                bg="#081528",
                highlightbackground=BORDER,
                highlightthickness=1,
            )

            row.pack(
                fill="x",
                pady=3,
            )

            color = (
                GREEN
                if status == "success"
                else RED
            )

            tk.Label(
                row,
                text="✓"
                if status == "success"
                else "!",
                bg="#081528",
                fg=color,
                font=("Segoe UI", 9, "bold"),
            ).pack(
                side="left",
                padx=(9, 7),
                pady=7,
            )

            text_box = tk.Frame(
                row,
                bg="#081528",
            )

            text_box.pack(
                side="left",
                fill="x",
                expand=True,
                pady=5,
            )

            tk.Label(
                text_box,
                text=command[:28],
                bg="#081528",
                fg=TEXT,
                font=("Segoe UI", 7, "bold"),
                anchor="w",
            ).pack(
                fill="x"
            )

            tk.Label(
                text_box,
                text=response[:32],
                bg="#081528",
                fg=MUTED,
                font=("Segoe UI", 7),
                anchor="w",
            ).pack(
                fill="x"
            )

            tk.Label(
                row,
                text=datetime.now().strftime(
                    "%H:%M"
                ),
                bg="#081528",
                fg=DIM,
                font=("Segoe UI", 7),
            ).pack(
                side="right",
                padx=8,
            )

    # ========================================================
    # UI HELPERS
    # ========================================================

    def set_state(
        self,
        text,
        color,
    ):

        self.state_text.configure(
            text=text
        )

        self.state_dot.configure(
            fg=color
        )

    def ui_state(
        self,
        text,
        color,
    ):

        if self.closing:
            return

        self.root.after(
            0,
            lambda: self.set_state(
                text,
                color,
            ),
        )

    def log_message(
        self,
        kind,
        message,
    ):

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        self.log.configure(
            state="normal"
        )

        self.log.insert(
            "end",
            (
                f"[{timestamp}] "
                f"[{kind}] "
                f"{message}\n"
            ),
        )

        self.log.see(
            "end"
        )

        self.log.configure(
            state="disabled"
        )

    def ui_log(
        self,
        kind,
        message,
    ):

        if self.closing:
            return

        self.root.after(
            0,
            lambda: self.log_message(
                kind,
                message,
            ),
        )

    def set_online(
        self,
        online,
    ):

        def update():

            if self.closing:
                return

            if online:

                self.system_status.configure(
                    text="● SYSTEM ONLINE",
                    fg=GREEN,
                )

                self.online_dot.configure(
                    fg=GREEN
                )

                self.online_text.configure(
                    text="Рей онлайн"
                )

                self.sidebar_status.configure(
                    text="Слушаю твой голос"
                )

            else:

                self.system_status.configure(
                    text="● SYSTEM OFFLINE",
                    fg=RED,
                )

                self.online_dot.configure(
                    fg=RED
                )

                self.online_text.configure(
                    text="Рей остановлен"
                )

                self.sidebar_status.configure(
                    text="Нажми кнопку запуска"
                )

        self.root.after(
            0,
            update,
        )

    def update_clock(self):

        if self.closing:
            return

        self.clock.configure(
            text=datetime.now().strftime(
                "%d.%m.%Y  •  %H:%M:%S"
            )
        )

        self.root.after(
            1000,
            self.update_clock,
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        if self.closing:
            return

        self.closing = True
        self.running = False

        self.root.destroy()


# ============================================================
# ENTRY
# ============================================================

def main():

    root = tk.Tk()

    RayUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()