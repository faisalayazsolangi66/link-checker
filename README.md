# Link Checker

Check a list of URLs and report broken links.

## Requirements

- Python 3 (standard library only — no third-party packages)
- Internet access

## Usage

```bash
python3 main.py https://example.com https://example.com/missing
python3 main.py --file urls.txt
python3 main.py --file urls.txt --timeout 10 --output report.txt
```

## Options

| Option | Description |
| --- | --- |
| `--file`, `-f` | File with one URL per line (`#` lines ignored) |
| `--timeout` | Timeout per URL in seconds (default: `10`) |
| `--user-agent` | User-Agent header to send |
| `--output`, `-o` | Write the report to a file |
| `--ok-only` | Only list working links |
| `--broken-only` | Only list broken links |

Exit code is 0 when every link works and 1 when any link is broken.

## Example

```bash
$ python3 main.py https://example.com https://example.com/no-such-page
OK     200  https://example.com
BROKEN 404  https://example.com/no-such-page
Checked 2 URL(s): 1 OK, 1 broken.
```

## License

MIT — see `LICENSE`.
