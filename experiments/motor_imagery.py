# experiments/motor_imagery.py

import pygame
import random
import time

from eeg.lsl_markers import create_marker_stream, send_marker


def run_motor_imagery(screen, trials):

    marker_outlet = create_marker_stream()

    font = pygame.font.SysFont("Arial",120)
    font_end = pygame.font.SysFont("Arial",60)

    cross = font.render("+",True,(255,255,255))
    left_arrow = font.render("←",True,(255,255,255))
    right_arrow = font.render("→",True,(255,255,255))

    # -------------------------
    # Balancear trials
    # -------------------------

    directions = ["left"] * trials + ["right"] * trials
    random.shuffle(directions)

    total_trials = len(directions)

    pygame.mixer.init()
    beep = pygame.mixer.Sound("stimuli/beep.mp3")

    for trial_id, direction in enumerate(directions, start=1):

        # enviar marker de trial
        send_marker(marker_outlet, f"TRIAL_{trial_id}")

        # -------------------------
        # BASELINE
        # -------------------------

        screen.fill((0,0,0))
        pygame.display.flip()

        send_marker(marker_outlet,"BASELINE")

        time.sleep(5)

        # -------------------------
        # PREPARACIÓN
        # -------------------------

        screen.fill((0,0,0))
        screen.blit(cross,(430,250))
        pygame.display.flip()

        send_marker(marker_outlet,"PREPARE")

        time.sleep(3)

        beep.play()

        time.sleep(2)

        # -------------------------
        # ESTÍMULO
        # -------------------------

        screen.fill((0,0,0))

        if direction == "left":

            screen.blit(left_arrow,(430,250))
            send_marker(marker_outlet,"MI_LEFT")

        else:

            screen.blit(right_arrow,(430,250))
            send_marker(marker_outlet,"MI_RIGHT")

        pygame.display.flip()

        print("Trial", trial_id, direction)

        time.sleep(5)

    # -------------------------
    # FIN DEL EXPERIMENTO
    # -------------------------

    screen.fill((0,0,0))

    text = font_end.render("Fin del experimento",True,(255,255,255))

    screen.blit(text,(250,260))

    pygame.display.flip()

    send_marker(marker_outlet,"END")

    time.sleep(5)