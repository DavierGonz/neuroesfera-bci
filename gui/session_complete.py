import os

import pygame

from core.state_manager import AppState
from gui.ui_theme import BG_COLOR, PANEL_BORDER, PANEL_COLOR, SUCCESS_COLOR, TEXT_ACCENT, TEXT_PRIMARY, TEXT_SECONDARY
from gui.ui_utils import draw_text_centered, make_font


def draw_session_complete(screen, session_result):
    width, height = screen.get_size()
    font_title = make_font(screen, 40, bold=True)
    font_body = make_font(screen, 22)
    font_hint = make_font(screen, 22, bold=True)

    screen.fill(BG_COLOR)
    panel = pygame.Rect(int(width * 0.12), int(height * 0.14), int(width * 0.76), int(height * 0.68))
    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=28)
    pygame.draw.rect(screen, PANEL_BORDER, panel, width=2, border_radius=28)

    draw_text_centered(
        screen,
        "Sesion guardada",
        font_title,
        SUCCESS_COLOR,
        (width // 2, int(height * 0.24)),
    )

    details = [
        f"Formato: {session_result['backend'].upper()}",
        f"Archivo: {os.path.basename(session_result['recording_path'])}",
        f"EEG stream: {session_result['stream_name']}",
        "Electrodos: " + ", ".join(session_result["channel_labels"]),
    ]

    for index, text in enumerate(details):
        label = font_body.render(text, True, TEXT_SECONDARY)
        screen.blit(label, label.get_rect(center=(width // 2, int(height * (0.38 + index * 0.09)))))

    hint = font_hint.render(
        "Presiona espacio para volver al menu",
        True,
        TEXT_ACCENT,
    )
    screen.blit(hint, hint.get_rect(center=(width // 2, int(height * 0.76))))


def handle_session_complete_events(event):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        return AppState.MENU

    return None
