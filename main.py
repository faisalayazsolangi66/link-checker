#!/usr/bin/env python3
"""Check a list of URLs and report broken links.

Usage:
    python3 main.py https://example.com https://example.com/missing
    python3 main.py --file urls.txt
    python3 main.py --file urls.txt --timeout 10 --output report.txt
"""
import argparse
import sys
import urllib.error
import urllib.request

DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; link-checker/1.0)"


def check(url, timeout, user_agent):
    """Return (ok, status_or_error). Follows redirects; HEAD falls back to GET."""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(
            url, method=method, headers={"User-Agent": user_agent})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return True, response.status
        except urllib.error.HTTPError as exc:
            if exc.code in (405, 501) and method == "HEAD":
                continue  # server rejects HEAD; retry with GET
            return False, exc.code
        except urllib.error.URLError as exc:
            return False, str(exc.reason)
        except TimeoutError:
            return False, "timeout"
        except (OSError, ValueError) as exc:
            return False, str(exc)
    return False, "HEAD not allowed"


def collect_urls(args):
    urls = list(args.urls)
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        urls.append(line)
        except FileNotFoundError:
            print(f"error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except OSError as exc:
            print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
            sys.exit(1)
    return urls


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check a list of URLs and report broken links.")
    parser.add_argument("urls", nargs="*", help="URL(s) to check")
    parser.add_argument("--file", "-f",
                        help="file with one URL per line (# comments ignored)")
    parser.add_argument("--timeout", type=float, default=10,
                        help="timeout per URL in seconds (default: 10)")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT,
                        help="User-Agent header to send")
    parser.add_argument("--output", "-o", help="write the report to a file")
    parser.add_argument("--ok-only", action="store_true",
                        help="only list working links")
    parser.add_argument("--broken-only", action="store_true",
                        help="only list broken links")
    args = parser.parse_args(argv)

    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")
    if args.ok_only and args.broken_only:
        parser.error("--ok-only and --broken-only cannot be combined")
    urls = collect_urls(args)
    if not urls:
        parser.error("no URLs given: pass URLs on the command line or --file")

    lines = []
    ok_count = 0
    broken_count = 0
    for url in urls:
        parsed_ok = url.startswith(("http://", "https://"))
        if not parsed_ok:
            status, ok = "not http(s)", False
        else:
            ok, status = check(url, args.timeout, args.user_agent)
        if ok:
            ok_count += 1
            line = f"OK     {status}  {url}"
            if not args.broken_only:
                lines.append(line)
                print(line)
        else:
            broken_count += 1
            line = f"BROKEN {status}  {url}"
            if not args.ok_only:
                lines.append(line)
                print(line)

    summary = (f"Checked {len(urls)} URL(s): {ok_count} OK, "
               f"{broken_count} broken.")
    print(summary)
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write("\n".join(lines + [summary]) + "\n")
        except OSError as exc:
            print(f"error: cannot write {args.output}: {exc}", file=sys.stderr)
            return 1
        print(f"Report written to {args.output}")
    return 0 if broken_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
