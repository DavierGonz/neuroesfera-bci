import ctypes
import os
import sys

from psychopy import core, event, logging as psychopy_logging, monitors, visual

from core.config import FULLSCREEN, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from core.protocol_catalog import (
    EXPERIMENT_3_BLOCK_KEYS,
    MAIN_EXPERIMENT_KEYS,
    PARADIGM_PROTOCOL_KEYS,
    STIMULUS_GENDER_KEYS,
    get_block_config,
    get_protocol_config,
    get_stimulus_gender_config,
    get_target_config,
)
from core.session_config import SessionConfig
from core.state_manager import AppState
from eeg.stream_metadata import default_channel_names
from experiments.movement_protocols import run_protocol_by_key
from gui.ui_theme import (
    BG_COLOR,
    BUTTON_ACTIVE,
    BUTTON_COLOR,
    BUTTON_MUTED,
    PANEL_BORDER,
    PANEL_COLOR,
    SUCCESS_COLOR,
    TEXT_ACCENT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from services.experiment_session import ExperimentSession


DEFAULT_TRIALS_PER_CLASS = 20


class Button:
    def __init__(
        self,
        win,
        label,
        center,
        size,
        fill_color,
        text_color=TEXT_PRIMARY,
        border_color=PANEL_BORDER,
        text_height=0.038,
    ):
        self.label = label
        self.shape = visual.Rect(
            win=win,
            width=size[0],
            height=size[1],
            pos=center,
            units="height",
            fillColor=fill_color,
            lineColor=border_color,
            colorSpace="rgb255",
            lineWidth=2,
        )
        self.text = visual.TextStim(
            win=win,
            text=label,
            pos=center,
            units="height",
            height=text_height,
            color=text_color,
            colorSpace="rgb255",
            bold=True,
            font="Segoe UI",
        )

    def draw(self):
        self.shape.draw()
        self.text.draw()

    def contains(self, mouse):
        return self.shape.contains(mouse.getPos())


class AppController:
    def __init__(self):
        self.window_size = self._resolve_window_size()
        monitor = self._build_monitor()

        self.window = visual.Window(
            size=self.window_size,
            fullscr=FULLSCREEN,
            color=BG_COLOR,
            colorSpace="rgb255",
            units="height",
            allowGUI=not FULLSCREEN,
            waitBlanking=True,
            title=WINDOW_TITLE,
            monitor=monitor,
        )
        self.mouse = event.Mouse(win=self.window, visible=True)
        self._mouse_was_down = False
        self.state = AppState.MENU
        self.recorder = None
        self.protocol_setup = {
            "stimulus_gender": "hombre",
            "trials_per_class": DEFAULT_TRIALS_PER_CLASS,
            "subject_number": 1,
            "block_key": "bloque1",
        }
        self.selected_protocol_key = None
        self.pending_session_config = None
        self.pending_trials_per_class = None
        self._setup_preview_cache = None
        self.last_session_result = None
        self.running = True

    def run(self):
        while self.running:
            if self.state == AppState.MENU:
                self._run_menu_frame()
            elif self.state == AppState.PARADIGM_MENU:
                self._run_paradigm_menu_frame()
            elif self.state == AppState.PROTOCOL_SETUP:
                self._run_protocol_setup_frame()
            elif self.state == AppState.PROTOCOL_READY:
                self._run_protocol_ready_frame()
            elif self.state == AppState.SESSION_COMPLETE:
                self._run_session_complete_frame()

            self.window.flip()

    def _run_menu_frame(self):
        buttons = self._menu_buttons()
        self._draw_menu(buttons)
        clicked = self._poll_button_click(buttons)
        keys = event.getKeys(keyList=["escape"])

        if "escape" in keys:
            self._shutdown()
        elif clicked in MAIN_EXPERIMENT_KEYS:
            self.selected_protocol_key = clicked
            self.pending_session_config = None
            self.pending_trials_per_class = None
            self.state = AppState.PROTOCOL_SETUP
        elif clicked == "paradigms":
            self.state = AppState.PARADIGM_MENU
        elif clicked == "exit":
            self._shutdown()

    def _run_paradigm_menu_frame(self):
        buttons = self._paradigm_menu_buttons()
        self._draw_paradigm_menu(buttons)
        clicked = self._poll_button_click(buttons)
        keys = event.getKeys(keyList=["escape"])

        if "escape" in keys or clicked == "back":
            self.state = AppState.MENU
            return

        if clicked in PARADIGM_PROTOCOL_KEYS:
            self.selected_protocol_key = clicked
            self.pending_session_config = None
            self.pending_trials_per_class = None
            self.state = AppState.PROTOCOL_SETUP

    def _run_protocol_setup_frame(self):
        if self.selected_protocol_key is None:
            self.state = AppState.MENU
            return

        buttons = self._protocol_setup_buttons()
        self._draw_protocol_setup(buttons)
        clicked = self._poll_button_click(buttons)
        keys = event.getKeys(keyList=["escape"])

        if "escape" in keys:
            return_state = self._menu_state_for_protocol()
            self.selected_protocol_key = None
            self.pending_session_config = None
            self.pending_trials_per_class = None
            self.state = return_state
            return

        if clicked is None:
            return

        if clicked.startswith("gender:"):
            self.protocol_setup["stimulus_gender"] = clicked.split(":", 1)[1]
            return

        if clicked.startswith("block:"):
            self.protocol_setup["block_key"] = clicked.split(":", 1)[1]
            self._setup_preview_cache = None
            return

        if clicked == "subject_minus":
            self.protocol_setup["subject_number"] = max(
                1, self.protocol_setup["subject_number"] - 1
            )
            return

        if clicked == "subject_plus":
            self.protocol_setup["subject_number"] += 1
            return

        if clicked == "continue":
            self.pending_session_config = SessionConfig.for_protocol(
                self.selected_protocol_key,
                self.protocol_setup["stimulus_gender"],
                self.protocol_setup["subject_number"],
                self.protocol_setup["trials_per_class"],
                self.protocol_setup["block_key"],
            )
            self.pending_trials_per_class = self.protocol_setup["trials_per_class"]
            self.state = AppState.PROTOCOL_READY
            event.clearEvents("keyboard")
            return

        if clicked == "back":
            return_state = self._menu_state_for_protocol()
            self.selected_protocol_key = None
            self.pending_session_config = None
            self.pending_trials_per_class = None
            self.state = return_state

    def _run_protocol_ready_frame(self):
        if self.selected_protocol_key is None or self.pending_session_config is None:
            self.state = AppState.MENU
            return

        self._draw_protocol_ready()
        keys = event.getKeys(keyList=["space", "escape"])
        protocol = get_protocol_config(self.selected_protocol_key)

        if "escape" in keys:
            self.pending_session_config = None
            self.pending_trials_per_class = None
            self.state = AppState.PROTOCOL_SETUP
            return

        if "space" in keys and protocol["implemented"]:
            trials_per_class = self.pending_trials_per_class
            self._draw_loading("Preparando sesion", "Abriendo LabRecorder y cargando estimulos")
            self.window.flip()
            self._run_session(
                self.pending_session_config,
                self._build_experiment_runner(
                    self.selected_protocol_key,
                    trials_per_class,
                    self.pending_session_config.stimulus_gender,
                ),
            )
            self.pending_session_config = None
            self.pending_trials_per_class = None
            self.state = AppState.SESSION_COMPLETE
            event.clearEvents("keyboard")

    def _run_session_complete_frame(self):
        if self.last_session_result is None:
            self.state = AppState.MENU
            return

        self._draw_session_complete()
        keys = event.getKeys(keyList=["space", "escape"])

        if "space" in keys or "escape" in keys:
            self.last_session_result = None
            self.selected_protocol_key = None
            self.state = AppState.MENU
            event.clearEvents("keyboard")

    def _build_experiment_runner(
        self,
        protocol_key,
        trials_per_class,
        stimulus_gender,
    ):
        protocol = get_protocol_config(protocol_key)

        if protocol["implemented"]:
            return lambda session: run_protocol_by_key(
                self.window,
                trials_per_class,
                session.marker_outlet,
                session.recorder,
                stimulus_gender,
                protocol_key,
            )

        raise NotImplementedError(
            f"El protocolo {protocol['label']} aun no tiene runner asignado."
        )

    def _menu_state_for_protocol(self):
        if self.selected_protocol_key in PARADIGM_PROTOCOL_KEYS:
            return AppState.PARADIGM_MENU

        return AppState.MENU

    def _run_session(self, session_config, experiment_runner):
        session = ExperimentSession(session_config)
        self.recorder = session.recorder

        try:
            experiment_runner(session)
        finally:
            session.close()
            self.last_session_result = session.session_result
            self._setup_preview_cache = None
            self.recorder = None

    def _shutdown(self):
        if self.recorder:
            self.recorder.close()
            self.recorder = None

        self.window.close()
        core.quit()
        sys.exit()

    def _poll_button_click(self, buttons):
        left_down = bool(self.mouse.getPressed()[0])
        clicked = None

        if left_down and not self._mouse_was_down:
            for key, button in buttons.items():
                if button.contains(self.mouse):
                    clicked = key
                    break

        self._mouse_was_down = left_down
        return clicked

    def _draw_menu(self, buttons):
        self.window.color = BG_COLOR
        self._draw_panel((0.0, 0.28), (0.78, 0.16))
        self._draw_text("NeuroEsfera BCI", (0.0, 0.38), 0.055, TEXT_PRIMARY, bold=True)
        self._draw_text(
            "Protocolos experimentales",
            (0.0, 0.29),
            0.023,
            TEXT_SECONDARY,
        )
        self._draw_text(
            "Experimentos",
            (0.0, 0.11),
            0.028,
            TEXT_PRIMARY,
            bold=True,
        )

        for button in buttons.values():
            button.draw()

    def _draw_paradigm_menu(self, buttons):
        self.window.color = BG_COLOR
        self._draw_panel((0.0, 0.28), (0.78, 0.16))
        self._draw_text("Paradigmas", (0.0, 0.38), 0.055, TEXT_PRIMARY, bold=True)
        self._draw_text(
            "Seleccion individual de modalidad",
            (0.0, 0.29),
            0.023,
            TEXT_SECONDARY,
        )
        self._draw_text(
            "Paradigma",
            (0.0, 0.11),
            0.028,
            TEXT_PRIMARY,
            bold=True,
        )

        for button in buttons.values():
            button.draw()

    def _draw_protocol_setup(self, buttons):
        protocol = get_protocol_config(self.selected_protocol_key)
        target = get_target_config(protocol["target_key"])
        gender = get_stimulus_gender_config(self.protocol_setup["stimulus_gender"])
        setup = self.protocol_setup
        panel = self._setup_panel_metrics()
        uses_mo = "MO" in protocol["modalities"]
        self.window.color = BG_COLOR
        self._draw_panel(panel["center"], panel["size"])
        self._draw_text(
            protocol["setup_title"],
            self._setup_panel_point(0.5, 0.06),
            0.042,
            TEXT_PRIMARY,
            bold=True,
            wrap_width=panel["inner_width"],
        )
        self._draw_text(
            f"{protocol['label']} | {target['label']}",
            self._setup_panel_point(0.5, 0.16),
            0.018,
            TEXT_SECONDARY,
            wrap_width=panel["inner_width"],
        )
        self._draw_text(
            self._trial_count_label(protocol),
            self._setup_panel_point(0.5, 0.27),
            0.022,
            TEXT_SECONDARY,
            bold=True,
        )

        for button in buttons.values():
            button.draw()

        self._draw_stepper(
            "Numero de sujeto",
            setup["subject_number"],
            label_pos=self._setup_panel_point(0.5, 0.40),
            value_pos=self._setup_panel_point(0.5, 0.51),
        )
        gender_label = "Genero de videos MO" if uses_mo else "Genero"
        self._draw_text(
            f"{gender_label}: {gender['label']}",
            self._setup_panel_point(0.5, 0.62),
            0.026,
            TEXT_PRIMARY,
            bold=True,
        )
        if protocol.get("requires_block"):
            block = get_block_config(setup["block_key"])
            self._draw_text(
                f"Bloque: {block['label']}",
                self._setup_panel_point(0.5, 0.755),
                0.021,
                TEXT_PRIMARY,
                bold=True,
                wrap_width=panel["inner_width"],
            )

        total_trials = self._total_trials_for_protocol(protocol, setup)
        preview_config = self._get_setup_preview_config()
        preview = preview_config.build_basename()
        total_y = 0.875 if protocol.get("requires_block") else 0.78
        hint_y = 0.905 if protocol.get("requires_block") else 0.83
        session_y = 0.93 if protocol.get("requires_block") else 0.88
        preview_y = 0.955 if protocol.get("requires_block") else 0.93

        self._draw_text(
            f"Trials totales: {total_trials}",
            self._setup_panel_point(0.5, total_y),
            0.022,
            TEXT_SECONDARY,
            bold=True,
        )
        protocol_hint = (
            "Protocolo implementado"
            if protocol["implemented"]
            else "Protocolo en menu, ejecucion pendiente"
        )
        self._draw_text(
            protocol_hint,
            self._setup_panel_point(0.5, hint_y),
            0.017,
            TEXT_SECONDARY,
        )
        self._draw_text(
            f"Sesion automatica: {preview_config.session_number:02d}",
            self._setup_panel_point(0.5, session_y),
            0.017,
            TEXT_SECONDARY,
            bold=True,
        )
        self._draw_text(
            preview,
            self._setup_panel_point(0.5, preview_y),
            0.017,
            TEXT_ACCENT,
            wrap_width=panel["inner_width"] * 0.84,
        )

    def _draw_protocol_ready(self):
        protocol = get_protocol_config(self.selected_protocol_key)
        config = self.pending_session_config
        self.window.color = BG_COLOR
        self._draw_panel((0.0, -0.02), (0.76, 0.68))
        self._draw_text("Preparado para iniciar", (0.0, 0.25), 0.056, TEXT_PRIMARY, bold=True)
        self._draw_text(
            "Verifica la configuracion y comienza cuando todo este listo",
            (0.0, 0.18),
            0.02,
            TEXT_SECONDARY,
        )

        details = [
            f"Protocolo: {config.protocol_name}",
            f"Objetivo: {config.target_name}",
            f"Genero: {get_stimulus_gender_config(config.stimulus_gender)['label']}",
            f"Sujeto: {config.subject_number:02d}",
            f"Sesion automatica: {config.session_number:02d}",
            f"Trials totales: {config.total_trials}",
            f"Archivo: {config.build_basename()}.xdf",
        ]
        if config.block_label:
            details.insert(4, f"Bloque: {config.block_label}")

        for index, text in enumerate(details):
            self._draw_text(
                text,
                (-0.28, 0.11 - index * 0.055),
                0.026,
                TEXT_SECONDARY,
                align="left",
                wrap_width=0.58,
            )

        hint = (
            "Presiona espacio para iniciar"
            if protocol["implemented"]
            else "Protocolo en construccion. Usa ESC para volver."
        )
        self._draw_text(hint, (0.0, -0.29), 0.03, TEXT_ACCENT, bold=True)

    def _draw_session_complete(self):
        result = self.last_session_result
        channel_labels = result.get("channel_labels", [])
        channel_count = int(result.get("channel_count", 0) or 0)

        if channel_labels:
            channels_text = ", ".join(channel_labels)
        elif channel_count:
            placeholder_labels = default_channel_names(min(channel_count, 8))
            channels_text = (
                f"{', '.join(placeholder_labels)} "
                "(mapeo configurado del proyecto; LSL sin labels)"
            )
        else:
            channels_text = "sin labels en el stream LSL"

        self.window.color = BG_COLOR
        self._draw_panel((0.0, -0.02), (0.80, 0.72))
        self._draw_text("Sesion guardada", (0.0, 0.25), 0.055, SUCCESS_COLOR, bold=True)
        self._draw_text(
            "La adquisicion termino correctamente y el archivo ya esta listo",
            (0.0, 0.18),
            0.02,
            TEXT_SECONDARY,
        )

        details = [
            f"Formato: {result['backend'].upper()}",
            f"Archivo: {os.path.basename(result['recording_path'])}",
            f"Objetivo: {result.get('target_name', 'unknown')}",
            f"Sujeto: {int(result.get('subject_number', 0)):02d}",
            f"Sesion: {int(result.get('session_number', 0)):02d}",
            f"EEG stream: {result['stream_name']}",
            f"Canales: {channels_text}",
        ]
        if result.get("block_label"):
            details.insert(3, f"Bloque: {result['block_label']}")

        for index, text in enumerate(details):
            self._draw_text(
                text,
                (-0.29, 0.10 - index * 0.060),
                0.023,
                TEXT_SECONDARY,
                align="left",
                wrap_width=0.60,
            )

        self._draw_text(
            "Presiona espacio para volver al menu",
            (0.0, -0.33),
            0.03,
            TEXT_ACCENT,
            bold=True,
        )

    def _draw_loading(self, title, subtitle):
        self.window.color = BG_COLOR
        self._draw_panel((0.0, -0.02), (0.76, 0.46))
        self._draw_text(title, (0.0, 0.08), 0.052, TEXT_PRIMARY, bold=True)
        self._draw_text(subtitle, (0.0, 0.00), 0.022, TEXT_SECONDARY)
        self._draw_text("Un momento...", (0.0, -0.10), 0.026, TEXT_ACCENT, bold=True)

    def _menu_buttons(self):
        buttons = {}

        start_y = 0.02
        gap = 0.073

        for index, protocol_key in enumerate(MAIN_EXPERIMENT_KEYS):
            protocol = get_protocol_config(protocol_key)
            buttons[protocol_key] = Button(
                self.window,
                protocol["menu_label"],
                (0.0, start_y - index * gap),
                (0.42, 0.055),
                BUTTON_COLOR,
                text_height=0.030,
            )

        paradigms_index = len(MAIN_EXPERIMENT_KEYS)
        buttons["paradigms"] = Button(
            self.window,
            "Paradigmas",
            (0.0, start_y - paradigms_index * gap),
            (0.42, 0.055),
            BUTTON_COLOR,
            text_height=0.030,
        )

        buttons["exit"] = Button(
            self.window,
            "Salir",
            (0.0, start_y - (paradigms_index + 1) * gap),
            (0.42, 0.055),
            BUTTON_MUTED,
            text_height=0.030,
        )

        return buttons

    def _paradigm_menu_buttons(self):
        buttons = {}

        start_y = 0.02
        gap = 0.073

        for index, protocol_key in enumerate(PARADIGM_PROTOCOL_KEYS):
            protocol = get_protocol_config(protocol_key)
            buttons[protocol_key] = Button(
                self.window,
                protocol["menu_label"],
                (0.0, start_y - index * gap),
                (0.42, 0.055),
                BUTTON_COLOR,
                text_height=0.030,
            )

        buttons["back"] = Button(
            self.window,
            "Volver",
            (0.0, start_y - len(PARADIGM_PROTOCOL_KEYS) * gap),
            (0.42, 0.055),
            BUTTON_MUTED,
            text_height=0.030,
        )

        return buttons

    def _protocol_setup_buttons(self):
        setup = self.protocol_setup
        protocol = get_protocol_config(self.selected_protocol_key)
        buttons = {}

        buttons["subject_minus"] = Button(
            self.window,
            "-",
            self._setup_panel_point(0.34, 0.51),
            (0.07, 0.05),
            BUTTON_MUTED,
            text_height=0.04,
        )
        buttons["subject_plus"] = Button(
            self.window,
            "+",
            self._setup_panel_point(0.66, 0.51),
            (0.07, 0.05),
            BUTTON_MUTED,
            text_height=0.04,
        )

        for index, gender_key in enumerate(STIMULUS_GENDER_KEYS):
            gender = get_stimulus_gender_config(gender_key)
            fill = BUTTON_ACTIVE if setup["stimulus_gender"] == gender_key else BUTTON_MUTED
            buttons[f"gender:{gender_key}"] = Button(
                self.window,
                gender["label"],
                self._setup_panel_point(0.38 + index * 0.24, 0.69),
                (0.18, 0.048),
                fill,
                text_color=BG_COLOR if fill == BUTTON_ACTIVE else TEXT_PRIMARY,
                text_height=0.026,
            )

        if protocol.get("requires_block"):
            for index, block_key in enumerate(EXPERIMENT_3_BLOCK_KEYS):
                block = get_block_config(block_key)
                fill = BUTTON_ACTIVE if setup["block_key"] == block_key else BUTTON_MUTED
                buttons[f"block:{block_key}"] = Button(
                    self.window,
                    block["code"],
                    self._setup_panel_point(0.26 + index * 0.24, 0.815),
                    (0.17, 0.044),
                    fill,
                    text_color=BG_COLOR if fill == BUTTON_ACTIVE else TEXT_PRIMARY,
                    text_height=0.024,
                )

        buttons["back"] = Button(
            self.window,
            "Volver",
            self._setup_panel_point(0.20, 0.975),
            (0.22, 0.04),
            BUTTON_MUTED,
            text_height=0.028,
        )
        buttons["continue"] = Button(
            self.window,
            "Continuar",
            self._setup_panel_point(0.80, 0.975),
            (0.24, 0.04),
            BUTTON_COLOR,
            text_height=0.028,
        )

        return buttons

    def _get_setup_preview_config(self):
        setup = self.protocol_setup
        cache_key = (
            self.selected_protocol_key,
            setup["stimulus_gender"],
            setup["subject_number"],
            setup["trials_per_class"],
            setup["block_key"],
        )

        if self._setup_preview_cache and self._setup_preview_cache[0] == cache_key:
            return self._setup_preview_cache[1]

        preview_config = SessionConfig.for_protocol(*cache_key)
        self._setup_preview_cache = (cache_key, preview_config)

        return preview_config

    def _draw_stepper(self, label, value, label_pos, value_pos):
        self._draw_text(label, label_pos, 0.025, TEXT_PRIMARY, bold=True, wrap_width=0.30)
        self._draw_text(f"{value:02d}", value_pos, 0.046, TEXT_PRIMARY, bold=True)

    def _trial_count_label(self, protocol):
        if "trials_per_modality" in protocol:
            return f"Trials por paradigma: {protocol['trials_per_modality']}"

        return f"Trials por clase fijos: {DEFAULT_TRIALS_PER_CLASS}"

    def _total_trials_for_protocol(self, protocol, setup):
        if "total_trials" in protocol:
            return protocol["total_trials"]

        return setup["trials_per_class"] * protocol["total_trials_multiplier"]

    def _draw_panel(self, center, size):
        visual.Rect(
            win=self.window,
            pos=center,
            width=size[0],
            height=size[1],
            units="height",
            fillColor=PANEL_COLOR,
            lineColor=PANEL_BORDER,
            colorSpace="rgb255",
            lineWidth=2,
        ).draw()

    def _setup_panel_metrics(self):
        center = (0.0, 0.0)
        size = (0.84, 0.96)
        pad_x = 0.10
        pad_top = 0.06
        pad_bottom = 0.06
        left = center[0] - size[0] / 2 + pad_x
        right = center[0] + size[0] / 2 - pad_x
        top = center[1] + size[1] / 2 - pad_top
        bottom = center[1] - size[1] / 2 + pad_bottom
        return {
            "center": center,
            "size": size,
            "left": left,
            "right": right,
            "top": top,
            "bottom": bottom,
            "inner_width": right - left,
            "inner_height": top - bottom,
        }

    def _setup_panel_point(self, x_fraction, y_fraction):
        panel = self._setup_panel_metrics()
        x = panel["left"] + x_fraction * panel["inner_width"]
        y = panel["top"] - y_fraction * panel["inner_height"]
        return (x, y)

    def _draw_text(
        self,
        text,
        pos,
        height,
        color,
        bold=False,
        wrap_width=0.72,
        align="center",
    ):
        anchor_horiz = "left" if align == "left" else "center"
        visual.TextStim(
            win=self.window,
            text=text,
            pos=pos,
            units="height",
            height=height,
            color=color,
            colorSpace="rgb255",
            bold=bold,
            font="Segoe UI",
            wrapWidth=wrap_width,
            alignText=align,
            anchorHoriz=anchor_horiz,
            anchorVert="center",
        ).draw()

    def _resolve_window_size(self):
        if not FULLSCREEN:
            return (WINDOW_WIDTH, WINDOW_HEIGHT)

        try:
            user32 = ctypes.windll.user32
            return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        except Exception:
            return (WINDOW_WIDTH, WINDOW_HEIGHT)

    def _build_monitor(self):
        monitor_name = "NeuroEsferaMonitor"
        monitor_dir = os.path.join(os.environ["APPDATA"], "psychopy3", "monitors")
        monitor_file = os.path.join(monitor_dir, f"{monitor_name}.json")

        previous_level = psychopy_logging.console.level
        should_seed_monitor = not os.path.exists(monitor_file)

        if should_seed_monitor:
            psychopy_logging.console.setLevel(psychopy_logging.ERROR)

        try:
            monitor = monitors.Monitor(monitor_name, width=34.5, distance=60.0)
            monitor.setSizePix(self.window_size)
            monitor.setNotes("Auto-generated local monitor profile for NeuroEsfera BCI.")

            if should_seed_monitor:
                os.makedirs(monitor_dir, exist_ok=True)
                monitor.save()
        finally:
            if should_seed_monitor:
                psychopy_logging.console.setLevel(previous_level)

        return monitor
