"""Build an unsigned Windows installer and a release ZIP from this checkout."""

import hashlib
import importlib.metadata
import pathlib
import shutil
import sys

import PyInstaller.__main__

ROOT = pathlib.Path(__file__).resolve().parents[1]
if sys.platform != "win32":
    raise SystemExit("Build the Windows executable on Windows.")
DIST = ROOT / "dist"
PyInstaller.__main__.run(
    [
        str(ROOT / "launcher.py"),
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--name",
        "Whirlpool-YURIS-JoyFix",
        "--paths",
        str(ROOT),
        "--collect-all",
        "capstone",
        "--distpath",
        str(DIST / "bin"),
        "--workpath",
        str(ROOT / "build"),
        "--specpath",
        str(ROOT / "build"),
    ]
)
bundle = DIST / "Whirlpool-YURIS-JoyFix-windows-x64"
bundle.mkdir(parents=True, exist_ok=True)
shutil.copy2(DIST / "bin/Whirlpool-YURIS-JoyFix.exe", bundle / "Whirlpool-YURIS-JoyFix.exe")
for name in ("README.md", "README.en.md", "LICENSE"):
    shutil.copy2(ROOT / name, bundle / name)
licenses = bundle / "licenses"
licenses.mkdir(exist_ok=True)
for package in ("capstone", "pefile", "pyinstaller"):
    dist = importlib.metadata.distribution(package)
    for item in dist.files or []:
        if (
            "license" in pathlib.Path(str(item)).name.lower()
            or pathlib.Path(str(item)).name.lower() == "copying.txt"
        ):
            path = pathlib.Path(dist.locate_file(item))
            if path.is_file():
                shutil.copy2(path, licenses / (package + "-" + path.name))
python_license = pathlib.Path(sys.base_prefix) / "LICENSE.txt"
if not python_license.is_file():
    raise RuntimeError("Python LICENSE.txt not found")
shutil.copy2(python_license, licenses / "Python-LICENSE.txt")
archive = pathlib.Path(
    shutil.make_archive(str(DIST / "Whirlpool-YURIS-JoyFix-windows-x64"), "zip", bundle)
)
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(DIST / "SHA256SUMS.txt").write_text(
    digest + "  " + archive.name + "\n", encoding="ascii"
)
print(archive)
