"""Capture benign Ubuntu ground truth for RQ1 fidelity (offline lab).

Uses a clean Ubuntu-24.04 WSL distro (not the Cowrie WSL). Writes:
  data/test_set/sessions.jsonl
  data/test_set/ground_truth.jsonl

Does not invent attack sequences. Commands are Magazov-style shell checks
(files, users, processes, local network, system info).
"""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "test_set"
SESSIONS_PATH = OUT_DIR / "sessions.jsonl"
TRUTH_PATH = OUT_DIR / "ground_truth.jsonl"
DISTRO = "Ubuntu-24.04"
USER = "ubuntu"
HOME = "/home/ubuntu"


def _plan() -> list[tuple[str, list[str]]]:
    """About 20 sessions / about 200 benign commands."""
    return [
        (
            "gt-s01-identity",
            [
                "whoami",
                "id",
                "pwd",
                "hostname",
                "uname -a",
                "uname -r",
                "groups",
                "echo $HOME",
                "echo $USER",
                "date",
            ],
        ),
        (
            "gt-s02-home-files",
            [
                "pwd",
                "ls",
                "ls -la",
                "ls -a",
                "touch notes.txt",
                "ls",
                "cat notes.txt",
                "echo hello > notes.txt",
                "cat notes.txt",
                "rm notes.txt",
            ],
        ),
        (
            "gt-s03-system-info",
            [
                "cat /etc/os-release",
                "cat /etc/hostname",
                "getent passwd ubuntu",
                "nproc",
                "free -h",
                "df -h",
                "uptime",
                "cat /proc/version",
                "head -n 5 /proc/cpuinfo",
                "cat /proc/uptime",
            ],
        ),
        (
            "gt-s04-paths",
            [
                "which bash",
                "which ls",
                "type pwd",
                "command -v python3",
                "ls /bin | head -n 10",
                "ls /usr/bin | head -n 10",
                "ls /tmp",
                "ls /var",
                "ls /etc | head -n 15",
                "readlink -f /bin/bash",
            ],
        ),
        (
            "gt-s05-navigation",
            [
                "pwd",
                "cd /tmp",
                "pwd",
                "ls",
                "cd /home",
                "pwd",
                "cd /home/ubuntu",
                "pwd",
                "cd /",
                "pwd",
            ],
        ),
        (
            "gt-s06-tmp-lab",
            [
                "mkdir -p /tmp/gt_lab",
                "cd /tmp/gt_lab",
                "pwd",
                "touch a.txt b.txt",
                "ls",
                "echo hello > a.txt",
                "cat a.txt",
                "cp a.txt c.txt",
                "ls",
                "rm -rf /tmp/gt_lab",
            ],
        ),
        (
            "gt-s07-processes",
            [
                "ps",
                "ps aux | head -n 10",
                "pgrep -a bash | head -n 5",
                "echo $$",
                "head -n 5 /proc/self/status",
                "ls /proc | head -n 15",
                "top -bn1 | head -n 8",
                "w",
                "who",
                "users",
            ],
        ),
        (
            "gt-s08-environment",
            [
                "env | head -n 20",
                "printenv PATH",
                "printenv HOME",
                "printenv SHELL",
                "locale | head -n 10",
                "echo $PATH",
                "echo $SHELL",
                "umask",
                "pwd",
                "echo $PWD",
            ],
        ),
        (
            "gt-s09-local-net",
            [
                "hostname -s",
                "hostname -f",
                "cat /etc/hosts",
                "cat /etc/resolv.conf",
                "ip -br addr",
                "ip link | head -n 20",
                "ping -c 1 127.0.0.1",
                "getent hosts localhost",
                "ss -lnt | head -n 15",
                "cat /etc/nsswitch.conf | head -n 15",
            ],
        ),
        (
            "gt-s10-users",
            [
                "whoami",
                "id -u",
                "id -g",
                "id -un",
                "id -gn",
                "groups",
                "getent group ubuntu",
                "ls /home",
                "ls -la /home/ubuntu",
                "head -n 5 /etc/group",
            ],
        ),
        (
            "gt-s11-text-utils",
            [
                "echo hello world",
                "printf 'a\\nb\\n'",
                "echo -n test; echo",
                "seq 1 5",
                "wc -l /etc/hostname",
                "head -n 2 /etc/os-release",
                "tail -n 2 /etc/os-release",
                "printf 'b\\na\\n' | sort",
                "printf 'a\\na\\nb\\n' | uniq",
                "tr a-z A-Z <<< 'ubuntu'",
            ],
        ),
        (
            "gt-s12-file-meta",
            [
                "touch /tmp/gt_meta",
                "ls -l /tmp/gt_meta",
                "stat /tmp/gt_meta",
                "file /tmp/gt_meta",
                "wc /tmp/gt_meta",
                "chmod 644 /tmp/gt_meta",
                "ls -l /tmp/gt_meta",
                "mkdir /tmp/gt_dir",
                "ls -ld /tmp/gt_dir",
                "rm -rf /tmp/gt_meta /tmp/gt_dir",
            ],
        ),
        (
            "gt-s13-shell-builtins",
            [
                "pwd",
                "echo test",
                "printf '%s\\n' ok",
                "true",
                "false",
                ":",
                "type ls",
                "builtin pwd",
                "command -v ls",
                "help | head -n 5",
            ],
        ),
        (
            "gt-s14-disk-memory",
            [
                "df",
                "df -h /",
                "du -sh /home/ubuntu",
                "du -sh /tmp",
                "free",
                "free -m",
                "mount | head -n 8",
                "findmnt | head -n 8",
                "sync",
                "df -h | head -n 5",
            ],
        ),
        (
            "gt-s15-time",
            [
                "date",
                "date -u",
                "date +%Y-%m-%d",
                "date +%s",
                "cal",
                "sleep 0",
                "touch /tmp/gt_t",
                "stat /tmp/gt_t | head -n 8",
                "rm /tmp/gt_t",
                "date '+%Y-%m-%d %H:%M:%S'",
            ],
        ),
        (
            "gt-s16-search-list",
            [
                "ls /etc/*.conf 2>/dev/null | head -n 15",
                "find /tmp -maxdepth 1 | head -n 15",
                "find /home/ubuntu -maxdepth 1",
                "ls -1 /usr | head -n 15",
                "ls /lib | head -n 10",
                "basename /home/ubuntu/notes",
                "dirname /home/ubuntu/notes",
                "realpath .",
                "realpath /tmp",
                "readlink /proc/self/cwd",
            ],
        ),
        (
            "gt-s17-lab-home",
            [
                "mkdir -p ~/lab1/sub",
                "cd ~/lab1",
                "pwd",
                "touch f1 f2",
                "ls",
                "echo x > f1",
                "cat f1",
                "mv f1 f1b",
                "ls",
                "cd ~",
            ],
        ),
        (
            "gt-s18-lab-tree",
            [
                "cd /tmp",
                "mkdir -p gt_tree/a/b",
                "cd gt_tree",
                "pwd",
                "touch a/b/c.txt",
                "find .",
                "cat a/b/c.txt",
                "cd /",
                "pwd",
                "rm -rf /tmp/gt_tree",
            ],
        ),
        (
            "gt-s19-kernel-readonly",
            [
                "uname -m",
                "uname -n",
                "uname -s",
                "uname -v",
                "head -n 5 /proc/meminfo",
                "cat /proc/loadavg",
                "cat /proc/uptime",
                "ls /sys/class/net",
                "cat /sys/class/net/lo/operstate",
                "cat /proc/sys/kernel/hostname",
            ],
        ),
        (
            "gt-s20-wrapup",
            [
                "whoami",
                "pwd",
                "hostname",
                "uname -a",
                "ls ~",
                "df -h | head -n 5",
                "free -h",
                "date",
                "id",
                "echo done",
            ],
        ),
    ]


def _events_for(command: str, cwd: str) -> list[dict]:
    """Best-effort structured events for simple verbs (matches SessionMemory)."""
    if any(ch in command for ch in ";&|`$()<>\n"):
        return []
    parts = command.split()
    if len(parts) < 2:
        return []
    verb, *args = parts
    out: list[dict] = []
    if verb == "cd" and len(args) == 1:
        target = args[0]
        if target == "~":
            path = HOME
        elif target.startswith("~/"):
            path = HOME + "/" + target[2:]
        elif target.startswith("/"):
            path = target
        else:
            path = cwd.rstrip("/") + "/" + target
        out.append({"type": "set_cwd", "path": path})
    elif verb in {"mkdir", "touch"}:
        for arg in args:
            if arg.startswith("-"):
                continue
            if arg.startswith("~/"):
                path = HOME + "/" + arg[2:]
            elif arg.startswith("/"):
                path = arg
            else:
                path = cwd.rstrip("/") + "/" + arg
            # mkdir -p path may include parents; record leaf path only
            out.append({"type": "file_created", "path": path})
    elif verb == "rm":
        for arg in args:
            if arg.startswith("-"):
                continue
            if arg.startswith("/"):
                path = arg
            elif arg.startswith("~/"):
                path = HOME + "/" + arg[2:]
            else:
                path = cwd.rstrip("/") + "/" + arg
            out.append({"type": "file_deleted", "path": path})
    return out


def _runner_script() -> str:
    # Runs inside Ubuntu-24.04 as user ubuntu. Emits one JSON object per line.
    return r'''
import json, os, subprocess, sys

plan_path = sys.argv[1]
out_path = sys.argv[2]
with open(plan_path, encoding="utf-8") as fh:
    plan = json.load(fh)

def resolve_cd(before, target):
    if target == "~":
        return "/home/ubuntu"
    if target.startswith("~/"):
        return os.path.normpath("/home/ubuntu/" + target[2:])
    if target.startswith("/"):
        return os.path.normpath(target)
    return os.path.normpath(os.path.join(before, target))

rows = []
for session_id, commands in plan:
    cwd = "/home/ubuntu"
    env = os.environ.copy()
    env["HOME"] = "/home/ubuntu"
    env["USER"] = "ubuntu"
    env["LOGNAME"] = "ubuntu"
    env["SHELL"] = "/bin/bash"
    env["PWD"] = cwd
    for step, command in enumerate(commands, start=1):
        before = cwd
        # If prior step deleted the directory, fall back to home.
        run_cwd = before if os.path.isdir(before) else "/home/ubuntu"
        env["PWD"] = run_cwd
        proc = subprocess.run(
            ["bash", "-c", command],
            cwd=run_cwd,
            env=env,
            capture_output=True,
            text=True,
        )
        # bash -c is a subshell; re-apply simple cd for session continuity.
        parts = command.split()
        if (
            parts
            and parts[0] == "cd"
            and len(parts) == 2
            and all(c not in command for c in ";&|`$()<>")
        ):
            candidate = resolve_cd(run_cwd, parts[1])
            cwd = candidate if os.path.isdir(candidate) else run_cwd
        else:
            cwd = run_cwd if os.path.isdir(run_cwd) else "/home/ubuntu"
        env["PWD"] = cwd
        rows.append({
            "session_id": session_id,
            "step": step,
            "command": command,
            "cwd": before,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "exit_code": int(proc.returncode),
        })

with open(out_path, "w", encoding="utf-8") as fh:
    for row in rows:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
print(f"captured_rows={len(rows)}")
'''


def _wsl_path(windows_path: Path) -> str:
    abs_path = windows_path.resolve()
    drive = abs_path.drive.rstrip(":").lower()
    rest = abs_path.as_posix()[len(abs_path.drive) :]
    return f"/mnt/{drive}{rest}"


def main() -> int:
    plan = _plan()
    n_sessions = len(plan)
    n_commands = sum(len(cmds) for _, cmds in plan)
    print(f"plan_sessions={n_sessions} plan_commands={n_commands}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    work = OUT_DIR / "_capture_work"
    work.mkdir(parents=True, exist_ok=True)
    plan_file = work / "plan.json"
    raw_file = work / "raw_capture.jsonl"
    runner_file = work / "runner.py"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    runner_file.write_text(_runner_script(), encoding="utf-8")

    # Clean leftover lab paths from prior attempts (as ubuntu).
    subprocess.run(
        [
            "wsl",
            "-d",
            DISTRO,
            "-u",
            USER,
            "--",
            "bash",
            "-lc",
            "rm -rf ~/lab1 /tmp/gt_lab /tmp/gt_tree /tmp/gt_meta /tmp/gt_dir /tmp/gt_t ~/notes.txt 2>/dev/null; true",
        ],
        check=False,
    )

    cmd = [
        "wsl",
        "-d",
        DISTRO,
        "-u",
        USER,
        "--cd",
        HOME,
        "--",
        "python3",
        _wsl_path(runner_file),
        _wsl_path(plan_file),
        _wsl_path(raw_file),
    ]
    print("running:", " ".join(shlex.quote(c) for c in cmd))
    completed = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    if completed.returncode != 0:
        print(f"capture failed with exit {completed.returncode}")
        return completed.returncode

    if not raw_file.is_file():
        print("raw capture missing")
        return 2

    session_rows: list[dict] = []
    truth_rows: list[dict] = []
    for line in raw_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cwd = row["cwd"]
        command = row["command"]
        session_rows.append(
            {
                "session_id": row["session_id"],
                "step": row["step"],
                "command": command,
                "cwd": cwd,
                "technique_label": "benign-shell-check",
                "events": _events_for(command, cwd),
            }
        )
        truth_rows.append(
            {
                "session_id": row["session_id"],
                "step": row["step"],
                "stdout": row.get("stdout") or "",
                "stderr": row.get("stderr") or "",
                "exit_code": int(row.get("exit_code") or 0),
                "split": "test",
            }
        )

    SESSIONS_PATH.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in session_rows) + "\n",
        encoding="utf-8",
    )
    TRUTH_PATH.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in truth_rows) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {SESSIONS_PATH} rows={len(session_rows)}")
    print(f"wrote {TRUTH_PATH} rows={len(truth_rows)}")
    print(f"unique_sessions={len({r['session_id'] for r in session_rows})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
