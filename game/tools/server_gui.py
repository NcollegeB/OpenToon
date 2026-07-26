"""Standalone Windows controller for the local Open Town server stack.

This tool deliberately launches the existing Astron, UberDOG, and AI entry
points directly without invoking a command shell, and does not modify game code.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import queue
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Optional


APP_TITLE = "Open Town Local Server Control"
LOCALHOST = "127.0.0.1"
MESSAGE_DIRECTOR_PORT = 7199
EVENT_LOGGER_PORT = 7197
STARTUP_TIMEOUT_SECONDS = 45.0
STOP_TIMEOUT_SECONDS = 6.0
MAX_LOG_LINES = 20_000
LOG_TRIM_LINES = 2_000
SELF_TEST_LOG_LINE_LIMIT = 250

PROCESS_ORDER = ("astron", "uberdog", "ai")
STOP_ORDER = tuple(reversed(PROCESS_ORDER))
DEPENDENCIES = {
    "astron": (),
    "uberdog": ("astron",),
    "ai": ("astron", "uberdog"),
}

READY_PATTERNS = {
    "astron": re.compile(
        r"\b(listen(?:ing)?|message\s+director|event\s+logger|ready)\b",
        re.IGNORECASE,
    ),
    "uberdog": re.compile(
        r"\b(uberdog|udrepository|message\s+director)\b.*"
        r"\b(ready|started|connected|online)\b",
        re.IGNORECASE,
    ),
    "ai": re.compile(
        r"(?:\b(ai|district|airepository)\b.*"
        r"\b(ready|started|connected|online|done)\b|"
        r"\btoontownairepository\b.*\bdone\b)",
        re.IGNORECASE,
    ),
}

JOIN_PATTERNS = (
    re.compile(
        r"\b(?:player|avatar|toon|client)\b.{0,100}"
        r"\b(?:joined|connected|logged\s+in|entered)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:new\s+client|client\s+connected|avatar\s+generated|"
        r"account\s+authenticated)\b",
        re.IGNORECASE,
    ),
)
LEAVE_PATTERNS = (
    re.compile(
        r"\b(?:player|avatar|toon|client)\b.{0,100}"
        r"\b(?:left|disconnected|logged\s+out|exited)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:client\s+disconnected|connection\s+lost|avatar\s+disabled)\b",
        re.IGNORECASE,
    ),
)
ERROR_PATTERN = re.compile(
    r"\b(?:fatal|error|exception|traceback|failed|failure)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ProcessSpec:
    key: str
    title: str
    color: str


@dataclass
class ManagedProcess:
    spec: ProcessSpec
    process: Optional[subprocess.Popen[str]] = None
    generation: int = 0
    state: str = "Stopped"
    ready_hint: bool = False
    intentional_stop: bool = False

    def is_active(self) -> bool:
        return self.process is not None and self.process.poll() is None


@dataclass(frozen=True)
class ResolvedPython:
    path: Path
    source: str


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _expand_windows_variables(value: str) -> str:
    """Expand both $NAME/${NAME} and Windows-style %NAME% variables."""

    expanded = os.path.expandvars(value)

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        return os.environ.get(name, match.group(0))

    return re.sub(r"%([^%]+)%", replace, expanded)


def _clean_path_line(value: str) -> str:
    value = value.lstrip("\ufeff").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1].strip()
    return _expand_windows_variables(value)


def resolve_ppython(root: Path, override: Optional[Path] = None) -> ResolvedPython:
    """Resolve a single PPython executable without interpreting command text."""

    candidates: list[tuple[str, str]] = []
    if override is not None:
        candidates.append(("GUI selection", str(override)))

    environment_value = os.environ.get("PPYTHON_PATH", "").strip()
    if environment_value:
        candidates.append(("PPYTHON_PATH environment variable", environment_value))

    config_path = root / "PPYTHON_PATH"
    if config_path.is_file():
        try:
            lines = config_path.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError) as error:
            raise RuntimeError(f"Could not read {config_path}: {error}") from error
        configured_line = next(
            (
                line
                for line in lines
                if line.strip() and not line.lstrip().startswith(("#", ";"))
            ),
            "",
        )
        if configured_line:
            candidates.append((str(config_path), configured_line))

    fallback_roots = (root.parent / "runtime", root.parent)
    for fallback_root in fallback_roots:
        direct = (
            fallback_root
            / "Panda3D-1.11.0-x64"
            / "python"
            / "ppython.exe"
        )
        candidates.append((f"sibling runtime fallback under {fallback_root}", str(direct)))
        if fallback_root.is_dir():
            for discovered in sorted(
                fallback_root.glob("Panda3D-*/python/ppython.exe"),
                reverse=True,
            ):
                candidates.append(
                    (f"discovered sibling runtime under {fallback_root}", str(discovered))
                )

    if not candidates:
        raise RuntimeError(
            "No PPython path is configured. Set PPYTHON_PATH or update the "
            "repository's PPYTHON_PATH file."
        )

    failures: list[str] = []
    for source, raw_value in candidates:
        clean_value = _clean_path_line(raw_value)
        if not clean_value:
            failures.append(f"{source}: empty path")
            continue
        candidate = Path(clean_value).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        if candidate.is_file():
            return ResolvedPython(candidate, source)
        failures.append(f"{source}: file not found: {candidate}")

    raise RuntimeError("Unable to resolve PPython.\n" + "\n".join(failures))


def classify_player_signal(line: str) -> Optional[str]:
    """Return a heuristic player event class for known server log phrasing."""

    if any(pattern.search(line) for pattern in LEAVE_PATTERNS):
        return "leave"
    if any(pattern.search(line) for pattern in JOIN_PATTERNS):
        return "join"
    return None


def validate_loopback_binds(config_path: Path) -> None:
    """Reject an Astron configuration that exposes any declared bind address."""

    try:
        config_text = config_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise RuntimeError(f"Could not read Astron configuration: {error}") from error
    bind_values = re.findall(
        r"^\s*bind\s*:\s*([^\s#]+)",
        config_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if not bind_values:
        raise RuntimeError(
            "Astron configuration has no explicit bind addresses; refusing to "
            "start because localhost-only behavior cannot be verified."
        )
    required_ports = {7197, 7198, 7199}
    observed_ports: set[int] = set()
    for raw_endpoint in bind_values:
        endpoint = raw_endpoint.strip().strip("\"'")
        if endpoint.startswith("[") and "]:" in endpoint:
            host, port_text = endpoint[1:].rsplit("]:", 1)
        else:
            try:
                host, port_text = endpoint.rsplit(":", 1)
            except ValueError as error:
                raise RuntimeError(
                    f"Unrecognized Astron bind endpoint: {endpoint}"
                ) from error
        if host.lower() not in {LOCALHOST, "localhost", "::1"}:
            raise RuntimeError(
                f"Refusing non-loopback Astron bind address: {endpoint}"
            )
        try:
            observed_ports.add(int(port_text))
        except ValueError as error:
            raise RuntimeError(
                f"Unrecognized Astron bind port: {endpoint}"
            ) from error
    missing_ports = required_ports - observed_ports
    if missing_ports:
        raise RuntimeError(
            "Astron localhost configuration is missing expected bind port(s): "
            + ", ".join(str(port) for port in sorted(missing_ports))
        )


def build_process_command(
    root: Path,
    ppython: Optional[ResolvedPython],
    ppython_error: str,
    key: str,
) -> tuple[list[str], Path]:
    """Build one fixed local command without consulting a command shell."""

    if key == "astron":
        executable = (root / "astron" / "win32" / "astrond.exe").resolve()
        config = (root / "astron" / "config" / "astrond.yml").resolve()
        if not executable.is_file():
            raise RuntimeError(f"Astron executable not found: {executable}")
        if not config.is_file():
            raise RuntimeError(f"Astron configuration not found: {config}")
        validate_loopback_binds(config)
        return (
            [str(executable), "--loglevel", "info", str(config)],
            executable.parent,
        )

    if ppython is None:
        raise RuntimeError(ppython_error or "PPython is not configured.")
    if not ppython.path.is_file():
        raise RuntimeError(f"PPython executable not found: {ppython.path}")

    common = [
        "--max-channels",
        "999999",
        "--stateserver",
        "4002",
        "--messagedirector-ip",
        f"{LOCALHOST}:{MESSAGE_DIRECTOR_PORT}",
        "--eventlogger-ip",
        f"{LOCALHOST}:{EVENT_LOGGER_PORT}",
    ]
    if key == "uberdog":
        return (
            [
                str(ppython.path),
                "-u",
                "-m",
                "toontown.uberdog.UDStart",
                "--base-channel",
                "1000000",
                *common,
            ],
            root,
        )
    if key == "ai":
        return (
            [
                str(ppython.path),
                "-u",
                "-m",
                "toontown.ai.AIStart",
                "--base-channel",
                "401000000",
                *common,
                "--district-name",
                "Toon Valley",
            ],
            root,
        )
    raise KeyError(f"Unknown process key: {key}")


class AstronEventLogTailer:
    """Follow newly appended Astron JSON event records without replaying history."""

    def __init__(
        self,
        log_directory: Path,
        event_queue: queue.Queue[tuple[object, ...]],
    ) -> None:
        self.log_directory = log_directory
        self.event_queue = event_queue
        self.stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self._run,
            name="astron-event-log-tailer",
            daemon=True,
        )

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()

    def _run(self) -> None:
        offsets: dict[Path, int] = {}
        if self.log_directory.is_dir():
            for path in self.log_directory.glob("events-*.log"):
                try:
                    offsets[path.resolve()] = path.stat().st_size
                except OSError:
                    continue

        while not self.stop_event.wait(0.2):
            if not self.log_directory.is_dir():
                continue
            try:
                event_logs = sorted(self.log_directory.glob("events-*.log"))
            except OSError:
                continue
            for unresolved_path in event_logs:
                path = unresolved_path.resolve()
                if path not in offsets:
                    offsets[path] = 0
                    self.event_queue.put(("event_log_file", str(path)))
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                if size < offsets[path]:
                    offsets[path] = 0
                if size <= offsets[path]:
                    continue
                self._read_appended_records(path, offsets)

    def _read_appended_records(
        self,
        path: Path,
        offsets: dict[Path, int],
    ) -> None:
        try:
            with path.open("rb") as stream:
                stream.seek(offsets[path])
                while True:
                    record_start = stream.tell()
                    raw_line = stream.readline()
                    if not raw_line:
                        break
                    if not raw_line.endswith(b"\n"):
                        offsets[path] = record_start
                        break
                    offsets[path] = stream.tell()
                    try:
                        record = json.loads(raw_line.decode("utf-8"))
                    except (UnicodeError, json.JSONDecodeError):
                        continue
                    if isinstance(record, dict) and record.get("type") in {
                        "avatarEnter",
                        "avatarExit",
                    }:
                        self.event_queue.put(("astron_event", record))
        except OSError:
            return


class ServerControlApp:
    def __init__(self, root_window: tk.Tk) -> None:
        self.root = root_window
        self.repo = repository_root()
        self.events: queue.Queue[tuple[object, ...]] = queue.Queue()
        self.processes = {
            "astron": ManagedProcess(ProcessSpec("astron", "Astron", "#55c7f3")),
            "uberdog": ManagedProcess(
                ProcessSpec("uberdog", "UberDOG", "#c792ea")
            ),
            "ai": ManagedProcess(ProcessSpec("ai", "AI District", "#7bd88f")),
        }
        self.rows: dict[str, dict[str, object]] = {}
        self.busy = False
        self.closing = False
        self.log_line_count = 0
        self.join_signals = 0
        self.leave_signals = 0
        self.estimated_online = 0
        self.active_avatars: dict[str, str] = {}
        self.ppython: Optional[ResolvedPython] = None
        self.ppython_error = ""
        self.event_log_tailer = AstronEventLogTailer(
            self.repo / "astron" / "logs",
            self.events,
        )

        try:
            self.ppython = resolve_ppython(self.repo)
        except RuntimeError as error:
            self.ppython_error = str(error)

        self._configure_window()
        self._build_ui()
        self._refresh_controls()
        self._write_system("Controller ready. Services are bound to localhost.")
        if self.ppython is not None:
            self._write_system(
                f"PPython: {self.ppython.path} ({self.ppython.source})"
            )
        else:
            self._write_system(self.ppython_error, level="error")
        self._write_system(
            "Player counts follow Astron avatarEnter/avatarExit JSON events; "
            "colored stdout phrase matches remain heuristic fallbacks."
        )

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.event_log_tailer.start()
        self.root.after(50, self._drain_events)
        self.root.after(500, self._poll_processes)

    def _configure_window(self) -> None:
        self.root.title(APP_TITLE)
        self.root.geometry("1120x720")
        self.root.minsize(850, 540)
        try:
            self.root.iconname("Server Control")
        except tk.TclError:
            pass
        style = ttk.Style(self.root)
        available = style.theme_names()
        if "vista" in available:
            style.theme_use("vista")
        elif "clam" in available:
            style.theme_use("clam")

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=10)
        outer.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        toolbar = ttk.Frame(outer)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.start_all_button = ttk.Button(
            toolbar, text="Start All", command=self.start_all
        )
        self.stop_all_button = ttk.Button(
            toolbar, text="Stop All", command=self.stop_all
        )
        self.restart_all_button = ttk.Button(
            toolbar, text="Restart All", command=self.restart_all
        )
        self.start_all_button.pack(side="left", padx=(0, 6))
        self.stop_all_button.pack(side="left", padx=(0, 6))
        self.restart_all_button.pack(side="left")

        ttk.Separator(toolbar, orient="vertical").pack(
            side="left", fill="y", padx=12
        )
        ttk.Label(toolbar, text="PPython:").pack(side="left")
        self.ppython_var = tk.StringVar(
            value=str(self.ppython.path)
            if self.ppython is not None
            else "Not configured — select ppython.exe"
        )
        ppython_entry = ttk.Entry(
            toolbar,
            textvariable=self.ppython_var,
            state="readonly",
            width=56,
        )
        ppython_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.browse_button = ttk.Button(
            toolbar, text="Browse…", command=self._browse_ppython
        )
        self.browse_button.pack(side="right")

        process_frame = ttk.LabelFrame(outer, text="Processes", padding=8)
        process_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        process_frame.columnconfigure(1, weight=1)
        ttk.Label(process_frame, text="Service").grid(
            row=0, column=0, sticky="w", padx=4
        )
        ttk.Label(process_frame, text="Status").grid(
            row=0, column=1, sticky="w", padx=4
        )
        ttk.Label(process_frame, text="PID").grid(
            row=0, column=2, sticky="w", padx=4
        )
        ttk.Label(process_frame, text="Controls").grid(
            row=0, column=3, sticky="w", padx=4
        )

        for row_number, key in enumerate(PROCESS_ORDER, start=1):
            managed = self.processes[key]
            state_var = tk.StringVar(value=managed.state)
            pid_var = tk.StringVar(value="—")
            name_label = tk.Label(
                process_frame,
                text=managed.spec.title,
                foreground=managed.spec.color,
                font=("Segoe UI", 9, "bold"),
                anchor="w",
            )
            name_label.grid(row=row_number, column=0, sticky="ew", padx=4, pady=3)
            ttk.Label(process_frame, textvariable=state_var).grid(
                row=row_number, column=1, sticky="w", padx=4
            )
            ttk.Label(process_frame, textvariable=pid_var, width=9).grid(
                row=row_number, column=2, sticky="w", padx=4
            )
            controls = ttk.Frame(process_frame)
            controls.grid(row=row_number, column=3, sticky="e")
            start_button = ttk.Button(
                controls,
                text="Start",
                width=8,
                command=lambda selected=key: self.start_component(selected),
            )
            stop_button = ttk.Button(
                controls,
                text="Stop",
                width=8,
                command=lambda selected=key: self.stop_component(selected),
            )
            restart_button = ttk.Button(
                controls,
                text="Restart",
                width=8,
                command=lambda selected=key: self.restart_component(selected),
            )
            start_button.pack(side="left", padx=2)
            stop_button.pack(side="left", padx=2)
            restart_button.pack(side="left", padx=2)
            self.rows[key] = {
                "state": state_var,
                "pid": pid_var,
                "start": start_button,
                "stop": stop_button,
                "restart": restart_button,
            }

        signal_frame = ttk.Frame(outer)
        signal_frame.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        self.player_signal_var = tk.StringVar()
        self.last_player_event_var = tk.StringVar(value="Last signal: none")
        self._update_player_signal_label()
        ttk.Label(
            signal_frame,
            textvariable=self.player_signal_var,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        ttk.Label(signal_frame, textvariable=self.last_player_event_var).pack(
            side="right"
        )

        log_frame = ttk.LabelFrame(outer, text="Merged server log", padding=4)
        log_frame.grid(row=3, column=0, sticky="nsew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_text = tk.Text(
            log_frame,
            wrap="none",
            state="disabled",
            bg="#12151a",
            fg="#d8dee9",
            insertbackground="#ffffff",
            selectbackground="#34536f",
            font=("Consolas", 9),
            undo=False,
        )
        y_scroll = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.log_text.yview
        )
        x_scroll = ttk.Scrollbar(
            log_frame, orient="horizontal", command=self.log_text.xview
        )
        self.log_text.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.log_text.tag_configure("timestamp", foreground="#697386")
        self.log_text.tag_configure("system", foreground="#ffd866")
        self.log_text.tag_configure("error", foreground="#ff6188")
        self.log_text.tag_configure("join", foreground="#a9dc76")
        self.log_text.tag_configure("leave", foreground="#fc9867")
        self.log_text.tag_configure("message", foreground="#d8dee9")
        for managed in self.processes.values():
            self.log_text.tag_configure(
                managed.spec.key,
                foreground=managed.spec.color,
            )

        footer = ttk.Frame(outer)
        footer.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        self.clear_button = ttk.Button(
            footer, text="Clear Log", command=self._clear_log
        )
        self.save_button = ttk.Button(
            footer, text="Save Log…", command=self._save_log
        )
        self.clear_button.pack(side="left")
        self.save_button.pack(side="left", padx=6)
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            footer,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
        ).pack(side="left", padx=10)
        self.operation_var = tk.StringVar(value="Idle")
        ttk.Label(footer, textvariable=self.operation_var).pack(side="right")

    def _browse_ppython(self) -> None:
        if any(managed.is_active() for managed in self.processes.values()):
            messagebox.showwarning(
                APP_TITLE,
                "Stop all services before changing the PPython executable.",
                parent=self.root,
            )
            return
        selected = filedialog.askopenfilename(
            parent=self.root,
            title="Select Panda3D PPython",
            initialdir=str(self.repo),
            filetypes=(
                ("Python executables", "ppython.exe python.exe"),
                ("Executables", "*.exe"),
                ("All files", "*.*"),
            ),
        )
        if not selected:
            return
        try:
            resolved = resolve_ppython(self.repo, Path(selected))
        except RuntimeError as error:
            messagebox.showerror(APP_TITLE, str(error), parent=self.root)
            return
        self.ppython = resolved
        self.ppython_error = ""
        self.ppython_var.set(str(resolved.path))
        self._write_system(
            f"Using PPython for this controller session: {resolved.path}"
        )
        self._refresh_controls()

    def _build_command(self, key: str) -> tuple[list[str], Path]:
        return build_process_command(
            self.repo,
            self.ppython,
            self.ppython_error,
            key,
        )

    def _preflight(self, keys: tuple[str, ...]) -> bool:
        if "astron" in keys and not self.processes["astron"].is_active():
            occupied_ports = [
                port
                for port, socket_type in (
                    (EVENT_LOGGER_PORT, socket.SOCK_DGRAM),
                    (7198, socket.SOCK_STREAM),
                    (MESSAGE_DIRECTOR_PORT, socket.SOCK_STREAM),
                )
                if not self._loopback_bind_available(port, socket_type)
            ]
            if occupied_ports:
                self._show_operation_error(
                    "Refusing to start a second Astron instance; localhost "
                    "port(s) are already occupied: "
                    + ", ".join(str(port) for port in occupied_ports)
                )
                return False
        try:
            for key in keys:
                self._build_command(key)
        except (OSError, RuntimeError, KeyError) as error:
            self._show_operation_error(str(error))
            return False
        return True

    def _start_one(self, key: str) -> bool:
        managed = self.processes[key]
        if managed.is_active():
            return True
        missing = [
            self.processes[dependency].spec.title
            for dependency in DEPENDENCIES[key]
            if not self.processes[dependency].is_active()
        ]
        if missing:
            self._show_operation_error(
                f"Cannot start {managed.spec.title}; required service(s) are "
                f"not running: {', '.join(missing)}."
            )
            return False

        try:
            command, working_directory = self._build_command(key)
            environment = os.environ.copy()
            previous_pythonpath = environment.get("PYTHONPATH", "")
            environment["PYTHONPATH"] = str(self.repo) + (
                os.pathsep + previous_pythonpath if previous_pythonpath else ""
            )
            environment["PYTHONUNBUFFERED"] = "1"
            environment["PYTHONIOENCODING"] = "utf-8"

            creation_flags = 0
            if os.name == "nt":
                creation_flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

            managed.generation += 1
            generation = managed.generation
            managed.ready_hint = False
            managed.intentional_stop = False
            managed.state = "Starting"
            self._update_process_row(key)
            process = subprocess.Popen(
                command,
                cwd=str(working_directory),
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                shell=False,
                creationflags=creation_flags,
            )
            managed.process = process
            self._update_process_row(key)
            self._write_system(
                f"Started {managed.spec.title} (PID {process.pid})."
            )
            self._write_system(
                f"{managed.spec.title} command: {subprocess.list2cmdline(command)}"
            )
            threading.Thread(
                target=self._read_process_output,
                args=(key, generation, process),
                name=f"{key}-log-reader",
                daemon=True,
            ).start()
            return True
        except (OSError, RuntimeError) as error:
            managed.process = None
            managed.state = "Start failed"
            self._update_process_row(key)
            self._show_operation_error(
                f"Could not start {managed.spec.title}: {error}"
            )
            return False

    def _read_process_output(
        self,
        key: str,
        generation: int,
        process: subprocess.Popen[str],
    ) -> None:
        try:
            if process.stdout is not None:
                for line in process.stdout:
                    self.events.put(("log", key, generation, line.rstrip("\r\n")))
        except (OSError, UnicodeError) as error:
            self.events.put(
                ("log", key, generation, f"[log reader error: {error}]")
            )
        finally:
            try:
                exit_code = process.wait()
            except OSError:
                exit_code = process.poll()
            self.events.put(("exit", key, generation, exit_code))

    def _start_sequence(
        self,
        keys: tuple[str, ...],
        finished: Callable[[bool], None],
        index: int = 0,
    ) -> None:
        if self.closing:
            finished(False)
            return
        if index >= len(keys):
            finished(True)
            return
        key = keys[index]
        managed = self.processes[key]
        if managed.is_active() and managed.state == "Running":
            self._start_sequence(keys, finished, index + 1)
            return
        if not managed.is_active() and not self._start_one(key):
            finished(False)
            return

        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS

        def check_ready() -> None:
            if self.closing:
                finished(False)
                return
            if not managed.is_active():
                self._show_operation_error(
                    f"{managed.spec.title} exited before it became ready."
                )
                finished(False)
                return

            if key == "astron":
                ready = self._localhost_port_open(MESSAGE_DIRECTOR_PORT)
            else:
                ready = managed.ready_hint

            if ready:
                managed.state = "Running"
                self._update_process_row(key)
                self._write_system(f"{managed.spec.title} is ready.")
                self._start_sequence(keys, finished, index + 1)
                return
            if time.monotonic() >= deadline:
                self._show_operation_error(
                    f"Timed out waiting for {managed.spec.title} to become ready."
                )
                finished(False)
                return
            self.root.after(150, check_ready)

        self.root.after(100, check_ready)

    @staticmethod
    def _localhost_port_open(port: int) -> bool:
        try:
            with socket.create_connection((LOCALHOST, port), timeout=0.15):
                return True
        except OSError:
            return False

    @staticmethod
    def _loopback_bind_available(port: int, socket_type: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket_type) as probe:
                if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                    probe.setsockopt(
                        socket.SOL_SOCKET,
                        socket.SO_EXCLUSIVEADDRUSE,
                        1,
                    )
                probe.bind((LOCALHOST, port))
                if socket_type == socket.SOCK_STREAM:
                    probe.listen(1)
                return True
        except OSError:
            return False

    def _request_stop(
        self,
        key: str,
        finished: Callable[[], None],
    ) -> None:
        managed = self.processes[key]
        process = managed.process
        if process is None or process.poll() is not None:
            managed.process = None
            managed.state = "Stopped"
            self._update_process_row(key)
            self.root.after(0, finished)
            return

        managed.intentional_stop = True
        managed.state = "Stopping"
        self._update_process_row(key)
        self._write_system(
            f"Stopping {managed.spec.title} (PID {process.pid})…"
        )
        try:
            if os.name == "nt" and hasattr(signal, "CTRL_BREAK_EVENT"):
                try:
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                except OSError:
                    process.terminate()
            else:
                process.terminate()
        except OSError as error:
            self._write_system(
                f"Stop signal for {managed.spec.title} failed: {error}",
                level="error",
            )

        deadline = time.monotonic() + STOP_TIMEOUT_SECONDS
        killed = False

        def check_stopped() -> None:
            nonlocal killed
            if process.poll() is not None:
                if managed.process is process:
                    managed.process = None
                    managed.state = "Stopped"
                    self._update_process_row(key)
                finished()
                return
            if time.monotonic() >= deadline and not killed:
                killed = True
                self._write_system(
                    f"{managed.spec.title} did not stop in time; terminating it.",
                    level="error",
                )
                try:
                    process.kill()
                except OSError:
                    pass
            self.root.after(120, check_stopped)

        self.root.after(120, check_stopped)

    def _stop_sequence(
        self,
        keys: tuple[str, ...],
        finished: Callable[[], None],
        index: int = 0,
    ) -> None:
        if index >= len(keys):
            finished()
            return
        self._request_stop(
            keys[index],
            lambda: self._stop_sequence(keys, finished, index + 1),
        )

    def _begin_operation(self, label: str) -> bool:
        if self.busy:
            self._write_system(
                f"Another operation is already running: {self.operation_var.get()}",
                level="error",
            )
            return False
        self.busy = True
        self.operation_var.set(label)
        self._refresh_controls()
        return True

    def _finish_operation(self, success: bool, label: str) -> None:
        if self.closing:
            return
        self.busy = False
        self.operation_var.set("Idle")
        self._refresh_controls()
        self._write_system(f"{label} {'completed' if success else 'stopped'}.")

    def start_all(self) -> None:
        if not self._preflight(PROCESS_ORDER):
            return
        if not self._begin_operation("Starting all"):
            return
        self._start_sequence(
            PROCESS_ORDER,
            lambda success: self._finish_operation(success, "Start All"),
        )

    def stop_all(self) -> None:
        if not self._begin_operation("Stopping all"):
            return

        def completed() -> None:
            self._reset_player_tracking("All services stopped.")
            self._finish_operation(True, "Stop All")

        self._stop_sequence(STOP_ORDER, completed)

    def restart_all(self) -> None:
        if not self._preflight(PROCESS_ORDER):
            return
        if not self._begin_operation("Restarting all"):
            return

        def stopped() -> None:
            self._reset_player_tracking("Services stopped for restart.")
            self._start_sequence(
                PROCESS_ORDER,
                lambda success: self._finish_operation(success, "Restart All"),
            )

        self._stop_sequence(STOP_ORDER, stopped)

    def start_component(self, key: str) -> None:
        keys = (key,)
        if not self._preflight(keys) or not self._begin_operation(
            f"Starting {self.processes[key].spec.title}"
        ):
            return
        self._start_sequence(
            keys,
            lambda success: self._finish_operation(
                success, f"Start {self.processes[key].spec.title}"
            ),
        )

    def stop_component(self, key: str) -> None:
        cascade = {
            "astron": ("ai", "uberdog", "astron"),
            "uberdog": ("ai", "uberdog"),
            "ai": ("ai",),
        }[key]
        if not self._begin_operation(
            f"Stopping {self.processes[key].spec.title}"
        ):
            return

        def stopped() -> None:
            if key in {"astron", "uberdog", "ai"}:
                self._reset_player_tracking(
                    f"{self.processes[key].spec.title} dependency chain stopped."
                )
            self._finish_operation(
                True, f"Stop {self.processes[key].spec.title}"
            )

        self._stop_sequence(
            cascade,
            stopped,
        )

    def restart_component(self, key: str) -> None:
        affected_start_order = {
            "astron": ("astron", "uberdog", "ai"),
            "uberdog": ("uberdog", "ai"),
            "ai": ("ai",),
        }[key]
        running_before = {
            name for name in affected_start_order if self.processes[name].is_active()
        }
        restart_keys = tuple(
            name
            for name in affected_start_order
            if name == key or name in running_before
        )
        stop_keys = tuple(reversed(restart_keys))
        if not self._preflight(restart_keys) or not self._begin_operation(
            f"Restarting {self.processes[key].spec.title}"
        ):
            return

        def stopped() -> None:
            self._start_sequence(
                restart_keys,
                lambda success: self._finish_operation(
                    success, f"Restart {self.processes[key].spec.title}"
                ),
            )

        self._stop_sequence(stop_keys, stopped)

    def _drain_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                event_type = event[0]
                if event_type == "log":
                    _, key, generation, line = event
                    managed = self.processes[str(key)]
                    if int(generation) != managed.generation:
                        continue
                    text_line = str(line)
                    ready_pattern = READY_PATTERNS.get(str(key))
                    if ready_pattern is not None and ready_pattern.search(text_line):
                        managed.ready_hint = True
                    self._append_process_log(str(key), text_line)
                elif event_type == "exit":
                    _, key, generation, exit_code = event
                    self._handle_process_exit(
                        str(key),
                        int(generation),
                        int(exit_code) if exit_code is not None else -1,
                    )
                elif event_type == "event_log_file":
                    _, path = event
                    self._write_system(f"Following Astron event log: {path}")
                elif event_type == "astron_event":
                    _, record = event
                    if isinstance(record, dict):
                        self._handle_astron_player_event(record)
        except queue.Empty:
            pass
        if not self.closing:
            self.root.after(50, self._drain_events)

    def _handle_process_exit(
        self,
        key: str,
        generation: int,
        exit_code: int,
    ) -> None:
        managed = self.processes[key]
        if generation != managed.generation:
            return
        if managed.process is None and (
            managed.state == "Stopped" or managed.state.startswith("Exited (")
        ):
            return
        managed.process = None
        if managed.intentional_stop:
            managed.state = "Stopped"
            self._write_system(
                f"{managed.spec.title} stopped (exit code {exit_code})."
            )
        else:
            managed.state = f"Exited ({exit_code})"
            self._write_system(
                f"{managed.spec.title} exited unexpectedly with code {exit_code}.",
                level="error",
            )
        if key in {"astron", "ai"} and self.active_avatars:
            self._reset_player_tracking(
                f"{managed.spec.title} exited; active-player tracking reset."
            )
        self._update_process_row(key)
        self._refresh_controls()

    def _poll_processes(self) -> None:
        for key, managed in self.processes.items():
            process = managed.process
            if process is not None and process.poll() is not None:
                self._handle_process_exit(
                    key,
                    managed.generation,
                    process.returncode if process.returncode is not None else -1,
                )
            else:
                self._update_process_row(key)
        if not self.closing:
            self.root.after(500, self._poll_processes)

    def _append_process_log(self, key: str, line: str) -> None:
        player_signal = (
            classify_player_signal(line) if key in {"uberdog", "ai"} else None
        )
        message_tag = "message"
        if player_signal == "join":
            message_tag = "join"
            self.last_player_event_var.set(
                f"Last fallback signal: possible JOIN from "
                f"{self.processes[key].spec.title}"
            )
        elif player_signal == "leave":
            message_tag = "leave"
            self.last_player_event_var.set(
                f"Last fallback signal: possible LEAVE from "
                f"{self.processes[key].spec.title}"
            )
        elif ERROR_PATTERN.search(line):
            message_tag = "error"
        self._insert_log(key, line, message_tag)

    def _handle_astron_player_event(self, record: dict[object, object]) -> None:
        event_type = str(record.get("type", ""))
        raw_avatar_id = record.get("_1")
        if raw_avatar_id is None:
            return
        avatar_id = str(raw_avatar_id)
        supplied_name = str(record.get("_2", "")).strip()

        if event_type == "avatarEnter":
            if avatar_id in self.active_avatars:
                if supplied_name:
                    self.active_avatars[avatar_id] = supplied_name
                return
            name = supplied_name or f"Avatar {avatar_id}"
            self.active_avatars[avatar_id] = name
            self.join_signals += 1
            self.estimated_online = len(self.active_avatars)
            self.last_player_event_var.set(
                f"Last event: JOIN {name} (avatar {avatar_id})"
            )
            self._insert_log(
                "system",
                f"PLAYER JOIN: {name} (avatar {avatar_id})",
                "join",
            )
            self._update_player_signal_label()
            return

        if event_type != "avatarExit":
            return
        # NPCs also emit avatarExit. Only an ID admitted by avatarEnter is a
        # tracked player and may produce a visible leave event.
        known_name = self.active_avatars.pop(avatar_id, None)
        if known_name is None:
            return
        name = supplied_name or known_name
        self.leave_signals += 1
        self.estimated_online = len(self.active_avatars)
        self.last_player_event_var.set(
            f"Last event: LEAVE {name} (avatar {avatar_id})"
        )
        self._insert_log(
            "system",
            f"PLAYER LEAVE: {name} (avatar {avatar_id})",
            "leave",
        )
        self._update_player_signal_label()

    def _write_system(self, message: str, level: str = "system") -> None:
        for line in str(message).splitlines() or [""]:
            self._insert_log("system", line, level)

    def _insert_log(self, source: str, message: str, message_tag: str) -> None:
        timestamp = dt.datetime.now().strftime("%H:%M:%S")
        source_title = (
            "Controller"
            if source == "system"
            else self.processes[source].spec.title
        )
        source_tag = "system" if source == "system" else source
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] ", "timestamp")
        self.log_text.insert("end", f"[{source_title}] ", source_tag)
        self.log_text.insert("end", message + "\n", message_tag)
        self.log_line_count += 1
        if self.log_line_count > MAX_LOG_LINES:
            self.log_text.delete("1.0", f"{LOG_TRIM_LINES + 1}.0")
            self.log_line_count -= LOG_TRIM_LINES
        self.log_text.configure(state="disabled")
        if self.auto_scroll_var.get():
            self.log_text.see("end")

    def _update_player_signal_label(self) -> None:
        self.player_signal_var.set(
            "Tracked player events: "
            f"{self.join_signals} join / {self.leave_signals} leave / "
            f"online now {self.estimated_online}"
        )

    def _reset_player_tracking(self, reason: str) -> None:
        self.active_avatars.clear()
        self.estimated_online = 0
        self.last_player_event_var.set("Last event: tracking reset")
        self._update_player_signal_label()
        self._write_system(reason)

    def _update_process_row(self, key: str) -> None:
        if key not in self.rows:
            return
        managed = self.processes[key]
        row = self.rows[key]
        state_var = row["state"]
        pid_var = row["pid"]
        assert isinstance(state_var, tk.StringVar)
        assert isinstance(pid_var, tk.StringVar)
        state_var.set(managed.state)
        pid_var.set(
            str(managed.process.pid)
            if managed.process is not None and managed.process.poll() is None
            else "—"
        )

    def _refresh_controls(self) -> None:
        any_active = any(
            managed.is_active() for managed in self.processes.values()
        )
        all_active = all(
            managed.is_active() for managed in self.processes.values()
        )
        if self.busy:
            global_start = global_stop = global_restart = "disabled"
        else:
            global_start = "disabled" if all_active else "normal"
            global_stop = "normal" if any_active else "disabled"
            global_restart = "normal" if any_active else "disabled"
        self.start_all_button.configure(state=global_start)
        self.stop_all_button.configure(state=global_stop)
        self.restart_all_button.configure(state=global_restart)
        self.browse_button.configure(
            state="disabled" if self.busy or any_active else "normal"
        )

        for key, row in self.rows.items():
            active = self.processes[key].is_active()
            if self.busy:
                start_state = stop_state = restart_state = "disabled"
            else:
                start_state = "disabled" if active else "normal"
                stop_state = "normal" if active else "disabled"
                restart_state = "normal" if active else "disabled"
            start_button = row["start"]
            stop_button = row["stop"]
            restart_button = row["restart"]
            assert isinstance(start_button, ttk.Button)
            assert isinstance(stop_button, ttk.Button)
            assert isinstance(restart_button, ttk.Button)
            start_button.configure(state=start_state)
            stop_button.configure(state=stop_state)
            restart_button.configure(state=restart_state)

    def _show_operation_error(self, message: str) -> None:
        self._write_system(message, level="error")
        if not self.closing:
            messagebox.showerror(APP_TITLE, message, parent=self.root)

    def _clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.log_line_count = 0
        self._write_system("Log cleared.")

    def _save_log(self) -> None:
        default_name = (
            "open-toontown-server-"
            + dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            + ".log"
        )
        selected = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save merged server log",
            initialdir=str(self.repo),
            initialfile=default_name,
            defaultextension=".log",
            filetypes=(("Log files", "*.log"), ("Text files", "*.txt")),
        )
        if not selected:
            return
        try:
            Path(selected).write_text(
                self.log_text.get("1.0", "end-1c") + "\n",
                encoding="utf-8",
            )
        except OSError as error:
            messagebox.showerror(
                APP_TITLE,
                f"Could not save the log:\n{error}",
                parent=self.root,
            )
            return
        self._write_system(f"Saved merged log to {selected}")

    def _on_close(self) -> None:
        active = any(managed.is_active() for managed in self.processes.values())
        if not active:
            self.closing = True
            self.event_log_tailer.stop()
            self.root.destroy()
            return
        if not messagebox.askyesno(
            APP_TITLE,
            "Server processes are still running. Stop all services and close?",
            parent=self.root,
        ):
            return
        self.closing = True
        self.busy = True
        self.operation_var.set("Stopping before close")
        self._refresh_controls()

        def finish_close() -> None:
            self.event_log_tailer.stop()
            self.root.destroy()

        self._stop_sequence(STOP_ORDER, finish_close)


class ConsoleOutputPump:
    """Copy one child stream to the self-test console and flag readiness."""

    def __init__(
        self,
        key: str,
        process: subprocess.Popen[str],
    ) -> None:
        self.key = key
        self.process = process
        self.ready = threading.Event()
        self.thread = threading.Thread(
            target=self._run,
            name=f"self-test-{key}-output",
            daemon=True,
        )

    def start(self) -> None:
        self.thread.start()

    def _run(self) -> None:
        stream = self.process.stdout
        if stream is None:
            return
        pattern = READY_PATTERNS[self.key]
        line_count = 0
        try:
            for line in stream:
                clean_line = line.rstrip("\r\n")
                line_count += 1
                if line_count <= SELF_TEST_LOG_LINE_LIMIT:
                    print(f"[{self.key}] {clean_line}", flush=True)
                elif line_count == SELF_TEST_LOG_LINE_LIMIT + 1:
                    print(
                        f"[{self.key}] further startup lines suppressed; "
                        "readiness scanning continues",
                        flush=True,
                    )
                if pattern.search(clean_line):
                    self.ready.set()
        except (OSError, UnicodeError) as error:
            print(f"[{self.key}] output reader error: {error}", file=sys.stderr)


def _child_environment(root: Path) -> dict[str, str]:
    environment = os.environ.copy()
    previous_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = str(root) + (
        os.pathsep + previous_pythonpath if previous_pythonpath else ""
    )
    environment["PYTHONUNBUFFERED"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    return environment


def _windows_creation_flags() -> int:
    if os.name != "nt":
        return 0
    return getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def _wait_for_self_test_ready(
    key: str,
    process: subprocess.Popen[str],
    pump: ConsoleOutputPump,
    timeout_seconds: float,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        exit_code = process.poll()
        if exit_code is not None:
            raise RuntimeError(
                f"{key} exited before readiness with code {exit_code}"
            )
        if key == "astron":
            ready = ServerControlApp._localhost_port_open(MESSAGE_DIRECTOR_PORT)
        else:
            ready = pump.ready.is_set()
        if ready:
            return
        time.sleep(0.1)
    raise RuntimeError(f"timed out waiting for {key} readiness")


def _stop_self_test_process(
    key: str,
    process: subprocess.Popen[str],
) -> None:
    if process.poll() is not None:
        print(f"[self-test] {key} already exited with code {process.returncode}")
        return
    print(f"[self-test] stopping {key} PID {process.pid}", flush=True)
    try:
        if os.name == "nt" and hasattr(signal, "CTRL_BREAK_EVENT"):
            try:
                process.send_signal(signal.CTRL_BREAK_EVENT)
            except OSError:
                process.terminate()
        else:
            process.terminate()
        process.wait(timeout=STOP_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2.0)
    except OSError as error:
        print(f"[self-test] stop error for {key}: {error}", file=sys.stderr)
        try:
            process.kill()
            process.wait(timeout=2.0)
        except (OSError, subprocess.TimeoutExpired):
            pass
    print(f"[self-test] {key} exit code {process.poll()}", flush=True)


def _wait_for_port_state(port: int, open_state: bool, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        observed = ServerControlApp._localhost_port_open(port)
        if observed == open_state:
            return True
        time.sleep(0.1)
    return False


def run_lifecycle_self_test(timeout_seconds: float) -> int:
    """Start, verify, and stop the complete stack without creating a GUI."""

    root = repository_root()
    print(f"[self-test] repository: {root}")
    if os.name != "nt":
        print("[self-test] Windows is required.", file=sys.stderr)
        return 2
    occupied = [
        port
        for port, socket_type in (
            (EVENT_LOGGER_PORT, socket.SOCK_DGRAM),
            (7198, socket.SOCK_STREAM),
            (MESSAGE_DIRECTOR_PORT, socket.SOCK_STREAM),
        )
        if not ServerControlApp._loopback_bind_available(port, socket_type)
    ]
    if occupied:
        print(
            "[self-test] refusing to disturb an existing service; localhost "
            f"port(s) already open: {', '.join(map(str, occupied))}",
            file=sys.stderr,
        )
        return 2

    try:
        ppython = resolve_ppython(root)
        commands = {
            key: build_process_command(root, ppython, "", key)
            for key in PROCESS_ORDER
        }
    except (OSError, RuntimeError, KeyError) as error:
        print(f"[self-test] preflight failed: {error}", file=sys.stderr)
        return 2

    print(f"[self-test] PPython: {ppython.path} ({ppython.source})")
    processes: dict[str, subprocess.Popen[str]] = {}
    failure: Optional[str] = None
    environment = _child_environment(root)
    creation_flags = _windows_creation_flags()

    try:
        for key in PROCESS_ORDER:
            command, working_directory = commands[key]
            print(
                f"[self-test] starting {key}: "
                f"{subprocess.list2cmdline(command)}",
                flush=True,
            )
            process = subprocess.Popen(
                command,
                cwd=str(working_directory),
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                shell=False,
                creationflags=creation_flags,
            )
            processes[key] = process
            pump = ConsoleOutputPump(key, process)
            pump.start()
            _wait_for_self_test_ready(
                key,
                process,
                pump,
                timeout_seconds,
            )
            print(f"[self-test] {key} ready, PID {process.pid}", flush=True)

        pids = [process.pid for process in processes.values()]
        if len(set(pids)) != len(PROCESS_ORDER) or any(pid <= 0 for pid in pids):
            raise RuntimeError(f"invalid or duplicate process IDs: {pids}")
        if not _wait_for_port_state(7198, True, 3.0):
            raise RuntimeError("localhost client-agent port 7198 did not open")
        if not ServerControlApp._localhost_port_open(MESSAGE_DIRECTOR_PORT):
            raise RuntimeError("localhost message-director port 7199 is not open")
        print(
            "[self-test] verified unique PIDs and localhost TCP ports 7198/7199",
            flush=True,
        )
    except (OSError, RuntimeError) as error:
        failure = str(error)
        print(f"[self-test] FAIL: {failure}", file=sys.stderr, flush=True)
    finally:
        for key in STOP_ORDER:
            process = processes.get(key)
            if process is not None:
                _stop_self_test_process(key, process)

    if not _wait_for_port_state(MESSAGE_DIRECTOR_PORT, False, 4.0):
        failure = failure or "localhost message-director port 7199 stayed open"
    if not _wait_for_port_state(7198, False, 4.0):
        failure = failure or "localhost client-agent port 7198 stayed open"
    if any(process.poll() is None for process in processes.values()):
        failure = failure or "one or more self-test child processes remained alive"

    if failure is not None:
        print(f"[self-test] lifecycle result: FAIL ({failure})", file=sys.stderr)
        return 1
    print(
        "[self-test] lifecycle PASS: Astron -> UberDOG -> AI started; "
        "AI -> UberDOG -> Astron stopped.",
        flush=True,
    )
    return 0


def parse_arguments(arguments: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run a non-GUI ordered lifecycle smoke test, then stop every "
            "process started by the test"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=45.0,
        help="per-service self-test readiness timeout in seconds (default: 45)",
    )
    return parser.parse_args(arguments)


def main(arguments: Optional[list[str]] = None) -> int:
    options = parse_arguments(arguments)
    if options.self_test:
        return run_lifecycle_self_test(max(5.0, float(options.timeout)))
    if os.name != "nt":
        print(
            "This controller is intended for the repository's Windows server "
            "executables.",
            file=sys.stderr,
        )
    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(f"Unable to create the Tkinter window: {error}", file=sys.stderr)
        return 1
    ServerControlApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
