import random
import time
from pathlib import Path

from psychopy import event, sound, visual

from eeg.lsl_markers import send_marker
from experiments.trial_sequences import (
    END_SECONDS,
    STAGE_BLANK,
    STAGE_CROSS,
    STAGE_STIMULUS,
    TRIAL_SEQUENCES,
)
from gui.ui_theme import BG_COLOR, BUTTON_MUTED, PANEL_BORDER, TEXT_PRIMARY


MAX_CONSECUTIVE_CLASS_REPEATS = 3

ARM_WORDS = ["APLAUDIR", "CONECTAR", "CORTAR", "ESCRIBIR", "LANZAR"]
LEG_WORDS = ["CAMINAR", "MARCHAR", "PATEAR", "SALTAR", "SENTAR"]

ARM_VIDEO_PREFIXES = ("aplaudir", "conectar", "cortar", "escribir", "lanzar")
LEG_VIDEO_PREFIXES = ("caminar", "marchar", "patear", "saltar", "sentar")


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


def run_motor_imagery(window, trials, marker_outlet, recorder, target_key, stimulus_gender):
    _run_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        target_key,
        stimulus_gender,
        ["MI"],
        "motor_imagery",
    )


def run_action_words(window, trials, marker_outlet, recorder, target_key, stimulus_gender):
    _run_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        target_key,
        stimulus_gender,
        ["AW"],
        "action_words",
    )


def run_motor_observation(window, trials, marker_outlet, recorder, target_key, stimulus_gender):
    _run_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        target_key,
        stimulus_gender,
        ["MO"],
        "motor_observation",
    )


def run_mixed_protocol(window, trials, marker_outlet, recorder, target_key, stimulus_gender):
    _run_protocol(
        window,
        trials,
        marker_outlet,
        recorder,
        target_key,
        stimulus_gender,
        ["MI", "AW", "MO"],
        "mix",
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
):
    classes = _target_classes(target_key)
    trial_plan = _build_trial_plan(trials, modalities, classes)
    trial_sequence = _trial_sequence(experiment_key)

    cross = _text_stim(window, "+", height=0.16, font="Arial")
    end_text = _text_stim(window, "Fin del experimento", height=0.08)
    abort_text = _text_stim(window, "Sesion finalizada", height=0.08)
    abort_control = AbortControl(window)
    mo_movie_paths = _prepare_mo_movie_paths(trial_plan, target_key, stimulus_gender)
    movie_cache = _build_movie_cache(window, mo_movie_paths.values())

    send_marker(marker_outlet, f"TARGET_{target_key.upper()}")
    send_marker(marker_outlet, f"GENDER_{stimulus_gender.upper()}")
    _draw_stage(window, abort_control=abort_control)

    try:
        ended_early = False

        try:
            for trial_id, (modality, class_key) in enumerate(trial_plan, start=1):
                stimulus, task_marker, cleanup = _build_task_stimulus(
                    window,
                    modality,
                    class_key,
                    target_key,
                    stimulus_gender,
                    movie_cache,
                    mo_movie_paths.get(trial_id - 1),
                )
                stimulus_cleaned = False

                def cleanup_stimulus():
                    nonlocal stimulus_cleaned

                    if stimulus_cleaned:
                        return

                    _stop_stimulus(stimulus)
                    cleanup()
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
                            stimulus=stimulus,
                            task_marker=task_marker,
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
    finally:
        _unload_movie_cache(movie_cache)


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
    stimulus,
    task_marker,
    cross,
    stage_options,
    cleanup_stimulus,
    abort_control,
):
    if stage_type == STAGE_BLANK:
        _draw_stage(window, abort_control=abort_control)
        send_marker(marker_outlet, stage_marker)
        _record_stage(
            recorder,
            duration,
            on_tick=lambda: _draw_stage(window, abort_control=abort_control),
            beep_config=stage_options.get("beep"),
            abort_control=abort_control,
        )
        return

    if stage_type == STAGE_CROSS:
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

    if stage_type == STAGE_STIMULUS:
        _start_stimulus(stimulus)
        send_marker(marker_outlet, stage_marker)
        send_marker(marker_outlet, task_marker)
        try:
            _record_stage(
                recorder,
                duration,
                on_tick=lambda current_stimulus=stimulus: _draw_stage(
                    window,
                    [current_stimulus],
                    abort_control=abort_control,
                ),
                beep_config=stage_options.get("beep"),
                abort_control=abort_control,
            )
        finally:
            cleanup_stimulus()
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
):
    if modality == "MI":
        return _build_mi_stimulus(window, class_key, target_key)
    if modality == "AW":
        return _build_aw_stimulus(window, class_key, target_key)
    if modality == "MO":
        return _build_mo_stimulus(
            window,
            class_key,
            target_key,
            stimulus_gender,
            movie_cache,
            movie_path,
        )

    raise ValueError(f"Modalidad no soportada: {modality}")


def _build_mi_stimulus(window, class_key, target_key):
    if target_key == "left_vs_right":
        text = "←" if class_key == "left" else "→"
        stimulus = _text_stim(window, text, height=0.16, font="Segoe UI Symbol")
    else:
        text = "BRAZOS" if class_key == "arm" else "PIERNAS"
        stimulus = _text_stim(window, text, height=0.075)

    return stimulus, f"MI_{class_key.upper()}", _noop


def _build_aw_stimulus(window, class_key, target_key):
    if target_key == "left_vs_right":
        text = "IZQUIERDA" if class_key == "left" else "DERECHA"
        marker = f"AW_{class_key.upper()}"
    else:
        words = ARM_WORDS if class_key == "arm" else LEG_WORDS
        text = random.choice(words)
        marker = f"AW_{class_key.upper()}_{_marker_token(text)}"

    stimulus = _text_stim(window, text, height=0.065)
    return stimulus, marker, _noop


def _build_mo_stimulus(
    window,
    class_key,
    target_key,
    stimulus_gender,
    movie_cache=None,
    movie_path=None,
):
    movie_path = movie_path or _select_movie_path(class_key, target_key, stimulus_gender)
    movie = (movie_cache or {}).get(movie_path)

    if movie is None:
        movie = _build_movie_stim(window, movie_path)
        cleanup = movie.unload
    else:
        cleanup = _noop

    marker = f"MO_{class_key.upper()}"
    return movie, marker, cleanup


def _build_trial_plan(trials, modalities, classes):
    pending_trials = [
        (modality, class_key)
        for modality in modalities
        for class_key in classes
        for _ in range(trials)
    ]
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


def _would_exceed_class_repeat(trial_plan, class_key, max_repeats):
    if len(trial_plan) < max_repeats:
        return False

    recent_classes = [trial_class for _, trial_class in trial_plan[-max_repeats:]]
    return all(recent_class == class_key for recent_class in recent_classes)


def _prepare_mo_movie_paths(trial_plan, target_key, stimulus_gender):
    movie_paths = {}

    for index, (modality, class_key) in enumerate(trial_plan):
        if modality == "MO":
            movie_paths[index] = _select_movie_path(class_key, target_key, stimulus_gender)

    return movie_paths


def _build_movie_cache(window, movie_paths):
    return {
        movie_path: _build_movie_stim(window, movie_path)
        for movie_path in sorted(set(movie_paths))
    }


def _build_movie_stim(window, movie_path):
    window_aspect = window.size[0] / window.size[1]

    return visual.MovieStim(
        window,
        str(movie_path),
        size=(window_aspect, 1.0),
        units="height",
        loop=False,
        noAudio=True,
        autoStart=False,
    )


def _unload_movie_cache(movie_cache):
    for movie in movie_cache.values():
        movie.unload()


def _select_movie_path(class_key, target_key, stimulus_gender):
    if target_key == "left_vs_right":
        filename = "raise_left_arm.mp4" if class_key == "left" else "raise_right_arm.mp4"
        path = Path("stimuli") / "motor_observation" / "left_vs_right" / filename
        if not path.exists():
            raise FileNotFoundError(f"No se encontro el video requerido: {path}")
        return path

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

    return random.choice(candidates)


def _target_classes(target_key):
    if target_key == "left_vs_right":
        return ["left", "right"]
    if target_key == "arm_vs_leg":
        return ["arm", "leg"]

    raise ValueError(f"Objetivo no soportado: {target_key}")


def _text_stim(window, text, height, font="Segoe UI"):
    return visual.TextStim(
        win=window,
        text=text,
        units="height",
        height=height,
        color=TEXT_PRIMARY,
        colorSpace="rgb255",
        bold=True,
        font=font,
        wrapWidth=0.95,
    )


def _draw_stage(window, stimuli=None, abort_control=None):
    window.color = BG_COLOR

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
