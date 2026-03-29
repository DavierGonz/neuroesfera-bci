import pygame

from core.session_config import SessionConfig
from core.state_manager import AppState
from gui.ui_theme import (
    BG_COLOR,
    BUTTON_ACTIVE,
    BUTTON_COLOR,
    BUTTON_MUTED,
    PANEL_BORDER,
    PANEL_COLOR,
    TEXT_ACCENT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    scale,
)
from gui.ui_utils import draw_button, draw_text_centered, make_font


def get_default_motor_imagery_setup():
    return {
        "trials_per_class": 5,
        "subject_number": 1,
        "experiment_number": 1,
    }


def draw_motor_imagery_setup(screen, setup_state):
    width, height = screen.get_size()
    layout = _build_layout(screen)

    font_title = make_font(screen, 40, bold=True)
    font_label = make_font(screen, 22, bold=True)
    font_button = make_font(screen, 22, bold=True)
    font_value = make_font(screen, 30, bold=True)
    font_preview = make_font(screen, 18)
    font_hint = make_font(screen, 16)

    screen.fill(BG_COLOR)
    panel = pygame.Rect(int(width * 0.12), int(height * 0.08), int(width * 0.76), int(height * 0.8))
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=28)
    pygame.draw.rect(screen, PANEL_BORDER, panel, width=2, border_radius=28)

    draw_text_centered(
        screen,
        "Configuracion de Motor Imagery",
        font_title,
        TEXT_PRIMARY,
        (width // 2, int(height * 0.16)),
    )
    draw_text_centered(
        screen,
        "Define la sesion antes de comenzar la adquisicion",
        font_hint,
        TEXT_SECONDARY,
        (width // 2, int(height * 0.22)),
    )

    draw_text_centered(
        screen,
        "Trials por clase",
        font_label,
        TEXT_PRIMARY,
        (width // 2, int(height * 0.31)),
    )

    for trial_count, rect in layout["trial_buttons"].items():
        color = BUTTON_MUTED
        if setup_state["trials_per_class"] == trial_count:
            color = BUTTON_ACTIVE

        draw_button(
            screen,
            rect,
            str(trial_count),
            font_button,
            color,
            BG_COLOR,
            PANEL_BORDER,
        )

    _draw_stepper(
        screen,
        "Numero de sujeto",
        setup_state["subject_number"],
        layout["subject_center_y"],
        layout["subject_minus_button"],
        layout["subject_plus_button"],
        layout["value_center_x"],
        font_label,
        font_value,
        font_button,
    )

    _draw_stepper(
        screen,
        "Numero de experimento",
        setup_state["experiment_number"],
        layout["experiment_center_y"],
        layout["experiment_minus_button"],
        layout["experiment_plus_button"],
        layout["value_center_x"],
        font_label,
        font_value,
        font_button,
    )

    total_trials = setup_state["trials_per_class"] * 2
    summary = SessionConfig.for_motor_imagery(
        setup_state["subject_number"],
        setup_state["experiment_number"],
        setup_state["trials_per_class"],
    ).build_basename()

    info = font_label.render(
        f"Trials totales: {total_trials}",
        True,
        TEXT_SECONDARY,
    )
    screen.blit(info, info.get_rect(center=(width // 2, int(height * 0.74))))

    name_preview = font_preview.render(summary, True, TEXT_ACCENT)
    screen.blit(name_preview, name_preview.get_rect(center=(width // 2, int(height * 0.79))))

    draw_button(
        screen,
        layout["back_button"],
        "Back",
        font_button,
        BUTTON_MUTED,
        TEXT_PRIMARY,
        PANEL_BORDER,
    )
    draw_button(
        screen,
        layout["continue_button"],
        "Continuar",
        font_button,
        BUTTON_COLOR,
        TEXT_PRIMARY,
        PANEL_BORDER,
    )


def handle_motor_imagery_setup_events(event, setup_state):
    if event.type != pygame.MOUSEBUTTONDOWN:
        return None

    mouse = pygame.mouse.get_pos()
    layout = _build_layout(pygame.display.get_surface())

    for trial_count, rect in layout["trial_buttons"].items():
        if rect.collidepoint(mouse):
            setup_state["trials_per_class"] = trial_count
            return ("update", setup_state)

    if layout["subject_minus_button"].collidepoint(mouse):
        setup_state["subject_number"] = max(1, setup_state["subject_number"] - 1)
        return ("update", setup_state)

    if layout["subject_plus_button"].collidepoint(mouse):
        setup_state["subject_number"] += 1
        return ("update", setup_state)

    if layout["experiment_minus_button"].collidepoint(mouse):
        setup_state["experiment_number"] = max(1, setup_state["experiment_number"] - 1)
        return ("update", setup_state)

    if layout["experiment_plus_button"].collidepoint(mouse):
        setup_state["experiment_number"] += 1
        return ("update", setup_state)

    if layout["continue_button"].collidepoint(mouse):
        return (
            "ready",
            SessionConfig.for_motor_imagery(
                setup_state["subject_number"],
                setup_state["experiment_number"],
                setup_state["trials_per_class"],
            ),
            setup_state["trials_per_class"],
        )

    if layout["back_button"].collidepoint(mouse):
        return ("back", AppState.MENU)

    return None


def _draw_stepper(
    screen,
    label_text,
    value,
    center_y,
    minus_button,
    plus_button,
    value_center_x,
    font_label,
    font_value,
    font_button,
):
    width, _ = screen.get_size()
    label = font_label.render(label_text, True, TEXT_PRIMARY)
    screen.blit(label, label.get_rect(center=(width // 2, center_y - scale(screen, 26))))

    draw_button(screen, minus_button, "-", font_button, BUTTON_MUTED, TEXT_PRIMARY, PANEL_BORDER)
    draw_button(screen, plus_button, "+", font_button, BUTTON_MUTED, TEXT_PRIMARY, PANEL_BORDER)

    value_text = font_value.render(f"{value:02d}", True, TEXT_PRIMARY)
    screen.blit(value_text, value_text.get_rect(center=(value_center_x, center_y + scale(screen, 18))))


def _build_layout(screen):
    width, height = screen.get_size()
    button_width = int(width * 0.1)
    button_height = int(height * 0.08)
    gap = int(width * 0.025)
    start_x = (width - (4 * button_width + 3 * gap)) // 2
    trial_y = int(height * 0.36)

    trial_buttons = {}
    for index, trial_count in enumerate((5, 10, 20, 40)):
        trial_buttons[trial_count] = pygame.Rect(
            start_x + index * (button_width + gap),
            trial_y,
            button_width,
            button_height,
        )

    stepper_width = int(width * 0.06)
    stepper_height = int(height * 0.07)
    value_center_x = width // 2
    subject_center_y = int(height * 0.54)
    experiment_center_y = int(height * 0.66)
    offset_x = int(width * 0.11)

    return {
        "trial_buttons": trial_buttons,
        "subject_minus_button": pygame.Rect(
            value_center_x - offset_x - stepper_width // 2,
            subject_center_y,
            stepper_width,
            stepper_height,
        ),
        "subject_plus_button": pygame.Rect(
            value_center_x + offset_x - stepper_width // 2,
            subject_center_y,
            stepper_width,
            stepper_height,
        ),
        "experiment_minus_button": pygame.Rect(
            value_center_x - offset_x - stepper_width // 2,
            experiment_center_y,
            stepper_width,
            stepper_height,
        ),
        "experiment_plus_button": pygame.Rect(
            value_center_x + offset_x - stepper_width // 2,
            experiment_center_y,
            stepper_width,
            stepper_height,
        ),
        "subject_center_y": subject_center_y,
        "experiment_center_y": experiment_center_y,
        "value_center_x": value_center_x,
        "back_button": pygame.Rect(
            int(width * 0.22),
            int(height * 0.84),
            int(width * 0.18),
            int(height * 0.08),
        ),
        "continue_button": pygame.Rect(
            int(width * 0.6),
            int(height * 0.84),
            int(width * 0.18),
            int(height * 0.08),
        ),
    }
