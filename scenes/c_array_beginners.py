from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from pathlib import Path

# AI Sankalp visual system
BG = "#071321"
PANEL = "#10243A"
PANEL_2 = "#16324F"
BLUE = "#1473E6"
CYAN = "#21D4FD"
MINT = "#55E6C1"
GOLD = "#FFC857"
SOFT_WHITE = "#F5F9FF"
MUTED = "#9EB3C7"
CORAL = "#FF6B6B"

# Force a true Full-HD master even if the short preview command (-ql) is used.
# This is especially important for the fine lettering and swoosh in the logo.
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 30


class CArrayBeginners(VoiceoverScene):

    def construct(self):

        self.camera.background_color = BG

        # Subtle, persistent background depth. These shapes stay far from the
        # lesson content and make the frame feel designed instead of empty.
        ambience = VGroup(
            Circle(radius=3.2, color=BLUE, stroke_width=2, stroke_opacity=0.08)
                .shift(LEFT * 6 + DOWN * 3),
            Circle(radius=2.4, color=CYAN, stroke_width=2, stroke_opacity=0.07)
                .shift(RIGHT * 6 + UP * 3),
            Line(LEFT * 7, RIGHT * 7, color=BLUE, stroke_width=1, stroke_opacity=0.16)
                .to_edge(DOWN, buff=0.38),
        )
        self.add(ambience)

        # ------------------------------------------------
        # AI SANKALP LOGO (fixed for the entire video)
        # Keep ai_sankalp_logo.svg in the shared assets folder.
        # ------------------------------------------------
        logo_path = Path(__file__).resolve().parents[1] / "assets" / "ai_sankalp_logo.svg"

        if not logo_path.exists():
            raise FileNotFoundError(
                f"AI Sankalp logo not found: {logo_path}. "
                "Keep ai_sankalp_logo.svg beside this Python file."
            )

        # Both the monogram and brand name are vector objects, so the logo
        # stays perfectly sharp at 1080p, 4K, or any future resolution.
        logo_mark = SVGMobject(str(logo_path)).set(width=0.82)
        logo_name = Text(
            "S A N K A L P",
            font_size=10,
            color="#032657",
            weight=BOLD,
        )
        ai_sankalp_logo = VGroup(logo_mark, logo_name)
        ai_sankalp_logo.arrange(DOWN, buff=0.035)
        ai_sankalp_logo.to_corner(UR, buff=0.18)

        logo_badge = RoundedRectangle(
            width=1.25,
            height=1.08,
            corner_radius=0.12,
            stroke_color=BLUE,
            stroke_width=1.0,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(ai_sankalp_logo)

        footer = Text(
            "AI SANKALP  •  VISUAL LEARNING",
            font_size=14,
            color=MUTED,
            weight=MEDIUM,
        ).to_edge(DOWN, buff=0.13).to_edge(LEFT, buff=0.30)

        # A foreground mobject stays above all lesson animations and remains
        # visible until the video ends.
        self.add_foreground_mobjects(logo_badge, ai_sankalp_logo, footer)

        # ------------------------------------------------
        # VOICE
        # ------------------------------------------------
        self.set_speech_service(
            GTTSService(lang="en")
        )

        # =================================================
        # 1. INTRODUCTION
        # =================================================

        title = Text(
            "C Programming for Beginners",
            font_size=46,
            weight=BOLD,
            color=SOFT_WHITE,
        )
        title.set_color_by_gradient(CYAN, BLUE)

        topic = Text(
            "Understanding Arrays",
            font_size=36,
            color=SOFT_WHITE,
            weight=SEMIBOLD,
        ).next_to(title, DOWN, buff=0.4)

        lesson_pill_text = Text("LESSON 01  •  C FOUNDATIONS", font_size=17, color=CYAN)
        lesson_pill = VGroup(
            RoundedRectangle(
                width=3.65, height=0.46, corner_radius=0.22,
                stroke_color=BLUE, fill_color=PANEL, fill_opacity=0.95,
            ),
            lesson_pill_text,
        )
        lesson_pill[1].move_to(lesson_pill[0])
        lesson_pill.next_to(title, UP, buff=0.48)

        title_line = Line(LEFT * 1.15, RIGHT * 1.15, color=CYAN, stroke_width=5)
        title_line.next_to(topic, DOWN, buff=0.28)

        intro_group = VGroup(lesson_pill, title, topic, title_line)

        with self.voiceover(
            text=(
                "Welcome to AI Sankalp. "
                "In this lesson, we are going to understand arrays "
                "in the C programming language, step by step."
            )
        ):
            self.play(
                FadeIn(lesson_pill, shift=DOWN * 0.15),
                FadeIn(title, shift=UP * 0.18),
                run_time=0.9,
            )
            self.play(
                FadeIn(topic, shift=UP * 0.15),
                GrowFromCenter(title_line),
                run_time=0.7,
            )

        self.wait(1)

        self.play(
            FadeOut(intro_group, shift=UP * 0.15)
        )

        # =================================================
        # 2. WHY DO WE NEED AN ARRAY?
        # =================================================

        heading = Text(
            "Why do we need an Array?",
            font_size=38,
            color=SOFT_WHITE,
            weight=BOLD,
        ).to_edge(UP, buff=0.38).shift(LEFT * 0.45)
        heading_accent = Line(LEFT, RIGHT, color=CYAN, stroke_width=4)
        heading_accent.set_width(2.0).next_to(heading, DOWN, buff=0.15)

        with self.voiceover(
            text=(
                "First, let us understand why arrays are useful. "
                "Suppose we want to store marks of five students."
            )
        ):
            self.play(FadeIn(heading, shift=DOWN * 0.18), GrowFromCenter(heading_accent))

        variables = VGroup(*[
            VGroup(
                RoundedRectangle(
                    width=3.55, height=0.58, corner_radius=0.10,
                    stroke_color=BLUE, stroke_opacity=0.55,
                    fill_color=PANEL, fill_opacity=0.95,
                ),
                Dot(radius=0.055, color=CYAN),
                Text(code, font="Monospace", font_size=25, color=SOFT_WHITE),
            )
            for code in [
                "int mark1 = 70;", "int mark2 = 85;", "int mark3 = 90;",
                "int mark4 = 75;", "int mark5 = 88;",
            ]
        ])

        for row in variables:
            row[1].move_to(row[0].get_left() + RIGHT * 0.23)
            row[2].move_to(row[0]).shift(RIGHT * 0.12)

        variables.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.12
        )

        with self.voiceover(
            text=(
                "Without an array, we may create five separate variables. "
                "Mark one, mark two, mark three, mark four, and mark five."
            )
        ):
            self.play(
                LaggedStart(
                    *[Write(x) for x in variables],
                    lag_ratio=0.2
                )
            )

        problem = Text(
            "What if we have 100 students?",
            font_size=31,
            color=GOLD,
            weight=BOLD,
        ).next_to(variables, DOWN, buff=0.6)

        with self.voiceover(
            text=(
                "But imagine having one hundred students. "
                "Creating one hundred separate variables would be difficult "
                "to manage."
            )
        ):
            self.play(FadeIn(problem, scale=0.9), Indicate(variables, color=CORAL))

        self.wait(1)

        self.play(
            FadeOut(variables),
            FadeOut(problem),
            FadeOut(heading),
            FadeOut(heading_accent)
        )

        # =================================================
        # 3. ARRAY IDEA
        # =================================================

        heading = Text(
            "Array = Many values under ONE name",
            font_size=36,
            color=SOFT_WHITE,
            weight=BOLD,
        ).to_edge(UP, buff=0.38).shift(LEFT * 0.45)

        with self.voiceover(
            text=(
                "An array solves this problem. "
                "An array allows us to store many values "
                "using a single variable name."
            )
        ):
            self.play(Write(heading))

        values = [70, 85, 90, 75, 88]

        boxes = VGroup()

        for value in values:

            box = Square(
                side_length=1.15,
                stroke_color=BLUE,
                stroke_width=2.5,
                fill_color=PANEL_2,
                fill_opacity=1,
            )

            value_text = Text(
                str(value),
                font_size=30,
                color=SOFT_WHITE,
                weight=BOLD,
            )

            value_text.move_to(box)

            cell = VGroup(
                box,
                value_text
            )

            boxes.add(cell)

        boxes.arrange(
            RIGHT,
            buff=0.08
        )

        boxes.move_to(ORIGIN)

        array_name = Text(
            "marks",
            font_size=32,
            color=CYAN,
            weight=BOLD,
        ).next_to(
            boxes,
            LEFT,
            buff=0.5
        )

        with self.voiceover(
            text=(
                "Here we have one array called marks. "
                "Inside this array, we can store five integer values."
            )
        ):
            self.play(FadeIn(array_name, shift=RIGHT * 0.2))
            self.play(
                LaggedStart(
                    *[FadeIn(cell, shift=UP * 0.22) for cell in boxes],
                    lag_ratio=0.15
                )
            )

        definition = Text(
            "An array stores multiple values of the same data type.",
            font_size=27,
            color=SOFT_WHITE,
        ).next_to(
            boxes,
            DOWN,
            buff=1
        )
        definition_panel = RoundedRectangle(
            width=definition.width + 0.65,
            height=definition.height + 0.42,
            corner_radius=0.14,
            stroke_color=MINT,
            fill_color=PANEL,
            fill_opacity=0.95,
        ).move_to(definition)

        with self.voiceover(
            text=(
                "A simple definition is this. "
                "An array stores multiple values of the same data type."
            )
        ):
            self.play(FadeIn(definition_panel, scale=0.96), Write(definition))

        self.wait(1)

        self.play(FadeOut(definition), FadeOut(definition_panel))

        # =================================================
        # 4. ARRAY DECLARATION
        # =================================================

        declaration = Text(
            "int marks[5] = {70, 85, 90, 75, 88};",
            font="Monospace",
            font_size=29,
            color=SOFT_WHITE,
        ).to_edge(DOWN, buff=1)
        declaration.set_color_by_t2c({"int": CYAN, "marks": GOLD, "[5]": MINT})
        declaration_panel = RoundedRectangle(
            width=declaration.width + 0.65,
            height=declaration.height + 0.48,
            corner_radius=0.12,
            stroke_color=BLUE,
            fill_color=PANEL,
            fill_opacity=0.98,
        ).move_to(declaration)

        with self.voiceover(
            text=(
                "This is how we create the array in C. "
                "Int tells C that the array stores integers. "
                "Marks is the name of the array. "
                "Five tells us that the array has space for five values."
            )
        ):
            self.play(FadeIn(declaration_panel, shift=UP * 0.15), Write(declaration))

        # Highlight pieces conceptually

        type_label = Text(
            "data type",
            font_size=21,
            color=MINT,
            weight=BOLD,
        ).next_to(declaration, UP, buff=0.4)

        with self.voiceover(
            text=(
                "All five values in this example are integers."
            )
        ):
            self.play(FadeIn(type_label))

        self.play(FadeOut(type_label))

        # =================================================
        # 5. INDEX
        # =================================================

        index_heading = Text(
            "Array Index",
            font_size=36,
            color=SOFT_WHITE,
            weight=BOLD,
        ).to_edge(UP, buff=0.38).shift(LEFT * 0.45)

        self.play(
            FadeOut(heading),
            ReplacementTransform(
                heading.copy(),
                index_heading
            )
        )

        indexes = VGroup()

        for i, cell in enumerate(boxes):

            index = Text(
                str(i),
                font_size=24,
                color=GOLD,
                weight=BOLD,
            )

            index.next_to(
                cell,
                DOWN,
                buff=0.25
            )

            indexes.add(index)

        index_word = Text(
            "Index:",
            font_size=24,
            color=MUTED,
        ).next_to(
            indexes,
            LEFT,
            buff=0.3
        )

        with self.voiceover(
            text=(
                "Every position in an array has an index number. "
                "This is extremely important. "
                "In C programming, array indexing starts from zero."
            )
        ):
            self.play(FadeIn(index_word))
            self.play(
                LaggedStart(
                    *[Write(x) for x in indexes],
                    lag_ratio=0.2
                )
            )

        zero_highlight = SurroundingRectangle(
            boxes[0],
            buff=0.08,
            color=GOLD,
            stroke_width=4,
            corner_radius=0.10,
        )

        with self.voiceover(
            text=(
                "So the first value, seventy, is at index zero."
            )
        ):
            self.play(Create(zero_highlight))

        self.play(FadeOut(zero_highlight))

        last_highlight = SurroundingRectangle(
            boxes[4],
            buff=0.08,
            color=GOLD,
            stroke_width=4,
            corner_radius=0.10,
        )

        with self.voiceover(
            text=(
                "The fifth value, eighty eight, is at index four. "
                "For five elements, the index numbers are zero through four."
            )
        ):
            self.play(Create(last_highlight))

        self.play(FadeOut(last_highlight))

        # =================================================
        # 6. ACCESSING AN ELEMENT
        # =================================================

        self.play(FadeOut(declaration), FadeOut(declaration_panel))

        access_title = Text(
            "Accessing an Array Element",
            font_size=35,
            color=SOFT_WHITE,
            weight=BOLD,
        ).to_edge(UP, buff=0.38).shift(LEFT * 0.45)

        self.play(
            ReplacementTransform(
                index_heading,
                access_title
            )
        )

        access_code = Text(
            "marks[2]",
            font="Monospace",
            font_size=40,
            color=GOLD,
            weight=BOLD,
        ).to_edge(DOWN, buff=1)

        highlight = SurroundingRectangle(
            boxes[2],
            buff=0.08,
            color=CYAN,
            stroke_width=4,
            corner_radius=0.10,
        )

        with self.voiceover(
            text=(
                "To access a value, we write the array name "
                "followed by its index inside square brackets. "
                "For example, marks at index two."
            )
        ):
            self.play(Write(access_code))
            self.play(Create(highlight))

        answer = Text(
            "marks[2] = 90",
            font="Monospace",
            font_size=32,
            color=MINT,
            weight=BOLD,
        ).next_to(
            access_code,
            UP,
            buff=0.5
        )

        with self.voiceover(
            text=(
                "Index two contains the value ninety. "
                "Therefore, marks at index two gives us ninety."
            )
        ):
            self.play(FadeIn(answer, shift=UP * 0.18), Indicate(boxes[2], color=MINT))

        self.wait(1)

        self.play(
            FadeOut(highlight),
            FadeOut(access_code),
            FadeOut(answer)
        )

        # =================================================
        # 7. CHANGING AN ARRAY ELEMENT
        # =================================================

        change_title = Text(
            "Changing an Array Element",
            font_size=35,
            color=SOFT_WHITE,
            weight=BOLD,
        ).to_edge(UP, buff=0.38).shift(LEFT * 0.45)

        self.play(
            ReplacementTransform(
                access_title,
                change_title
            )
        )

        change_code = Text(
            "marks[2] = 95;",
            font="Monospace",
            font_size=37,
            color=GOLD,
            weight=BOLD,
        ).to_edge(DOWN, buff=1)

        highlight = SurroundingRectangle(
            boxes[2],
            buff=0.08,
            color=CORAL,
            stroke_width=4,
            corner_radius=0.10,
        )

        with self.voiceover(
            text=(
                "We can also change a value inside an array. "
                "Suppose we write marks at index two equals ninety five."
            )
        ):
            self.play(Write(change_code))
            self.play(Create(highlight))

        old_value = boxes[2][1]

        new_value = Text(
            "95",
            font_size=30,
            color=MINT,
            weight=BOLD,
        ).move_to(old_value)

        with self.voiceover(
            text=(
                "The value at index two changes from ninety to ninety five."
            )
        ):
            self.play(
                Transform(
                    old_value,
                    new_value
                ),
                Flash(boxes[2].get_center(), color=MINT, flash_radius=0.75),
            )

        self.play(
            FadeOut(highlight),
            FadeOut(change_code)
        )

        # =================================================
        # 8. USING A FOR LOOP
        # =================================================

        loop_title = Text(
            "Reading the Array with a for Loop",
            font_size=34,
            color=SOFT_WHITE,
            weight=BOLD,
        ).to_edge(UP, buff=0.38).shift(LEFT * 0.45)

        self.play(
            ReplacementTransform(
                change_title,
                loop_title
            )
        )

        # move array up a little

        self.play(
            boxes.animate.shift(UP * 0.8),
            indexes.animate.shift(UP * 0.8),
            index_word.animate.shift(UP * 0.8),
            array_name.animate.shift(UP * 0.8)
        )

        loop_code = VGroup(
            Text(
                "for (int i = 0; i < 5; i++)",
                font="Monospace",
                font_size=25,
                color=CYAN,
            ),
            Text(
                '    printf("%d\\n", marks[i]);',
                font="Monospace",
                font_size=25,
                color=SOFT_WHITE,
            )
        )

        loop_code.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.25
        )

        loop_code.to_edge(
            LEFT,
            buff=0.8
        )

        loop_code.shift(DOWN * 1.6)
        loop_panel = RoundedRectangle(
            width=loop_code.width + 0.55,
            height=loop_code.height + 0.48,
            corner_radius=0.12,
            stroke_color=BLUE,
            fill_color=PANEL,
            fill_opacity=0.98,
        ).move_to(loop_code)

        with self.voiceover(
            text=(
                "A for loop is commonly used to process every element "
                "of an array. "
                "The variable i starts at zero and increases by one "
                "until it reaches four."
            )
        ):
            self.play(FadeIn(loop_panel, shift=RIGHT * 0.15), Write(loop_code))

        # Output area

        output_title = Text(
            "Output",
            font_size=27,
            color=CYAN,
            weight=BOLD,
        ).to_edge(
            RIGHT,
            buff=1.4
        ).shift(DOWN * 0.6)

        output_box = Rectangle(
            width=2.5,
            height=2.8,
            stroke_color=MINT,
            stroke_width=2,
            fill_color=PANEL,
            fill_opacity=0.98,
        ).next_to(
            output_title,
            DOWN,
            buff=0.2
        )

        self.play(
            FadeIn(output_title),
            Create(output_box)
        )

        outputs = VGroup()

        current_values = [70, 85, 95, 75, 88]

        for i, value in enumerate(current_values):

            pointer = Triangle(
                fill_opacity=1,
                fill_color=CYAN,
                stroke_color=CYAN,
            ).scale(0.15)

            pointer.rotate(-PI / 2)

            pointer.next_to(
                boxes[i],
                UP,
                buff=0.15
            )

            i_text = Text(
                f"i = {i}",
                font_size=22,
                color=GOLD,
                weight=BOLD,
            ).next_to(
                boxes[i],
                UP,
                buff=0.45
            )

            highlight = SurroundingRectangle(
                boxes[i],
                buff=0.06,
                color=CYAN,
                stroke_width=4,
                corner_radius=0.10,
            )

            with self.voiceover(
                text=(
                    f"Now i is {i}. "
                    f"So marks at index {i} gives us {value}."
                )
            ):
                self.play(
                    FadeIn(pointer),
                    FadeIn(i_text),
                    Create(highlight)
                )

            output = Text(
                str(value),
                font_size=24,
                color=MINT,
                weight=BOLD,
            )

            outputs.add(output)

            outputs.arrange(
                DOWN,
                buff=0.15
            )

            outputs.move_to(
                output_box.get_center()
            )

            self.play(FadeIn(output))

            self.play(
                FadeOut(pointer),
                FadeOut(i_text),
                FadeOut(highlight)
            )

        # =================================================
        # 9. FINAL PROGRAM
        # =================================================

        self.play(
            FadeOut(boxes),
            FadeOut(indexes),
            FadeOut(index_word),
            FadeOut(array_name),
            FadeOut(loop_code),
            FadeOut(loop_panel),
            FadeOut(output_box),
            FadeOut(output_title),
            FadeOut(outputs),
            FadeOut(loop_title)
        )

        final_title = Text(
            "Complete C Program",
            font_size=37,
            color=SOFT_WHITE,
            weight=BOLD,
        ).to_edge(UP, buff=0.38).shift(LEFT * 0.45)

        final_program = VGroup(

            Text(
                "#include <stdio.h>",
                font="Monospace", font_size=23, color=CYAN,
            ),

            Text(
                "int main() {",
                font="Monospace", font_size=23, color=MINT,
            ),

            Text(
                "    int marks[5] = {70, 85, 95, 75, 88};",
                font="Monospace", font_size=23, color=SOFT_WHITE,
            ),

            Text(
                "    for (int i = 0; i < 5; i++) {",
                font="Monospace", font_size=23, color=GOLD,
            ),

            Text(
                '        printf("%d\\n", marks[i]);',
                font="Monospace", font_size=23, color=SOFT_WHITE,
            ),

            Text(
                "    }",
                font="Monospace", font_size=23, color=MUTED,
            ),

            Text(
                "    return 0;",
                font="Monospace", font_size=23, color=CYAN,
            ),

            Text(
                "}",
                font="Monospace", font_size=23, color=MUTED,
            )
        )

        final_program.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.18
        )

        final_program.next_to(
            final_title,
            DOWN,
            buff=0.5
        )
        final_panel = RoundedRectangle(
            width=final_program.width + 0.85,
            height=final_program.height + 0.55,
            corner_radius=0.16,
            stroke_color=BLUE,
            stroke_width=1.8,
            fill_color=PANEL,
            fill_opacity=0.98,
        ).move_to(final_program)
        code_dots = VGroup(
            Dot(radius=0.055, color=CORAL),
            Dot(radius=0.055, color=GOLD),
            Dot(radius=0.055, color=MINT),
        ).arrange(RIGHT, buff=0.10)
        code_dots.move_to(final_panel.get_corner(UL) + RIGHT * 0.32 + DOWN * 0.22)

        with self.voiceover(
            text=(
                "Now we can understand the complete program. "
                "We create an integer array called marks. "
                "It stores five values. "
                "Then a for loop accesses every element using its index "
                "and prints each value."
            )
        ):
            self.play(FadeIn(final_title, shift=DOWN * 0.18))
            self.play(FadeIn(final_panel, scale=0.98), FadeIn(code_dots))

            self.play(
                LaggedStart(
                    *[
                        Write(line)
                        for line in final_program
                    ],
                    lag_ratio=0.15
                )
            )

        self.wait(2)

        # =================================================
        # 10. SUMMARY
        # =================================================

        self.play(
            FadeOut(final_title),
            FadeOut(final_program),
            FadeOut(final_panel),
            FadeOut(code_dots)
        )

        summary_title = Text(
            "Array Concepts You Learned",
            font_size=38,
            color=SOFT_WHITE,
            weight=BOLD,
        ).to_edge(UP, buff=0.38).shift(LEFT * 0.45)

        summary = VGroup(

            Text(
                "1. Array stores multiple values",
                font_size=26, color=SOFT_WHITE,
            ),

            Text(
                "2. All values have the same data type",
                font_size=26, color=SOFT_WHITE,
            ),

            Text(
                "3. Index starts from 0",
                font_size=26, color=SOFT_WHITE,
            ),

            Text(
                "4. marks[index] accesses a value",
                font_size=26, color=SOFT_WHITE,
            ),

            Text(
                "5. Array values can be changed",
                font_size=26, color=SOFT_WHITE,
            ),

            Text(
                "6. for loops can process the whole array",
                font_size=26, color=SOFT_WHITE,
            )
        )

        summary.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.35
        )

        summary.next_to(
            summary_title,
            DOWN,
            buff=0.6
        )
        summary_panels = VGroup(*[
            RoundedRectangle(
                width=summary.width + 0.65,
                height=point.height + 0.24,
                corner_radius=0.10,
                stroke_color=BLUE,
                stroke_opacity=0.45,
                fill_color=PANEL,
                fill_opacity=0.93,
            ).move_to(point)
            for point in summary
        ])

        with self.voiceover(
            text=(
                "Let us summarize. "
                "An array stores multiple values of the same data type. "
                "Array indexing starts from zero. "
                "We use square brackets to access an element. "
                "We can also change array elements. "
                "And a for loop is an easy way to process the entire array."
            )
        ):
            self.play(FadeIn(summary_title, shift=DOWN * 0.18))

            self.play(
                LaggedStart(
                    *[
                        AnimationGroup(
                            FadeIn(panel, shift=RIGHT * 0.15),
                            FadeIn(point, shift=RIGHT * 0.15),
                        )
                        for panel, point in zip(summary_panels, summary)
                    ],
                    lag_ratio=0.2
                )
            )

        self.wait(2)

        # =================================================
        # END
        # =================================================

        self.play(
            FadeOut(summary_title),
            FadeOut(summary),
            FadeOut(summary_panels)
        )

        end = Text(
            "AI Sankalp",
            font_size=58,
            color=SOFT_WHITE,
            weight=BOLD,
        )
        end.set_color_by_gradient(CYAN, BLUE)

        end_subtitle = Text(
            "Understand the Code. See How It Works.",
            font_size=27,
            color=MUTED,
        ).next_to(
            end,
            DOWN,
            buff=0.4
        )
        end_line = Line(LEFT * 1.25, RIGHT * 1.25, color=CYAN, stroke_width=5)
        end_line.next_to(end_subtitle, DOWN, buff=0.30)

        with self.voiceover(
            text=(
                "You now understand the basic concept of arrays in C. "
                "Thank you for learning with AI Sankalp."
            )
        ):
            self.play(FadeIn(end, scale=0.86), Flash(ORIGIN, color=BLUE, flash_radius=2.2))
            self.play(FadeIn(end_subtitle, shift=UP * 0.15), GrowFromCenter(end_line))

        self.wait(2)
