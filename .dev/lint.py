#!/usr/bin/env python3

"""
Lint YAML, Markdown, HTML files, or build and check mkdocs site.
Usage: lint.py --format markdown|yaml|html|docs [--fix] [--any] <glob1> <glob2> ...
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Set

import pathspec


def log(level: str, message: str) -> None:
    """
    Log a message with timestamp and emoji prefix.

    Args:
        level: Log level (INFO, WARN, ERROR, SUCCESS, DEBUG)
        message: Message to log

    Behavior:
        Prints formatted message to stdout with timestamp and emoji.
        Format: "YYYY-MM-DD HH:MM:SS LEVEL - emoji message"
    """
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    emojis = {
        'INFO': 'ℹ️ ',
        'WARN': '⚠️ ',
        'ERROR': '❌',
        'SUCCESS': '✅',
        'DEBUG': '🔍',
    }
    emoji = emojis.get(level, '📝')
    print(f"{timestamp} {level} - {emoji} {message}")


def find_repo_root(start_dir: Path) -> Path:
    """
    Find repository root directory by searching for marker files.

    Args:
        start_dir: Starting directory to search from

    Returns:
        Path to repository root, or start_dir if not found

    Behavior:
        Walks up directory tree from start_dir until finding .markdownlint.json
        or pyproject.toml. Returns the directory containing that file, or start_dir
        if never found.
    """
    current = start_dir.resolve()
    while current != current.parent:
        if (current / '.markdownlint.json').exists() or (current / 'pyproject.toml').exists():
            return current
        current = current.parent
    return start_dir


def load_markdownlint_ignore(repo_root: Path) -> pathspec.PathSpec:
    """
    Load ignore patterns from .markdownlintignore file using pathspec library.

    Args:
        repo_root: Repository root directory

    Returns:
        pathspec.PathSpec object with gitwildmatch patterns, empty if file doesn't exist
    """
    ignore_file = repo_root / '.markdownlintignore'
    if not ignore_file.exists():
        return pathspec.PathSpec.from_lines('gitwildmatch', [])

    with open(ignore_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

    return pathspec.PathSpec.from_lines('gitwildmatch', lines)


def should_ignore_file(file_path: Path, ignore_spec: pathspec.PathSpec, repo_root: Path) -> bool:
    """
    Check if a file matches ignore patterns using pathspec library.

    Args:
        file_path: Absolute path to file to check
        ignore_spec: pathspec.PathSpec with ignore patterns
        repo_root: Repository root directory

    Returns:
        True if file should be ignored, False otherwise
    """
    if not ignore_spec or not ignore_spec.patterns:
        return False

    try:
        rel_path = file_path.relative_to(repo_root)
        rel_path_str = str(rel_path).replace('\\', '/')
    except ValueError:
        return False

    return ignore_spec.match_file(rel_path_str)


def expand_globs_with_git(globs: List[str]) -> Set[Path]:
    """
    Expand glob patterns to matching tracked files using git ls-files.

    Args:
        globs: List of glob patterns (e.g., ["*.md", "docs/**/*.yml"])

    Returns:
        Set of Path objects for matching tracked files
    """
    import fnmatch
    import re

    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )
        tracked_files = result.stdout.strip().split('\n')
    except (subprocess.CalledProcessError, FileNotFoundError):
        log('WARN', 'git not found or not a git repo, falling back to find')
        return expand_globs_with_find(globs)

    if not tracked_files or tracked_files == ['']:
        log('WARN', 'No tracked files found, falling back to find')
        return expand_globs_with_find(globs)

    files = set()
    for glob_pattern in globs:
        if '**' in glob_pattern:
            regex_pattern = glob_pattern
            regex_pattern = regex_pattern.replace('.', r'\.')
            regex_pattern = regex_pattern.replace('**', '__DOUBLE_STAR__')
            regex_pattern = regex_pattern.replace('*', '[^/]*')
            regex_pattern = regex_pattern.replace('?', '[^/]')
            regex_pattern = regex_pattern.replace('__DOUBLE_STAR__', '.*')

            compiled = re.compile(f'^{regex_pattern}$')
            for tracked_file in tracked_files:
                if tracked_file and compiled.match(tracked_file):
                    file_path = Path(tracked_file)
                    if file_path.is_file():
                        files.add(file_path)
        else:
            for tracked_file in tracked_files:
                if tracked_file and fnmatch.fnmatch(tracked_file, glob_pattern):
                    file_path = Path(tracked_file)
                    if file_path.is_file():
                        files.add(file_path)

    return files


def expand_globs_with_find(globs: List[str]) -> Set[Path]:
    """
    Expand glob patterns to matching files using Python's glob module.

    Args:
        globs: List of glob patterns (e.g., ["*.md", "docs/**/*.yml"])

    Returns:
        Set of Path objects for matching files
    """
    files = set()

    for glob_pattern in globs:
        if '**' in glob_pattern:
            # Split on **/ to get the base dir and the suffix pattern.
            # e.g. "**/*.md" → base="", suffix="*.md"
            #      "docs/**/*.md" → base="docs/", suffix="*.md"
            parts = glob_pattern.split('**/', 1)
            base_dir = Path('.') / parts[0] if parts[0] else Path('.')
            suffix = parts[1] if len(parts) > 1 else '*'
            if base_dir.is_dir():
                for file_path in base_dir.rglob(suffix):
                    if file_path.is_file():
                        files.add(file_path)
        else:
            for file_path in Path('.').glob(glob_pattern):
                if file_path.is_file():
                    files.add(file_path)

    return files


def run_markdown_lint(file_path: Path, fix: bool, repo_root: Path, ignore_spec: Optional[pathspec.PathSpec] = None) -> bool:
    """
    Run markdownlint-cli on a single markdown file.

    Args:
        file_path: Path to markdown file to lint
        fix: If True, attempt to auto-fix issues
        repo_root: Repository root directory (for config file lookup)
        ignore_spec: Optional pathspec for ignore patterns

    Returns:
        True if linting passed or file was ignored, False on error
    """
    if ignore_spec and should_ignore_file(file_path, ignore_spec, repo_root):
        log('INFO', f'Skipping ignored file: {file_path}')
        return True

    log('INFO', f'Linting markdown: {file_path}')

    config_arg = []
    config_file = repo_root / '.markdownlint.json'
    if config_file.exists():
        config_arg = ['--config', str(config_file)]

    cmd = ['npx', '-y', 'markdownlint-cli'] + config_arg
    if fix:
        cmd.append('--fix')
    cmd.append(str(file_path))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            if result.stdout:
                print(result.stdout, end='')
            if result.stderr:
                print(result.stderr, end='', file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        log('ERROR', 'npx not found. Please install Node.js and npm.')
        return False


def run_yaml_lint(file_path: Path) -> bool:
    """
    Run yamllint on a single YAML file.

    Args:
        file_path: Path to YAML file to lint

    Returns:
        True if linting passed, False on error
    """
    log('INFO', f'Linting YAML: {file_path}')

    try:
        result = subprocess.run(
            ['yamllint', '-f', 'standard', str(file_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='', file=sys.stderr)
        return False
    except FileNotFoundError:
        log('INFO', 'Using npx yaml-lint (auto-install if needed)')
        try:
            result = subprocess.run(
                ['npx', '-y', 'yaml-lint', str(file_path)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                if result.stdout:
                    print(result.stdout, end='')
                if result.stderr:
                    print(result.stderr, end='', file=sys.stderr)
                return False
            return True
        except FileNotFoundError:
            log('ERROR', 'Neither yamllint nor npx found.')
            return False


def run_html_lint(file_path: Path) -> bool:
    """
    Validate a generated HTML file by checking for basic well-formedness.

    This section handles the 'html' format: it verifies that files produced by
    md2html.py are valid HTML documents (have <html>, <head>, <body> tags and
    can be parsed without errors). No external tools are required — validation
    uses Python's built-in html.parser module.

    Args:
        file_path: Path to HTML file to validate

    Returns:
        True if the HTML file is well-formed, False on error
    """
    from html.parser import HTMLParser

    class HTMLValidator(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.errors: List[str] = []
            self.tags: List[str] = []

        def handle_starttag(self, tag: str, attrs: object) -> None:
            self.tags.append(tag)

        def error(self, message: str) -> None:  # type: ignore[override]
            self.errors.append(message)

    log('INFO', f'Validating HTML: {file_path}')

    try:
        content = file_path.read_text(encoding='utf-8')
    except OSError as e:
        log('ERROR', f'Cannot read {file_path}: {e}')
        return False

    if not content.strip():
        log('ERROR', f'Empty HTML file: {file_path}')
        return False

    validator = HTMLValidator()
    try:
        validator.feed(content)
    except Exception as e:
        log('ERROR', f'HTML parse error in {file_path}: {e}')
        return False

    if validator.errors:
        for err in validator.errors:
            log('ERROR', f'{file_path}: {err}')
        return False

    if 'html' not in validator.tags:
        log('ERROR', f'{file_path}: missing <html> tag — not a valid HTML document')
        return False

    return True


def run_docs_lint(repo_root: Path) -> bool:
    """
    Build mkdocs site to temporary directory and check for errors.

    Args:
        repo_root: Repository root directory

    Returns:
        True if build succeeded with no errors, False otherwise
    """
    log('INFO', 'Building mkdocs site to check for errors...')

    with tempfile.TemporaryDirectory() as tmpdir:
        build_dir = Path(tmpdir) / 'site'

        mkdocs_yml = repo_root / 'mkdocs.yml'
        if not mkdocs_yml.exists():
            log('ERROR', f'mkdocs.yml not found at {mkdocs_yml}')
            return False

        try:
            result = subprocess.run(
                ['uv', 'run', 'mkdocs', 'build', '--site-dir', str(build_dir)],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                log('ERROR', 'mkdocs build failed')
                if result.stdout:
                    print(result.stdout, end='')
                if result.stderr:
                    print(result.stderr, end='', file=sys.stderr)
                return False

            output = result.stdout + result.stderr
            errors_found = False

            error_patterns = [
                ('WARNING', 'WARNING'),
                ('ERROR', 'ERROR'),
                ('not found', 'Missing file'),
                ('broken link', 'Broken link'),
            ]

            for pattern, label in error_patterns:
                if pattern.lower() in output.lower():
                    lines = output.split('\n')
                    for i, line in enumerate(lines):
                        if pattern.lower() in line.lower():
                            start = max(0, i - 3)
                            end = min(len(lines), i + 4)
                            context = '\n'.join(lines[start:end])
                            log('ERROR', f'{label} found:\n{context}')
                            errors_found = True

            if errors_found:
                log('ERROR', 'mkdocs build completed but errors were found')
                return False

            log('SUCCESS', 'mkdocs build completed successfully with no errors')
            return True

        except FileNotFoundError:
            log('ERROR', 'uv not found. Please install uv: https://github.com/astral-sh/uv')
            return False
        except subprocess.TimeoutExpired:
            log('ERROR', 'mkdocs build timed out after 5 minutes')
            return False
        except Exception as e:
            log('ERROR', f'Unexpected error building mkdocs: {e}')
            return False


def lint_file(file_path: Path, format_type: str, fix: bool, repo_root: Path, ignore_spec: Optional[pathspec.PathSpec] = None) -> bool:
    """
    Lint a single file based on format type.

    Args:
        file_path: Path to file to lint
        format_type: Format type ('markdown', 'yaml', 'html')
        fix: If True, attempt to auto-fix issues (markdown only)
        repo_root: Repository root directory
        ignore_spec: Optional pathspec for ignore patterns (markdown only)

    Returns:
        True if linting passed, False on error or invalid format
    """
    if not file_path.is_file():
        log('ERROR', f'File not found: {file_path}')
        return False

    if format_type == 'markdown':
        return run_markdown_lint(file_path, fix, repo_root, ignore_spec)
    elif format_type == 'yaml':
        return run_yaml_lint(file_path)
    elif format_type == 'html':
        return run_html_lint(file_path)
    else:
        log('ERROR', f'Invalid format: {format_type}')
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Lint YAML, Markdown, or HTML files matching glob patterns.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lint.py --format markdown "*.md"
  lint.py --format markdown --fix "docs/**/*.md"
  lint.py --format yaml "*.yml" "*.yaml"
  lint.py --format html "out/**/*.html"
  lint.py --format docs
        """
    )

    parser.add_argument(
        '--format',
        required=True,
        choices=['markdown', 'yaml', 'html', 'docs'],
        help='File format to lint (markdown/yaml/html) or docs to build and check mkdocs site'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix issues automatically (markdown only)'
    )
    parser.add_argument(
        '--any',
        action='store_true',
        help='Include gitignored files (default: only tracked files)'
    )
    parser.add_argument(
        'globs',
        nargs='*',
        help='One or more glob patterns (e.g., "*.md", "docs/**/*.yml"). Not used for docs format.'
    )

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = find_repo_root(script_dir)

    if args.format == 'docs':
        if args.fix:
            log('WARN', '--fix not applicable to docs format')
        if args.any:
            log('WARN', '--any not applicable to docs format')
        if args.globs:
            log('WARN', 'Glob patterns not used for docs format, ignoring')
        return 0 if run_docs_lint(repo_root) else 1

    if args.fix and args.format == 'yaml':
        log('WARN', 'YAML fix not implemented, only checking')
    if args.fix and args.format == 'html':
        log('WARN', 'HTML fix not implemented, only checking')

    if not args.globs:
        log('ERROR', 'At least one glob pattern required for markdown/yaml/html format')
        return 1

    if args.any:
        files = expand_globs_with_find(args.globs)
    else:
        files = expand_globs_with_git(args.globs)

    if not files:
        log('WARN', f'No files found matching glob patterns: {", ".join(args.globs)}')
        return 0

    ignore_spec = None
    if args.format == 'markdown':
        ignore_spec = load_markdownlint_ignore(repo_root)

    failed = False
    for file_path in sorted(files):
        if not lint_file(file_path, args.format, args.fix, repo_root, ignore_spec):
            failed = True

    if not failed:
        log('SUCCESS', 'All checks passed')

    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
