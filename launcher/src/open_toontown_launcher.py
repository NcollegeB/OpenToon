"""Small relative-path launcher for an Open Town development bundle."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
from typing import Iterable, Optional, Tuple


RUNTIME_CHECK = (
    "import json, sys; "
    "import panda3d.core, panda3d.otp, panda3d.toontown, pytz; "
    "print(json.dumps({"
    "'python': sys.version.split()[0], "
    "'panda3d': panda3d.core.PandaSystem.getVersionString(), "
    "'executable': sys.executable"
    "}))"
)


def find_bundle_root(explicit: Optional[Path] = None) -> Path:
    if explicit is not None:
        candidates = (explicit.resolve(),)
    else:
        origin = Path(
            sys.executable if getattr(sys, 'frozen', False) else __file__
        ).resolve()
        candidates = (origin.parent,) + tuple(origin.parents)

    for candidate in candidates:
        if (
            (candidate / 'game' / 'toontown').is_dir()
            and (candidate / 'game' / 'etc' / 'Configrc.prc').is_file()
        ):
            return candidate
    raise RuntimeError(
        'Could not locate the bundle root containing game/toontown and '
        'game/etc/Configrc.prc.')


def _configured_ppython(game_root: Path) -> Optional[Path]:
    config = game_root / 'PPYTHON_PATH'
    if not config.is_file():
        return None
    for line in config.read_text(encoding='utf-8-sig').splitlines():
        value = line.strip().strip('"').strip("'")
        if not value or value.startswith(('#', ';')):
            continue
        value = os.path.expandvars(value)
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = game_root / candidate
        return candidate.resolve()
    return None


def runtime_candidates(bundle_root: Path) -> Iterable[Path]:
    configured_environment = os.environ.get('OPEN_TOONTOWN_PYTHON', '').strip()
    if configured_environment:
        yield Path(configured_environment).expanduser()

    game_root = bundle_root / 'game'
    configured = _configured_ppython(game_root)
    if configured is not None:
        yield configured

    if sys.platform == 'win32':
        yield (
            bundle_root
            / 'runtime'
            / 'Panda3D-1.11.0-x64'
            / 'python'
            / 'ppython.exe'
        )
    elif sys.platform == 'darwin':
        yield bundle_root / 'runtime' / 'macos-arm64' / 'bin' / 'python3'
        yield bundle_root / 'runtime' / 'macos-x86_64' / 'bin' / 'python3'
        yield bundle_root / 'runtime' / 'python' / 'bin' / 'python3'
    else:
        yield bundle_root / 'runtime' / 'linux-x86_64' / 'bin' / 'python3'
        yield bundle_root / 'runtime' / 'python' / 'bin' / 'python3'

    for name in ('python3.9', 'python3'):
        discovered = shutil.which(name)
        if discovered:
            yield Path(discovered)


def _hidden_process_flags() -> int:
    if sys.platform != 'win32':
        return 0
    return getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def validate_runtime(
    executable: Path, bundle_root: Path
) -> Tuple[bool, str]:
    executable = executable.resolve()
    if not executable.is_file():
        return False, 'not found'
    try:
        result = subprocess.run(
            [str(executable), '-c', RUNTIME_CHECK],
            cwd=str(bundle_root / 'game'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            creationflags=_hidden_process_flags(),
        )
    except (OSError, subprocess.SubprocessError) as error:
        return False, str(error)
    if result.returncode != 0:
        detail = result.stderr.strip() or 'custom module import failed'
        return False, detail
    return True, result.stdout.strip()


def resolve_runtime(bundle_root: Path) -> Tuple[Path, str]:
    failures = []
    seen = set()
    for candidate in runtime_candidates(bundle_root):
        candidate = candidate.expanduser().resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        valid, detail = validate_runtime(candidate, bundle_root)
        if valid:
            return candidate, detail
        failures.append('%s: %s' % (candidate, detail))
    raise RuntimeError(
        'No compatible Python runtime was found. The runtime must contain '
        'panda3d.otp and panda3d.toontown; stock Panda3D is insufficient.\n'
        + '\n'.join(failures)
    )


def child_environment() -> dict:
    environment = os.environ.copy()
    environment.setdefault('LOGIN_TOKEN', 'dev')
    environment.setdefault('GAME_SERVER', '127.0.0.1')
    environment['PYTHONUNBUFFERED'] = '1'
    environment['PYTHONIOENCODING'] = 'utf-8'
    return environment


def start_client(bundle_root: Path, runtime: Path) -> subprocess.Popen:
    flags = 0
    if sys.platform == 'win32':
        flags = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
    return subprocess.Popen(
        [
            str(runtime),
            '-u',
            '-m',
            'toontown.launcher.QuickStartLauncher',
        ],
        cwd=str(bundle_root / 'game'),
        env=child_environment(),
        creationflags=flags,
    )


def start_server_gui(bundle_root: Path, runtime: Path) -> subprocess.Popen:
    if sys.platform != 'win32':
        raise RuntimeError(
            'The bundled server GUI is currently Windows-only. Use the '
            'target platform scripts under game/darwin or game/linux after '
            'installing target-native Panda3D and Astron builds.')
    return subprocess.Popen(
        [str(runtime), str(bundle_root / 'game' / 'tools' / 'server_gui.py')],
        cwd=str(bundle_root / 'game'),
        env=child_environment(),
        creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0),
    )


def open_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform == 'win32':
        os.startfile(str(path))
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', str(path)])
    else:
        opener = shutil.which('xdg-open')
        if not opener:
            raise RuntimeError('xdg-open is not installed.')
        subprocess.Popen([opener, str(path)])


def run_check(bundle_root: Path) -> int:
    try:
        runtime, detail = resolve_runtime(bundle_root)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                'bundle_root': str(bundle_root),
                'runtime': str(runtime),
                'runtime_detail': json.loads(detail),
                'platform': sys.platform,
            },
            indent=2,
        )
    )
    return 0


def run_gui(bundle_root: Path) -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ImportError as error:
        print('Tkinter is required for the source launcher: %s' % error)
        return 1

    class LauncherWindow:
        def __init__(self):
            self.runtime = None
            self.runtimeDetail = ''
            self.statusQueue = queue.Queue()
            self.window = tk.Tk()
            self.window.title('Open Town Launcher')
            self.window.geometry('620x390')
            self.window.minsize(560, 360)

            outer = ttk.Frame(self.window, padding=18)
            outer.pack(fill='both', expand=True)
            ttk.Label(
                outer,
                text='Open Town',
                font=('Segoe UI', 20, 'bold'),
            ).pack(anchor='w')
            ttk.Label(
                outer,
                text=(
                    'Local development launcher. A target-native custom '
                    'Panda3D runtime is required.'
                ),
                wraplength=570,
            ).pack(anchor='w', pady=(2, 16))

            buttons = ttk.Frame(outer)
            buttons.pack(fill='x')
            ttk.Button(
                buttons, text='Start Client', command=self.startClient
            ).grid(row=0, column=0, sticky='ew', padx=(0, 6), pady=4)
            self.serverButton = ttk.Button(
                buttons, text='Server GUI', command=self.startServer
            )
            self.serverButton.grid(
                row=0, column=1, sticky='ew', padx=(6, 0), pady=4)
            ttk.Button(
                buttons, text='Validate Runtime', command=self.checkRuntime
            ).grid(row=1, column=0, sticky='ew', padx=(0, 6), pady=4)
            ttk.Button(
                buttons,
                text='Open Logs',
                command=lambda: self.openPath(bundle_root / 'game' / 'logs'),
            ).grid(row=1, column=1, sticky='ew', padx=(6, 0), pady=4)
            ttk.Button(
                buttons,
                text='Open Game Folder',
                command=lambda: self.openPath(bundle_root / 'game'),
            ).grid(row=2, column=0, columnspan=2, sticky='ew', pady=4)
            buttons.columnconfigure(0, weight=1)
            buttons.columnconfigure(1, weight=1)

            if sys.platform != 'win32':
                self.serverButton.state(['disabled'])

            self.status = tk.StringVar(value='Checking runtime...')
            ttk.Separator(outer).pack(fill='x', pady=14)
            ttk.Label(
                outer,
                textvariable=self.status,
                wraplength=570,
                justify='left',
            ).pack(fill='x', anchor='w')
            ttk.Label(
                outer,
                text='Bundle: %s' % bundle_root,
                wraplength=570,
                foreground='#555555',
            ).pack(fill='x', anchor='w', pady=(12, 0))
            threading.Thread(
                target=self._resolveRuntime, daemon=True
            ).start()
            self.window.after(100, self._drainStatusQueue)

        def _setStatus(self, text):
            self.statusQueue.put(text)

        def _drainStatusQueue(self):
            try:
                while True:
                    self.status.set(self.statusQueue.get_nowait())
            except queue.Empty:
                pass
            self.window.after(100, self._drainStatusQueue)

        def _resolveRuntime(self):
            try:
                runtime, detail = resolve_runtime(bundle_root)
            except RuntimeError as error:
                self.runtime = None
                self.runtimeDetail = ''
                self._setStatus(str(error))
                return
            self.runtime = runtime
            self.runtimeDetail = detail
            parsed = json.loads(detail)
            self._setStatus(
                'Ready: Python %(python)s, Panda3D %(panda3d)s\n%(executable)s'
                % parsed
            )

        def _requireRuntime(self):
            if self.runtime is None:
                messagebox.showerror(
                    'Runtime unavailable',
                    'No compatible runtime is ready. Choose Validate Runtime '
                    'after installing a target-native custom Panda3D build.',
                )
                return None
            return self.runtime

        def checkRuntime(self):
            self.status.set('Checking runtime...')
            threading.Thread(
                target=self._resolveRuntime, daemon=True
            ).start()

        def startClient(self):
            runtime = self._requireRuntime()
            if runtime is None:
                return
            try:
                process = start_client(bundle_root, runtime)
            except OSError as error:
                messagebox.showerror('Client failed to start', str(error))
                return
            self.status.set('Client started (PID %s).' % process.pid)

        def startServer(self):
            runtime = self._requireRuntime()
            if runtime is None:
                return
            try:
                process = start_server_gui(bundle_root, runtime)
            except (OSError, RuntimeError) as error:
                messagebox.showerror('Server GUI failed to start', str(error))
                return
            self.status.set('Server GUI started (PID %s).' % process.pid)

        def openPath(self, path):
            try:
                open_folder(path)
            except (OSError, RuntimeError) as error:
                messagebox.showerror('Unable to open folder', str(error))

        def run(self):
            self.window.mainloop()

    LauncherWindow().run()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--bundle-root',
        type=Path,
        help='Explicit bundle root; normally auto-detected.',
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Validate paths and custom Panda3D modules without opening a GUI.',
    )
    args = parser.parse_args(argv)
    try:
        bundle_root = find_bundle_root(args.bundle_root)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1
    if args.check:
        return run_check(bundle_root)
    return run_gui(bundle_root)


if __name__ == '__main__':
    raise SystemExit(main())
