"""Zero-dependency test runner (works with or without pytest installed).

Usage:  python3 tests/run_tests.py
If pytest is available you can also run:  python3 -m pytest tests/
"""

from __future__ import annotations

import importlib
import sys
import traceback
import types
from contextlib import contextmanager
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _install_pytest_shim() -> None:
    try:
        import pytest  # noqa: F401
        return
    except ImportError:
        pass

    shim = types.ModuleType("pytest")

    @contextmanager
    def raises(exc):
        try:
            yield
        except exc:
            return
        except Exception as e:  # wrong exception type
            raise AssertionError("expected %s, got %s" % (exc, type(e))) from e
        raise AssertionError("did not raise %s" % exc)

    shim.raises = raises  # type: ignore
    sys.modules["pytest"] = shim


def main() -> int:
    _install_pytest_shim()
    test_files = sorted(p for p in (REPO / "tests").glob("test_*.py"))
    passed = failed = 0
    failures = []
    for tf in test_files:
        mod_name = "tests." + tf.stem
        mod = importlib.import_module(mod_name)
        for name in dir(mod):
            if not name.startswith("test_"):
                continue
            fn = getattr(mod, name)
            if not callable(fn):
                continue
            try:
                fn()
                passed += 1
                print("PASS %s::%s" % (tf.stem, name))
            except Exception as e:  # noqa: BLE001
                failed += 1
                failures.append("%s::%s -> %s" % (tf.stem, name, e))
                print("FAIL %s::%s" % (tf.stem, name))
                traceback.print_exc()
    print("\n%d passed, %d failed" % (passed, failed))
    if failures:
        print("\nFailures:")
        for f in failures:
            print("  - " + f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
