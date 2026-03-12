set dotenv-load := true

default:
    just --list

# Setup IDE environment (just-lsp, shfmt, etc.)
[group('dev')]
setup:
    bash .dev/setup-ides.sh

# Serve the documentation locally with auto-reload
[group('dev')]
dev:
    uv run mkdocs serve --livereload

# Lint markdown files
[group('dev')]
lint fix="" any="":
    uv run python .dev/lint.py --format markdown {{ if fix != "" { "--fix" } else { "" } }} {{ if any != "" { "--any" } else { "" } }} "**/*.md"

# Lint YAML files
[group('dev')]
lint-yaml any="":
    uv run python .dev/lint.py --format yaml {{ if any != "" { "--any" } else { "" } }} "**/*.yml" "**/*.yaml"

# Build the prod documentation
[group('ci')]
build:
    rm -rf site/
    uv run mkdocs build

# Convert all markdown files to HTML and chatbot YAML
[group('ci')]
md2html out="out":
    uv run python .dev/md2html.py --out-dir {{ out }}

# Deploy the site to Cloudflare Pages
[group('ci')]
deploy: build
    npx wrangler pages deploy ./site
