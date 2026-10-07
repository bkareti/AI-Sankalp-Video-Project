import unittest
from pathlib import Path
from unittest import mock

try:
    from ai_sankalp.gui import LessonApp
except ImportError:  # Python built without Tk
    LessonApp = None


class FakeWindow:
    """Queues `after` callbacks, as Tk does, so they run after _work has returned."""

    def __init__(self):
        self.queued = []

    def after(self, _milliseconds, callback):
        self.queued.append(callback)

    def run_queued(self):
        for callback in self.queued:
            callback()


@unittest.skipIf(LessonApp is None, "tkinter is not available")
class GuiWorkTests(unittest.TestCase):
    def app(self, generator):
        app = object.__new__(LessonApp)  # skip __init__: it opens a Tk window
        app.generator, app.renderer, app.window = generator, mock.Mock(), FakeWindow()
        app._done = mock.Mock()
        return app

    def test_generation_failure_reaches_the_error_dialog(self):
        generator = mock.Mock()
        generator.generate.side_effect = RuntimeError("template is broken")
        app = self.app(generator)
        app._work(mock.Mock(), False, Path("out"), "low")
        app.window.run_queued()  # after the except block has ended, as in Tk
        app._done.assert_called_once_with("", "template is broken")

    def test_success_reports_the_saved_paths(self):
        generator = mock.Mock()
        generator.generate.return_value = mock.Mock(scene_path="scene.py", config_path="config.json")
        app = self.app(generator)
        app._work(mock.Mock(), False, Path("out"), "low")
        app.window.run_queued()
        message, error = app._done.call_args[0]
        self.assertIn("scene.py", message)
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
