import pygame


def make_font(screen, size, bold=False):
    from gui.ui_theme import scale

    return pygame.font.SysFont("Segoe UI", scale(screen, size), bold=bold)


def centered_rect(screen, width_ratio, height_ratio, y_ratio):
    width, height = screen.get_size()
    rect_width = int(width * width_ratio)
    rect_height = int(height * height_ratio)
    rect_x = (width - rect_width) // 2
    rect_y = int(height * y_ratio)
    return pygame.Rect(rect_x, rect_y, rect_width, rect_height)


def draw_text_centered(screen, text, font, color, center):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)
    return rect


def draw_button(screen, rect, text, font, fill_color, text_color, border_color):
    pygame.draw.rect(screen, fill_color, rect, border_radius=18)
    pygame.draw.rect(screen, border_color, rect, width=2, border_radius=18)
    draw_text_centered(screen, text, font, text_color, rect.center)
