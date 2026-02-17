from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from tools.ci.check_no_db_imports_in_api_gateway import main  # noqa: E402


def test_no_db_imports_in_api_gateway() -> None:
    assert main() == 0
