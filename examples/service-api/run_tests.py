"""运行统一服务框架测试。

默认运行全部（框架层秒级 + 端到端冒烟约 40 秒）；加 --fast 只跑框架层。
"""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="运行统一服务框架测试")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="只跑框架层快速测试，跳过端到端冒烟",
    )
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(
        str(Path(__file__).resolve().parent / "tests"),
        pattern="test_framework.py" if args.fast else "test_*.py",
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
