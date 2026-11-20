"""Entrypoint for the news-image-20261119 entry.

When the harness runs this file, it materialises the front-page artwork
at /output/entry.png so the judge can read it. The artwork itself lives
in entry.png next to this file; this script only places a copy where the
harness expects it, and reports the size it wrote.
"""

from pathlib import Path
import shutil
import sys


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    target_dir = Path("/output")
    target = target_dir / "entry.png"

    if not source.is_file():
        print(f"missing artwork: {source}", file=sys.stderr)
        return 1

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
