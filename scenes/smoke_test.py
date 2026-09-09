from manim import *


class SmokeTest(Scene):
    def construct(self):
        self.camera.background_color = "#071321"

        title = Text(
            "AI Sankalp Video Setup Ready",
            font_size=42,
            weight=BOLD,
            color="#F5F9FF",
        )
        subtitle = Text(
            "Manim is rendering correctly.",
            font_size=26,
            color="#9EB3C7",
        ).next_to(title, DOWN, buff=0.35)

        self.play(FadeIn(title, shift=UP * 0.2))
        self.play(FadeIn(subtitle, shift=UP * 0.15))
        self.wait(1)
