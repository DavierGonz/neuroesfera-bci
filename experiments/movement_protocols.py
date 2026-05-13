import json
import random
import shutil
import subprocess
import time
from pathlib import Path

from psychopy import event, sound, visual

from core.protocol_catalog import get_protocol_config
from eeg.lsl_markers import send_marker
from experiments.trial_sequences import (
    END_SECONDS,
    STAGE_ACTIVE,
    STAGE_BLANK,
    STAGE_REST,
    STAGE_STIMULUS,
    TRIAL_SEQUENCES,
)
from gui.ui_theme import BG_COLOR, BUTTON_MUTED, PANEL_BORDER, TEXT_PRIMARY


MAX_CONSECUTIVE_CLASS_REPEATS = 3
EXPERIMENT_BG_COLOR = (0, 0, 0)
REST_BG_COLOR = (128, 128, 128)
WHITE = (255, 255, 255)
MI_BLUE = (30, 110, 255)
ME_GREEN = (70, 170, 80)
AW_ORANGE = (255, 150, 45)

ARM_WORDS = ["APLAUDIR", "CONECTAR", "CORTAR", "ESCRIBIR", "LANZAR"]
LEG_WORDS = ["CAMINAR", "MARCHAR", "PATEAR", "SALTAR", "SENTAR"]

ARM_VIDEO_PREFIXES = ("aplaudir", "conectar", "cortar", "escribir", "lanzar")
LEG_VIDEO_PREFIXES = ("caminar", "marchar", "patear", "saltar", "sentar")
MO_CUE_IMAGE_PATH = Path("stimuli") / "Estimulo_MO.png"


class TrialSessionAbort(Exception):
    pass


class AbortControl:
    def __init__(self, window):
        self.mouse = event.Mouse(win=window, visible=True)
        self._mouse_was_down = False
        self.shape = visual.Rect(
            win=window,
            pos=(0.38, 0.455),
            width=0.18,
            height=0.045,
            units="height",
            fillColor=BUTTON_MUTED,
            lineColor=PANEL_BORDER,
            colorSpace="rgb255",
            lineWidth=2,
        )
        self.text = visual.TextStim(
            win=window,
            text="Finalizar",
            pos=(0.38, 0.455),
            units="height",
            height=0.022,
            color=TEXT_PRIMARY,
            colorSpace="rgb255",
            bold=True,
            font="Segoe UI",
        )

    def draw(self):
        self.shape.draw()
        self.text.draw()

    def was_requested(self):
        if "escape" in event.getKeys(keyList=["escape"]):
            return True

        left_down = bool(self.mouse.getPressed()[0])
        clicked = (
            left_down
            and not self._mouse_was_down
            and self.shape.contains(self.mouse.getPos())
        )
        self._mouse_was_down = left_down

        return clicked


def run_motor_imagery(window, trials, marker_outlet, recorder, stimulus_gender):
    _run_catalog_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        stimulus_gender,
        "paradigm_mi",
    )


def run_action_words(window, trials, marker_outlet, recorder, stimulus_gender):
    _run_catalog_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        stimulus_gender,
        "paradigm_aw",
    )


def run_motor_execution(window, trials, marker_outlet, recorder, stimulus_gender):
    _run_catalog_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        stimulus_gender,
        "paradigm_me",
    )


def run_motor_observation(window, trials, marker_outlet, recorder, stimulus_gender):
    _run_catalog_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        stimulus_gender,
        "paradigm_mo",
    )


def run_protocol_by_key(
    window,
    trials,
    marker_outlet,
    recorder,
    stimulus_gender,
    experiment_key,
):
    _run_catalog_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        stimulus_gender,
        experiment_key,
    )


def _run_catalog_protocol(
    window,
    trials,
    marker_outlet,
    recorder,
    stimulus_gender,
    experiment_key,
):
    protocol = get_protocol_config(experiment_key)
    _run_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        protocol["target_key"],
        stimulus_gender,
        protocol["modalities"],
        experiment_key,
        classes=protocol["class_keys"],
        trials_per_modality=protocol.get("trials_per_modality"),
    )


def _run_protocol(
    window,
    trials,
    marker_outlet,
    recorder,
    target_key,
    stimulus_gender,
    modalities,
    experiment_key,
    classes=None,
    trials_per_modality=None,
):
    classes = classes or _target_classes(target_key)
    trial_plan = _build_trial_plan(
        trials,
        modalities,
        classes,
        trials_per_modality=trials_per_modality,
    )
    trial_sequence = _trial_sequence(experiment_key)

    cross = _text_stim(window, "+", height=0.16, font="Arial", color=WHITE)
    end_text = _text_stim(window, "Fin del experimento", height=0.08)
    abort_text = _text_stim(window, "Sesion finalizada", height=0.08)
    abort_control = AbortControl(window)
    mo_cue_image = _build_mo_cue_image(window) if "MO" in modalities else None

    send_marker(marker_outlet, f"TARGET_{target_key.upper()}")
    send_marker(marker_outlet, f"GENDER_{stimulus_gender.upper()}")
    _draw_stage(window, abort_control=abort_control)

    ended_early = False

    try:
        for trial_id, (modality, class_key) in enumerate(trial_plan, start=1):
            task_stimulus = _build_task_stimulus(
                window,
                modality,
                class_key,
                target_key,
                stimulus_gender,
                mo_cue_image=mo_cue_image,
            )
            stimulus_cleaned = False

            def cleanup_stimulus():
                nonlocal stimulus_cleaned

                if stimulus_cleaned:
                    return

                _stop_task_stimulus(task_stimulus)
                task_stimulus["cleanup"]()
                stimulus_cleaned = True

            send_marker(marker_outlet, f"TRIAL_{trial_id}")
            send_marker(marker_outlet, f"CLASS_{class_key.upper()}")

            try:
                for stage_config in trial_sequence:
                    stage_marker, duration, stage_type, stage_options = (
                        _parse_stage_config(stage_config)
                    )
                    _run_trial_stage(
                        window,
                        recorder,
                        marker_outlet,
                        stage_marker,
                        duration,
                        stage_type,
                        task_stimulus=task_stimulus,
                        cross=cross,
                        stage_options=stage_options,
                        cleanup_stimulus=cleanup_stimulus,
                        abort_control=abort_control,
                    )
            finally:
                cleanup_stimulus()
    except TrialSessionAbort:
        ended_early = True
        send_marker(marker_outlet, "END_EARLY")

    final_text = abort_text if ended_early else end_text
    _draw_stage(window, [final_text])
    send_marker(marker_outlet, "END")
    recorder.record_for_duration(
        END_SECONDS,
        on_tick=lambda: _draw_stage(window, [final_text]),
    )


def _trial_sequence(experiment_key):
    if experiment_key not in TRIAL_SEQUENCES:
        raise ValueError(f"No hay secuencia configurada para: {experiment_key}")

    return TRIAL_SEQUENCES[experiment_key]


def _parse_stage_config(stage_config):
    if len(stage_config) == 3:
        stage_marker, duration, stage_type = stage_config
        return stage_marker, duration, stage_type, {}

    if len(stage_config) == 4:
        stage_marker, duration, stage_type, stage_options = stage_config
        return stage_marker, duration, stage_type, stage_options or {}

    raise ValueError(f"Fase invalida en TRIAL_SEQUENCES: {stage_config}")


def _run_trial_stage(
    window,
    recorder,
    marker_outlet,
    stage_marker,
    duration,
    stage_type,
    task_stimulus,
    cross,
    stage_options,
    cleanup_stimulus,
    abort_control,
):
    if stage_type == STAGE_BLANK:
        _draw_stage(window, [cross], abort_control=abort_control)
        send_marker(marker_outlet, stage_marker)
        _record_stage(
            recorder,
            duration,
            on_tick=lambda: _draw_stage(window, [cross], abort_control=abort_control),
            beep_config=stage_options.get("beep"),
            abort_control=abort_control,
        )
        return

    if stage_type == STAGE_REST:
        _draw_stage(window, abort_control=abort_control, bg_color=REST_BG_COLOR)
        send_marker(marker_outlet, stage_marker)
        _record_stage(
            recorder,
            duration,
            on_tick=lambda: _draw_stage(
                window,
                abort_control=abort_control,
                bg_color=REST_BG_COLOR,
            ),
            beep_config=stage_options.get("beep"),
            abort_control=abort_control,
        )
        return

    if stage_type in (STAGE_STIMULUS, STAGE_ACTIVE):
        stage_stimulus = _stage_stimulus(task_stimulus, stage_type, cross)
        _start_stimulus(stage_stimulus)
        _draw_stage(window, [stage_stimulus], abort_control=abort_control)
        send_marker(marker_outlet, stage_marker)
        if task_stimulus["marker_stage"] == stage_type:
            send_marker(marker_outlet, task_stimulus["marker"])
        try:
            _record_stage(
                recorder,
                duration,
                on_tick=lambda current_stimulus=stage_stimulus: _draw_stage(
                    window,
                    [current_stimulus],
                    abort_control=abort_control,
                ),
                beep_config=stage_options.get("beep"),
                abort_control=abort_control,
            )
        finally:
            if task_stimulus["cleanup_stage"] == stage_type:
                cleanup_stimulus()
            else:
                _stop_stimulus(stage_stimulus)
        return

    raise ValueError(f"Tipo de fase no soportado: {stage_type}")


def _record_stage(recorder, duration, on_tick, beep_config=None, abort_control=None):
    beep_sound = _build_beep(beep_config) if beep_config else None
    beep_played = False
    stage_start = None

    def tick():
        nonlocal beep_played, stage_start

        if stage_start is None:
            stage_start = time.perf_counter()

        if beep_sound is not None and not beep_played:
            elapsed = time.perf_counter() - stage_start
            if elapsed >= float(beep_config.get("start", 0.0)):
                beep_sound.play()
                beep_played = True

        on_tick()

        if abort_control is not None and abort_control.was_requested():
            raise TrialSessionAbort()

    recorder.record_for_duration(duration, on_tick=tick)


def _build_task_stimulus(
    window,
    modality,
    class_key,
    target_key,
    stimulus_gender,
    movie_cache=None,
    movie_path=None,
    mo_cue_image=None,
):
    if modality == "MI":
        stimulus, marker = _build_mi_stimulus(window, class_key)
        return _task_stimulus(
            cue=stimulus,
            marker=marker,
            marker_stage=STAGE_STIMULUS,
            cleanup_stage=STAGE_STIMULUS,
        )
    if modality == "AW":
        cue, active, marker = _build_aw_stimulus(window, class_key)
        return _task_stimulus(
            cue=cue,
            active=active,
            marker=marker,
            marker_stage=STAGE_ACTIVE,
            cleanup_stage=STAGE_ACTIVE,
        )
    if modality == "MO":
        movie, marker, cleanup = _build_mo_stimulus(
            window,
            class_key,
            target_key,
            stimulus_gender,
            movie_cache,
            movie_path,
        )
        return _task_stimulus(
            cue=mo_cue_image or _build_mo_cue_image(window),
            active=movie,
            marker=marker,
            marker_stage=STAGE_ACTIVE,
            cleanup=cleanup,
            cleanup_stage=STAGE_ACTIVE,
        )
    if modality == "ME":
        stimulus, marker = _build_me_stimulus(window, class_key)
        return _task_stimulus(
            cue=stimulus,
            marker=marker,
            marker_stage=STAGE_STIMULUS,
            cleanup_stage=STAGE_STIMULUS,
        )

    raise ValueError(f"Modalidad no soportada: {modality}")

def _build_mi_stimulus(window, class_key):
    text = "\u2191" if class_key == "arm" else "\u2193"
    stimulus = _text_stim(
        window,
        text,
        height=0.18,
        font="Segoe UI Symbol",
        color=MI_BLUE,
    )

    return stimulus, f"MI_{class_key.upper()}"


def _build_aw_stimulus(window, class_key):
    words = ARM_WORDS if class_key == "arm" else LEG_WORDS
    text = random.choice(words)
    cue = _text_stim(window, "Palabra", height=0.075, color=AW_ORANGE)
    active = _text_stim(window, text, height=0.075, color=AW_ORANGE)
    marker = f"AW_{class_key.upper()}_{_marker_token(text)}"

    return cue, active, marker


def _build_me_stimulus(window, class_key):
    text = "\u2191" if class_key == "arm" else "\u2193"
    stimulus = _text_stim(
        window,
        text,
        height=0.18,
        font="Segoe UI Symbol",
        color=ME_GREEN,
    )
    return stimulus, f"ME_{class_key.upper()}"


def _build_mo_stimulus(
    window,
    class_key,
    target_key,
    stimulus_gender,
    movie_cache=None,
    movie_path=None,
):
    if movie_path is not None:
        candidate_paths = [movie_path]
    else:
        candidate_paths = _movie_candidates(class_key, target_key, stimulus_gender)
        random.shuffle(candidate_paths)

    failures = []
    for candidate_path in candidate_paths:
        movie = (movie_cache or {}).get(candidate_path)

        if movie is not None:
            marker = f"MO_{class_key.upper()}"
            return movie, marker, _noop

        try:
            movie = _build_movie_stim(window, candidate_path)
        except Exception as error:
            failures.append(f"{candidate_path}: {error}")
            continue

        marker = f"MO_{class_key.upper()}"
        return movie, marker, movie.unload

    details = "\n".join(failures) if failures else "No hubo candidatos."
    raise RuntimeError(
        f"No se pudo cargar ningun video MO para {class_key} ({stimulus_gender}).\n"
        f"Videos intentados:\n{details}"
    )


def _task_stimulus(
    cue,
    marker,
    marker_stage,
    cleanup_stage,
    active=None,
    cleanup=None,
):
    return {
        "cue": cue,
        "active": active,
        "marker": marker,
        "marker_stage": marker_stage,
        "cleanup": cleanup or _noop,
        "cleanup_stage": cleanup_stage,
    }


def _stage_stimulus(task_stimulus, stage_type, default_cross):
    if stage_type == STAGE_ACTIVE:
        return task_stimulus["active"] or default_cross

    return task_stimulus["cue"]


def _stop_task_stimulus(task_stimulus):
    _stop_stimulus(task_stimulus["cue"])
    if task_stimulus["active"] is not None:
        _stop_stimulus(task_stimulus["active"])


def _build_trial_plan(trials, modalities, classes, trials_per_modality=None):
    if trials_per_modality is None:
        pending_trials = [
            (modality, class_key)
            for modality in modalities
            for class_key in classes
            for _ in range(trials)
        ]
    else:
        pending_trials = []
        for modality in modalities:
            pending_trials.extend(
                (modality, class_key)
                for class_key in _balanced_class_sequence(classes, trials_per_modality)
            )

    random.shuffle(pending_trials)

    trial_plan = []
    while pending_trials:
        eligible_trials = [
            trial
            for trial in pending_trials
            if not _would_exceed_class_repeat(
                trial_plan,
                trial[1],
                MAX_CONSECUTIVE_CLASS_REPEATS,
            )
        ]

        if not eligible_trials:
            eligible_trials = pending_trials

        class_counts = {
            class_key: sum(1 for _, pending_class in eligible_trials if pending_class == class_key)
            for class_key in classes
        }
        most_available = max(class_counts.values())
        candidate_classes = [
            class_key
            for class_key, count in class_counts.items()
            if count == most_available
        ]
        selected_class = random.choice(candidate_classes)
        selected_trial = random.choice(
            [trial for trial in eligible_trials if trial[1] == selected_class]
        )

        pending_trials.remove(selected_trial)
        trial_plan.append(selected_trial)

    return trial_plan


def _balanced_class_sequence(classes, total_trials):
    base_repeats, extra_trials = divmod(total_trials, len(classes))
    sequence = [
        class_key
        for class_key in classes
        for _ in range(base_repeats)
    ]
    sequence.extend(random.sample(classes, extra_trials))
    random.shuffle(sequence)
    return sequence


def _would_exceed_class_repeat(trial_plan, class_key, max_repeats):
    if len(trial_plan) < max_repeats:
        return False

    recent_classes = [trial_class for _, trial_class in trial_plan[-max_repeats:]]
    return all(recent_class == class_key for recent_class in recent_classes)


def _build_movie_stim(window, movie_path):
    movie_path = Path(movie_path).resolve()
    window_aspect = window.size[0] / window.size[1]
    max_width = window_aspect * 0.95
    max_height = 0.95

    movie = visual.MovieStim(
        window,
        str(movie_path),
        units="height",
        loop=False,
        noAudio=True,
        autoStart=False,
    )
    dimensions = _movie_dimensions(movie_path) or _stimulus_dimensions(
        getattr(movie, "size", None)
    )

    if dimensions:
        movie.size = _fit_media_size(
            dimensions[0],
            dimensions[1],
            max_width=max_width,
            max_height=max_height,
        )

    return movie


def _build_mo_cue_image(window):
    if not MO_CUE_IMAGE_PATH.exists():
        raise FileNotFoundError(f"No se encontro la imagen MO requerida: {MO_CUE_IMAGE_PATH}")

    return visual.ImageStim(
        win=window,
        image=str(MO_CUE_IMAGE_PATH),
        units="height",
        size=_fit_image_size(MO_CUE_IMAGE_PATH, max_width=0.95, max_height=0.78),
    )


def _fit_image_size(image_path, max_width, max_height):
    try:
        from PIL import Image

        with Image.open(image_path) as image:
            width, height = image.size
    except Exception:
        return (max_width, max_height)

    return _fit_media_size(width, height, max_width, max_height)


def _fit_media_size(width, height, max_width, max_height):
    aspect = width / height
    if aspect >= max_width / max_height:
        return (max_width, max_width / aspect)

    return (max_height * aspect, max_height)


def _movie_dimensions(movie_path):
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        try:
            result = subprocess.run(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height",
                    "-of",
                    "json",
                    str(movie_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            streams = json.loads(result.stdout).get("streams", [])
            if streams:
                width = int(streams[0]["width"])
                height = int(streams[0]["height"])
                if width > 0 and height > 0:
                    return (width, height)
        except Exception:
            pass

    return None


def _stimulus_dimensions(size):
    if not size or len(size) < 2:
        return None

    width = float(size[0])
    height = float(size[1])
    if width <= 0 or height <= 0:
        return None

    return (width, height)


def _select_movie_path(class_key, target_key, stimulus_gender):
    return random.choice(_movie_candidates(class_key, target_key, stimulus_gender))


def _movie_candidates(class_key, target_key, stimulus_gender):
    if target_key == "left_vs_right":
        filename = "raise_left_arm.mp4" if class_key == "left" else "raise_right_arm.mp4"
        path = Path("stimuli") / "motor_observation" / "left_vs_right" / filename
        if not path.exists():
            raise FileNotFoundError(f"No se encontro el video requerido: {path}")
        return [path]

    folder = Path("stimuli") / "motor_observation" / "arm_vs_leg" / stimulus_gender
    prefixes = ARM_VIDEO_PREFIXES if class_key == "arm" else LEG_VIDEO_PREFIXES
    candidates = [
        path
        for path in folder.glob("*.mp4")
        if path.stem.lower().startswith(prefixes)
    ]

    if not candidates:
        raise FileNotFoundError(
            f"No hay videos MO para clase {class_key} en la carpeta {folder}."
        )

    return candidates


def _target_classes(target_key):
    if target_key == "left_vs_right":
        return ["left", "right"]
    if target_key == "arm_vs_leg":
        return ["arm", "leg"]

    raise ValueError(f"Objetivo no soportado: {target_key}")


def _text_stim(window, text, height, font="Segoe UI", color=TEXT_PRIMARY):
    return visual.TextStim(
        win=window,
        text=text,
        units="height",
        height=height,
        color=color,
        colorSpace="rgb255",
        bold=True,
        font=font,
        wrapWidth=0.95,
    )


def _draw_stage(window, stimuli=None, abort_control=None, bg_color=EXPERIMENT_BG_COLOR):
    window.color = bg_color

    for stimulus in stimuli or []:
        stimulus.draw()

    if abort_control is not None:
        abort_control.draw()

    window.flip()


def _build_beep(beep_config):
    return sound.Sound(
        value=beep_config.get("frequency", 880),
        secs=beep_config.get("duration", 0.3),
    )


def _start_stimulus(stimulus):
    play = getattr(stimulus, "play", None)
    seek = getattr(stimulus, "seek", None)

    if seek is not None:
        seek(0.0, log=False)
    if play is not None:
        play(log=False)


def _stop_stimulus(stimulus):
    stop = getattr(stimulus, "stop", None)

    if stop is not None:
        stop(log=False)


def _marker_token(value):
    return str(value).upper().replace(" ", "_").replace("-", "_")


def _noop():
    return None
