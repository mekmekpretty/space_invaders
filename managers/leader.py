import pygame
from db import load_leaderboard


class Leader:
    def __init__(self, screen, w, h, player=None):
        self.screen = screen
        self.w = w
        self.h = h
        self.player = player
        self.action = None

        self.title_font = pygame.font.SysFont(
            "Arial",
            42,
            bold=True
        )

        self.header_font = pygame.font.SysFont(
            "Arial",
            18,
            bold=True
        )

        self.text_font = pygame.font.SysFont(
            "Arial",
            17
        )

        self.small_font = pygame.font.SysFont(
            "Arial",
            14
        )

        self.stars = []

        for i in range(90):
            x = (i * 137) % w
            y = (i * 83) % h
            size = 1 if i % 4 else 2
            self.stars.append((x, y, size))

        self.back_btn = pygame.Rect(
            45,
            h - 75,
            125,
            45
        )

        self.rows = []

        self.load_data()

    def load_data(self):
        self.rows = load_leaderboard()

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

        self.draw_moon(
            55,
            145,
            105
        )

        self.draw_moon(
            self.w - 65,
            self.h - 110,
            120
        )

        pygame.draw.line(
            self.screen,
            (20, 220, 220),
            (70, 210),
            (self.w - 70, 210),
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

    def draw_header(self):
        title = self.title_font.render(
            "LEADERBOARD",
            True,
            (180, 255, 248)
        )

        self.screen.blit(
            title,
            (
                self.w // 2 -
                title.get_width() // 2,
                65
            )
        )

        subtitle = self.small_font.render(
            "TOP SPACE INVADERS SCORES",
            True,
            (30, 220, 220)
        )

        self.screen.blit(
            subtitle,
            (
                self.w // 2 -
                subtitle.get_width() // 2,
                120
            )
        )

    def draw_table(self):
        table_x = 55
        table_y = 165
        table_w = 690
        header_h = 45
        row_h = 42

        pygame.draw.rect(
            self.screen,
            (5, 38, 48),
            (
                table_x,
                table_y,
                table_w,
                header_h
            ),
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            (25, 190, 195),
            (
                table_x,
                table_y,
                table_w,
                header_h
            ),
            2,
            border_radius=7
        )

        headers = [
            ("NAME", 80),
            ("SCORE", 315),
            ("RANK", 435),
            ("DATE / TIME", 535)
        ]

        for text, x in headers:
            surface = self.header_font.render(
                text,
                True,
                (100, 255, 248)
            )

            self.screen.blit(
                surface,
                (
                    x,
                    table_y + 13
                )
            )

        if not self.rows:
            text = self.text_font.render(
                "NO SCORES YET",
                True,
                (120, 200, 205)
            )

            self.screen.blit(
                text,
                (
                    self.w // 2 -
                    text.get_width() // 2,
                    235
                )
            )

            return

        for index, row in enumerate(
            self.rows,
            start=1
        ):
            y = (
                table_y +
                header_h +
                7 +
                (index - 1) * row_h
            )

            pygame.draw.rect(
                self.screen,
                (4, 25, 33),
                (
                    table_x,
                    y,
                    table_w,
                    row_h - 3
                ),
                border_radius=5
            )

            pygame.draw.rect(
                self.screen,
                (10, 75, 85),
                (
                    table_x,
                    y,
                    table_w,
                    row_h - 3
                ),
                1,
                border_radius=5
            )

            username = str(
                row.get(
                    "username",
                    "PLAYER"
                )
            )

            score = str(
                row.get(
                    "score",
                    0
                )
            )

            rank = str(index)

            date_value = row.get(
                "date_added",
                None
            )

            if date_value:
                try:
                    date_text = date_value.strftime(
                        "%d/%m/%Y %I:%M %p"
                    )
                except:
                    date_text = str(date_value)
            else:
                date_text = "N/A"

            values = [
                (username, 80),
                (score, 315),
                (rank, 435),
                (date_text, 535)
            ]

            for text, x in values:
                surface = self.text_font.render(
                    text,
                    True,
                    (225, 255, 252)
                )

                self.screen.blit(
                    surface,
                    (
                        x,
                        y + 10
                    )
                )

    def draw_back_button(self):
        mouse = pygame.mouse.get_pos()
        hover = self.back_btn.collidepoint(mouse)

        if hover:
            bg = (8, 70, 82)
            border = (100, 255, 245)
        else:
            bg = (5, 38, 48)
            border = (25, 190, 195)

        pygame.draw.rect(
            self.screen,
            bg,
            self.back_btn,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            border,
            self.back_btn,
            2,
            border_radius=7
        )

        pygame.draw.line(
            self.screen,
            border,
            (
                self.back_btn.x + 38,
                self.back_btn.centery
            ),
            (
                self.back_btn.x + 20,
                self.back_btn.centery
            ),
            2
        )

        pygame.draw.line(
            self.screen,
            border,
            (
                self.back_btn.x + 20,
                self.back_btn.centery
            ),
            (
                self.back_btn.x + 28,
                self.back_btn.centery - 7
            ),
            2
        )

        pygame.draw.line(
            self.screen,
            border,
            (
                self.back_btn.x + 20,
                self.back_btn.centery
            ),
            (
                self.back_btn.x + 28,
                self.back_btn.centery + 7
            ),
            2
        )

        text = self.text_font.render(
            "BACK",
            True,
            (225, 255, 252)
        )

        self.screen.blit(
            text,
            (
                self.back_btn.x + 52,
                self.back_btn.centery -
                text.get_height() // 2
            )
        )

    def draw(self):
        self.draw_background()
        self.draw_header()
        self.draw_table()
        self.draw_back_button()

    def handle_events(self, events):
        self.action = None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.back_btn.collidepoint(
                        event.pos
                    ):
                        self.action = "back"