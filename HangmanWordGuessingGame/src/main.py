
from pathlib import Path
import random
import sys
import pygame

pygame.init()

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "images"
CHAR = ROOT / "assets" / "character"

WIDTH, HEIGHT = 1280, 720
LIVES = 6
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hangman: Guess the Word")
clock = pygame.time.Clock()

WHITE = (250, 245, 255)
PURPLE = (195, 85, 255)
DARK = (22, 8, 39)
GREEN = (65, 230, 145)
RED = (255, 85, 110)
FONT_NAME = pygame.font.match_font("dejavusans")


def get_fonts():
    scale = min(
        screen.get_width() / WIDTH,
        screen.get_height() / HEIGHT,
    )
    scale = max(0.55, min(scale, 1.6))

    return (
        pygame.font.Font(FONT_NAME, max(15, int(25 * scale))),
        pygame.font.Font(FONT_NAME, max(12, int(18 * scale))),
        pygame.font.Font(FONT_NAME, max(20, int(38 * scale))),
        pygame.font.Font(FONT_NAME, max(24, int(44 * scale))),
    )


FONT, SMALL, WORD_FONT, TITLE_FONT = get_fonts()


def load(path):
    try:
        return pygame.image.load(str(path)).convert_alpha()
    except (pygame.error, FileNotFoundError):
        print(f"[Missing or unreadable asset] {path}")
        return None


def image(*paths):
    for path in paths:
        if path.is_file():
            loaded = load(path)
            if loaded is not None:
                return loaded
    return None


# UI assets
forest = image(IMG / "background_forest.png")
title_image = image(IMG / "title.png")
play_image = image(IMG / "btn_play.png")
new_image = image(IMG / "btn_new.png")
quit_image = image(IMG / "btn_quit.png")
heart_full = image(IMG / "heart_full.png")
heart_empty = image(IMG / "heart_empty.png")
panel_image = image(IMG / "panel_main.png")
slot_image = image(IMG / "panel_slot.png")

# Character scene files currently in assets/character/
scene_files = [
    "character_scene_01_scared.png",
    "character_scene_02_grabbing_rope.png",
    "character_scene_03_running.png",
    "character_scene_04_struggling.png",
    "character_scene_05_frightened.png",
    "character_scene_06_struggling.png",
    "character_scene_07_defeated.png",
]

scenes = [load(CHAR / name) for name in scene_files]

# Optional escape/win artwork.
win_scene = image(CHAR / "character_scene_08_win.png")


def cover(image_to_draw, target):
    """Fill the target surface, cropping excess while preserving proportions."""
    sw, sh = target.get_size()

    if image_to_draw is None:
        target.fill(DARK)
        return

    iw, ih = image_to_draw.get_size()
    scale = max(sw / iw, sh / ih)

    size = (
        max(1, round(iw * scale)),
        max(1, round(ih * scale)),
    )

    scaled = pygame.transform.smoothscale(image_to_draw, size)

    target.blit(
        scaled,
        (
            (sw - scaled.get_width()) // 2,
            (sh - scaled.get_height()) // 2,
        ),
    )


def blit_fit(image_to_draw, rect):
    """Fit the complete image inside a rectangle without distortion."""
    if image_to_draw is None or rect.width <= 0 or rect.height <= 0:
        return

    iw, ih = image_to_draw.get_size()
    scale = min(rect.width / iw, rect.height / ih)

    size = (
        max(1, round(iw * scale)),
        max(1, round(ih * scale)),
    )

    scaled = pygame.transform.smoothscale(image_to_draw, size)
    screen.blit(scaled, scaled.get_rect(center=rect.center))


def draw_button(image_to_draw, label, rect):
    if image_to_draw is not None:
        blit_fit(image_to_draw, rect)
    else:
        pygame.draw.rect(
            screen, (54, 18, 85), rect, border_radius=12
        )
        pygame.draw.rect(
            screen, PURPLE, rect, 2, border_radius=12
        )

        text = FONT.render(label, True, WHITE)
        screen.blit(text, text.get_rect(center=rect.center))


def draw_panel(rect):
    # The panel texture must fill the panel's entire layout rectangle.
    if panel_image is not None:
        scaled = pygame.transform.smoothscale(
            panel_image, rect.size
        )
        screen.blit(scaled, rect)
    else:
        pygame.draw.rect(
            screen, (26, 9, 46), rect, border_radius=24
        )
        pygame.draw.rect(
            screen, PURPLE, rect, 2, border_radius=24
        )


def draw_title():
    cover(forest, screen)
    sw, sh = screen.get_size()

    if title_image is not None:
        iw, ih = title_image.get_size()

        scale = min(
            (sw * 0.88) / iw,
            (sh * 0.66) / ih,
        )

        size = (
            max(1, round(iw * scale)),
            max(1, round(ih * scale)),
        )

        logo = pygame.transform.smoothscale(title_image, size)
        screen.blit(
            logo,
            logo.get_rect(center=(sw // 2, int(sh * 0.39))),
        )

    button_w = min(int(sw * 0.36), 420)
    button_h = min(int(sh * 0.14), 92)

    play_rect = pygame.Rect(
        0, 0, max(150, button_w), max(48, button_h)
    )
    play_rect.center = (sw // 2, int(sh * 0.84))

    draw_button(play_image, "PLAY GAME", play_rect)

    return {"play": play_rect}


def load_words():
    path = ROOT / "words.txt"

    if path.exists():
        words = [
            line.strip().upper()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip().isalpha()
        ]

        if words:
            return words

    return [
        "PYTHON", "SECURITY", "COMPUTER", "ALGORITHM",
        "DEVELOPER", "TERMINAL", "FUNCTION", "VARIABLE",
        "DATABASE", "NETWORK", "FIREWALL", "ENCRYPTION",
        "PROGRAMMING", "HARDWARE", "SOFTWARE",
    ]


WORDS = load_words()

word = ""
guessed = set()
wrong = 0
message = ""
won = False
lost = False
scene = "title"


def new_game():
    global word, guessed, wrong, message, won, lost

    word = random.choice(WORDS)
    guessed = set()
    wrong = 0
    message = "Choose a letter"
    won = False
    lost = False

    print(f"New round started ({len(word)} letters)")


def guess(letter):
    global wrong, message, won, lost

    letter = letter.upper()

    if len(letter) != 1 or not letter.isalpha():
        return

    if letter in guessed or won or lost:
        return

    guessed.add(letter)

    if letter in word:
        if all(char in guessed for char in word):
            won = True
            message = "YOU WIN!"
        else:
            message = f"Correct guess: {letter}"
    else:
        wrong = min(LIVES, wrong + 1)

        if wrong >= LIVES:
            lost = True
            message = f"GAME OVER - Word: {word}"
        else:
            message = f"Wrong guess: {letter}"


def draw_game():
    global FONT, SMALL, WORD_FONT, TITLE_FONT

    cover(forest, screen)

    sw, sh = screen.get_size()
    scale = min(sw / WIDTH, sh / HEIGHT)
    scale = max(0.55, min(scale, 1.6))

    FONT, SMALL, WORD_FONT, TITLE_FONT = get_fonts()

    margin = max(10, int(sw * 0.025))
    gap = max(8, int(sw * 0.018))
    top = max(10, int(sh * 0.045))
    bottom = max(10, int(sh * 0.045))

    left_w = int(sw * 0.42)

    left = pygame.Rect(
        margin,
        top,
        left_w,
        sh - top - bottom,
    )

    right_x = left.right + gap

    right = pygame.Rect(
        right_x,
        top,
        max(1, sw - right_x - margin),
        sh - top - bottom,
    )

    draw_panel(right)

    # Display the escape artwork after a win and the defeated
    # artwork when all six lives have been lost.
    if won and win_scene is not None:
        scene_image = win_scene
    elif lost or wrong >= LIVES:
        scene_image = scenes[6] if len(scenes) > 6 else None
    else:
        scene_index = min(wrong, 5)
        scene_image = (
            scenes[scene_index]
            if scene_index < len(scenes)
            else None
        )

    if scene_image is not None:
        blit_fit(scene_image, left)
    else:
        pygame.draw.rect(
            screen, (28, 12, 46), left, border_radius=18
        )
        pygame.draw.rect(
            screen, PURPLE, left, 2, border_radius=18
        )

        missing = SMALL.render(
            "Character scene missing", True, WHITE
        )
        screen.blit(
            missing,
            missing.get_rect(center=left.center),
        )

    pad = max(
        10,
        min(int(right.width * 0.045), int(24 * scale)),
    )

    # Heading
    heading = TITLE_FONT.render("GUESS THE WORD", True, WHITE)
    heading_w = max(1, right.width - pad * 2)

    if heading.get_width() > heading_w:
        heading = pygame.transform.smoothscale(
            heading,
            (heading_w, heading.get_height()),
        )

    screen.blit(
        heading,
        (right.x + pad, right.y + pad),
    )

    # Hearts and lives count
    heart_size = max(
        16,
        min(int(34 * scale), right.width // 16),
    )
    heart_y = right.y + int(76 * scale)

    for i in range(LIVES):
        rect = pygame.Rect(
            right.x + pad + i * (heart_size + 4),
            heart_y,
            heart_size,
            heart_size,
        )

        icon = heart_full if i < LIVES - wrong else heart_empty

        if icon is not None:
            blit_fit(icon, rect)
        else:
            heart_text = SMALL.render(
                "♥" if i < LIVES - wrong else "♡",
                True,
                RED if i >= LIVES - wrong else WHITE,
            )
            screen.blit(
                heart_text,
                heart_text.get_rect(center=rect.center),
            )

    lives = SMALL.render(
        f"{LIVES - wrong}/{LIVES} lives",
        True,
        WHITE,
    )

    screen.blit(
        lives,
        (
            right.right - lives.get_width() - pad,
            heart_y + max(
                0, (heart_size - lives.get_height()) // 2
            ),
        ),
    )

    # Word slots
    slot_y = right.y + int(right.height * 0.27)
    available = max(1, right.width - pad * 2)
    count = max(1, len(word))
    slot_gap = max(2, min(6, int(6 * scale)))

    cell_w = max(
        8,
        min(
            int(43 * scale),
            (available - slot_gap * (count - 1)) // count,
        ),
    )

    total = count * cell_w + (count - 1) * slot_gap
    start_x = right.centerx - total // 2

    slot_h = max(
        28,
        min(int(49 * scale), int(right.height * 0.10)),
    )

    for i, char in enumerate(word):
        rect = pygame.Rect(
            start_x + i * (cell_w + slot_gap),
            slot_y,
            cell_w,
            slot_h,
        )

        if slot_image is not None:
            blit_fit(slot_image, rect)
        else:
            pygame.draw.rect(
                screen, (42, 15, 68), rect, border_radius=6
            )
            pygame.draw.rect(
                screen, PURPLE, rect, 1, border_radius=6
            )

        if char in guessed or lost:
            letter_size = max(
                10,
                min(int(38 * scale), slot_h - 4, cell_w - 2),
            )

            shown = pygame.font.Font(
                FONT_NAME, letter_size
            ).render(
                char,
                True,
                GREEN if char in guessed else WHITE,
            )

            screen.blit(
                shown,
                shown.get_rect(center=rect.center),
            )

    # Status message
    status_y = slot_y + slot_h + max(10, int(14 * scale))
    status_color = GREEN if won else RED if lost else WHITE

    status = SMALL.render(message, True, status_color)

    if status.get_width() > right.width - pad * 2:
        status = pygame.transform.smoothscale(
            status,
            (
                max(1, right.width - pad * 2),
                status.get_height(),
            ),
        )

    screen.blit(
        status,
        status.get_rect(center=(right.centerx, status_y)),
    )

    # On-screen keyboard
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key_gap = max(2, int(5 * scale))
    keyboard_top = status_y + max(25, int(30 * scale))

    controls_y = right.bottom - max(43, int(50 * scale))
    keyboard_space = max(
        45, controls_y - keyboard_top - 5
    )

    key_h = max(
        18,
        min(int(34 * scale), (keyboard_space - 2 * 4) // 3),
    )

    key_w = min(
        int(39 * scale),
        max(
            12,
            (right.width - pad * 2 - 9 * key_gap) // 10,
        ),
    )

    key_rects = {}

    for i, letter in enumerate(alphabet):
        row, col = divmod(i, 10)
        row_count = min(10, len(alphabet) - row * 10)

        row_width = (
            row_count * key_w
            + (row_count - 1) * key_gap
        )

        x = (
            right.centerx
            - row_width // 2
            + col * (key_w + key_gap)
        )

        y = keyboard_top + row * (key_h + key_gap)

        rect = pygame.Rect(x, y, key_w, key_h)
        key_rects[letter] = rect

        if letter in guessed:
            color = GREEN if letter in word else RED
        else:
            color = (48, 18, 73)

        pygame.draw.rect(
            screen, color, rect, border_radius=5
        )
        pygame.draw.rect(
            screen, (200, 110, 255), rect, 1, border_radius=5
        )

        key_font = pygame.font.Font(
            FONT_NAME,
            max(10, min(int(18 * scale), key_h - 2)),
        )

        text = key_font.render(letter, True, WHITE)
        screen.blit(
            text,
            text.get_rect(center=rect.center),
        )

    # New Game and Quit buttons
    button_y = right.bottom - max(40, int(46 * scale))
    button_h = max(
        30,
        min(int(40 * scale), right.height // 10),
    )

    button_gap = max(6, int(10 * scale))
    button_w = max(
        60,
        (right.width - pad * 2 - button_gap) // 2,
    )

    new_rect = pygame.Rect(
        right.x + pad,
        button_y,
        button_w,
        button_h,
    )

    quit_rect = pygame.Rect(
        right.right - pad - button_w,
        button_y,
        button_w,
        button_h,
    )

    draw_button(new_image, "NEW GAME", new_rect)
    draw_button(quit_image, "QUIT", quit_rect)

    return {
        "new": new_rect,
        "quit": quit_rect,
        "keys": key_rects,
    }


def main():
    global scene, screen, FONT, SMALL, WORD_FONT, TITLE_FONT

    new_game()
    running = True
    rects = {}

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (max(640, event.w), max(420, event.h)),
                    pygame.RESIZABLE,
                )

                FONT, SMALL, WORD_FONT, TITLE_FONT = get_fonts()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if scene == "game":
                        scene = "title"
                    else:
                        running = False

                elif scene == "game" and event.unicode.isalpha():
                    guess(event.unicode)

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                pos = event.pos

                if scene == "title":
                    if (
                        rects.get("play")
                        and rects["play"].collidepoint(pos)
                    ):
                        new_game()
                        scene = "game"

                else:
                    if (
                        rects.get("new")
                        and rects["new"].collidepoint(pos)
                    ):
                        new_game()

                    elif (
                        rects.get("quit")
                        and rects["quit"].collidepoint(pos)
                    ):
                        running = False

                    else:
                        for letter, rect in rects.get(
                            "keys", {}
                        ).items():
                            if rect.collidepoint(pos):
                                guess(letter)
                                break

        rects = (
            draw_title()
            if scene == "title"
            else draw_game()
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
