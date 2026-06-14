from __future__ import annotations

import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "wiki-publish.json"
MKDOCS_CONFIG = ROOT / "mkdocs.yml"

CATEGORY_TITLES = {
    "Cases": "Расследования",
    "Characters": "Персонажи",
    "Groups": "Группы",
    "Party": "Партия",
    "Places": "Места",
    "Sources": "Дайджесты источников",
}

ROOT_NAV = [
    "index.md",
    "Start.md",
    "Overview.md",
    "Timeline.md",
    "Party",
    "Cases",
    "Characters",
    "Places",
    "Groups",
    "Sources",
    "LOG.md",
]

ROOT_TITLES = {
    "index.md": "Главная",
    "Start.md": "Старт для игроков",
    "Overview.md": "Обзор",
    "Timeline.md": "Хронология",
    "LOG.md": "Журнал обновлений",
}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]\n]+)\]\((<)?([^)\n>]+?)(>)?\)")


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def to_posix(path: Path) -> str:
    return path.as_posix()


def resolve_workspace_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def ensure_safe_generated_dir(path: Path) -> None:
    resolved = path.resolve()
    build_root = (ROOT / "build").resolve()
    if resolved == ROOT or build_root not in resolved.parents:
        raise RuntimeError(f"Refusing to remove non-generated path: {resolved}")


def matches_any(rel_posix: str, patterns: list[str]) -> bool:
    folded = rel_posix.casefold()
    return any(fnmatch(folded, pattern.casefold()) for pattern in patterns)


def has_private_marker(path: Path, markers: list[str]) -> bool:
    if path.suffix.casefold() != ".md":
        return False
    try:
        head = path.read_text(encoding="utf-8")[:2048].casefold()
    except UnicodeDecodeError:
        return False
    return any(marker.casefold() in head for marker in markers)


def rewrite_generated_markdown(text: str, source_rel: Path) -> str:
    def replace_link(match: re.Match[str]) -> str:
        label, left_angle, dest, right_angle = match.groups()
        rewritten = rewrite_link_destination(dest, source_rel)
        if rewritten is None:
            return label
        if rewritten == dest:
            return match.group(0)
        return f"[{label}]({left_angle or ''}{rewritten}{right_angle or ''})"

    return MARKDOWN_LINK_RE.sub(replace_link, text)


def rewrite_link_destination(dest: str, source_rel: Path) -> str | None:
    if "://" in dest or dest.startswith("#") or dest.startswith("mailto:"):
        return dest

    path_part = dest
    anchor = ""
    if "#" in path_part:
        path_part, anchor = path_part.split("#", 1)
        anchor = f"#{anchor}"

    normalized = path_part.replace("\\", "/")
    if normalized.endswith(".md"):
        source_parent = source_rel.parent.as_posix()
        resolved = posixpath.normpath(posixpath.join(source_parent, normalized))
        if resolved == ".." or resolved.startswith("../"):
            return None

    if normalized == "INDEX.md" or normalized.endswith("/INDEX.md"):
        normalized = f"{normalized[:-8]}index.md"

    return f"{normalized}{anchor}"


def target_rel_path(rel: Path) -> Path:
    if rel.name == "INDEX.md":
        return rel.with_name("index.md")
    return rel


def write_pages_file(path: Path, *, title: str | None = None, nav: list[str] | None = None) -> None:
    lines: list[str] = []
    if title:
        lines.append(f"title: {title}")
    if nav:
        lines.append("nav:")
        for item in nav:
            lines.append(f"  - {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_text_file(path: Path, text: str, rel_posix: str) -> None:
    try:
        path.write_text(text, encoding="utf-8", newline="\n")
    except OSError as exc:
        raise RuntimeError(f"Failed to write generated copy of {rel_posix} to {path}") from exc


def copy_binary_file(source: Path, destination: Path, rel_posix: str) -> None:
    try:
        shutil.copy2(source, destination)
    except OSError as exc:
        raise RuntimeError(f"Failed to copy generated asset {rel_posix} to {destination}") from exc


def prepare() -> int:
    config = load_config()
    source_dir = resolve_workspace_path(config["source_dir"])
    docs_dir = resolve_workspace_path(config["docs_dir"])
    exclude_globs = list(config.get("exclude_globs", []))
    private_markers = list(config.get("private_markers", []))

    if not source_dir.exists():
        raise RuntimeError(f"Source wiki directory does not exist: {source_dir}")

    ensure_safe_generated_dir(docs_dir)
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped: list[str] = []

    for source_path in sorted(source_dir.rglob("*")):
        if not source_path.is_file():
            continue

        rel = source_path.relative_to(source_dir)
        rel_posix = to_posix(rel)
        if matches_any(rel_posix, exclude_globs) or has_private_marker(source_path, private_markers):
            skipped.append(rel_posix)
            continue

        destination = docs_dir / target_rel_path(rel)
        destination.parent.mkdir(parents=True, exist_ok=True)

        if source_path.suffix.casefold() == ".md":
            text = source_path.read_text(encoding="utf-8")
            write_text_file(destination, rewrite_generated_markdown(text, rel), rel_posix)
        else:
            copy_binary_file(source_path, destination, rel_posix)
        copied += 1

    root_nav = [item for item in ROOT_NAV if (docs_dir / item).exists()]
    write_pages_file(docs_dir / ".pages", nav=[ROOT_TITLES.get(item, item) + f": {item}" for item in root_nav])

    for directory, title in CATEGORY_TITLES.items():
        directory_path = docs_dir / directory
        if directory_path.exists():
            write_pages_file(directory_path / ".pages", title=title)

    print(f"Prepared {copied} public wiki files in {docs_dir.relative_to(ROOT)}")
    if skipped:
        print("Skipped by publication filters:")
        for item in skipped:
            print(f"  - {item}")
    return 0


def run_mkdocs(args: list[str]) -> int:
    command = [sys.executable, "-m", "mkdocs", *args, "-f", str(MKDOCS_CONFIG)]
    return subprocess.call(command, cwd=ROOT)


def build(strict: bool) -> int:
    prepare()
    args = ["build"]
    if strict:
        args.append("--strict")
    return run_mkdocs(args)


def serve(host: str, port: int) -> int:
    prepare()
    return run_mkdocs(["serve", "-a", f"{host}:{port}"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare, build, or serve the Avernus wiki site.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("prepare", help="Copy the public Wiki/ layer into the generated MkDocs docs directory.")

    build_parser = subparsers.add_parser("build", help="Prepare and build the MkDocs site.")
    build_parser.add_argument("--strict", action="store_true", help="Fail the build on MkDocs warnings.")

    serve_parser = subparsers.add_parser("serve", help="Prepare and serve the MkDocs site locally.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8000, type=int)

    args = parser.parse_args()
    if args.command == "prepare":
        return prepare()
    if args.command == "build":
        return build(strict=args.strict)
    if args.command == "serve":
        return serve(host=args.host, port=args.port)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
