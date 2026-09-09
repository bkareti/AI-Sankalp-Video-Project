from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService


BG = "#071321"
PANEL = "#10243A"
BLUE = "#1473E6"
CYAN = "#21D4FD"
MINT = "#55E6C1"
GOLD = "#FFC857"
SOFT_WHITE = "#F5F9FF"
MUTED = "#9EB3C7"

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30


class LessonTemplate(VoiceoverScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_speech_service(GTTSService(lang="en"))

        self.add_branding()
        self.intro()
        self.main_explanation()
        self.summary()

    def add_branding(self):
        logo_path = Path(__file__).resolve().parents[1] / "assets" / "ai_sankalp_logo.svg"

        logo = SVGMobject(str(logo_path)).set(width=0.65)
        badge = RoundedRectangle(
            width=0.9,
            height=0.78,
            corner_radius=0.1,
            stroke_color=BLUE,
            stroke_width=1,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(logo)
        logo_group = VGroup(badge, logo).to_corner(UR, buff=0.25)

        footer = Text(
            "AI SANKALP  •  VISUAL LEARNING",
            font_size=14,
            color=MUTED,
        ).to_edge(DOWN, buff=0.13).to_edge(LEFT, buff=0.30)

        self.add_foreground_mobjects(logo_group, footer)

    def intro(self):
        title = Text(
            "Lesson Title",
            font_size=52,
            weight=BOLD,
            color=SOFT_WHITE,
        )
        title.set_color_by_gradient(CYAN, BLUE)

        with self.voiceover(text="Welcome to AI Sankalp. In this lesson, we will learn a new programming concept."):
            self.play(FadeIn(title, shift=UP * 0.2))

        self.wait(0.5)
        self.play(FadeOut(title))

    def main_explanation(self):
        heading = Text(
            "Main Concept",
            font_size=40,
            weight=BOLD,
            color=SOFT_WHITE,
        ).to_edge(UP, buff=0.5)

        code = Text(
            "print('Hello, AI Sankalp')",
            font="Monospace",
            font_size=34,
            color=GOLD,
        )

        panel = RoundedRectangle(
            width=code.width + 0.8,
            height=code.height + 0.6,
            corner_radius=0.12,
            stroke_color=BLUE,
            fill_color=PANEL,
            fill_opacity=0.98,
        ).move_to(code)

        with self.voiceover(text="Replace this section with the visual explanation for your topic."):
            self.play(Write(heading))
            self.play(FadeIn(panel), Write(code))

        self.wait(0.5)
        self.play(FadeOut(heading), FadeOut(panel), FadeOut(code))

    def summary(self):
        end = Text(
            "Thank you for learning with AI Sankalp",
            font_size=38,
            weight=BOLD,
            color=SOFT_WHITE,
        )

        with self.voiceover(text="Thank you for learning with AI Sankalp."):
            self.play(FadeIn(end, scale=0.9))

        self.wait(1)
