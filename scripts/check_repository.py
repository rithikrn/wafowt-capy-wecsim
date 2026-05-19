"""Static smoke test for the OWC-FOWT hydro workflow repository.

The check intentionally does not parse HDF5/NetCDF internals. It verifies file
presence, references, Python syntax, SLX readability as zip files, and absence
of user-specific hard-coded paths.
"""

from __future__ import annotations

from pathlib import Path
import ast
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CASES = [ROOT / "cases" / "oc4_baseline_no_owc", ROOT / "cases" / "oc4_hollow_owc_4m"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def check_required_paths() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "src" / "owc_fowt_hydro" / "capytaine_runner.py",
        ROOT / "docs" / "CASE_TREE.md",
        ROOT / "docs" / "FILE_AUDIT.md",
        ROOT / "docs" / "METHOD_THEORY.md",
        ROOT / "docs" / "OFFICIAL_DOC_REFERENCES.md",
    ]
    for case in CASES:
        required.extend([
            case / "wecSimInputFile.m",
            case / "userDefinedFunctions.m",
            case / "hydroData",
            case / "geometry",
        ])
    for path in required:
        require(path.exists(), f"Missing required path: {rel(path)}")


def check_wecsim_references() -> None:
    for case in CASES:
        input_text = (case / "wecSimInputFile.m").read_text(encoding="utf-8")
        referenced = re.findall(r"'([^']+\.(?:slx|h5|stl))'", input_text)
        for item in referenced:
            require((case / item).exists(), f"{rel(case / 'wecSimInputFile.m')} references missing file: {item}")


def check_hydro_files_exist_without_opening() -> None:
    expected = [
        ROOT / "cases/oc4_baseline_no_owc/hydroData/oc4_baseline_capytaine.nc",
        ROOT / "cases/oc4_baseline_no_owc/hydroData/oc4_baseline_wecsim.h5",
        ROOT / "cases/oc4_hollow_owc_4m/hydroData/oc4_hollow_owc_4m_capytaine.nc",
        ROOT / "cases/oc4_hollow_owc_4m/hydroData/oc4_hollow_owc_4m_wecsim.h5",
    ]
    for path in expected:
        require(path.exists(), f"Missing hydrodynamic data file: {rel(path)}")
        require(path.stat().st_size > 0, f"Hydrodynamic data file is empty: {rel(path)}")


def check_slx_archives() -> None:
    for slx in ROOT.glob("cases/**/*.slx"):
        require(zipfile.is_zipfile(slx), f"Simulink file is not a readable SLX archive: {rel(slx)}")
        with zipfile.ZipFile(slx) as archive:
            require("simulink/systems/system_root.xml" in archive.namelist(), f"SLX missing system_root.xml: {rel(slx)}")


def check_python_syntax() -> None:
    for py_file in list((ROOT / "src").glob("**/*.py")) + list((ROOT / "cases").glob("**/*.py")) + [ROOT / "scripts/check_repository.py"]:
        ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))


def check_no_generated_cache() -> None:
    forbidden_patterns = ["slprj", "__pycache__", ".pytest_cache"]
    for path in ROOT.rglob("*"):
        if path.is_dir() and path.name in forbidden_patterns:
            raise AssertionError(f"Generated/cache directory should not be committed: {rel(path)}")


def check_no_user_specific_paths() -> None:
    bad_patterns = [
        "C:" + "\\\\" + "Users" + "\\\\",
        "/home/" + "rithik",
        "Box" + "\\\\" + "Rithik",
        "weekly" + " updates",
        "/root/" + "OpenFOAM",
    ]
    text_files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in {".m", ".py", ".md", ".yml", ".txt", ".toml", ".cff"}]
    for path in text_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in bad_patterns:
            require(not re.search(pattern, text, re.IGNORECASE), f"User-specific path pattern found in {rel(path)}: {pattern}")


def main() -> int:
    checks = [
        check_required_paths,
        check_wecsim_references,
        check_hydro_files_exist_without_opening,
        check_slx_archives,
        check_python_syntax,
        check_no_generated_cache,
        check_no_user_specific_paths,
    ]
    for check in checks:
        check()
        print(f"PASS: {check.__name__}")
    print("\nRepository smoke test passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
