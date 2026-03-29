# experiments/motor_imagery.py

import pygame
import random

from eeg.lsl_markers import send_marker


def run_motor_imagery(screen, trials, marker_outlet, recorder):
    keep_alive = pygame.event.pump

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

        recorder.record_for_duration(5, on_tick=keep_alive)

        # -------------------------
        # PREPARACIÓN
        # -------------------------

        screen.fill((0,0,0))
        screen.blit(cross,(430,250))
        pygame.display.flip()

        send_marker(marker_outlet,"PREPARE")

        recorder.record_for_duration(3, on_tick=keep_alive)

        beep.play()

        recorder.record_for_duration(2, on_tick=keep_alive)

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

        recorder.record_for_duration(5, on_tick=keep_alive)

    # -------------------------
    # FIN DEL EXPERIMENTO
    # -------------------------

    screen.fill((0,0,0))

    text = font_end.render("Fin del experimento",True,(255,255,255))

    screen.blit(text,(250,260))

    pygame.display.flip()

    send_marker(marker_outlet,"END")

    recorder.record_for_duration(5, on_tick=keep_alive)
