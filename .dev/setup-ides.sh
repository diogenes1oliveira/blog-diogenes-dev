#!/usr/bin/env bash

set -euo pipefail

usage() {
	cat <<EOF
Usage: ${BASH_SOURCE[0]} [OPTIONS]

Sets up the IDE environments.

Options:
  --dry-run               Don't actually install, just print the command [\$DEV_DRY_RUN]
  --no-envfile            Don't load the .env file [\$DEV_NO_ENVFILE]
  --verbose               Verbose output
  -h, --help              Show this help message and exit

Environment Variables:
  \$DEV_IDES               IDE commands to use, comma separated
  \$DEV_ADHOC_VSIX_URLS    URL of a .vsix extension to override the marketplace, comma separated
EOF
}

REPO_ROOT=
REPO_BIN=
TMPDIR=
VERBOSE=

main() {
	set_vars "$@"
	prepare_tmpdir
	[ -z "$VERBOSE" ] || print_vars

	install_just_lsp
	install_shfmt
	[ -z "$DEV_ADHOC_VSIX_URLS" ] || install_extensions_from_vsix_urls
}

install_just_lsp() (
	if ! is_dry_run && [ -f "$REPO_BIN/just-lsp" ] && uv run --no-sync just-lsp --version >/dev/null 2>&1; then
		echo "INFO: just-lsp is already installed"
		return 0
	fi

	echo "INFO: installing just-lsp"
	maybe_run cargo install just-lsp
	mkdir -p "$REPO_BIN"
	maybe_run ln -s "$(which just-lsp)" "$REPO_BIN/just-lsp"
)

install_shfmt() (
	if ! is_dry_run && [ -f "$REPO_BIN/shfmt" ] && uv run --no-sync shfmt --version >/dev/null 2>&1; then
		echo "INFO: shfmt is already installed"
		return 0
	fi

	echo "INFO: installing shfmt"
	mkdir -p "$REPO_BIN"
	export GOBIN="$REPO_BIN"
	maybe_run go install -v mvdan.cc/sh/v3/cmd/shfmt@latest
)

install_extensions_from_vsix_urls() (
	local IFS=,
	local urls=($DEV_ADHOC_VSIX_URLS)
	local commands=($DEV_IDES)

	for url in "${urls[@]}"; do
		local fname="$url"
		fname="${fname%%\?*}"
		fname="${fname%%\#*}"
		fname="${fname##*/}"
		fname="${fname:-extension.vsix}"
		local output_path="$TMPDIR/$fname"

		echo "INFO: downloading remote extension file: $url"
		maybe_run curl -L -o "$output_path" "$url"

		echo "INFO: installing extension file: $fname"
		for command in "${commands[@]}"; do
			(
				eval set -- "$command"
				maybe_run "$@" --install-extension "$output_path"
			)
		done
	done
)

maybe_run() (
	if [[ "${1:-}" = '-n' ]]; then
		shift
		local nl=
	else
		local nl=1
	fi

	printf >&2 '$ '
	printf >&2 '%q ' "$@"
	[ -z "$nl" ] || printf >&2 '\n'
	if ! is_dry_run; then
		"$@"
	fi
)

require_var() {
	local var_name="$1"
	local msg="${2:-no value for \$$var_name}"

	if [ -z "${!var_name}" ]; then
		usage_error "$msg"
	fi
}

emptify() {
	local var_name="$1"
	local value="${!var_name:-}"
	local value="${value,,}"

	case "$value" in
	1 | yes | true | on)
		eval "$var_name=1"
		;;
	"" | no | false | off)
		eval "$var_name="
		;;
	*)
		printf 'invalid value for $%s: %q' "$var_name" "$value" | usage_error
		;;
	esac
}

usage_error() {
	usage >&2
	echo >&2
	echo >&2 "ERROR: ${1:-$(cat)}"
	exit 1
}

print_vars() {
	for varname in DEV_DRY_RUN DEV_NO_ENVFILE DEV_IDES DEV_ADHOC_VSIX_URLS TMPDIR REPO_BIN; do
		printf >&2 '$ export %s=%q\n' "$varname" "${!varname:-}"
	done
}

load_envfile() {
	if [ -n "$DEV_NO_ENVFILE" ]; then
		echo >&2 "INFO: .env file loading is disabled"
	elif [ -f .env ]; then
		echo >&2 "INFO: loading .env file"
		set -a
		source .env
		set +a
	else
		echo >&2 "INFO: no .env file to load"
	fi
}

set_vars() {
	if ! OPTS="$(getopt -o h --long help,dry-run,no-envfile,verbose -- "$@")"; then
		usage
		exit 1
	fi

	eval set -- "$OPTS"
	local dry_run=

	while true; do
		case "$1" in
		--dry-run)
			dry_run=1
			shift
			;;
		--no-envfile)
			DEV_NO_ENVFILE=1
			shift
			;;
		--verbose)
			VERBOSE=1
			shift
			;;
		--help | -h)
			usage
			exit 0
			;;
		--)
			shift
			break
			;;
		*)
			printf 'invalid option: %q' "$1" | usage_error
			;;
		esac
	done

	emptify DEV_NO_ENVFILE
	load_envfile

	REPO_ROOT="$(dirname "$(dirname "$(realpath "${BASH_SOURCE[0]}")")")"
	REPO_BIN="${REPO_ROOT}/.venv/bin"

	DEV_DRY_RUN="${dry_run:-${DEV_DRY_RUN:-}}"
	DEV_IDES="${DEV_IDES:-code}"
	DEV_ADHOC_VSIX_URLS="${DEV_ADHOC_VSIX_URLS:-}"

	emptify DEV_DRY_RUN
	emptify VERBOSE
	require_var DEV_IDES

	export DEV_DRY_RUN DEV_IDES DEV_ADHOC_VSIX_URLS DEV_NO_ENVFILE REPO_BIN REPO_ROOT
}

prepare_tmpdir() {
	if is_dry_run; then
		TMPDIR='/tmp/some/path'
		return 0
	fi

	TMPDIR="$(mktemp -d)"
	trap 'rm -rf "$TMPDIR"' EXIT
}

is_dry_run() {
	[ -n "$DEV_DRY_RUN" ]
}

main "$@"
