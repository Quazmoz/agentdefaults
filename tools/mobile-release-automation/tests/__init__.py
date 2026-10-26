"""Keep the suite off the operator's real credential home (Play edit locks live there)."""

import os
import tempfile

os.environ.setdefault("MRA_HOME", tempfile.mkdtemp(prefix="mra-test-home-"))
