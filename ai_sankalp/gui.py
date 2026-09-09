from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .generator import LessonGenerator
from .models import LessonConfig
from .renderer import ManimRenderer


class LessonApp:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.generator = LessonGenerator(project_root)
        self.renderer = ManimRenderer(project_root)
        self.window = tk.Tk()
        self.window.title("AI Sankalp Video Generator")
        self.window.geometry("980x780")
        self.window.minsize(820, 680)
        self.output_dir = tk.StringVar(value=str(project_root / "generated" / "videos"))
        self.voiceover = tk.BooleanVar(value=True)
        self.quality = tk.StringVar(value="low")
        self.status = tk.StringVar(value="Ready")
        self._build()

    def _build(self) -> None:
        outer = ttk.Frame(self.window, padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="AI Sankalp Video Generator", font=("Helvetica", 20, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Turn a programming lesson into a branded Manim video.").pack(anchor="w", pady=(2, 14))

        form = ttk.Frame(outer)
        form.pack(fill="both", expand=True)
        self.entries = {}
        fields = [
            ("topic", "Topic", "Python for loops"),
            ("title", "Lesson title", "Mastering Python For Loops"),
            ("language", "Programming language", "Python"),
            ("output_video_name", "Output video name", "python_for_loops"),
        ]
        for row, (key, label, default) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)
            entry = ttk.Entry(form)
            entry.insert(0, default)
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.entries[key] = entry

        explanation_row = len(fields)
        ttk.Label(form, text="Explanation\n(blank line = new step)").grid(
            row=explanation_row, column=0, sticky="nw", padx=(0, 12), pady=6
        )
        self.explanation = tk.Text(form, height=9, wrap="word")
        self.explanation.insert(
            "1.0",
            "What is a for loop?\nA for loop repeats an action for every item in a sequence.\nIt avoids writing the same code again and again.\n\n"
            "How iteration works\nPython takes one item at a time.\nThe loop body runs once for each item.\n\n"
            "The range function\nrange(1, 6) creates numbers from 1 through 5.\nThe ending value is not included.",
        )
        self.explanation.grid(row=explanation_row, column=1, sticky="nsew", pady=6)

        code_row = explanation_row + 1
        ttk.Label(form, text="Code example").grid(row=code_row, column=0, sticky="nw", padx=(0, 12), pady=6)
        self.code = tk.Text(form, height=7, wrap="none", font=("Menlo", 11))
        self.code.insert("1.0", "for number in range(1, 6):\n    print(number)")
        self.code.grid(row=code_row, column=1, sticky="nsew", pady=6)

        options_row = code_row + 1
        options = ttk.Frame(form)
        options.grid(row=options_row, column=1, sticky="ew", pady=6)
        ttk.Checkbutton(options, text="Generate gTTS voiceover", variable=self.voiceover).pack(side="left")
        ttk.Label(options, text="Quality:").pack(side="left", padx=(24, 6))
        ttk.Combobox(
            options, textvariable=self.quality, values=("low", "medium", "high", "production"),
            width=12, state="readonly",
        ).pack(side="left")

        output_row = options_row + 1
        ttk.Label(form, text="Output folder").grid(row=output_row, column=0, sticky="w", padx=(0, 12), pady=4)
        output_frame = ttk.Frame(form)
        output_frame.grid(row=output_row, column=1, sticky="ew", pady=4)
        ttk.Entry(output_frame, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        ttk.Button(output_frame, text="Choose…", command=self._choose_output).pack(side="left", padx=(8, 0))

        form.columnconfigure(1, weight=1)
        form.rowconfigure(explanation_row, weight=1)
        form.rowconfigure(code_row, weight=1)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(14, 0))
        self.generate_button = ttk.Button(actions, text="Generate Scene", command=lambda: self._start(False))
        self.generate_button.pack(side="left")
        self.render_button = ttk.Button(actions, text="Generate & Render MP4", command=lambda: self._start(True))
        self.render_button.pack(side="left", padx=8)
        ttk.Label(actions, textvariable=self.status).pack(side="right")

    def _choose_output(self) -> None:
        chosen = filedialog.askdirectory(initialdir=self.output_dir.get())
        if chosen:
            self.output_dir.set(chosen)

    def _lesson(self) -> LessonConfig:
        return LessonConfig.from_dict({
            **{key: entry.get() for key, entry in self.entries.items()},
            "explanation": self.explanation.get("1.0", "end").strip(),
            "code_example": self.code.get("1.0", "end").rstrip(),
            "voiceover": {"enabled": self.voiceover.get(), "language": "en"},
        })

    def _start(self, render: bool) -> None:
        try:
            lesson = self._lesson()
        except Exception as exc:
            messagebox.showerror("Invalid lesson", str(exc))
            return
        self.generate_button.configure(state="disabled")
        self.render_button.configure(state="disabled")
        self.status.set("Rendering…" if render else "Generating…")
        output_dir = Path(self.output_dir.get())
        quality = self.quality.get()
        threading.Thread(
            target=self._work, args=(lesson, render, output_dir, quality), daemon=True
        ).start()

    def _work(self, lesson: LessonConfig, render: bool, output_dir: Path, quality: str) -> None:
        try:
            generated = self.generator.generate(lesson)
            if render:
                result = self.renderer.render(generated, lesson, output_dir, quality=quality)
                message = f"Video saved to:\n{result.video_path}"
            else:
                message = f"Scene saved to:\n{generated.scene_path}\n\nConfig saved to:\n{generated.config_path}"
            self.window.after(0, lambda: self._done(message, None))
        except Exception as exc:
            self.window.after(0, lambda: self._done("", str(exc)))

    def _done(self, message: str, error: str | None) -> None:
        self.generate_button.configure(state="normal")
        self.render_button.configure(state="normal")
        if error:
            self.status.set("Failed")
            messagebox.showerror("Generation failed", error)
        else:
            self.status.set("Complete")
            messagebox.showinfo("AI Sankalp", message)

    def run(self) -> None:
        self.window.mainloop()


def launch_gui(project_root: Path) -> None:
    LessonApp(project_root).run()
