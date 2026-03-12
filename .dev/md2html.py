#!/usr/bin/env python3

"""
Convert all markdown files in the repository to HTML and chatbot YAML.

Usage: md2html.py [--out-dir <dir>] [--any]

Outputs:
  <out-dir>/<relative-path>.html  — HTML rendering of the markdown
  <out-dir>/<relative-path>.yaml  — ChatGPT-style conversation thread

The YAML format mirrors the OpenAI Chat API schema (model + messages with roles),
making each section of the markdown a turn in a conversation. This lets you feed
the repo docs straight into an LLM or query them with DuckDB WASM — no extra
conversion step needed. Think of it as a "Guess Who" dataset: each file is a
character card, each section is a clue, and you get to ask the model anything.

Note: No new dependencies needed — markdown is already pulled in by mkdocs.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import markdown
import yaml


def find_repo_root(start_dir: Path) -> Path:
    """
    Find repository root by searching for pyproject.toml or .git directory.

    Args:
        start_dir: Starting directory for upward search

    Returns:
        Path to repo root, or start_dir if no marker found
    """
    current = start_dir.resolve()
    while current != current.parent:
        if (current / 'pyproject.toml').exists() or (current / '.git').exists():
            return current
        current = current.parent
    return start_dir


def parse_markdown_sections(content: str) -> List[Tuple[str, str]]:
    """
    Split markdown content into (heading, body) tuples.

    The first chunk before any heading is yielded as ('', body).
    Each subsequent heading and its content are yielded together.

    Args:
        content: Raw markdown text

    Returns:
        List of (heading, body) tuples
    """
    heading_re = re.compile(r'^(#{1,6}\s+.+)$', re.MULTILINE)
    parts = heading_re.split(content)

    sections: List[Tuple[str, str]] = []
    i = 0
    # parts alternates: body, heading, body, heading, ...
    preamble = parts[i].strip()
    if preamble:
        sections.append(('', preamble))
    i += 1

    while i < len(parts) - 1:
        heading = parts[i].strip()
        body = parts[i + 1].strip()
        if heading or body:
            sections.append((heading, body))
        i += 2

    return sections


def md_to_html(content: str) -> str:
    """
    Convert markdown text to a full HTML document.

    Args:
        content: Raw markdown text

    Returns:
        Complete HTML document string
    """
    body_html = markdown.markdown(
        content,
        extensions=['tables', 'fenced_code', 'toc'],
    )
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "  <title>Document</title>\n"
        "</head>\n"
        "<body>\n"
        f"{body_html}\n"
        "</body>\n"
        "</html>\n"
    )


def md_to_chatbot_yaml(content: str, source_path: str) -> Dict[str, Any]:
    """
    Convert markdown content to a ChatGPT-style conversation thread.

    The schema mirrors the OpenAI Chat Completions API:
      - model: the model identifier (set to "gpt-4o")
      - source: relative path of the original markdown file
      - messages: list of {role, content} dicts

    The system message introduces the document. Each markdown section becomes
    a user/assistant exchange: the user asks about the section topic, and the
    assistant provides the section body as its answer.

    Args:
        content: Raw markdown text
        source_path: Relative path of the source file (used in system prompt)

    Returns:
        Dict ready to be serialised as YAML
    """
    sections = parse_markdown_sections(content)
    messages: List[Dict[str, str]] = [
        {
            'role': 'system',
            'content': (
                f"You are a helpful assistant. The following conversation covers the "
                f"documentation from '{source_path}'. Answer questions based on its content."
            ),
        }
    ]

    for heading, body in sections:
        if heading:
            # Strip leading #s to get plain text topic
            topic = re.sub(r'^#{1,6}\s+', '', heading)
            messages.append({'role': 'user', 'content': f'Tell me about: {topic}'})
        if body:
            messages.append({'role': 'assistant', 'content': body})

    return {
        'model': 'gpt-4o',
        'source': source_path,
        'messages': messages,
    }


def collect_markdown_files(repo_root: Path, include_all: bool) -> List[Path]:
    """
    Collect all markdown files in the repository.

    Args:
        repo_root: Repository root directory
        include_all: If True, include untracked/gitignored files too

    Returns:
        Sorted list of markdown file paths (absolute)
    """
    import fnmatch
    import subprocess

    if not include_all:
        try:
            result = subprocess.run(
                ['git', 'ls-files', '*.md', '**/*.md'],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
            )
            files = [
                repo_root / f
                for f in result.stdout.strip().splitlines()
                if f.endswith('.md')
            ]
            if files:
                return sorted(files)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Fallback: git ls-files without patterns, then filter
        try:
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
            )
            files = [
                repo_root / f
                for f in result.stdout.strip().splitlines()
                if f.endswith('.md') and (repo_root / f).is_file()
            ]
            if files:
                return sorted(files)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Fallback to filesystem scan
    return sorted(repo_root.rglob('*.md'))


def convert_file(md_path: Path, repo_root: Path, out_dir: Path) -> bool:
    """
    Convert a single markdown file to HTML and YAML.

    Args:
        md_path: Absolute path to the markdown file
        repo_root: Repository root directory
        out_dir: Output directory for generated files

    Returns:
        True on success, False on error
    """
    try:
        rel = md_path.relative_to(repo_root)
    except ValueError:
        rel = Path(md_path.name)

    content = md_path.read_text(encoding='utf-8')

    html_path = out_dir / rel.with_suffix('.html')
    yaml_path = out_dir / rel.with_suffix('.yaml')

    html_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    html_path.write_text(md_to_html(content), encoding='utf-8')
    chatbot = md_to_chatbot_yaml(content, str(rel))
    yaml_path.write_text(
        yaml.dump(chatbot, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding='utf-8',
    )

    print(f'  {rel} → {html_path.relative_to(out_dir.parent)} + {yaml_path.relative_to(out_dir.parent)}')
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Convert all repo markdown files to HTML and chatbot YAML.',
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--out-dir',
        default='out',
        metavar='DIR',
        help='Output directory (default: out/)',
    )
    parser.add_argument(
        '--any',
        action='store_true',
        help='Include untracked / gitignored files (default: git-tracked only)',
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = find_repo_root(script_dir)
    out_dir = (repo_root / args.out_dir).resolve()

    md_files = collect_markdown_files(repo_root, include_all=args.any)

    if not md_files:
        print('No markdown files found.')
        return 0

    print(f'Converting {len(md_files)} markdown file(s) → {out_dir}')
    print()

    errors = 0
    for md_path in md_files:
        if not convert_file(md_path, repo_root, out_dir):
            errors += 1

    print()
    if errors:
        print(f'❌  {errors} file(s) failed to convert.')
        return 1

    print(f'✅  All {len(md_files)} file(s) converted successfully.')
    print()
    print('💡  Next step for new developers:')
    print('    Go to Settings → Pages in this repository and set the source to')
    print('    "GitHub Actions" to enable the GitHub Pages deployment workflow.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
