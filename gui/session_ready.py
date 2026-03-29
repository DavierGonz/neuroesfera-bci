import pygame

from core.state_manager import AppState
from gui.ui_theme import BG_COLOR, PANEL_BORDER, PANEL_COLOR, TEXT_ACCENT, TEXT_PRIMARY, TEXT_SECONDARY
from gui.ui_utils import draw_text_centered, make_font


def draw_session_ready(screen, session_config):
    width, height = screen.get_size()
    font_title = make_font(screen, 42, bold=True)
    font_body = make_font(screen, 24)
    font_hint = make_font(screen, 22, bold=True)

    screen.fill(BG_COLOR)
    panel = pygame.Rect(int(width * 0.15), int(height * 0.16), int(width * 0.7), int(height * 0.62))
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=28)
    pygame.draw.rect(screen, PANEL_BORDER, panel, width=2, border_radius=28)

    draw_text_centered(
        screen,
        "Preparado para iniciar",
        font_title,
        TEXT_PRIMARY,
        (width // 2, int(height * 0.24)),
    )

    details = [
        f"Sujeto: {session_config.subject_number:02d}",
        f"Experimento: {session_config.experiment_number:02d}",
        f"Trials totales: {session_config.total_trials}",
        f"Sesion: {session_config.build_basename()}",
    ]

    for index, text in enumerate(details):
        label = font_body.render(text, True, TEXT_SECONDARY)
        screen.blit(label, label.get_rect(center=(width // 2, int(height * (0.38 + index * 0.08)))))

    hint = font_hint.render(
        "Dale al espacio para iniciar el experimento",
        True,
        TEXT_ACCENT,
    )
    screen.blit(hint, hint.get_rect(center=(width // 2, int(height * 0.72))))


def handle_session_ready_events(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            return "start"

        if event.key == pygame.K_ESCAPE:
            return AppState.MOTOR_IMAGERY_SETUP

    return None
