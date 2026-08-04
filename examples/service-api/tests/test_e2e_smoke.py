"""一致性 API 端到端冒烟测试（真实加密/生产门面，约 40 秒）。

以子进程运行 run_demo.py，断言退出码 0 且关键输出存在——证明统一
服务框架 + 一致性 API 在真实模块上完整可用（含 SM2/SM4 加密、编排链、
合并回执、简报与知识入库）。

说明：本测试较慢；`run_tests.py --fast` 可跳过它，只跑框架层快速测试。
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEMO = ROOT / "examples" / "service-api" / "run_demo.py"


class E2ESmokeTest(unittest.TestCase):
    def test_full_demo_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(DEMO),
                    "--output-dir",
                    tmp,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )
            self.assertEqual(0, completed.returncode, completed.stderr[-2000:])
            # 使用 ASCII 稳定标记断言（避免 Windows 管道编码差异）
            self.assertIn("API", completed.stdout)
            self.assertIn("16", completed.stdout)
            self.assertIn("kb.PRJ001", completed.stdout)
            self.assertIn("ok=True", completed.stdout)


class FullLoopE2ETest(unittest.TestCase):
    """完整业务闭环 E2E：一致性 API 承载多角色连续合并与三类简报。"""

    def test_full_loop_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "examples" / "service-api" / "run_demo_full.py"),
                    "--output-dir",
                    tmp,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )
            self.assertEqual(0, completed.returncode, completed.stderr[-2000:])
            self.assertIn("PRJ001-R0005", completed.stdout)
            self.assertIn("kb.PRJ001", completed.stdout)
            self.assertIn("brief.", completed.stdout)
            self.assertIn("SUPERVISION_NOTICE", completed.stdout)
            self.assertIn("AUDIT_CHECKPOINT", completed.stdout)


if __name__ == "__main__":
    unittest.main()
