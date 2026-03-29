import sys

import pygame

from core.session_config import SessionConfig
from core.state_manager import AppState
from experiments.motor_imagery import run_motor_imagery
from gui.menu import draw_menu, handle_menu_events
from gui.motor_imagery_setup import (
    draw_motor_imagery_setup,
    get_default_motor_imagery_setup,
    handle_motor_imagery_setup_events,
)
from gui.session_complete import (
    draw_session_complete,
    handle_session_complete_events,
)
from gui.session_ready import draw_session_ready, handle_session_ready_events
from services.experiment_session import ExperimentSession


class AppController:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.state = AppState.MENU
        self.recorder = None
        self.motor_imagery_setup = get_default_motor_imagery_setup()
        self.pending_session_config = None
        self.pending_trials_per_class = None
        self.last_session_result = None

    def run(self):
        while True:
            self._draw_current_screen()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._shutdown()

                self._handle_event(event)

            self.clock.tick(250)

    def _draw_current_screen(self):
        if self.state == AppState.MENU:
            draw_menu(self.screen)
        elif self.state == AppState.MOTOR_IMAGERY_SETUP:
            draw_motor_imagery_setup(self.screen, self.motor_imagery_setup)
        elif self.state == AppState.MOTOR_IMAGERY_READY and self.pending_session_config:
            draw_session_ready(self.screen, self.pending_session_config)
        elif self.state == AppState.SESSION_COMPLETE and self.last_session_result:
            draw_session_complete(self.screen, self.last_session_result)

    def _handle_event(self, event):
        if self.state == AppState.MENU:
            self._handle_menu_event(event)
        elif self.state == AppState.MOTOR_IMAGERY_SETUP:
            self._handle_motor_imagery_setup_event(event)
        elif self.state == AppState.MOTOR_IMAGERY_READY:
            self._handle_motor_imagery_ready_event(event)
        elif self.state == AppState.SESSION_COMPLETE:
            self._handle_session_complete_event(event)

    def _handle_menu_event(self, event):
        new_state = handle_menu_events(event)

        if new_state is not None:
            self.state = new_state

    def _handle_motor_imagery_setup_event(self, event):
        result = handle_motor_imagery_setup_events(event, self.motor_imagery_setup)

        if result is None:
            return

        action = result[0]

        if action == "update":
            self.motor_imagery_setup = result[1]
        elif action == "ready":
            self.pending_session_config = result[1]
            self.pending_trials_per_class = result[2]
            self.state = AppState.MOTOR_IMAGERY_READY
        elif action == "back":
            self.state = result[1]

    def _handle_motor_imagery_ready_event(self, event):
        result = handle_session_ready_events(event)

        if result == "start" and self.pending_session_config is not None:
            trials_per_class = self.pending_trials_per_class

            self._run_session(
                self.pending_session_config,
                lambda session: run_motor_imagery(
                    self.screen,
                    trials_per_class,
                    session.marker_outlet,
                    session.recorder,
                )
            )
            self.pending_session_config = None
            self.pending_trials_per_class = None
            self.state = AppState.SESSION_COMPLETE
        elif result == AppState.MOTOR_IMAGERY_SETUP:
            self.pending_session_config = None
            self.pending_trials_per_class = None
            self.state = result

    def _handle_session_complete_event(self, event):
        result = handle_session_complete_events(event)

        if result == AppState.MENU:
            self.last_session_result = None
            self.state = result

    def _run_session(self, session_config, experiment_runner):
        session = ExperimentSession(session_config)
        self.recorder = session.recorder

        try:
            experiment_runner(session)
        finally:
            session.close()
            self.last_session_result = session.session_result
            self.recorder = None

    def _shutdown(self):
        if self.recorder:
            self.recorder.close()

        pygame.quit()
        sys.exit()
