import pygame
from db import update_player_profile, delete_player, get_player_highest_score


class Profile:
    def __init__(self, screen, w, h, player):
        self.screen = screen
        self.w = w
        self.h = h
        self.player = player

        self.action = None
        self.editing = False
        self.message = ""
        self.delete_success_time = 0

        self.title_font = pygame.font.SysFont("Arial", 38, bold=True)
        self.label_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 22)
        self.button_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 15)
        self.warning_font = pygame.font.SysFont("Arial", 17, bold=True)

        self.player_id = self.get_player_id()
        self.username = self.get_username()
        self.email = self.get_email()

        self.username_box = pygame.Rect(200, 230, 400, 50)
        self.email_box = pygame.Rect(200, 315, 400, 50)

        self.save_btn = pygame.Rect(200, 400, 185, 50)
        self.cancel_btn = pygame.Rect(415, 400, 185, 50)

        self.edit_btn = pygame.Rect(285, 400, 230, 55)
        self.delete_btn = pygame.Rect(285, 475, 230, 50)

        self.back_btn = pygame.Rect(30, 530, 140, 45)

        self.confirm_delete_btn = pygame.Rect(215, 405, 175, 50)
        self.cancel_delete_btn = pygame.Rect(410, 405, 175, 50)

        self.active = "username"

        self.stars = []

        for i in range(90):
            x = (i * 137) % w
            y = (i * 83) % h
            size = 1 if i % 4 else 2
            self.stars.append((x, y, size))

        self.highest_score = get_player_highest_score(self.player_id)

    def get_player_id(self):
        if isinstance(self.player, dict):
            return self.player.get("player_id")

        if isinstance(self.player, (tuple, list)):
            return self.player[0]

        return None

    def get_username(self):
        if isinstance(self.player, dict):
            return self.player.get("username", "")

        if isinstance(self.player, (tuple, list)):
            if len(self.player) > 1:
                return self.player[1]

        return ""

    def get_email(self):
        if isinstance(self.player, dict):
            return self.player.get("email") or ""

        if isinstance(self.player, (tuple, list)):
            if len(self.player) > 2:
                return self.player[2] or ""

        return ""

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

        pygame.draw.circle(
            self.screen,
            (7, 28, 36),
            (75, 145),
            105
        )

        pygame.draw.circle(
            self.screen,
            (15, 85, 95),
            (75, 145),
            105,
            2
        )

        pygame.draw.circle(
            self.screen,
            (7, 28, 36),
            (self.w - 75, self.h - 120),
            125
        )

        pygame.draw.circle(
            self.screen,
            (15, 85, 95),
            (self.w - 75, self.h - 120),
            125,
            2
        )

        pygame.draw.line(
            self.screen,
            (20, 220, 220),
            (50, 175),
            (self.w - 50, 175),
            2
        )

    def draw_button(self, rect, text):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)

        bg = (8, 80, 90) if hover else (5, 42, 52)
        border = (100, 255, 245) if hover else (30, 190, 195)

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
                rect.centerx - surface.get_width() // 2,
                rect.centery - surface.get_height() // 2
            )
        )

    def draw_input(self, rect, label, value, active):
        label_surface = self.small_font.render(
            label,
            True,
            (30, 220, 220)
        )

        self.screen.blit(
            label_surface,
            (rect.x, rect.y - 22)
        )

        border = (80, 255, 245) if active else (20, 110, 120)

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

        text = self.text_font.render(
            value,
            True,
            (220, 255, 250)
        )

        self.screen.blit(
            text,
            (rect.x + 14, rect.y + 12)
        )

        if active:
            blink = (pygame.time.get_ticks() // 500) % 2

            if blink:
                cursor_x = min(
                    rect.x + 14 + text.get_width(),
                    rect.right - 15
                )

                pygame.draw.line(
                    self.screen,
                    (100, 255, 245),
                    (cursor_x, rect.y + 10),
                    (cursor_x, rect.y + 38),
                    2
                )

    def draw(self):
        self.draw_background()

        if self.action == "delete_success":
            title = self.title_font.render(
                "ACCOUNT DELETED",
                True,
                (180, 255, 248)
            )

            self.screen.blit(
                title,
                (
                    self.w // 2 - title.get_width() // 2,
                    230
                )
            )

            message = self.text_font.render(
                self.message,
                True,
                (80, 255, 200)
            )

            self.screen.blit(
                message,
                (
                    self.w // 2 - message.get_width() // 2,
                    300
                )
            )

            return

        title = self.title_font.render(
            "PLAYER PROFILE",
            True,
            (180, 255, 248)
        )

        self.screen.blit(
            title,
            (
                self.w // 2 - title.get_width() // 2,
                105
            )
        )

        if self.action == "confirm_delete":
            self.draw_delete_confirmation()
            return

        if self.editing:
            self.draw_edit()
        else:
            self.draw_profile()

        self.draw_button(
            self.back_btn,
            "BACK"
        )

    def draw_profile(self):
        panel = pygame.Rect(150, 205, 500, 250)

        pygame.draw.rect(
            self.screen,
            (3, 25, 32),
            panel,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            (20, 190, 195),
            panel,
            2,
            border_radius=10
        )

        name_label = self.label_font.render(
            "PLAYER NAME",
            True,
            (30, 220, 220)
        )

        self.screen.blit(
            name_label,
            (190, 240)
        )

        name = self.text_font.render(
            self.username,
            True,
            (225, 255, 252)
        )

        self.screen.blit(
            name,
            (190, 270)
        )

        score_label = self.label_font.render(
            "HIGHEST SCORE",
            True,
            (30, 220, 220)
        )

        self.screen.blit(
            score_label,
            (430, 240)
        )

        score = self.text_font.render(
            str(self.highest_score),
            True,
            (225, 255, 252)
        )

        self.screen.blit(
            score,
            (430, 270)
        )

        self.draw_button(
            self.edit_btn,
            "EDIT PROFILE"
        )

        self.draw_button(
            self.delete_btn,
            "DELETE ACCOUNT"
        )

    def draw_edit(self):
        self.draw_input(
            self.username_box,
            "USERNAME",
            self.username,
            self.active == "username"
        )

        self.draw_input(
            self.email_box,
            "EMAIL",
            self.email,
            self.active == "email"
        )

        self.draw_button(
            self.save_btn,
            "SAVE"
        )

        self.draw_button(
            self.cancel_btn,
            "CANCEL"
        )

        self.draw_button(
            self.delete_btn,
            "DELETE ACCOUNT"
        )

        if self.message:
            message = self.small_font.render(
                self.message,
                True,
                (255, 100, 120)
            )

            self.screen.blit(
                message,
                (
                    self.w // 2 - message.get_width() // 2,
                    505
                )
            )

    def draw_delete_confirmation(self):
        overlay = pygame.Surface(
            (self.w, self.h),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(
            125,
            175,
            550,
            330
        )

        pygame.draw.rect(
            self.screen,
            (3, 22, 30),
            panel,
            border_radius=14
        )

        pygame.draw.rect(
            self.screen,
            (220, 70, 90),
            panel,
            2,
            border_radius=14
        )

        warning = self.title_font.render(
            "DELETE ACCOUNT?",
            True,
            (255, 100, 120)
        )

        self.screen.blit(
            warning,
            (
                self.w // 2 - warning.get_width() // 2,
                205
            )
        )

        question = self.text_font.render(
            "Are you sure you want to delete",
            True,
            (225, 245, 245)
        )

        self.screen.blit(
            question,
            (
                self.w // 2 - question.get_width() // 2,
                275
            )
        )

        player_text = self.text_font.render(
            f'"{self.username}"?',
            True,
            (80, 255, 245)
        )

        self.screen.blit(
            player_text,
            (
                self.w // 2 - player_text.get_width() // 2,
                310
            )
        )

        warning_text = self.small_font.render(
            "This action cannot be undone.",
            True,
            (255, 120, 130)
        )

        self.screen.blit(
            warning_text,
            (
                self.w // 2 - warning_text.get_width() // 2,
                350
            )
        )

        self.draw_button(
            self.confirm_delete_btn,
            "CONFIRM DELETE"
        )

        self.draw_button(
            self.cancel_delete_btn,
            "CANCEL"
        )

    def handle_events(self, events):
        if self.action == "delete_success":
            if pygame.time.get_ticks() - self.delete_success_time >= 2000:
                self.action = "deleted"

            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if self.editing:
                    self.keyboard_input(event)

    def mouse_click(self, pos):
        if self.action == "confirm_delete":

            if self.confirm_delete_btn.collidepoint(pos):
                self.confirm_delete()

            elif self.cancel_delete_btn.collidepoint(pos):
                self.action = None
                self.message = ""

            return

        if self.back_btn.collidepoint(pos):
            self.action = "back"
            return

        if not self.editing:

            if self.edit_btn.collidepoint(pos):
                self.editing = True
                self.username = self.get_username()
                self.email = self.get_email()
                self.active = "username"
                self.message = ""

            elif self.delete_btn.collidepoint(pos):
                self.ask_delete_confirmation()

        else:

            if self.username_box.collidepoint(pos):
                self.active = "username"

            elif self.email_box.collidepoint(pos):
                self.active = "email"

            elif self.save_btn.collidepoint(pos):
                self.save_profile()

            elif self.cancel_btn.collidepoint(pos):
                self.editing = False
                self.message = ""

            elif self.delete_btn.collidepoint(pos):
                self.ask_delete_confirmation()

    def keyboard_input(self, event):
        if event.key == pygame.K_TAB:

            if self.active == "username":
                self.active = "email"
            else:
                self.active = "username"

        elif event.key == pygame.K_BACKSPACE:

            if self.active == "username":
                self.username = self.username[:-1]

            elif self.active == "email":
                self.email = self.email[:-1]

        elif event.key == pygame.K_RETURN:
            self.save_profile()

        elif event.unicode.isprintable():

            if self.active == "username":

                if len(self.username) < 50:
                    self.username += event.unicode

            elif self.active == "email":

                if len(self.email) < 100:
                    self.email += event.unicode

    def save_profile(self):
        username = self.username.strip()
        email = self.email.strip()

        if not username or not email:
            self.message = "PLEASE ENTER ALL FIELDS"
            return

        if len(username) < 3:
            self.message = "USERNAME MUST BE AT LEAST 3 CHARACTERS"
            return

        if "@" not in email or "." not in email:
            self.message = "PLEASE ENTER A VALID EMAIL"
            return

        success = update_player_profile(
            self.player_id,
            username,
            email
        )

        if success:

            self.username = username
            self.email = email

            if isinstance(self.player, dict):
                self.player["username"] = username
                self.player["email"] = email

            self.editing = False
            self.message = ""

        else:
            self.message = "USERNAME OR EMAIL ALREADY EXISTS"

    def ask_delete_confirmation(self):
        self.action = "confirm_delete"
        self.message = ""

    def confirm_delete(self):
        if not self.player_id:
            self.message = "INVALID PLAYER ACCOUNT"
            return

        player_name = self.username.strip()

        if not player_name:
            self.message = "INVALID PLAYER NAME"
            return

        success = delete_player(self.player_id)

        if success:

            self.message = f"{player_name} SUCCESSFULLY DELETED"

            self.delete_success_time = pygame.time.get_ticks()

            self.action = "delete_success"

        else:
            self.message = "DELETE ACCOUNT FAILED"
            self.action = None