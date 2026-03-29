# gui/menu.py
import pygame

from core.state_manager import AppState
from gui.ui_theme import (
    BG_COLOR,
    BUTTON_COLOR,
    BUTTON_MUTED,
    PANEL_BORDER,
    PANEL_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from gui.ui_utils import centered_rect, draw_button, draw_text_centered, make_font


def _get_buttons(screen):
    primary = centered_rect(screen, 0.3, 0.1, 0.42)
    secondary = centered_rect(screen, 0.3, 0.1, 0.57)
    return {
        "Motor Imagery": primary,
        "Exit": secondary,
    }


def draw_menu(screen):
    title_font = make_font(screen, 44, bold=True)
    subtitle_font = make_font(screen, 18)
    button_font = make_font(screen, 24, bold=True)
    width, height = screen.get_size()

    screen.fill(BG_COLOR)
    hero = pygame.Rect(int(width * 0.16), int(height * 0.14), int(width * 0.68), int(height * 0.2))
    pygame.draw.rect(screen, PANEL_COLOR, hero, border_radius=24)
    pygame.draw.rect(screen, PANEL_BORDER, hero, width=2, border_radius=24)

    draw_text_centered(
        screen,
        "NeuroEsfera BCI",
        title_font,
        TEXT_PRIMARY,
        (width // 2, int(height * 0.2)),
    )
    draw_text_centered(
        screen,
        "Adquisicion EEG en tiempo real para paradigmas BCI",
        subtitle_font,
        TEXT_SECONDARY,
        (width // 2, int(height * 0.27)),
    )

    buttons = _get_buttons(screen)
    draw_button(
        screen,
        buttons["Motor Imagery"],
        "Motor Imagery",
        button_font,
        BUTTON_COLOR,
        TEXT_PRIMARY,
        PANEL_BORDER,
    )
    draw_button(
        screen,
        buttons["Exit"],
        "Salir",
        button_font,
        BUTTON_MUTED,
        TEXT_PRIMARY,
        PANEL_BORDER,
    )


def handle_menu_events(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        buttons = _get_buttons(pygame.display.get_surface())
        mouse = pygame.mouse.get_pos()

        if buttons["Motor Imagery"].collidepoint(mouse):
            print("Motor Imagery seleccionado")
            return AppState.MOTOR_IMAGERY_SETUP

        if buttons["Exit"].collidepoint(mouse):
            pygame.quit()
            exit()

    return None
