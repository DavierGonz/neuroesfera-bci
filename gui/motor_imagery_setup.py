import pygame
from core.state_manager import AppState

trial_buttons = {
    "10": pygame.Rect(300,250,100,60),
    "20": pygame.Rect(420,250,100,60),
    "40": pygame.Rect(540,250,100,60)
}

back_button = pygame.Rect(350,420,200,60)

def draw_motor_imagery_setup(screen):

    font_title = pygame.font.SysFont("Arial",60)
    font_button = pygame.font.SysFont("Arial",35)

    screen.fill((20,20,20))

    title = font_title.render("Motor Imagery Setup",True,(255,255,255))
    screen.blit(title,(230,100))

    text = font_button.render("Trials por clase",True,(255,255,255))
    screen.blit(text,(360,180))

    for t,rect in trial_buttons.items():

        pygame.draw.rect(screen,(80,80,80),rect)

        label = font_button.render(t,True,(255,255,255))
        screen.blit(label,(rect.x+35,rect.y+15))

    pygame.draw.rect(screen,(80,80,80),back_button)

    label = font_button.render("Back",True,(255,255,255))
    screen.blit(label,(back_button.x+60,back_button.y+15))


def handle_motor_imagery_setup_events(event):

    if event.type == pygame.MOUSEBUTTONDOWN:

        mouse = pygame.mouse.get_pos()

        for t,rect in trial_buttons.items():

            if rect.collidepoint(mouse):
                return int(t)

        if back_button.collidepoint(mouse):
            return AppState.MENU

    return None