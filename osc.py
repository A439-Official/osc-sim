import pygame
import soundfile
import sys
import os
from typing import Tuple, Optional, List

def resource_path(p: str) -> str:
    return os.path.join(sys._MEIPASS, p) if hasattr(sys, '_MEIPASS') else os.path.join(os.path.abspath("."), p)

def load_audio_channels(f: str) -> Tuple[Optional[int], Optional[List[List[float]]]]:
    try:
        y, sr = soundfile.read(f, dtype='float32', always_2d=True)
        return sr, [y[:, 0].tolist(), y[:, 1].tolist()] if y.shape[1] > 1 else [y[:, 0].tolist(), y[:, 0].copy().tolist()]
    except Exception:
        print("Error: Failed to load audio file.")
        return None, None

def main(audio_path: str) -> None:
    pygame.init()
    bg: pygame.Surface = pygame.image.load(resource_path("bg.png"))
    screen: pygame.Surface = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Oscilloscope")
    pygame.display.set_icon(pygame.image.load(resource_path("A439-256.png")))
    screen.fill((0, 0, 0))
    mask: pygame.Surface = screen.copy().convert_alpha()
    sr, audio_channels = load_audio_channels(audio_path)
    if audio_channels is None: return
    pygame.mixer_music.load(audio_path)
    basepos: float = 0.5
    pygame.mixer_music.play()
    last_i: int = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
        screen.blit(mask, (0, 0))
        now_time: float = pygame.mixer_music.get_pos() / 1000.0
        if now_time > audio_channels[0].__len__() / sr:  pygame.quit(); return
        i1, i2 = last_i, int(now_time * sr)
        mask.set_alpha(int((abs(i2 - i1) / 100 + 1) ** 0.25 * 16))
        for i in range(i1, i2):
            x, y = audio_channels[0][i], audio_channels[1][i]
            pos: Tuple[int, int] = (
                int(screen.get_width() / 2 + (screen.get_width() + (screen.get_height() - screen.get_width()) * basepos) / 2 * x),
                int(screen.get_height() / 2 - (screen.get_width() + (screen.get_height() - screen.get_width()) * basepos) / 2 * y)
            )
            if pos[0] < 0 or pos[0] >= screen.get_width() or pos[1] < 0 or pos[1] >= screen.get_height(): continue
            pygame.draw.circle(screen, bg.get_at(pos), pos, 2)
        pygame.draw.line(screen, (255, 255, 255), (0, screen.get_height()),
                         (screen.get_width() * i2 / len(audio_channels[0]), screen.get_height()), 10)
        last_i = i2
        pygame.display.update()

if __name__ == "__main__":
    if audio_path := sys.argv[1] if len(sys.argv) > 1 else None:
        main(audio_path)
    else:
        print("Usage: osc <audio_file>")