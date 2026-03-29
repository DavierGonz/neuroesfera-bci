# main.py

import pygame

from core.app_controller import AppController
from core.config import FULLSCREEN, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH


pygame.init()

flags = pygame.FULLSCREEN if FULLSCREEN else 0
screen_size = (0, 0) if FULLSCREEN else (WINDOW_WIDTH, WINDOW_HEIGHT)

screen = pygame.display.set_mode(screen_size, flags)
pygame.display.set_caption(WINDOW_TITLE)

clock = pygame.time.Clock()
controller = AppController(screen, clock)

controller.run()
