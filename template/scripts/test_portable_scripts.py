#!/usr/bin/env python3
"""Isolated shell runtime checks; no npm install, TTS, or real render is run.

Run with a working Python 3: python scripts/test_portable_scripts.py
Remotion/npm/ffmpeg are stubbed. GBK is simulated for implicit Python text reads,
so the UTF-8 regressions can be tested on macOS/Linux without a Windows host.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
ENTRY_POINTS = ("new_project.sh", "preview.sh", "render.sh", "still.sh", "test_render.sh")


class PortableScriptsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="a2e-portable-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.root = self.work / "project with spaces"
        self.bin = self.work / "tools with spaces"
        self.bin.mkdir()
        (self.root / "scripts").mkdir(parents=True)
        (self.root / "src/common").mkdir(parents=True)
        for name in ENTRY_POINTS:
            shutil.copy2(SCRIPTS / name, self.root / "scripts" / name)
        (self.root / "src/config.ts").write_text(
            "// 配置🌍：中文文件必须显式用 UTF-8 读取\nexport const config = {slug: 'demo'};\n",
            encoding="utf-8",
        )
        (self.root / "src/common/timeline.ts").write_text(
            "// 时间轴🌍\nexport const TOTAL_FRAMES = 300;\n", encoding="utf-8"
        )
        (self.root / "scripts/sheet.py").write_text("pass\n", encoding="utf-8")
        # Deliberately omit rsync; exercise the safe staging fallback.
        for name in ("bash", "dirname", "mkdir", "cp", "rm", "find", "mktemp", "sed", "head", "ls", "wc"):
            binary = shutil.which(name)
            if binary is None:
                self.skipTest("Required shell utility not available: " + name)
            (self.bin / name).symlink_to(binary)
        self.log = self.work / "calls.log"
        self.env = dict(os.environ, PATH=str(self.bin), TMPDIR=str(self.work), CLEAN_TMP="0", A2E_TEST_CALLS=str(self.log))
        for key in ("PY", "CONC", "VER", "SKIP_BUNDLE", "KEEP_BUNDLE", "FORCE_BUNDLE"):
            self.env.pop(key, None)
        self.write_executable("npm", "import sys\nsys.exit(0)\n")
        self.write_executable("npx", """
import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ['A2E_TEST_CALLS'], 'a', encoding='utf-8') as log:
    log.write(json.dumps(args) + '\\n')
if args == ['tsc', '--noEmit']:
    pass
elif args[:2] == ['remotion', 'bundle']:
    pathlib.Path(args[args.index('--out-dir') + 1]).mkdir(exist_ok=True)
elif args[:2] == ['remotion', 'render']:
    out = pathlib.Path(args[4])
    if '--sequence' in args:
        out.mkdir(exist_ok=True)
        for frame in range(30):
            (out / ('f_%04d.jpeg' % frame)).write_bytes(b'fixture')
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b'fixture')
elif args[:2] == ['remotion', 'still']:
    pathlib.Path(args[4]).write_bytes(b'fixture')
else:
    raise SystemExit('Unexpected mocked npx invocation')
""")
        self.write_executable("ffmpeg", "from pathlib import Path\nPath('fin_frames/f_0001.jpg').write_bytes(b'fixture')\n")
        self.python_candidate("python3", broken=True)
        self.python_candidate("python", broken=False)

    def write_executable(self, name, source):
        target = self.bin / name
        target.write_text("#!" + sys.executable + "\n" + source, encoding="utf-8")
        target.chmod(0o755)

    def python_candidate(self, name, broken):
        if broken:
            self.write_executable(name, "raise SystemExit(49)\n")
            return
        self.write_executable(name, """
import builtins, runpy, sys
original_open = builtins.open
def locale_open(file, mode='r', buffering=-1, encoding=None, *args, **kwargs):
    if 'b' not in mode and encoding is None:
        encoding = 'gbk'
    return original_open(file, mode, buffering, encoding, *args, **kwargs)
builtins.open = locale_open
if sys.argv[1] == '-c':
    exec(compile(sys.argv[2], '<command>', 'exec'), {'__name__': '__main__'})
else:
    target = sys.argv[1]
    sys.argv = sys.argv[1:]
    runpy.run_path(target, run_name='__main__')
""")

    def run_script(self, name, *args):
        result = subprocess.run(
            [str(self.root / "scripts" / name), *map(str, args)],
            env=self.env, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_all_five_entry_points_use_bash_and_keep_executable_mode(self):
        for name in ENTRY_POINTS:
            with self.subTest(script=name):
                original = SCRIPTS / name
                self.assertEqual(original.read_text(encoding="utf-8").splitlines()[0], "#!/usr/bin/env bash")
                self.assertTrue(original.stat().st_mode & 0o111)
                subprocess.run([str(self.bin / "bash"), "-n", str(original)], check=True)

    def test_preview_falls_back_from_broken_python3_and_reads_utf8(self):
        self.run_script("preview.sh", 2, 1)
        self.assertTrue((self.root / "renders/demo_preview_1-3s.mp4").exists())

    def test_render_falls_back_from_broken_python3_and_reads_utf8(self):
        self.run_script("render.sh")
        self.assertTrue((self.root / "renders/demo_v1.mp4").exists())
        self.assertTrue((self.root / "render.done").exists())

    def test_preview_accepts_working_python3_with_gbk_default(self):
        self.python_candidate("python3", broken=False)
        self.run_script("preview.sh", 2)
        self.assertTrue((self.root / "renders/demo_preview_0-2s.mp4").exists())

    def test_missing_working_python_fails_before_rendering(self):
        self.python_candidate("python", broken=True)
        result = subprocess.run(
            [str(self.root / "scripts/preview.sh")], env=self.env, text=True, capture_output=True, timeout=30
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Python 3 interpreter not found", result.stderr)
        self.assertFalse(self.log.exists())

    def test_still_outputs_all_requested_frames(self):
        output = self.work / "still output"
        self.run_script("still.sh", "G1", "3,5,17", output)
        self.assertEqual(sorted(p.name for p in output.iterdir()), ["f_0003.png", "f_0005.png", "f_0017.png"])

    def test_test_render_runs_directly_without_zsh(self):
        result = self.run_script("test_render.sh", "G1", 1)
        self.assertEqual(result.stdout.strip(), "30")
        self.assertFalse((self.bin / "zsh").exists())

    def test_no_rsync_fallback_preserves_existing_destination_content(self):
        destination = self.work / "existing project"
        excluded = ("renders", "build_saved", "stills", "fin_frames", "audio/cache", "node_modules")
        for name in excluded:
            directory = destination / name
            directory.mkdir(parents=True)
            (directory / "keep.txt").write_text("existing work", encoding="utf-8")
        self.run_script("new_project.sh", destination, "new-slug")
        for name in excluded:
            self.assertTrue((destination / name / "keep.txt").exists(), name)
        self.assertIn("slug: 'new-slug'", (destination / "src/config.ts").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
