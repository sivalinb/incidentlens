from __future__ import annotations

import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def repo_tempdir():
    root = Path.cwd() / ".tmp-tests"
    root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as directory:
        yield Path(directory)

