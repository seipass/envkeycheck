# envkeycheck

Compare the *names* of environment variables across dotenv-style files without displaying their values. This helps catch configuration drift between an example file and deployment environments while keeping secrets out of command output.

## Install

```sh
python -m pip install .
```

Requires Python 3.10 or newer. There are no runtime dependencies.

## Usage

```sh
envkeycheck .env.example .env.production
envkeycheck .env.example .env.staging .env.production
python -m envkeycheck .env.example .env.production
```

The first file is the reference. Each following file is compared against it. Output lists only missing or extra variable names; values are never included. The tool does not modify files or evaluate shell syntax.

Supported lines are simple `KEY=value` and `export KEY=value` assignments. Blank lines and lines whose first non-whitespace character is `#` are ignored. Any other non-empty line is reported as malformed. Variable names must follow the common shell identifier form: a letter or underscore followed by letters, digits, or underscores.

Exit codes:

- `0`: all variable-name sets match
- `1`: one or more files have missing or extra names
- `2`: a file cannot be read or contains a malformed line

## Development

```sh
python -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
