import contextlib
import importlib.machinery
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


def _load_conductor_module():
    # bin/conductor is an executable Python script without a .py extension.
    conductor_path = Path(__file__).resolve().parents[1] / "bin" / "conductor"
    loader = importlib.machinery.SourceFileLoader("conductor_cli", str(conductor_path))
    spec = importlib.util.spec_from_loader("conductor_cli", loader)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CONDUCTOR = _load_conductor_module()


def run_cli(args):
    out = io.StringIO()
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = CONDUCTOR.main(args)
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    return int(rc), out.getvalue(), err.getvalue()


class TestMemoryAppend(unittest.TestCase):
    def test_memory_append_happy_path_creates_transcript_and_state(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            track_id = "t1"
            (repo / ".conductor" / "tracks" / track_id).mkdir(parents=True)

            event = {
                "event_type": "message",
                "role": "user",
                "content": {"format": "text", "text": "hello"},
            }
            event_path = repo / "event.json"
            event_path.write_text(json.dumps(event), encoding="utf-8")

            rc, stdout, stderr = run_cli(
                [
                    "memory",
                    "append",
                    "--repo-root",
                    str(repo),
                    "--track-id",
                    track_id,
                    "--event-file",
                    str(event_path),
                ]
            )

            self.assertEqual(rc, 0, msg=(stdout, stderr))
            self.assertIn("OK memory append", stdout)
            self.assertEqual("", stderr)

            transcript_path = (
                repo
                / ".conductor"
                / "tracks"
                / track_id
                / "memory"
                / "transcript.jsonl"
            )
            state_path = (
                repo / ".conductor" / "tracks" / track_id / "memory" / "state.json"
            )
            self.assertTrue(transcript_path.exists())
            self.assertTrue(state_path.exists())

            lines = transcript_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            persisted = json.loads(lines[0])
            self.assertEqual(persisted["schema_version"], 1)
            self.assertEqual(persisted["track_id"], track_id)
            self.assertEqual(persisted["seq"], 1)
            self.assertEqual(persisted["event_type"], "message")

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["schema_version"], 1)
            self.assertEqual(state["next_seq"], 2)

    def test_memory_append_invalid_json_returns_11(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            track_id = "t1"
            (repo / ".conductor" / "tracks" / track_id).mkdir(parents=True)

            bad_path = repo / "event.json"
            bad_path.write_text("{", encoding="utf-8")

            rc, stdout, stderr = run_cli(
                [
                    "memory",
                    "append",
                    "--repo-root",
                    str(repo),
                    "--track-id",
                    track_id,
                    "--event-file",
                    str(bad_path),
                ]
            )

            self.assertEqual(rc, 11, msg=(stdout, stderr))
            self.assertIn("ERROR", stderr)

    def test_memory_append_missing_track_returns_12(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            track_id = "t_missing"
            (repo / ".conductor" / "tracks").mkdir(parents=True)

            event = {
                "event_type": "message",
                "role": "user",
                "content": {"format": "text", "text": "hello"},
            }
            event_path = repo / "event.json"
            event_path.write_text(json.dumps(event), encoding="utf-8")

            rc, stdout, stderr = run_cli(
                [
                    "memory",
                    "append",
                    "--repo-root",
                    str(repo),
                    "--track-id",
                    track_id,
                    "--event-file",
                    str(event_path),
                ]
            )

            self.assertEqual(rc, 12, msg=(stdout, stderr))
            self.assertIn("ERROR", stderr)


class TestDependencyUX(unittest.TestCase):
    def test_memory_db_up_when_docker_missing_prints_instructions_and_exits_20(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / ".conductor" / "memory").mkdir(parents=True)

            # Monkeypatch conductor's executable lookup to simulate missing docker.
            orig_which = getattr(CONDUCTOR, "_which", None)
            self.assertIsNotNone(orig_which)
            CONDUCTOR._which = lambda _name: None  # type: ignore[assignment]
            try:
                rc, stdout, stderr = run_cli(
                    ["memory", "db", "up", "--repo-root", str(repo)]
                )
            finally:
                CONDUCTOR._which = orig_which  # type: ignore[assignment]

            self.assertEqual(rc, 20, msg=(stdout, stderr))
            self.assertIn("Docker", stderr)
            self.assertIn("docker version", stderr)
            self.assertIn("docker compose version", stderr)

    def test_memory_db_migrate_when_docker_missing_prints_instructions_and_exits_20(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / ".conductor" / "memory").mkdir(parents=True)

            orig_which = getattr(CONDUCTOR, "_which", None)
            self.assertIsNotNone(orig_which)
            CONDUCTOR._which = lambda _name: None  # type: ignore[assignment]
            try:
                rc, stdout, stderr = run_cli(
                    ["memory", "db", "migrate", "--repo-root", str(repo)]
                )
            finally:
                CONDUCTOR._which = orig_which  # type: ignore[assignment]

            self.assertEqual(rc, 20, msg=(stdout, stderr))
            self.assertIn("Docker", stderr)
            self.assertIn("docker version", stderr)
            self.assertIn("docker compose version", stderr)

    def test_memory_db_status_when_docker_missing_exits_20(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / ".conductor" / "memory").mkdir(parents=True)

            orig_which = getattr(CONDUCTOR, "_which", None)
            self.assertIsNotNone(orig_which)
            CONDUCTOR._which = lambda _name: None  # type: ignore[assignment]
            try:
                rc, stdout, stderr = run_cli(
                    ["memory", "db", "status", "--repo-root", str(repo)]
                )
            finally:
                CONDUCTOR._which = orig_which  # type: ignore[assignment]

            self.assertEqual(rc, 20, msg=(stdout, stderr))
            self.assertIn("Docker", stderr)

    def test_memory_db_down_when_docker_missing_exits_20(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / ".conductor" / "memory").mkdir(parents=True)

            orig_which = getattr(CONDUCTOR, "_which", None)
            self.assertIsNotNone(orig_which)
            CONDUCTOR._which = lambda _name: None  # type: ignore[assignment]
            try:
                rc, stdout, stderr = run_cli(
                    ["memory", "db", "down", "--repo-root", str(repo)]
                )
            finally:
                CONDUCTOR._which = orig_which  # type: ignore[assignment]

            self.assertEqual(rc, 20, msg=(stdout, stderr))
            self.assertIn("Docker", stderr)

    def test_memory_db_psql_when_docker_missing_exits_20(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / ".conductor" / "memory").mkdir(parents=True)

            orig_which = getattr(CONDUCTOR, "_which", None)
            self.assertIsNotNone(orig_which)
            CONDUCTOR._which = lambda _name: None  # type: ignore[assignment]
            try:
                rc, stdout, stderr = run_cli(
                    ["memory", "db", "psql", "--repo-root", str(repo)]
                )
            finally:
                CONDUCTOR._which = orig_which  # type: ignore[assignment]

            self.assertEqual(rc, 20, msg=(stdout, stderr))
            self.assertIn("Docker", stderr)


class TestMemorySync(unittest.TestCase):
    def test_memory_sync_stub_prints_remote_sync_not_configured(self):
        rc, stdout, stderr = run_cli(["memory", "sync"])
        self.assertEqual(rc, 0, msg=(stdout, stderr))
        self.assertEqual("", stderr)
        self.assertIn("Remote sync not configured", stdout)


class TestMemoryBackfillDb(unittest.TestCase):
    def test_memory_backfill_db_when_docker_missing_exits_20(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            track_id = "t1"
            (repo / ".conductor" / "tracks" / track_id / "memory").mkdir(parents=True)
            (repo / ".conductor" / "memory").mkdir(parents=True)

            # minimal transcript
            transcript = repo / ".conductor" / "tracks" / track_id / "memory" / "transcript.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "event_id": "00000000-0000-0000-0000-000000000000",
                        "track_id": track_id,
                        "seq": 1,
                        "ts": "2026-01-01T00:00:00Z",
                        "event_type": "message",
                        "role": "user",
                        "content": {"format": "text", "text": "hi"},
                        "source": {"ide": "generic"},
                        "sync": {"policy": "sync_ok", "redactions_applied": False, "contains_sensitive": False},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            orig_which = getattr(CONDUCTOR, "_which", None)
            self.assertIsNotNone(orig_which)
            CONDUCTOR._which = lambda _name: None  # type: ignore[assignment]
            try:
                rc, stdout, stderr = run_cli(
                    [
                        "memory",
                        "backfill-db",
                        "--repo-root",
                        str(repo),
                        "--track-id",
                        track_id,
                    ]
                )
            finally:
                CONDUCTOR._which = orig_which  # type: ignore[assignment]

            self.assertEqual(rc, 20, msg=(stdout, stderr))
            self.assertIn("Docker", stderr)

    def test_memory_backfill_db_calls_psql_and_updates_state_without_docker(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            track_id = "t1"
            track_mem = repo / ".conductor" / "tracks" / track_id / "memory"
            track_mem.mkdir(parents=True)
            (repo / ".conductor" / "memory").mkdir(parents=True)

            # required compose path
            compose = repo / ".conductor" / "memory" / "docker-compose.yml"
            compose.write_text("services: {}\n", encoding="utf-8")

            transcript = track_mem / "transcript.jsonl"
            transcript.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "schema_version": 1,
                                "event_id": "00000000-0000-0000-0000-000000000000",
                                "track_id": track_id,
                                "seq": 1,
                                "ts": "2026-01-01T00:00:00Z",
                                "event_type": "message",
                                "role": "user",
                                "content": {"format": "text", "text": "hi"},
                                "source": {"ide": "generic"},
                                "sync": {"policy": "sync_ok", "redactions_applied": False, "contains_sensitive": False},
                            }
                        ),
                        json.dumps(
                            {
                                "schema_version": 1,
                                "event_id": "00000000-0000-0000-0000-000000000001",
                                "track_id": track_id,
                                "seq": 2,
                                "ts": "2026-01-01T00:00:01Z",
                                "event_type": "message",
                                "role": "assistant",
                                "content": {"format": "text", "text": "there"},
                                "source": {"ide": "generic"},
                                "sync": {"policy": "sync_ok", "redactions_applied": False, "contains_sensitive": False},
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            # Mocks
            orig_require = getattr(CONDUCTOR, "_require_docker")
            orig_run = CONDUCTOR.subprocess.run
            calls = []

            def fake_run(cmd, **kwargs):
                calls.append((cmd, kwargs))
                return CONDUCTOR.subprocess.CompletedProcess(cmd, 0, b"", b"")

            CONDUCTOR._require_docker = lambda: True  # type: ignore[assignment]
            CONDUCTOR.subprocess.run = fake_run  # type: ignore[assignment]
            try:
                rc, stdout, stderr = run_cli(
                    [
                        "memory",
                        "backfill-db",
                        "--repo-root",
                        str(repo),
                        "--track-id",
                        track_id,
                        "--no-auto-start-db",
                    ]
                )
            finally:
                CONDUCTOR._require_docker = orig_require  # type: ignore[assignment]
                CONDUCTOR.subprocess.run = orig_run  # type: ignore[assignment]

            self.assertEqual(rc, 0, msg=(stdout, stderr))
            self.assertEqual("", stderr)
            self.assertTrue(any("psql" in " ".join(c[0]) for c in calls))

            state = json.loads((track_mem / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["last_ingested_seq"], 2)


class TestMemorySummarize(unittest.TestCase):
    def test_memory_summarize_creates_summary_md_deterministically(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            track_id = "t1"
            mem_dir = repo / ".conductor" / "tracks" / track_id / "memory"
            mem_dir.mkdir(parents=True)

            transcript = mem_dir / "transcript.jsonl"
            transcript.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "schema_version": 1,
                                "event_id": "00000000-0000-0000-0000-000000000000",
                                "track_id": track_id,
                                "seq": 1,
                                "ts": "2026-01-01T00:00:00Z",
                                "event_type": "message",
                                "role": "user",
                                "content": {"format": "text", "text": "hello"},
                                "source": {"ide": "generic"},
                                "sync": {"policy": "sync_ok", "redactions_applied": False, "contains_sensitive": False},
                            }
                        ),
                        json.dumps(
                            {
                                "schema_version": 1,
                                "event_id": "00000000-0000-0000-0000-000000000001",
                                "track_id": track_id,
                                "seq": 2,
                                "ts": "2026-01-01T00:00:01Z",
                                "event_type": "message",
                                "role": "assistant",
                                "content": {"format": "text", "text": "world"},
                                "source": {"ide": "generic"},
                                "sync": {"policy": "sync_ok", "redactions_applied": False, "contains_sensitive": False},
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            rc, stdout, stderr = run_cli(
                [
                    "memory",
                    "summarize",
                    "--repo-root",
                    str(repo),
                    "--track-id",
                    track_id,
                ]
            )
            self.assertEqual(rc, 0, msg=(stdout, stderr))
            self.assertEqual("", stderr)
            self.assertIn("OK memory summarize", stdout)

            summary_path = mem_dir / "summary.md"
            self.assertTrue(summary_path.exists())
            summary = summary_path.read_text(encoding="utf-8")
            self.assertIn("BEGIN GENERATED", summary)
            self.assertIn("hello", summary)
            self.assertIn("world", summary)


class TestInstallUpgradeTemplate(unittest.TestCase):
    def test_init_installs_memory_templates(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            rc, stdout, stderr = run_cli(["init", "--yes", str(repo)])
            self.assertEqual(rc, 0, msg=(stdout, stderr))

            self.assertTrue((repo / ".conductor" / "memory" / "config.json").exists())
            self.assertTrue(
                (repo / ".conductor" / "memory" / "docker-compose.yml").exists()
            )
            self.assertTrue(
                (
                    repo
                    / ".conductor"
                    / "memory"
                    / "migrations"
                    / "001_init.sql"
                ).exists()
            )
            self.assertTrue((repo / ".conductor" / ".gitignore").exists())

    def test_doctor_checks_memory_templates(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            rc, stdout, stderr = run_cli(["init", "--yes", str(repo)])
            self.assertEqual(rc, 0, msg=(stdout, stderr))

            rc, stdout, stderr = run_cli(["doctor", str(repo)])
            self.assertEqual(rc, 0, msg=(stdout, stderr))
            self.assertEqual("", stderr)

            repo_r = repo.resolve()
            self.assertIn(
                str(repo_r / ".conductor" / "memory" / "config.json"), stdout
            )
            self.assertIn(
                str(repo_r / ".conductor" / "memory" / "docker-compose.yml"), stdout
            )
            self.assertIn(
                str(repo_r / ".conductor" / "memory" / "migrations" / "001_init.sql"),
                stdout,
            )
            self.assertIn(str(repo_r / ".conductor" / ".gitignore"), stdout)

    def test_doctor_prints_memory_db_dependency_instructions_when_docker_missing(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            rc, stdout, stderr = run_cli(["init", "--yes", str(repo)])
            self.assertEqual(rc, 0, msg=(stdout, stderr))

            orig_which = getattr(CONDUCTOR, "_which", None)
            self.assertIsNotNone(orig_which)
            CONDUCTOR._which = lambda _name: None  # type: ignore[assignment]
            try:
                rc, stdout, stderr = run_cli(["doctor", str(repo)])
            finally:
                CONDUCTOR._which = orig_which  # type: ignore[assignment]

            self.assertEqual(rc, 0, msg=(stdout, stderr))
            self.assertIn("Docker is required", stdout)
