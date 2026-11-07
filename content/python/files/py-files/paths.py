# 5.3 Files: reading, writing, modes, paths and streams
# Example "paths" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from pathlib import Path
import tempfile

base = Path(tempfile.mkdtemp())
folder = base / "reports" / "2026"           # / joins path parts on every system
folder.mkdir(parents=True, exist_ok=True)
(folder / "jan.csv").write_text("a,b\n1,2\n", encoding="utf-8")
(folder / "feb.csv").write_text("a,b\n3,4\n", encoding="utf-8")
(folder / "notes.txt").write_text("hi", encoding="utf-8")

p = folder / "jan.csv"
print(p.name, p.stem, p.suffix, p.parent.name)
print(p.exists(), p.is_file(), folder.is_dir())
print(sorted(f.name for f in folder.glob("*.csv")))
print(p.read_text(encoding="utf-8").splitlines())
p.rename(folder / "january.csv")
print(sorted(f.name for f in folder.iterdir()))
