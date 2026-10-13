import pygame
import math


class Home:
    def __init__(self, screen, w, h, player=None):
        self.screen = screen
        self.w = w
        self.h = h
        self.player = player
        self.action = None

        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 21, bold=True)
        self.play_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 15)

        self.stars = []

        for i in range(90):
            x = (i * 137) % w
            y = (i * 83) % h
            size = 1 if i % 4 else 2
            self.stars.append((x, y, size))

        self.profile_btn = pygame.Rect(
            45, 320, 190, 52
        )

        self.leaderboard_btn = pygame.Rect(
            45, 385, 190, 52
        )

        self.settings_btn = pygame.Rect(
            45, 450, 190, 52
        )

        play_w = 310
        play_h = 85

        self.play_btn = pygame.Rect(
            w // 2 - play_w // 2,
            330,
            play_w,
            play_h
        )

        self.logout_btn = pygame.Rect(
            w - 190,
            h - 85,
            145,
            48
        )

        self.spaceship = None

        try:
            self.spaceship = pygame.image.load(
                "spaceship.png"
            ).convert_alpha()

            self.spaceship = pygame.transform.smoothscale(
                self.spaceship,
                (85, 85)
            )

        except:
            try:
                self.spaceship = pygame.image.load(
                    "logo.png"
                ).convert_alpha()

                self.spaceship = pygame.transform.smoothscale(
                    self.spaceship,
                    (85, 85)
                )

            except:
                self.spaceship = None

    def draw_background(self):
        self.screen.fill((2, 8, 14))

        for x in range(-300, self.w + 300, 75):
            pygame.draw.line(
                self.screen,
                (4, 30, 40),
                (x, 0),
                (x + 230, self.h),
                1
            )

        for x, y, size in self.stars:
            pygame.draw.circle(
                self.screen,
                (70, 180, 190),
                (x, y),
                size
            )

        self.draw_moon(55, 145, 105)
        self.draw_moon(
            self.w - 65,
            self.h - 110,
            120
        )

        pygame.draw.line(
            self.screen,
            (20, 220, 220),
            (70, 250),
            (self.w - 70, 250),
            2
        )

        pygame.draw.line(
            self.screen,
            (10, 110, 125),
            (70, self.h - 35),
            (self.w - 70, self.h - 35),
            1
        )

    def draw_moon(self, x, y, radius):
        pygame.draw.circle(
            self.screen,
            (7, 28, 36),
            (x, y),
            radius
        )

        pygame.draw.circle(
            self.screen,
            (15, 85, 95),
            (x, y),
            radius,
            2
        )

        craters = [
            (-35, -25, 12),
            (25, -45, 8),
            (40, 20, 15),
            (-15, 35, 9),
            (-50, 15, 6)
        ]

        for dx, dy, r in craters:
            pygame.draw.circle(
                self.screen,
                (5, 22, 29),
                (x + dx, y + dy),
                r
            )

            pygame.draw.circle(
                self.screen,
                (10, 55, 65),
                (x + dx, y + dy),
                r,
                1
            )

    def draw_spaceship_logo(self, x, y):
        if self.spaceship:
            rect = self.spaceship.get_rect(
                center=(x, y)
            )

            self.screen.blit(
                self.spaceship,
                rect
            )

            return

        pygame.draw.circle(
            self.screen,
            (10, 130, 145),
            (x, y),
            38,
            1
        )

        pygame.draw.circle(
            self.screen,
            (20, 220, 220),
            (x, y),
            30,
            1
        )

        ship = [
            (x, y - 25),
            (x - 10, y + 5),
            (x - 27, y + 18),
            (x - 10, y + 15),
            (x, y + 27),
            (x + 10, y + 15),
            (x + 27, y + 18),
            (x + 10, y + 5)
        ]

        pygame.draw.polygon(
            self.screen,
            (5, 40, 50),
            ship
        )

        pygame.draw.polygon(
            self.screen,
            (100, 255, 245),
            ship,
            2
        )

        pygame.draw.circle(
            self.screen,
            (80, 240, 235),
            (x, y - 5),
            5
        )

        pygame.draw.line(
            self.screen,
            (30, 210, 215),
            (x - 12, y + 8),
            (x - 30, y + 27),
            2
        )

        pygame.draw.line(
            self.screen,
            (30, 210, 215),
            (x + 12, y + 8),
            (x + 30, y + 27),
            2
        )

    def draw_header(self):
        self.draw_spaceship_logo(
            self.w // 2,
            65
        )

        title = self.title_font.render(
            "SPACE INVADERS",
            True,
            (180, 255, 248)
        )

        self.screen.blit(
            title,
            (
                self.w // 2 -
                title.get_width() // 2,
                105
            )
        )

        subtitle = self.subtitle_font.render(
            "By: PAGAMONGAN, MELCA G.",
            True,
            (30, 220, 220)
        )

        self.screen.blit(
            subtitle,
            (
                self.w // 2 -
                subtitle.get_width() // 2,
                160
            )
        )

    def draw_side_button(self, rect, text, icon):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)

        if hover:
            bg = (8, 70, 82)
            border = (100, 255, 245)
        else:
            bg = (5, 38, 48)
            border = (25, 190, 195)

        pygame.draw.rect(
            self.screen,
            bg,
            rect,
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            border,
            rect,
            2,
            border_radius=8
        )

        icon_x = rect.x + 28
        icon_y = rect.centery

        pygame.draw.circle(
            self.screen,
            (3, 25, 32),
            (icon_x, icon_y),
            16
        )

        pygame.draw.circle(
            self.screen,
            border,
            (icon_x, icon_y),
            16,
            2
        )

        self.draw_side_icon(
            icon,
            icon_x,
            icon_y,
            border
        )

        text_surface = self.button_font.render(
            text,
            True,
            (225, 255, 252)
        )

        self.screen.blit(
            text_surface,
            (
                rect.x + 55,
                rect.centery -
                text_surface.get_height() // 2
            )
        )

    def draw_side_icon(self, icon, x, y, color):

        if icon == "profile":

            pygame.draw.circle(
                self.screen,
                color,
                (x, y - 5),
                5,
                2
            )

            pygame.draw.arc(
                self.screen,
                color,
                (x - 9, y + 1, 18, 14),
                math.pi,
                2 * math.pi,
                2
            )

        elif icon == "leaderboard":

            pygame.draw.rect(
                self.screen,
                color,
                (x - 9, y - 2, 5, 9),
                2
            )

            pygame.draw.rect(
                self.screen,
                color,
                (x - 2, y - 8, 5, 15),
                2
            )

            pygame.draw.rect(
                self.screen,
                color,
                (x + 5, y - 5, 5, 12),
                2
            )

            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                3
            )

        elif icon == "settings":

            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                7,
                2
            )

            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                2
            )

            for angle in range(0, 360, 45):

                rad = math.radians(angle)

                x1 = int(
                    x + math.cos(rad) * 10
                )

                y1 = int(
                    y + math.sin(rad) * 10
                )

                x2 = int(
                    x + math.cos(rad) * 15
                )

                y2 = int(
                    y + math.sin(rad) * 15
                )

                pygame.draw.line(
                    self.screen,
                    color,
                    (x1, y1),
                    (x2, y2),
                    3
                )

        elif icon == "logout":

            pygame.draw.line(
                self.screen,
                color,
                (x - 9, y),
                (x + 7, y),
                2
            )

            pygame.draw.line(
                self.screen,
                color,
                (x + 1, y - 6),
                (x + 7, y),
                2
            )

            pygame.draw.line(
                self.screen,
                color,
                (x + 1, y + 6),
                (x + 7, y),
                2
            )

    def draw_play_button(self):
        mouse = pygame.mouse.get_pos()
        hover = self.play_btn.collidepoint(mouse)

        if hover:
            bg = (8, 90, 100)
            border = (120, 255, 248)
        else:
            bg = (5, 45, 55)
            border = (30, 205, 210)

        pygame.draw.rect(
            self.screen,
            bg,
            self.play_btn,
            border_radius=12
        )

        pygame.draw.rect(
            self.screen,
            border,
            self.play_btn,
            2,
            border_radius=12
        )

        pygame.draw.polygon(
            self.screen,
            border,
            [
                (
                    self.play_btn.x + 45,
                    self.play_btn.centery - 17
                ),
                (
                    self.play_btn.x + 45,
                    self.play_btn.centery + 17
                ),
                (
                    self.play_btn.x + 71,
                    self.play_btn.centery
                )
            ]
        )

        text = self.play_font.render(
            "PLAY NOW",
            True,
            (225, 255, 252)
        )

        self.screen.blit(
            text,
            (
                self.play_btn.x + 95,
                self.play_btn.centery -
                text.get_height() // 2
            )
        )

    def draw_player(self):
        username = "PLAYER"

        if isinstance(self.player, dict):
            username = self.player.get(
                "username",
                "PLAYER"
            )
        elif self.player:
            username = str(self.player)

        label = self.small_font.render(
            "WELCOME, " + username.upper(),
            True,
            (70, 180, 185)
        )

        self.screen.blit(
            label,
            (
                self.w // 2 -
                label.get_width() // 2,
                285
            )
        )

    def draw_logout(self):
        mouse = pygame.mouse.get_pos()
        hover = self.logout_btn.collidepoint(mouse)

        if hover:
            bg = (8, 70, 82)
            border = (100, 255, 245)
        else:
            bg = (5, 38, 48)
            border = (25, 190, 195)

        pygame.draw.rect(
            self.screen,
            bg,
            self.logout_btn,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            border,
            self.logout_btn,
            2,
            border_radius=7
        )

        self.draw_side_icon(
            "logout",
            self.logout_btn.x + 25,
            self.logout_btn.centery,
            border
        )

        text = self.small_font.render(
            "LOG OUT",
            True,
            (225, 255, 252)
        )

        self.screen.blit(
            text,
            (
                self.logout_btn.x + 48,
                self.logout_btn.centery -
                text.get_height() // 2
            )
        )

    def draw(self):
        self.draw_background()
        self.draw_header()
        self.draw_player()

        self.draw_side_button(
            self.profile_btn,
            "PROFILE",
            "profile"
        )

        self.draw_side_button(
            self.leaderboard_btn,
            "LEADERBOARD",
            "leaderboard"
        )

        self.draw_side_button(
            self.settings_btn,
            "SETTINGS",
            "settings"
        )

        self.draw_play_button()
        self.draw_logout()

    def handle_events(self, events):
        self.action = None

        for event in events:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.mouse_click(event.pos)

    def mouse_click(self, pos):

        if self.profile_btn.collidepoint(pos):

            self.action = "profile"

        elif self.leaderboard_btn.collidepoint(pos):

            self.action = "leaderboard"

        elif self.settings_btn.collidepoint(pos):

            self.action = "settings"

        elif self.play_btn.collidepoint(pos):

            self.action = "play"

        elif self.logout_btn.collidepoint(pos):

            self.action = "logout"