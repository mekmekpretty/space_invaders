import pygame
import random
import json
import os

from entities.player import Player
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet

from db import (
    get_db_connection,
    save_score,
    load_leaderboard,
    update_player_profile,
    delete_player,
    get_player_highest_score
)


class GameManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        self.font_large = pygame.font.SysFont("arial", 52, bold=True)
        self.font_title = pygame.font.SysFont("arial", 34, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 25, bold=True)
        self.font_small = pygame.font.SysFont("arial", 20)
        self.font_tiny = pygame.font.SysFont("arial", 16)

        self.cyan = (0, 255, 255)
        self.white = (240, 245, 255)
        self.gray = (130, 145, 160)
        self.dark = (8, 12, 22)
        self.panel = (15, 23, 38)
        self.red = (255, 70, 90)
        self.green = (60, 255, 170)

        self.game_state = "enter_name"

        self.player_name = ""
        self.current_player_id = None
        self.highest_score = 0

        self.score = 0
        self.spawn_number = 5
        self.score_saved = False

        self.player = None
        self.buttons = None
        self.bullet = None
        self.enemies = []

        self.enemy_timer = 0
        self.blink_timer = 0
        self.history = []

        self.selected_player_id = None
        self.selected_player_name = ""
        self.selected_player_email = ""
        self.edit_mode = False

        self.leaderboard_data = []

        self.settings_file = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),
            "settings.json"
        )

        self.show_controls = True
        self.load_game_settings()

        self.name_box = pygame.Rect(
            self.width // 2 - 180,
            self.height // 2 - 20,
            360,
            50
        )

        self.play_again_rect = pygame.Rect(
            self.width // 2 - 150,
            395,
            300,
            55
        )

        self.back_home_rect = pygame.Rect(
            self.width - 180,
            self.height - 65,
            160,
            45
        )

        self.leaderboard_back_rect = pygame.Rect(
            self.width // 2 - 100,
            self.height - 70,
            200,
            45
        )

        self.edit_rect = pygame.Rect(
            self.width // 2 - 160,
            self.height - 130,
            145,
            45
        )

        self.delete_rect = pygame.Rect(
            self.width // 2 + 15,
            self.height - 130,
            145,
            45
        )

        self.reset_game_vars()

    def load_game_settings(self):
        try:
            with open(
                self.settings_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.show_controls = data.get(
                "show_controls",
                True
            )

        except:
            self.show_controls = True

    def reset_game_vars(self):
        self.player = Player(
            self.width,
            self.height
        )

        self.buttons = MobileButtons()
        self.bullet = None
        self.enemies = []
        self.score = 0
        self.spawn_number = 5
        self.enemy_timer = 0
        self.blink_timer = 0
        self.history = []
        self.score_saved = False

        self.spawn_enemies()

    def set_player(self, player):
        if not player:
            return

        self.current_player_id = player.get("player_id")
        self.player_name = player.get("username", "")

        if self.current_player_id:
            self.highest_score = get_player_highest_score(
                self.current_player_id
            )
        else:
            self.highest_score = 0

        self.game_state = "playing"
        self.start_again()

    def register_player_and_get_id(self, username):
        username = username.strip()

        if not username:
            return False

        conn = get_db_connection()

        if not conn:
            return False

        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT player_id
                FROM players
                WHERE username = %s
                """,
                (username,)
            )

            existing = cursor.fetchone()

            if existing:
                self.current_player_id = existing[0]
                self.player_name = username
                return True

            cursor.execute(
                """
                INSERT INTO players
                (username)
                VALUES (%s)
                """,
                (username,)
            )

            conn.commit()

            self.current_player_id = cursor.lastrowid
            self.player_name = username

            return True

        except Exception as e:
            print(f"Player Error: {e}")
            conn.rollback()
            return False

        finally:
            cursor.close()
            conn.close()

    def update(self, events):

        if self.game_state in ("playing", "blinking"):

            for event in events:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        return "settings"

            self.update_playing(events)

            return None

        if self.game_state == "game_over":

            self.update_game_over(events)

            if self.game_state == "back_home":
                return "home"

            if self.game_state == "leaderboard":
                return "leaderboard"

            return None

        if self.game_state == "leaderboard":

            self.update_leaderboard(events)

            if self.game_state == "back_home":
                return "home"

            return None

        if self.game_state == "enter_name":

            self.update_enter_name(events)

            if self.game_state == "back_home":
                return "home"

            return None

        return None

    def update_enter_name(self, events):

        for event in events:

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_BACKSPACE:

                self.player_name = self.player_name[:-1]

            elif event.key == pygame.K_RETURN:

                if self.player_name.strip():

                    if self.register_player_and_get_id(
                        self.player_name
                    ):
                        self.start_game()

            elif event.key == pygame.K_ESCAPE:

                self.game_state = "back_home"

            else:

                if len(self.player_name) < 18:

                    if event.unicode.isprintable():
                        self.player_name += event.unicode

    def update_playing(self, events):

        if self.player is None:
            self.start_game()
            return

        self.load_game_settings()

        self.history.append(
            (self.player.x, self.player.y)
        )

        if len(self.history) > 60:
            self.history.pop(0)

        if self.game_state == "blinking":

            self.player.update_blink()
            self.blink_timer += 1

            for enemy in self.enemies:
                enemy.update()

            if self.blink_timer >= 180:
                self.game_state = "game_over"

            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        fired = False

        if self.show_controls and self.buttons:

            fired = self.buttons.handle_mouse(
                self.player,
                events
            )

        fired |= any(
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
            for event in events
        )

        if fired and self.bullet is None:

            rect = self.player.get_rect()

            self.bullet = Bullet(
                rect.centerx,
                rect.top
            )

        self.player.keep_inside_screen()

        if self.bullet:

            self.bullet.update()

            if hasattr(self.bullet, "is_active"):

                if not self.bullet.is_active:
                    self.bullet = None

            elif hasattr(self.bullet, "active"):

                if not self.bullet.active:
                    self.bullet = None

        self.enemy_timer += 1

        if self.enemy_timer >= 180:

            waiting = [
                enemy
                for enemy in self.enemies
                if enemy.state == "waiting"
            ]

            if waiting and self.history:

                random.choice(waiting).start_drop(
                    *self.history[0]
                )

            self.enemy_timer = 0

        for enemy in self.enemies:
            enemy.update()

        if self.enemies and all(
            enemy.state == "offscreen"
            for enemy in self.enemies
        ):

            self.spawn_number += 1
            self.spawn_enemies()

        self.check_collisions()

    def update_game_over(self, events):

        if not self.score_saved:

            if self.current_player_id:

                save_score(
                    self.current_player_id,
                    self.score
                )

                self.highest_score = get_player_highest_score(
                    self.current_player_id
                )

            else:

                self.highest_score = max(
                    self.highest_score,
                    self.score
                )

            self.score_saved = True

        for event in events:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if self.play_again_rect.collidepoint(
                    event.pos
                ):

                    self.start_again()
                    return

                if self.back_home_rect.collidepoint(
                    event.pos
                ):

                    self.game_state = "back_home"
                    return

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    self.start_again()
                    return

                if event.key == pygame.K_ESCAPE:

                    self.game_state = "back_home"
                    return

    def update_leaderboard(self, events):

        self.leaderboard_data = load_leaderboard()

        for event in events:

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if self.leaderboard_back_rect.collidepoint(
                    event.pos
                ):

                    self.game_state = "back_home"
                    return

                if self.edit_rect.collidepoint(event.pos):

                    if self.selected_player_id:
                        self.edit_mode = True
                        return

                if self.delete_rect.collidepoint(event.pos):

                    if self.selected_player_id:

                        if delete_player(
                            self.selected_player_id
                        ):

                            self.selected_player_id = None
                            self.selected_player_name = ""
                            self.selected_player_email = ""
                            self.edit_mode = False

            elif event.type == pygame.KEYDOWN:

                if self.edit_mode:

                    if event.key == pygame.K_ESCAPE:

                        self.edit_mode = False

                    elif event.key == pygame.K_BACKSPACE:

                        self.selected_player_name = (
                            self.selected_player_name[:-1]
                        )

                    elif event.key == pygame.K_RETURN:

                        if self.selected_player_id:

                            new_name = (
                                self.selected_player_name.strip()
                            )

                            if new_name:

                                success = update_player_profile(
                                    self.selected_player_id,
                                    new_name,
                                    self.selected_player_email
                                )

                                if success:
                                    self.edit_mode = False

                    else:

                        if len(self.selected_player_name) < 18:

                            if event.unicode.isprintable():
                                self.selected_player_name += (
                                    event.unicode
                                )

                else:

                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "back_home"

        mouse_pos = pygame.mouse.get_pos()

        if pygame.mouse.get_pressed()[0]:
            self.select_leaderboard_player(
                mouse_pos
            )

    def start_game(self):

        self.game_state = "playing"
        self.score = 0
        self.score_saved = False
        self.spawn_number = 5

        self.reset_game_vars()

    def start_again(self):

        self.game_state = "playing"
        self.score = 0
        self.score_saved = False
        self.spawn_number = 5
        self.enemy_timer = 0
        self.blink_timer = 0
        self.history = []

        self.player = Player(
            self.width,
            self.height
        )

        self.buttons = MobileButtons()
        self.bullet = None
        self.enemies = []

        self.spawn_enemies()

    def spawn_enemies(self):

        self.enemies = [
            Enemy(
                i,
                self.spawn_number,
                self.width
            )
            for i in range(self.spawn_number)
        ]

        self.enemy_timer = 0

    def spawn_enemy(self):

        index = len(self.enemies)

        enemy = Enemy(
            index,
            self.spawn_number,
            self.width
        )

        self.enemies.append(enemy)

    def fire_bullet(self):

        if self.game_state != "playing":
            return

        if self.player is None:
            return

        if self.bullet is not None:
            return

        rect = self.player.get_rect()

        self.bullet = Bullet(
            rect.centerx,
            rect.top
        )

    def update_bullets(self):

        if not self.bullet:
            return

        self.bullet.update()

        if hasattr(self.bullet, "is_active"):

            if not self.bullet.is_active:
                self.bullet = None

        elif hasattr(self.bullet, "active"):

            if not self.bullet.active:
                self.bullet = None

    def update_enemies(self):

        self.enemy_timer += 1

        if self.enemy_timer >= 180:

            waiting = [
                enemy
                for enemy in self.enemies
                if enemy.state == "waiting"
            ]

            if waiting and self.history:

                random.choice(waiting).start_drop(
                    *self.history[0]
                )

            self.enemy_timer = 0

        for enemy in self.enemies:
            enemy.update()

    def check_collisions(self):

        if self.game_state != "playing":
            return

        if not self.player:
            return

        player_rect = self.player.get_rect()

        for enemy in self.enemies:

            if enemy.state == "offscreen":
                continue

            enemy_rect = enemy.get_rect()

            if player_rect.colliderect(enemy_rect):

                self.game_state = "blinking"
                self.player.is_blinking = True
                self.blink_timer = 0

                return

            if self.bullet:

                if hasattr(
                    self.bullet,
                    "get_rect"
                ):

                    bullet_rect = (
                        self.bullet.get_rect()
                    )

                else:

                    bullet_rect = self.bullet.rect

                if bullet_rect.colliderect(
                    enemy_rect
                ):

                    enemy.state = "offscreen"

                    if hasattr(
                        self.bullet,
                        "active"
                    ):

                        self.bullet.active = False

                    self.bullet = None
                    self.score += 1

                    break

    def select_leaderboard_player(
        self,
        mouse_pos
    ):

        start_y = 175
        row_height = 42

        for index, row in enumerate(
            self.leaderboard_data
        ):

            row_rect = pygame.Rect(
                150,
                start_y + index * row_height,
                self.width - 300,
                row_height
            )

            if row_rect.collidepoint(
                mouse_pos
            ):

                self.selected_player_id = (
                    row.get("player_id")
                )

                self.selected_player_name = (
                    row.get("username", "")
                )

                self.selected_player_email = (
                    row.get("email", "")
                )

                self.edit_mode = False

                break

    def draw(self):

        self.draw_background()

        if self.game_state == "enter_name":

            self.draw_enter_name()

        elif self.game_state == "playing":

            self.draw_playing()

        elif self.game_state == "blinking":

            self.draw_playing()

        elif self.game_state == "game_over":

            self.draw_game_over()

        elif self.game_state == "leaderboard":

            self.draw_leaderboard()

    def draw_background(self):

        self.screen.fill(self.dark)

        for i in range(70):

            x = (i * 83) % self.width
            y = (i * 47) % self.height

            pygame.draw.circle(
                self.screen,
                (50, 75, 95),
                (x, y),
                1
            )

        pygame.draw.line(
            self.screen,
            self.cyan,
            (30, 80),
            (self.width - 30, 80),
            1
        )

        title = self.font_medium.render(
            "SPACE INVADERS",
            True,
            self.cyan
        )

        title_rect = title.get_rect(
            center=(self.width // 2, 35)
        )

        self.screen.blit(
            title,
            title_rect
        )

        player_text = self.font_small.render(
            self.player_name.upper(),
            True,
            self.white
        )

        score_text = self.font_small.render(
            f"SCORE: {self.score}",
            True,
            self.cyan
        )

        score_rect = score_text.get_rect(
            top=25,
            right=self.width - 30
        )

        player_rect = player_text.get_rect(
            top=25,
            right=score_rect.left - 20
        )

        self.screen.blit(
            player_text,
            player_rect
        )

        self.screen.blit(
            score_text,
            score_rect
        )

    def draw_enter_name(self):

        title = self.font_large.render(
            "SPACE INVADERS",
            True,
            self.cyan
        )

        rect = title.get_rect(
            center=(self.width // 2, 210)
        )

        self.screen.blit(
            title,
            rect
        )

        label = self.font_medium.render(
            "ENTER PLAYER NAME",
            True,
            self.white
        )

        label_rect = label.get_rect(
            center=(self.width // 2, 290)
        )

        self.screen.blit(
            label,
            label_rect
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            self.name_box,
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            self.cyan,
            self.name_box,
            2,
            border_radius=8
        )

        text = self.font_medium.render(
            self.player_name + "|",
            True,
            self.white
        )

        self.screen.blit(
            text,
            (
                self.name_box.x + 15,
                self.name_box.y + 10
            )
        )

        hint = self.font_small.render(
            "PRESS ENTER TO START",
            True,
            self.gray
        )

        hint_rect = hint.get_rect(
            center=(self.width // 2, 370)
        )

        self.screen.blit(
            hint,
            hint_rect
        )

    def draw_playing(self):

        self.draw_background()

        self.load_game_settings()

        if self.player:
            self.player.draw(self.screen)

        for enemy in self.enemies:

            if enemy.active:
                enemy.draw(self.screen)

        if self.bullet:

            if hasattr(
                self.bullet,
                "active"
            ):

                if self.bullet.active:
                    self.bullet.draw(
                        self.screen
                    )

            else:

                self.bullet.draw(
                    self.screen
                )

        if self.buttons and self.show_controls:

            self.buttons.draw(
                self.screen
            )

    def draw_game_over(self):

        self.draw_background()

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 170)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        title = self.font_large.render(
            "GAME OVER",
            True,
            self.red
        )

        title_rect = title.get_rect(
            center=(self.width // 2, 190)
        )

        self.screen.blit(
            title,
            title_rect
        )

        player_text = self.font_medium.render(
            f"PLAYER: {self.player_name}",
            True,
            self.white
        )

        player_rect = player_text.get_rect(
            center=(self.width // 2, 260)
        )

        self.screen.blit(
            player_text,
            player_rect
        )

        score_text = self.font_medium.render(
            f"SCORE: {self.score}",
            True,
            self.cyan
        )

        score_rect = score_text.get_rect(
            center=(self.width // 2, 305)
        )

        self.screen.blit(
            score_text,
            score_rect
        )

        self.draw_button(
            self.play_again_rect,
            "PLAY AGAIN",
            self.cyan
        )

        self.draw_small_button(
            self.back_home_rect,
            "BACK TO HOME",
            self.white
        )

    def draw_button(
        self,
        rect,
        text,
        border_color
    ):

        pygame.draw.rect(
            self.screen,
            self.panel,
            rect,
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            border_color,
            rect,
            2,
            border_radius=8
        )

        surface = self.font_medium.render(
            text,
            True,
            border_color
        )

        surface_rect = surface.get_rect(
            center=rect.center
        )

        self.screen.blit(
            surface,
            surface_rect
        )

    def draw_small_button(
        self,
        rect,
        text,
        border_color
    ):

        pygame.draw.rect(
            self.screen,
            self.panel,
            rect,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            border_color,
            rect,
            2,
            border_radius=7
        )

        surface = self.font_tiny.render(
            text,
            True,
            border_color
        )

        surface_rect = surface.get_rect(
            center=rect.center
        )

        self.screen.blit(
            surface,
            surface_rect
        )

    def draw_leaderboard(self):

        self.draw_background()

        title = self.font_large.render(
            "LEADERBOARD",
            True,
            self.cyan
        )

        title_rect = title.get_rect(
            center=(self.width // 2, 105)
        )

        self.screen.blit(
            title,
            title_rect
        )

        header_y = 145

        headers = [
            ("RANK", 180),
            ("PLAYER", 360),
            ("SCORE", 680)
        ]

        for text, x in headers:

            surface = self.font_small.render(
                text,
                True,
                self.gray
            )

            self.screen.blit(
                surface,
                (x, header_y)
            )

        start_y = 175
        row_height = 42

        for index, row in enumerate(
            self.leaderboard_data
        ):

            y = start_y + index * row_height

            row_rect = pygame.Rect(
                150,
                y,
                self.width - 300,
                row_height - 3
            )

            selected = (
                row.get("player_id")
                == self.selected_player_id
            )

            pygame.draw.rect(
                self.screen,
                self.panel
                if not selected
                else (20, 45, 60),
                row_rect,
                border_radius=5
            )

            rank = self.font_small.render(
                str(index + 1),
                True,
                self.white
            )

            name = self.font_small.render(
                str(row.get("username", "")),
                True,
                self.white
            )

            score = self.font_small.render(
                str(row.get("score", 0)),
                True,
                self.cyan
            )

            self.screen.blit(
                rank,
                (180, y + 8)
            )

            self.screen.blit(
                name,
                (360, y + 8)
            )

            self.screen.blit(
                score,
                (680, y + 8)
            )

        if self.selected_player_id:

            self.draw_small_button(
                self.edit_rect,
                "EDIT",
                self.cyan
            )

            self.draw_small_button(
                self.delete_rect,
                "DELETE",
                self.red
            )

        self.draw_small_button(
            self.leaderboard_back_rect,
            "BACK",
            self.white
        )

        if self.edit_mode:
            self.draw_edit_overlay()

    def draw_edit_overlay(self):

        overlay = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 190)
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        box = pygame.Rect(
            self.width // 2 - 250,
            160,
            500,
            260
        )

        pygame.draw.rect(
            self.screen,
            self.panel,
            box,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            self.cyan,
            box,
            2,
            border_radius=10
        )

        title = self.font_medium.render(
            "EDIT PROFILE",
            True,
            self.cyan
        )

        self.screen.blit(
            title,
            (
                box.centerx -
                title.get_width() // 2,
                box.y + 25
            )
        )

        name_box = pygame.Rect(
            box.x + 50,
            box.y + 90,
            400,
            45
        )

        pygame.draw.rect(
            self.screen,
            self.dark,
            name_box,
            border_radius=6
        )

        pygame.draw.rect(
            self.screen,
            self.gray,
            name_box,
            1,
            border_radius=6
        )

        name_text = self.font_small.render(
            self.selected_player_name + "|",
            True,
            self.white
        )

        self.screen.blit(
            name_text,
            (
                name_box.x + 12,
                name_box.y + 12
            )
        )

        email = self.font_tiny.render(
            self.selected_player_email,
            True,
            self.gray
        )

        self.screen.blit(
            email,
            (
                box.x + 50,
                box.y + 155
            )
        )

        save_text = self.font_small.render(
            "PRESS ENTER TO SAVE",
            True,
            self.green
        )

        self.screen.blit(
            save_text,
            (
                box.centerx -
                save_text.get_width() // 2,
                box.y + 200
            )
        )

    def open_leaderboard(self):

        self.game_state = "leaderboard"
        self.leaderboard_data = load_leaderboard()

        self.selected_player_id = None
        self.selected_player_name = ""
        self.selected_player_email = ""
        self.edit_mode = False

    def get_state(self):
        return self.game_state

    def get_score(self):
        return self.score

    def get_highest_score(self):
        return self.highest_score

    def get_player_name(self):
        return self.player_name

    def set_game_state(self, state):
        self.game_state = state

    def reset_game(self):

        self.game_state = "enter_name"

        self.player_name = ""
        self.current_player_id = None
        self.highest_score = 0

        self.score = 0
        self.score_saved = False

        self.player = None
        self.bullet = None
        self.enemies = []

        self.reset_game_vars()