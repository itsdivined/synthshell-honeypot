"""Lab tests. They do not call the network and they do not print session text."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analyse import summarise
from src.backends import Backend, Reply, build_backends, build_openai_body
from src.config import SYSTEMS, LabConfig
from src.containment import passed, audit
from src.corpus import load_sessions
from src.fixed_replies import fixed_reply
from src.replay import run_replay
from src.screen import classify
from src.session_memory import SessionMemory


class SessionMemoryTests(unittest.TestCase):
    def test_structured_update_does_not_touch_the_process_cwd(self) -> None:
        before = os.getcwd()
        memory = SessionMemory()
        memory.apply({"type": "set_cwd", "path": "/var/www"})
        memory.apply({"type": "file_created", "path": "/var/www/index.html"})
        memory.apply({"type": "file_changed", "path": "/var/www/index.html"})
        memory.apply({"type": "user_added", "name": "deploy"})
        memory.apply({"type": "file_deleted", "path": "/var/www/index.html"})
        self.assertEqual(os.getcwd(), before)
        self.assertEqual(memory.cwd, "/var/www")
        self.assertEqual(memory.files_deleted, ["/var/www/index.html"])
        self.assertEqual(memory.users_added, ["deploy"])
        self.assertIn("cwd: /var/www", memory.render())

    def test_rejects_command_records(self) -> None:
        memory = SessionMemory()
        with self.assertRaises(ValueError):
            memory.apply({"type": "set_cwd", "path": "/tmp", "command": "pwd"})

    def test_simple_command_updates_memory_only(self) -> None:
        before = os.getcwd()
        memory = SessionMemory(cwd="/var/www")
        memory.note_simple_command("mkdir html")
        memory.note_simple_command("cd /var/www && rm html")
        self.assertEqual(os.getcwd(), before)
        self.assertEqual(memory.cwd, "/var/www")
        self.assertEqual(memory.files_created, ["/var/www/html"])


class ContainmentTests(unittest.TestCase):
    def test_default_config_passes(self) -> None:
        self.assertTrue(passed(audit(LabConfig())))

    def test_public_bind_fails(self) -> None:
        checks = audit(LabConfig(listen_host="0.0.0.0"))
        self.assertFalse(passed(checks))


class BackendContractTests(unittest.TestCase):
    def test_four_systems_stay_in_order(self) -> None:
        names = [item.system for item in build_backends(LabConfig())]
        self.assertEqual(tuple(names), SYSTEMS)

    def test_openai_body_has_no_tools(self) -> None:
        body = build_openai_body("gpt-4o-mini", 0.0, "pwd")
        self.assertNotIn("tools", body)
        self.assertNotIn("functions", body)

    def test_fixed_denial_covers_the_two_plan_categories(self) -> None:
        self.assertIsNotNone(fixed_reply("sudo"))
        self.assertIsNotNone(fixed_reply("cat /etc/shadow"))
        self.assertIsNone(fixed_reply("pwd"))


class ReplayTests(unittest.TestCase):
    def test_same_sessions_record_a_skip_without_dropping_a_system(self) -> None:
        records = [
            {
                "session_id": "s",
                "step": 1,
                "command": "pwd",
                "cwd": "/home/ubuntu",
                "events": [],
                "technique_label": "",
            }
        ]

        class Fake(Backend):
            def __init__(self, system: str, skip: str | None) -> None:
                super().__init__(system=system)
                self._skip = skip

            def prepare(self):
                return self._skip

            def reply(self, **kwargs):
                return Reply(text="/home/ubuntu", delay_seconds=0.01, status="ok")

        fakes = [
            Fake("cowrie", None),
            Fake("gpt-4o-mini", "missing key"),
            Fake("llama-3.1-8b", None),
            Fake("qwen-2.5-7b", None),
        ]
        import src.replay as replay_module

        original = replay_module.build_backends
        replay_module.build_backends = lambda config: fakes
        try:
            with tempfile.TemporaryDirectory() as tmp:
                log_path = Path(tmp) / "replay.jsonl"
                summary = run_replay(
                    records,
                    config=LabConfig(),
                    log_path=log_path,
                    runs=1,
                    temperature=0.0,
                    history_window=10,
                    source_name="unit",
                )
                rows = [
                    json.loads(line)
                    for line in log_path.read_text(encoding="utf-8").splitlines()
                    if json.loads(line).get("record_type") == "command"
                ]
        finally:
            replay_module.build_backends = original

        self.assertEqual([row["system"] for row in rows], list(SYSTEMS))
        self.assertEqual(summary["counts"]["gpt-4o-mini"]["skipped"], 1)
        self.assertEqual(summary["counts"]["cowrie"]["ok"], 1)
        self.assertFalse(summary["study_complete"])
        table = summarise(rows)
        self.assertEqual([item["system"] for item in table["systems"]], list(SYSTEMS))
        self.assertTrue(table["rq4_containment"]["passed"])

    def test_replay_refuses_a_public_bind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                run_replay(
                    [
                        {
                            "session_id": "s",
                            "step": 1,
                            "command": "pwd",
                            "cwd": "/tmp",
                            "events": [],
                            "technique_label": "",
                        }
                    ],
                    config=LabConfig(listen_host="0.0.0.0"),
                    log_path=Path(tmp) / "replay.jsonl",
                    runs=1,
                    temperature=0.0,
                    history_window=5,
                    source_name="unit",
                )


class CorpusTests(unittest.TestCase):
    def test_loader_keeps_archive_order_and_honours_the_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.zip"
            line_a = json.dumps(
                {"session_id": "a", "command": "pwd", "cwd": "/home/ubuntu", "ts": "1"}
            )
            line_b = json.dumps(
                {"session_id": "b", "command": "ls", "cwd": "/home/ubuntu", "ts": "2"}
            )
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("data/adaptive/example/commands-one.jsonl", line_a + "\n" + line_b + "\n")
            capped = load_sessions(path, max_sessions=1)
            self.assertEqual(len(capped), 1)
            self.assertEqual(capped[0]["session_id"], "a")


class ScreenTests(unittest.TestCase):
    def test_placeholder_range_is_not_a_review_address(self) -> None:
        self.assertEqual(classify("198.51.100.10"), "author_placeholder")
        self.assertEqual(classify("127.0.0.1"), "reserved_or_private")
        self.assertEqual(classify("8.8.8.8"), "needs_review")


if __name__ == "__main__":
    unittest.main()
