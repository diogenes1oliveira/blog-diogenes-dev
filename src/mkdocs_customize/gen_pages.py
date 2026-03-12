from pathlib import Path

import mkdocs_gen_files  # type: ignore

FILES = [
    ("docs/ARCHITECTURE.md", "ARCHITECTURE.md"),
]

for source, target in FILES:
    source_path = Path(source)
    if source_path.exists():
        content = source_path.read_text()
        with mkdocs_gen_files.open(target, "w") as fp:
            fp.write(content)
