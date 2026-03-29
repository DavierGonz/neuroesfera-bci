BG_COLOR = (12, 16, 26)
PANEL_COLOR = (24, 31, 48)
PANEL_BORDER = (58, 74, 112)
BUTTON_COLOR = (68, 102, 196)
BUTTON_ACTIVE = (244, 200, 96)
BUTTON_MUTED = (70, 78, 100)
TEXT_PRIMARY = (245, 247, 255)
TEXT_SECONDARY = (188, 196, 216)
TEXT_ACCENT = (255, 220, 120)
SUCCESS_COLOR = (112, 214, 153)


def scale(screen, value):
    width, height = screen.get_size()
    base = min(width / 900, height / 600)
    return max(1, int(value * base))
