# gui/menu.py
import pygame
from core.state_manager import AppState


buttons = {

    "Motor Imagery": pygame.Rect(350,180,200,60),
    "Motor Imagery TEST": pygame.Rect(350,260,200,60),
    "Action Words": pygame.Rect(350,340,200,60),
    "Exit": pygame.Rect(350,420,200,60)

}


def draw_menu(screen):

    font_title = pygame.font.SysFont("Arial",60)
    font_button = pygame.font.SysFont("Arial",35)

    screen.fill((20,20,20))

    title = font_title.render("NeuroEsfera BCI",True,(255,255,255))
    screen.blit(title,(270,80))

    for text,rect in buttons.items():

        pygame.draw.rect(screen,(80,80,80),rect)

        label = font_button.render(text,True,(255,255,255))
        screen.blit(label,(rect.x+15,rect.y+15))


def handle_menu_events(event):

    if event.type == pygame.MOUSEBUTTONDOWN:

        mouse = pygame.mouse.get_pos()

        if buttons["Motor Imagery"].collidepoint(mouse):
            print("Motor Imagery seleccionado")
            return AppState.MOTOR_IMAGERY_SETUP

        if buttons["Motor Imagery TEST"].collidepoint(mouse):
            return AppState.MOTOR_IMAGERY_TEST

        if buttons["Exit"].collidepoint(mouse):
            pygame.quit()
            exit()

    return None