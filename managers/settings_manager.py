import pygame
import json
import os
import math
import random


class SettingsManager:

    def __init__(self, screen, width, height):
        self.screen = screen
        self.w = width
        self.h = height

        self.title_font = pygame.font.SysFont(
            "Arial", 38, bold=True
        )

        self.label_font = pygame.font.SysFont(
            "Arial", 18, bold=True
        )

        self.small_font = pygame.font.SysFont(
            "Arial", 10, bold=True
        )

        self.status_font = pygame.font.SysFont(
            "Arial", 12, bold=True
        )

        self.neon_cyan = (0, 245, 255)
        self.neon_blue = (45, 130, 255)
        self.neon_purple = (145, 55, 255)

        self.time = 0
        self.return_to_game = False

        self.stars = []

        for _ in range(90):
            self.stars.append({
                "x": random.randint(0, self.w),
                "y": random.randint(0, self.h),
                "size": random.choice([1, 1, 1, 2]),
                "speed": random.uniform(0.15, 0.6),
                "phase": random.uniform(0, math.pi * 2)
            })

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.settings_file = os.path.join(
            base_dir,
            "settings.json"
        )

        self.settings = self.load_settings()

        self.control_button = pygame.Rect(
            170, 245, 460, 95
        )

        self.toggle_rect = pygame.Rect(
            505, 270, 100, 44
        )

        self.back_button = pygame.Rect(
            270, 385, 260, 55
        )

    def open_from_game(self):
        self.return_to_game = True

    def load_settings(self):

        default_settings = {
            "remembered_username": "",
            "show_controls": True
        }

        if not os.path.exists(self.settings_file):

            self.settings = default_settings
            self.save_settings()
            return self.settings

        try:

            with open(
                self.settings_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if "remembered_username" not in data:
                data["remembered_username"] = ""

            if "show_controls" not in data:
                data["show_controls"] = True

            self.settings = data
            self.save_settings()

            return self.settings

        except:

            self.settings = default_settings
            return self.settings

    def save_settings(self):

        try:

            with open(
                self.settings_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.settings,
                    file,
                    indent=4
                )

        except:
            pass

    def update(self, events):

        self.time += 0.05

        for star in self.stars:

            star["y"] += star["speed"]

            if star["y"] > self.h:

                star["y"] = 0
                star["x"] = random.randint(
                    0,
                    self.w
                )

        for event in events:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    if self.control_button.collidepoint(
                        event.pos
                    ):

                        self.settings["show_controls"] = not self.settings.get(
                            "show_controls",
                            True
                        )

                        self.save_settings()

                    elif self.back_button.collidepoint(
                        event.pos
                    ):

                        if self.return_to_game:

                            self.return_to_game = False
                            return "game"

                        return "home"

        return None

    def draw(self):

        self.draw_background()
        self.draw_header()
        self.draw_title()
        self.draw_control_panel()
        self.draw_back_button()
        self.draw_footer()

    def draw_background(self):

        self.screen.fill(
            (2, 4, 18)
        )

        for star in self.stars:

            brightness = int(
                100 +
                80 * math.sin(
                    self.time * 2 +
                    star["phase"]
                )
            )

            brightness = max(
                40,
                min(255, brightness)
            )

            pygame.draw.circle(
                self.screen,
                (30, brightness, 255),
                (
                    int(star["x"]),
                    int(star["y"])
                ),
                star["size"]
            )

        pygame.draw.line(
            self.screen,
            (10, 35, 65),
            (0, 115),
            (self.w, 115),
            1
        )

        pygame.draw.line(
            self.screen,
            (10, 35, 65),
            (0, 535),
            (self.w, 535),
            1
        )

    def draw_header(self):

        pygame.draw.rect(
            self.screen,
            (3, 10, 25),
            (0, 0, self.w, 115)
        )

        pygame.draw.line(
            self.screen,
            self.neon_cyan,
            (0, 114),
            (self.w, 114),
            2
        )

        logo_font = pygame.font.SysFont(
            "Arial",
            25,
            bold=True
        )

        logo = logo_font.render(
            "SPACE INVADERS",
            True,
            self.neon_cyan
        )

        self.screen.blit(
            logo,
            (25, 25)
        )

        by = self.small_font.render(
            "BY: PRINCES BENDOY",
            True,
            self.neon_purple
        )

        self.screen.blit(
            by,
            (27, 58)
        )

        status = self.small_font.render(
            "● SYSTEM ONLINE",
            True,
            self.neon_cyan
        )

        self.screen.blit(
            status,
            (665, 35)
        )

        version = self.small_font.render(
            "v1.0.0",
            True,
            (100, 120, 145)
        )

        self.screen.blit(
            version,
            (738, 58)
        )

    def draw_title(self):

        self.draw_gear_icon(
            335,
            165,
            self.neon_cyan
        )

        title = self.title_font.render(
            "SETTINGS",
            True,
            self.neon_cyan
        )

        title_rect = title.get_rect(
            center=(420, 165)
        )

        self.screen.blit(
            title,
            title_rect
        )

    def draw_control_panel(self):

        mouse = pygame.mouse.get_pos()

        hover = self.control_button.collidepoint(
            mouse
        )

        if hover:
            fill = (8, 25, 45)
            border = self.neon_cyan
        else:
            fill = (4, 12, 28)
            border = (20, 65, 95)

        pygame.draw.rect(
            self.screen,
            fill,
            self.control_button,
            border_radius=16
        )

        pygame.draw.rect(
            self.screen,
            border,
            self.control_button,
            2,
            border_radius=16
        )

        self.draw_gamepad_icon(
            215,
            292,
            self.neon_cyan
        )

        label = self.label_font.render(
            "SHOW GAME CONTROLS",
            True,
            (235, 245, 255)
        )

        self.screen.blit(
            label,
            (260, 263)
        )

        description = self.small_font.render(
            "Display control buttons during gameplay",
            True,
            (100, 135, 165)
        )

        self.screen.blit(
            description,
            (260, 291)
        )

        self.draw_toggle()

    def draw_toggle(self):

        show_controls = self.settings.get(
            "show_controls",
            True
        )

        mouse = pygame.mouse.get_pos()

        hover = self.toggle_rect.collidepoint(
            mouse
        )

        x, y, w, h = self.toggle_rect

        if show_controls:

            track = self.neon_cyan
            knob_x = x + w - 22
            status = "ON"

        else:

            track = (85, 55, 105)
            knob_x = x + 22
            status = "OFF"

        if hover:

            track = tuple(
                min(255, value + 25)
                for value in track
            )

        pygame.draw.rect(
            self.screen,
            (3, 10, 22),
            self.toggle_rect,
            border_radius=22
        )

        pygame.draw.rect(
            self.screen,
            track,
            self.toggle_rect,
            2,
            border_radius=22
        )

        pygame.draw.circle(
            self.screen,
            track,
            (
                knob_x,
                y + h // 2
            ),
            16
        )

        status_text = self.status_font.render(
            status,
            True,
            track
        )

        if show_controls:

            status_rect = status_text.get_rect(
                midleft=(
                    x + 12,
                    y + h // 2
                )
            )

        else:

            status_rect = status_text.get_rect(
                midright=(
                    x + w - 12,
                    y + h // 2
                )
            )

        self.screen.blit(
            status_text,
            status_rect
        )

    def draw_gamepad_icon(self, x, y, color):

        body = pygame.Rect(
            x - 27,
            y - 15,
            54,
            30
        )

        pygame.draw.rect(
            self.screen,
            color,
            body,
            2,
            border_radius=10
        )

        pygame.draw.line(
            self.screen,
            color,
            (x - 17, y),
            (x - 5, y),
            3
        )

        pygame.draw.line(
            self.screen,
            color,
            (x - 11, y - 6),
            (x - 11, y + 6),
            3
        )

        pygame.draw.circle(
            self.screen,
            color,
            (x + 12, y - 4),
            3
        )

        pygame.draw.circle(
            self.screen,
            color,
            (x + 21, y + 4),
            3
        )

    def draw_gear_icon(self, x, y, color):

        pygame.draw.circle(
            self.screen,
            color,
            (x, y),
            15,
            2
        )

        pygame.draw.circle(
            self.screen,
            color,
            (x, y),
            5,
            2
        )

        for angle in range(0, 360, 45):

            rad = math.radians(angle)

            inner_x = int(
                x + math.cos(rad) * 14
            )

            inner_y = int(
                y + math.sin(rad) * 14
            )

            outer_x = int(
                x + math.cos(rad) * 20
            )

            outer_y = int(
                y + math.sin(rad) * 20
            )

            pygame.draw.line(
                self.screen,
                color,
                (inner_x, inner_y),
                (outer_x, outer_y),
                3
            )

    def draw_back_button(self):

        mouse = pygame.mouse.get_pos()

        hover = self.back_button.collidepoint(
            mouse
        )

        if hover:
            fill = (8, 30, 50)
            border = self.neon_cyan
        else:
            fill = (4, 12, 28)
            border = (30, 90, 125)

        pygame.draw.rect(
            self.screen,
            fill,
            self.back_button,
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            border,
            self.back_button,
            2,
            border_radius=12
        )

        if self.return_to_game:
            button_text = "← BACK TO GAME"
        else:
            button_text = "← BACK TO HOME"

        text = self.label_font.render(
            button_text,
            True,
            border
        )

        text_rect = text.get_rect(
            center=self.back_button.center
        )

        self.screen.blit(
            text,
            text_rect
        )

    def draw_footer(self):

        left = self.small_font.render(
            "SETTINGS SAVED",
            True,
            self.neon_cyan
        )

        right = self.small_font.render(
            "SYSTEM ONLINE",
            True,
            self.neon_blue
        )

        self.screen.blit(
            left,
            (25, 570)
        )

        self.screen.blit(
            right,
            (690, 570)
        )