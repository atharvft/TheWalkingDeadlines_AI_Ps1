"""Backend package.

The repository intentionally keeps the top-level ``ai`` package separate from
``backend``. Add the project root when the documented ``cd backend`` launch
command is used.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
