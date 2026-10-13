import pygame
import math
from db import register_player, login_player


class LoginManager:
    def __init__(self, screen, w, h):
        self.screen = screen
        self.w = w
        self.h = h

        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.button_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.input_font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)

        self.page = "menu"
        self.username = ""
        self.email = ""
        self.password = ""
        self.active = "username"
        self.message = ""
        self.logged_in_player = None
        self.show_password = False

        cx = w // 2

        self.login_menu_btn = pygame.Rect(
            cx - 190, 315, 380, 62
        )

        self.register_menu_btn = pygame.Rect(
            cx - 190, 395, 380, 62
        )

        box_w = 380
        box_x = cx - box_w // 2

        self.login_user_box = pygame.Rect(
            box_x, 285, box_w, 48
        )

        self.login_pass_box = pygame.Rect(
            box_x, 380, box_w, 48
        )

        self.register_user_box = pygame.Rect(
            box_x, 285, box_w, 48
        )

        self.register_email_box = pygame.Rect(
            box_x, 365, box_w, 48
        )

        self.register_pass_box = pygame.Rect(
            box_x, 435, box_w, 48
        )

        self.action_btn = pygame.Rect(
            cx - 155, 485, 145, 48
        )

        self.back_btn = pygame.Rect(
            cx + 10, 485, 145, 48
        )

        self.stars = []

        for i in range(90):
            x = (i * 137) % w
            y = (i * 83) % h
            size = 1 if i % 4 else 2
            self.stars.append((x, y, size))

    def clear_data(self):
        self.username = ""
        self.email = ""
        self.password = ""
        self.active = "username"
        self.message = ""
        self.logged_in_player = None
        self.show_password = False

    def logout(self):
        self.clear_data()
        self.page = "menu"

    def open_login(self):
        self.clear_data()
        self.page = "login"

    def open_register(self):
        self.clear_data()
        self.page = "register"

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

        self.draw_moon(75, 145, 105)
        self.draw_moon(
            self.w - 75,
            self.h - 120,
            125
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
            (90, self.h - 35),
            (self.w - 90, self.h - 35),
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

    def draw_title(self):
        self.draw_spaceship_logo(
            self.w // 2,
            75
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
                115
            )
        )

        subtitle = self.subtitle_font.render(
            "BY: PAGAMONGAN, MELCA G.",
            True,
            (30, 220, 220)
        )

        self.screen.blit(
            subtitle,
            (
                self.w // 2 -
                subtitle.get_width() // 2,
                170
            )
        )

    def draw_menu_button(self, rect, text, icon):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)

        bg = (
            (8, 70, 82)
            if hover
            else (5, 38, 48)
        )

        border = (
            (100, 255, 245)
            if hover
            else (25, 190, 195)
        )

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

        icon_x = rect.x + 42
        icon_y = rect.centery

        pygame.draw.circle(
            self.screen,
            (3, 25, 32),
            (icon_x, icon_y),
            19
        )

        pygame.draw.circle(
            self.screen,
            border,
            (icon_x, icon_y),
            19,
            2
        )

        self.draw_icon(
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
                rect.centerx -
                text_surface.get_width() // 2 + 15,
                rect.centery -
                text_surface.get_height() // 2
            )
        )

    def draw_icon(self, icon, x, y, color):
        if icon == "login":
            pygame.draw.polygon(
                self.screen,
                color,
                [
                    (x - 8, y),
                    (x + 5, y - 9),
                    (x + 5, y - 4),
                    (x + 10, y - 4),
                    (x + 10, y + 4),
                    (x + 5, y + 4),
                    (x + 5, y + 9)
                ]
            )

        elif icon == "register":
            pygame.draw.circle(
                self.screen,
                color,
                (x, y - 6),
                5,
                2
            )

            pygame.draw.arc(
                self.screen,
                color,
                (x - 10, y, 20, 15),
                math.pi,
                2 * math.pi,
                2
            )

            pygame.draw.line(
                self.screen,
                color,
                (x - 10, y + 7),
                (x + 10, y + 7),
                2
            )

    def draw_eye(self, rect, visible):
        x = rect.right - 28
        y = rect.centery
        color = (80, 255, 245)

        pygame.draw.ellipse(
            self.screen,
            color,
            (x - 11, y - 7, 22, 14),
            2
        )

        if visible:
            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                4
            )
        else:
            pygame.draw.line(
                self.screen,
                color,
                (x - 10, y - 9),
                (x + 10, y + 9),
                2
            )

    def draw_input(
        self,
        rect,
        label,
        value,
        active,
        password=False
    ):
        label_surface = self.small_font.render(
            label,
            True,
            (30, 220, 220)
        )

        self.screen.blit(
            label_surface,
            (rect.x, rect.y - 22)
        )

        border = (
            (80, 255, 245)
            if active
            else (20, 110, 120)
        )

        pygame.draw.rect(
            self.screen,
            (3, 25, 32),
            rect,
            border_radius=6
        )

        pygame.draw.rect(
            self.screen,
            border,
            rect,
            2,
            border_radius=6
        )

        if password:
            if self.show_password:
                display = value
            else:
                display = "*" * len(value)
        else:
            display = value

        text = self.input_font.render(
            display,
            True,
            (220, 255, 250)
        )

        max_text_width = rect.width - 55

        if text.get_width() > max_text_width:
            display = display[-25:]

            text = self.input_font.render(
                display,
                True,
                (220, 255, 250)
            )

        self.screen.blit(
            text,
            (
                rect.x + 14,
                rect.y + 12
            )
        )

        if password:
            self.draw_eye(
                rect,
                self.show_password
            )

        if active:
            blink = (
                pygame.time.get_ticks() // 500
            ) % 2

            if blink:
                cursor_x = (
                    rect.x + 14 +
                    text.get_width()
                )

                if password:
                    cursor_x = min(
                        cursor_x,
                        rect.right - 50
                    )
                else:
                    cursor_x = min(
                        cursor_x,
                        rect.right - 15
                    )

                pygame.draw.line(
                    self.screen,
                    (100, 255, 245),
                    (cursor_x, rect.y + 10),
                    (cursor_x, rect.y + 38),
                    2
                )

    def draw_action_button(self, rect, text):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)

        bg = (
            (8, 80, 90)
            if hover
            else (5, 42, 52)
        )

        border = (
            (100, 255, 245)
            if hover
            else (30, 190, 195)
        )

        pygame.draw.rect(
            self.screen,
            bg,
            rect,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            border,
            rect,
            2,
            border_radius=7
        )

        surface = self.button_font.render(
            text,
            True,
            (220, 255, 252)
        )

        self.screen.blit(
            surface,
            (
                rect.centerx -
                surface.get_width() // 2,
                rect.centery -
                surface.get_height() // 2
            )
        )

    def draw_login(self):
        self.draw_input(
            self.login_user_box,
            "USERNAME / EMAIL",
            self.username,
            self.active == "username"
        )

        self.draw_input(
            self.login_pass_box,
            "PASSWORD",
            self.password,
            self.active == "password",
            True
        )

        self.draw_action_button(
            self.action_btn,
            "LOGIN"
        )

        self.draw_action_button(
            self.back_btn,
            "BACK"
        )

        self.draw_message()

    def draw_register(self):
        self.draw_input(
            self.register_user_box,
            "USERNAME",
            self.username,
            self.active == "username"
        )

        self.draw_input(
            self.register_email_box,
            "EMAIL",
            self.email,
            self.active == "email"
        )

        self.draw_input(
            self.register_pass_box,
            "PASSWORD",
            self.password,
            self.active == "password",
            True
        )

        self.draw_action_button(
            self.action_btn,
            "REGISTER"
        )

        self.draw_action_button(
            self.back_btn,
            "BACK"
        )

        self.draw_message()

    def draw_message(self):
        if self.message:
            text = self.small_font.render(
                self.message,
                True,
                (255, 100, 120)
            )

            self.screen.blit(
                text,
                (
                    self.w // 2 -
                    text.get_width() // 2,
                    self.h - 65
                )
            )

    def draw(self):
        self.draw_background()
        self.draw_title()

        if self.page == "menu":
            self.draw_menu()

        elif self.page == "login":
            self.draw_login()

        elif self.page == "register":
            self.draw_register()

    def draw_menu(self):
        self.draw_menu_button(
            self.login_menu_btn,
            "LOGIN",
            "login"
        )

        self.draw_menu_button(
            self.register_menu_btn,
            "REGISTER",
            "register"
        )

        info = self.small_font.render(
            "SELECT AN OPTION TO CONTINUE",
            True,
            (70, 180, 185)
        )

        self.screen.blit(
            info,
            (
                self.w // 2 -
                info.get_width() // 2,
                480
            )
        )

    def handle_events(self, events):
        for event in events:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:
                    self.mouse_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                self.keyboard_input(event)

    def mouse_click(self, pos):

        if self.page == "menu":

            if self.login_menu_btn.collidepoint(pos):
                self.open_login()

            elif self.register_menu_btn.collidepoint(pos):
                self.open_register()

        elif self.page == "login":

            if self.login_user_box.collidepoint(pos):
                self.active = "username"

            elif self.login_pass_box.collidepoint(pos):

                eye_area = pygame.Rect(
                    self.login_pass_box.right - 55,
                    self.login_pass_box.y,
                    55,
                    self.login_pass_box.height
                )

                if eye_area.collidepoint(pos):
                    self.show_password = not self.show_password
                else:
                    self.active = "password"

            elif self.action_btn.collidepoint(pos):
                self.login()

            elif self.back_btn.collidepoint(pos):
                self.back()

        elif self.page == "register":

            if self.register_user_box.collidepoint(pos):
                self.active = "username"

            elif self.register_email_box.collidepoint(pos):
                self.active = "email"

            elif self.register_pass_box.collidepoint(pos):

                eye_area = pygame.Rect(
                    self.register_pass_box.right - 55,
                    self.register_pass_box.y,
                    55,
                    self.register_pass_box.height
                )

                if eye_area.collidepoint(pos):
                    self.show_password = not self.show_password
                else:
                    self.active = "password"

            elif self.action_btn.collidepoint(pos):
                self.register()

            elif self.back_btn.collidepoint(pos):
                self.back()

    def keyboard_input(self, event):

        if event.key == pygame.K_TAB:

            if self.page == "login":

                if self.active == "username":
                    self.active = "password"
                else:
                    self.active = "username"

            elif self.page == "register":

                if self.active == "username":
                    self.active = "email"

                elif self.active == "email":
                    self.active = "password"

                else:
                    self.active = "username"

        elif event.key == pygame.K_BACKSPACE:

            if self.active == "username":
                self.username = self.username[:-1]

            elif self.active == "email":
                self.email = self.email[:-1]

            elif self.active == "password":
                self.password = self.password[:-1]

        elif event.key == pygame.K_RETURN:

            if self.page == "login":
                self.login()

            elif self.page == "register":
                self.register()

        elif event.unicode.isprintable():

            if self.active == "username":

                if len(self.username) < 100:
                    self.username += event.unicode

            elif self.active == "email":

                if len(self.email) < 100:
                    self.email += event.unicode

            elif self.active == "password":

                if len(self.password) < 100:
                    self.password += event.unicode

    def login(self):

        identifier = self.username.strip()
        password = self.password

        if not identifier or not password:
            self.message = "PLEASE ENTER ALL FIELDS"
            return

        player = login_player(
            identifier,
            password
        )

        if player:
            self.logged_in_player = player
            self.message = ""

        else:
            self.message = "INVALID USERNAME / EMAIL OR PASSWORD"

    def register(self):

        username = self.username.strip()
        email = self.email.strip()
        password = self.password

        if not username or not email or not password:
            self.message = "PLEASE ENTER ALL FIELDS"
            return

        if len(username) < 3:
            self.message = "USERNAME MUST BE AT LEAST 3 CHARACTERS"
            return

        if "@" not in email or "." not in email:
            self.message = "PLEASE ENTER A VALID EMAIL"
            return

        if len(password) < 3:
            self.message = "PASSWORD MUST BE AT LEAST 3 CHARACTERS"
            return

        success, result = register_player(
            username,
            email,
            password
        )

        if success:
            self.clear_data()
            self.page = "login"
            self.message = "ACCOUNT CREATED - PLEASE LOGIN"

        else:
            self.message = result

    def back(self):
        self.clear_data()
        self.page = "menu"