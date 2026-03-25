# main.py

import pygame
import sys

from gui.menu import draw_menu, handle_menu_events
from gui.motor_imagery_setup import draw_motor_imagery_setup, handle_motor_imagery_setup_events

from experiments.motor_imagery import run_motor_imagery
from experiments.motor_imagery_test import run_motor_imagery_test

from eeg.recorder import EEGRecorder
from eeg.lsl_markers import create_marker_stream   # 👈 NUEVO

from core.state_manager import AppState


pygame.init()

WIDTH = 900
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NeuroEsfera BCI")

clock = pygame.time.Clock()

state = AppState.MENU

recorder = None


while True:

    # -----------------------
    # Dibujar pantalla
    # -----------------------

    if state == AppState.MENU:
        draw_menu(screen)

    elif state == AppState.MOTOR_IMAGERY_SETUP:
        draw_motor_imagery_setup(screen)

    pygame.display.flip()

    # -----------------------
    # Eventos
    # -----------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            if recorder:
                recorder.close()

            pygame.quit()
            sys.exit()

        # -----------------------
        # MENU
        # -----------------------

        if state == AppState.MENU:

            new_state = handle_menu_events(event)

            if new_state == AppState.MOTOR_IMAGERY_TEST:

                print("Motor Imagery TEST seleccionado")

                marker_outlet = create_marker_stream()   # 👈 NUEVO

                recorder = EEGRecorder()

                run_motor_imagery_test(screen, marker_outlet, recorder)

                recorder.close()
                recorder = None

                state = AppState.MENU

            elif new_state is not None:

                state = new_state

        # -----------------------
        # MOTOR IMAGERY SETUP
        # -----------------------

        elif state == AppState.MOTOR_IMAGERY_SETUP:

            result = handle_motor_imagery_setup_events(event)

            if isinstance(result, int):

                marker_outlet = create_marker_stream()   # 👈 NUEVO

                recorder = EEGRecorder()

                run_motor_imagery(screen, result)

                recorder.close()
                recorder = None

                state = AppState.MENU

            elif result is not None:

                state = result

    # -----------------------
    # Grabación EEG
    # -----------------------

    if recorder:

        recorder.update_marker()
        recorder.record_sample()

    clock.tick(250)