# Windows local server controller

`tools/server_gui.py` is a standalone Tkinter controller for the existing local
server programs. It does not modify Astron, UberDOG, AI, or game code, and it
does not download runtimes or resources.

## Launch

Double-click:

```text
win32\start_server_gui.bat
```

The launcher needs an existing Python 3 installation with Tkinter. It first
tries the Windows `py` launcher and `python.exe`, then the executable recorded in
`PPYTHON_PATH`.

The services still require the project's compatible Panda3D PPython runtime.
`PPYTHON_PATH` may contain one quoted or unquoted executable path:

```text
"C:\Panda3D-1.11.0-x64\python\ppython.exe"
```

The GUI strips surrounding quotes, expands environment variables, resolves
relative paths from the repository root, and verifies the file. An environment
variable named `PPYTHON_PATH` takes precedence. **Browse** selects a session-only
override and does not rewrite the repository file.

If an absolute path became stale after moving the local bundle, the controller
also checks these constrained sibling layouts:

```text
<bundle>\game                         (this repository)
<bundle>\runtime\Panda3D-*\python\ppython.exe
```

It also recognizes the development layout with `Panda3D-*` directly beside the
repository. It reports a missing runtime rather than downloading or silently
substituting one.

## Controls

- **Start All** launches Astron, waits for the local message-director port, then
  launches UberDOG and AI in dependency order. UberDOG and AI are not marked
  Running until their explicit ready log records appear.
- **Stop All** stops AI, UberDOG, then Astron.
- **Restart All** performs both sequences.
- Each service has Start, Stop, and Restart buttons. Stopping a dependency also
  stops its dependents; restarting it restores dependents that were running.
- Each row shows current state and PID.
- The merged live log tags Astron, UberDOG, and AI with different colors.
- **Clear Log** clears the visible buffer; **Save Log** writes the visible
  merged buffer as UTF-8.

Player counts follow new `avatarEnter` and `avatarExit` JSON records appended to
`astron\logs\events-*.log`. The controller tracks avatar IDs observed entering
and displays an exit only for an ID in that set. This prevents NPC `avatarExit`
records from appearing as player departures. The current count covers events
observed during the controller session, not a database query.

Common connection phrases in UberDOG/AI stdout are still color-highlighted as
heuristic fallback signals, but they do not change the tracked count.

## Local-only behavior

The controller passes `127.0.0.1:7199` for the message director and
`127.0.0.1:7197` for the event logger. Before launching Astron, it verifies that
declared ports 7197, 7198, and 7199 all use loopback bind addresses; it refuses
an external bind. It also refuses to launch a second Astron instance when any
of those local ports is already occupied. Do not expose this development stack
to the Internet without a separate security design.

Astron's configured database and all other prerequisites must already be
available. The controller manages only:

1. `astron\win32\astrond.exe`
2. `toontown.uberdog.UDStart`
3. `toontown.ai.AIStart`

UberDOG and AI install a Windows break handler that exits through Python's
normal exception unwinding. If any service does not stop after a Windows break
request, the controller terminates it after six seconds. Keep development
database backups.

## Non-GUI lifecycle self-test

Run this only when no local server is already active:

```bat
win32\start_server_gui.bat --self-test
```

The self-test refuses to run if localhost port 7198 or 7199 is occupied. It:

1. starts Astron and waits for message-director readiness;
2. starts UberDOG and waits for its explicit ready log;
3. starts AI and waits for its explicit repository-ready log;
4. verifies three unique live PIDs and localhost ports 7198/7199;
5. always stops AI, UberDOG, and Astron in reverse order, including after a
   failure;
6. verifies child processes exited and both TCP ports closed.

The default readiness timeout is 45 seconds per service. Override it for a slow
machine:

```bat
win32\start_server_gui.bat --self-test --timeout 90
```

## Direct launch and troubleshooting

From a command prompt with a suitable standard Python:

```bat
python tools\server_gui.py
```

If the GUI cannot start, verify:

```bat
python -c "import tkinter"
```

If the GUI starts but UberDOG/AI cannot start, use **Browse** to select the
compatible `ppython.exe` and confirm resources and Astron prerequisites were set
up independently. Saved logs include each exact argument list without invoking
a command shell.
