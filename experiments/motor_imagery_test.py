import pygame
import random
import time

from eeg.lsl_markers import send_marker


def run_motor_imagery_test(screen, marker_outlet, recorder):

    font = pygame.font.SysFont("Arial",120)
    font_end = pygame.font.SysFont("Arial",60)

    cross = font.render("+",True,(255,255,255))
    left_arrow = font.render("←",True,(255,255,255))
    right_arrow = font.render("→",True,(255,255,255))

    directions = ["left"] * 3 + ["right"] * 3
    random.shuffle(directions)

    pygame.mixer.init()
    beep = pygame.mixer.Sound("stimuli/beep.mp3")

    for trial_id, direction in enumerate(directions, start=1):

        send_marker(marker_outlet, f"TRIAL_{trial_id}")

        # -------------------------
        # BASELINE (5s)
        # -------------------------

        screen.fill((0,0,0))
        pygame.display.flip()

        send_marker(marker_outlet,"BASELINE")

        start = time.time()

        while time.time() - start < 5:

            recorder.update_marker()
            recorder.record_sample()

            time.sleep(0.004)

        # -------------------------
        # PREPARE (3s)
        # -------------------------

        screen.fill((0,0,0))
        screen.blit(cross,(430,250))
        pygame.display.flip()

        send_marker(marker_outlet,"PREPARE")

        start = time.time()

        while time.time() - start < 3:

            recorder.update_marker()
            recorder.record_sample()

            time.sleep(0.004)

        beep.play()

        # -------------------------
        # ESPERA 2s
        # -------------------------

        start = time.time()

        while time.time() - start < 2:

            recorder.update_marker()
            recorder.record_sample()

            time.sleep(0.004)

        # -------------------------
        # MOTOR IMAGERY (5s)
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

        start = time.time()

        while time.time() - start < 5:

            recorder.update_marker()
            recorder.record_sample()

            time.sleep(0.004)

    # -------------------------
    # FIN DEL TEST
    # -------------------------

    screen.fill((0,0,0))

    text = font_end.render("Fin del TEST",True,(255,255,255))

    screen.blit(text,(300,260))

    pygame.display.flip()

    send_marker(marker_outlet,"END")

    start = time.time()

    while time.time() - start < 5:

        recorder.update_marker()
        recorder.record_sample()

        time.sleep(0.004)