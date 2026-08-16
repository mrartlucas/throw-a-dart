from __future__ import annotations

GLYPHS = {
    " ": ("000","000","000","000","000"),
    "A": ("010","101","111","101","101"), "B": ("110","101","110","101","110"),
    "C": ("011","100","100","100","011"), "D": ("110","101","101","101","110"),
    "E": ("111","100","110","100","111"), "F": ("111","100","110","100","100"),
    "G": ("011","100","101","101","011"), "H": ("101","101","111","101","101"),
    "I": ("111","010","010","010","111"), "J": ("001","001","001","101","010"),
    "K": ("101","101","110","101","101"), "L": ("100","100","100","100","111"),
    "M": ("101","111","111","101","101"), "N": ("101","111","111","111","101"),
    "O": ("010","101","101","101","010"), "P": ("110","101","110","100","100"),
    "Q": ("010","101","101","111","011"), "R": ("110","101","110","101","101"),
    "S": ("011","100","010","001","110"), "T": ("111","010","010","010","010"),
    "U": ("101","101","101","101","111"), "V": ("101","101","101","101","010"),
    "W": ("101","101","111","111","101"), "X": ("101","101","010","101","101"),
    "Y": ("101","101","010","010","010"), "Z": ("111","001","010","100","111"),
    "0": ("111","101","101","101","111"), "1": ("010","110","010","010","111"),
    "2": ("110","001","010","100","111"), "3": ("110","001","010","001","110"),
    "4": ("101","101","111","001","001"), "5": ("111","100","110","001","110"),
    "6": ("011","100","111","101","111"), "7": ("111","001","010","010","010"),
    "8": ("111","101","111","101","111"), "9": ("111","101","111","001","110"),
    "+": ("000","010","111","010","000"), "-": ("000","000","111","000","000"),
    "!": ("010","010","010","000","010"), ":": ("000","010","000","010","000"),
    "/": ("001","001","010","100","100"),
}

def measure(text: str, sx: int = 1, advance: int | None = None) -> int:
    if not text:
        return 0
    step = advance if advance is not None else 4 * sx
    return (len(text) - 1) * step + 3 * sx

def draw_text(surface, text: str, x: int, y: int, color, sx: int = 1, sy: int = 1, advance: int | None = None) -> None:
    import pygame
    step = advance if advance is not None else 4 * sx
    cx = x
    for char in text.upper():
        glyph = GLYPHS.get(char, GLYPHS[" "])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    pygame.draw.rect(surface, color, (cx + col * sx, y + row * sy, sx, sy))
        cx += step

def draw_centered(surface, text: str, center_x: int, y: int, color, sx: int = 1, sy: int = 1, advance: int | None = None) -> None:
    draw_text(surface, text, center_x - measure(text, sx=sx, advance=advance) // 2, y, color, sx=sx, sy=sy, advance=advance)

def draw_right(surface, text: str, right_x: int, y: int, color, sx: int = 1, sy: int = 1, advance: int | None = None) -> None:
    draw_text(surface, text, right_x - measure(text, sx=sx, advance=advance) + 1, y, color, sx=sx, sy=sy, advance=advance)

def draw_chevron(surface, x: int, y: int, color, right: bool) -> None:
    import pygame
    points = ((x,y),(x+2,y+2),(x,y+4)) if right else ((x+2,y),(x,y+2),(x+2,y+4))
    for px, py in points:
        pygame.draw.rect(surface, color, (px, py, 1, 1))

def draw_down_marker(surface, center_x: int, y: int, color) -> None:
    import pygame
    pygame.draw.rect(surface, color, (center_x - 1, y, 3, 1))
    pygame.draw.rect(surface, color, (center_x, y + 1, 1, 1))
