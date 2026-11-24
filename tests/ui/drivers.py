"""
UI drivers: operate the real application window the way a user does.

Both programs build their GUI with Tk. A driver only needs one primitive - evaluate a Tcl script in the
application's Tcl interpreter (``eval``) - and loads tests/ui/driver.tcl there. Everything else
(finding widgets by text, clicking, choosing menu items, replacing the dialogs) is done by the Tcl
helpers, so it works the same for both programs.

* PythonAppDriver - runs the Python program's Controller in this process and calls its interpreter
  through tkinter.
* CAppDriver - starts the C program as a child process in test mode and talks to it over stdin/stdout
  (protocol below).

Protocol of the C program's test mode (``<c-app> --test-driver``)
-----------------------------------------------------------------
The program starts its GUI normally, but reads requests from stdin while its Tk event loop runs and
writes nothing to stdout except the replies. All text is UTF-8.

    request:  "<n>\\n" followed by n bytes: a Tcl script
    reply:    "ok <n>\\n" followed by n bytes: the script's result
              "error <n>\\n" followed by n bytes: the error message

The script is evaluated at global level in the GUI's interpreter, in the event loop (like a Tk event
handler). End of input closes the program.
"""

import contextlib
import io
import os
import queue
import subprocess
import sys
import threading
import tkinter
from dataclasses import dataclass

DRIVER_TCL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "driver.tcl")

# a Tcl interpreter without Tk, only for parsing the lists returned by the helpers
_parser = tkinter.Tcl()


class AppError(Exception):
    """The application failed: a Tcl error or an exception in one of its callbacks."""


def tcl_quote(value) -> str:
    """One Tcl word whose value is exactly str(value)."""
    text = str(value)
    for ch in "\\$[]\"{}":
        text = text.replace(ch, "\\" + ch)
    return '"' + text.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t") + '"'


def split_list(text: str) -> list:
    return list(_parser.splitlist(text))


def split_dict(text: str) -> dict:
    items = split_list(text)
    return dict(zip(items[0::2], items[1::2]))


@dataclass
class Widget:
    path: str
    cls: str        # Tk class: Button, Label, Checkbutton, Menubutton (option menu), Canvas, ...
    text: str       # text the user reads on it
    value: str      # "1"/"0" for a checked/unchecked check button, "" otherwise
    state: str
    window: str     # title of its window
    x: int          # position and size inside the window
    y: int
    width: int
    height: int


class UIDriver:
    """Operations of a user on the application. Subclasses implement start/eval/close."""

    # ---- transport (subclasses) -----------------------------------------------------------------
    def eval(self, script: str) -> str:
        """Evaluates a Tcl script in the application; raises AppError on failure."""
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def _ensure_helpers(self) -> None:
        """Loads driver.tcl unless the application's current interpreter already has it."""
        if self._raw_eval("namespace exists ::uidriver") != "1":
            self._raw_eval("source -encoding utf-8 " + tcl_quote(DRIVER_TCL))

    def _raw_eval(self, script: str) -> str:
        raise NotImplementedError

    def call(self, *words) -> str:
        """Calls one Tcl command with the given words (each quoted)."""
        return self.eval(" ".join(tcl_quote(w) if i else w for i, w in enumerate(words)))

    def settle(self) -> None:
        """Lets the application process all pending events (redraws, geometry changes)."""
        self.eval("update")

    def _action(self, *words) -> None:
        self.call(*words)
        self.settle()

    # ---- dialogs --------------------------------------------------------------------------------
    def answer_open_file(self, path: str) -> None:
        """The next 'open file' dialog returns path ("" = Cancel)."""
        self.call("::uidriver::answer", "open", path)

    def answer_save_file(self, path: str) -> None:
        """The next 'save file' dialog returns path ("" = Cancel)."""
        self.call("::uidriver::answer", "save", path)

    def dialogs(self, kind: str = None) -> list:
        """Dialog calls since clear_log() as (kind, options) with kind open/save/message, oldest first."""
        calls = []
        for item in split_list(self.eval("::uidriver::log")):
            k, opts = split_list(item)
            if kind is None or k == kind:
                calls.append((k, split_dict(opts)))
        return calls

    def messages(self) -> list:
        """Message boxes shown since clear_log() as dicts {"-icon", "-title", "-message", ...}."""
        return [opts for _, opts in self.dialogs("message")]

    def clear_log(self) -> None:
        self.eval("::uidriver::clear_log")

    # ---- reading the window ---------------------------------------------------------------------
    def widgets(self, window: str = None) -> list:
        """Shown widgets (of the window with this title), sorted top to bottom, left to right."""
        words = ["::uidriver::widgets"] + ([window] if window is not None else [])
        result = []
        for item in split_list(self.call(*words)):
            d = split_dict(item)
            result.append(Widget(d["path"], d["class"], d["text"], d["value"], d["state"], d["window"],
                                 int(d["x"]), int(d["y"]), int(d["width"]), int(d["height"])))
        return sorted(result, key=lambda w: (w.y, w.x))

    def windows(self) -> list:
        """Shown windows as dicts {"path", "title", "width", "height"}."""
        result = []
        for item in split_list(self.eval("::uidriver::windows")):
            d = split_dict(item)
            d["width"], d["height"] = int(d["width"]), int(d["height"])
            result.append(d)
        return result

    def window_titles(self) -> list:
        return [w["title"] for w in self.windows()]

    def menu_items(self, menu_text: str) -> list:
        """Items of the option menu that currently shows menu_text."""
        return split_list(self.call("::uidriver::menu_items", menu_text))

    def canvas_images(self, window: str = None) -> list:
        """Images on shown canvases as dicts {"image", "x", "y", "anchor", "width", "height"}."""
        words = ["::uidriver::canvas_images"] + ([window] if window is not None else [])
        result = []
        for item in split_list(self.call(*words)):
            d = split_dict(item)
            for key in ("x", "y", "width", "height"):
                d[key] = int(d[key])
            result.append(d)
        return result

    def image_pixel(self, image: str, x: int, y: int) -> tuple:
        return tuple(int(v) for v in split_list(self.call("::uidriver::image_pixel", image, x, y)))

    # ---- user actions ---------------------------------------------------------------------------
    def click(self, text: str) -> None:
        """Presses the shown button or check button with this text."""
        self._action("::uidriver::click", text)

    def choose(self, menu_text: str, item: str) -> None:
        """Chooses item in the option menu that currently shows menu_text."""
        self._action("::uidriver::choose", menu_text, item)

    def close_window(self, title: str) -> None:
        """Closes the window with this title like the window's close button."""
        self._action("::uidriver::close_window", title)


class PythonAppDriver(UIDriver):
    """Runs the Python program's GUI (gui.controller.Controller) in this process."""

    def __init__(self, python_root: str, workdir: str):
        root = os.path.abspath(python_root)
        if root not in sys.path:
            sys.path.insert(0, root)
        self._old_cwd = os.getcwd()
        os.chdir(workdir)       # the program uses paths relative to the working directory
        self.app = None
        old_root = tkinter._default_root
        try:
            from gui.controller import Controller
            with self._catch_callback_errors():
                self.app = Controller()
            self._ensure_helpers()
            self.settle()
        except BaseException:
            # A Tk left alive would stay tkinter's default root, and the dialogs of later tests would
            # open in it (without the test versions from driver.tcl). Controller() may also fail after
            # its Tk was created, before self.app is set.
            root = self.app if self.app is not None else tkinter._default_root
            if root is not None and root is not old_root:
                try:
                    root.destroy()
                except tkinter.TclError:
                    pass
            os.chdir(self._old_cwd)
            raise

    @contextlib.contextmanager
    def _catch_callback_errors(self):
        """tkinter prints exceptions raised in callbacks to stderr instead of passing them on;
        turn them into AppError so a crashing program fails the test."""
        captured = io.StringIO()
        try:
            with contextlib.redirect_stderr(captured):
                yield
        finally:
            output = captured.getvalue()
            if output:
                sys.stderr.write(output)
        if "Traceback (most recent call last)" in output:
            raise AppError(output)

    def _raw_eval(self, script: str) -> str:
        # Controller.reset() replaces the interpreter, so always use the current one
        try:
            with self._catch_callback_errors():
                return self.app.tk.eval(script)
        except tkinter.TclError as e:
            raise AppError(str(e)) from None

    def eval(self, script: str) -> str:
        self._ensure_helpers()
        return self._raw_eval(script)

    def close(self) -> None:
        try:
            self.app.destroy()
        except tkinter.TclError:
            pass
        finally:
            os.chdir(self._old_cwd)


class CAppDriver(UIDriver):
    """Runs the C program in test mode as a child process (see the protocol above)."""

    TIMEOUT = 300   # seconds for one request (generating can take a while)

    def __init__(self, app_path: str, workdir: str):
        self._proc = subprocess.Popen([os.path.abspath(app_path), "--test-driver"], cwd=workdir,
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self._replies = queue.Queue()
        self._broken = None     # why no more replies can come, once that happened
        threading.Thread(target=self._read_replies, daemon=True).start()
        try:
            self._ensure_helpers()
            self.settle()
        except BaseException:
            self.close()
            raise

    def _read_replies(self):
        out = self._proc.stdout
        try:
            while True:
                header = out.readline()
                if not header:
                    self._broken = "the C program closed its output"
                    return
                try:
                    status, length = header.decode("ascii").split()
                    body = out.read(int(length)).decode("utf-8")
                except ValueError:
                    self._broken = "the C program wrote something that is not a reply: " + repr(header)
                    return
                self._replies.put((status, body))
        except (OSError, ValueError) as e:     # the pipe was closed by close()
            self._broken = "reading the C program's output failed: " + repr(e)
        finally:
            self._replies.put(None)     # wakes up a waiting request

    def _broken_error(self) -> AppError:
        code = self._proc.poll()
        return AppError(self._broken + ("" if code is None else f" (exit code {code})"))

    def _raw_eval(self, script: str) -> str:
        if self._broken is not None:    # fail at once instead of waiting TIMEOUT for each request
            raise self._broken_error()
        data = script.encode("utf-8")
        try:
            self._proc.stdin.write(str(len(data)).encode("ascii") + b"\n" + data)
            self._proc.stdin.flush()
        except OSError as e:
            raise AppError("cannot send a request to the C program: " + repr(e)) from None
        try:
            reply = self._replies.get(timeout=self.TIMEOUT)
        except queue.Empty:
            # a late reply would be taken as the answer to the next request, so stop the program
            self._proc.kill()
            raise AppError(f"no reply from the C program within {self.TIMEOUT} s") from None
        if reply is None:
            raise self._broken_error()
        status, body = reply
        if status != "ok":
            raise AppError(body)
        return body

    def eval(self, script: str) -> str:
        self._ensure_helpers()
        return self._raw_eval(script)

    def close(self) -> None:
        try:
            self._proc.stdin.close()
            self._proc.wait(timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            self._proc.kill()
            self._proc.wait()
        finally:
            self._proc.stdout.close()
