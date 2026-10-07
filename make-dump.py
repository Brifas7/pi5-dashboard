#!/usr/bin/env python3
"""
make-dump.py — build the Pi5 Dashboard source dumps (Part 1-5 markdown docs).

Run from the repo root, after sync-mirrors.sh and after committing:

    ./sync-mirrors.sh
    git add -A && git commit -m "..."
    python3 make-dump.py

Writes dump/Pi5-Dashboard-Code-Part{1..5}-*.md, then upload those to the
Claude project (deleting the previous set first).

Design notes, because the point of this script is that it stays correct
without anyone re-reading it every time:

  * No hardcoded file list. Files are discovered with `git ls-files` and
    routed by RULES below. Anything that matches no rule still lands in
    Part 4 and is reported under "UNROUTED" so you know to look.
  * No hardcoded index.html split line. The split point is found fresh each
    run: the blank line nearest the midpoint.
  * Nothing is retyped. Every byte is read from disk and passed through.
  * The script verifies its own output byte-for-byte before it writes, and
    refuses to write anything if a check fails. A partial dump is worse
    than no dump.
  * A dirty working tree is stamped into the header, so a dump that does
    not match its commit says so on its face.

Exit codes: 0 ok, 1 refused (secrets, verification failure, or bad repo state).
"""

import os
import re
import subprocess
import sys
from datetime import date

# ---------------------------------------------------------------- config ----

OUT_DIR = os.path.expanduser("~/dump")  # outside the web root (~/dashboard-html is served on :8000)

# Files whose contents are deliberately NOT dumped. They still appear in the
# manifest with their true line count and byte size, and get a placeholder
# section explaining the omission. Keep this list tiny and justified.
OMIT_CONTENTS = {
    "chart.min.js": (
        "Unmodified Chart.js vendor library, one minified line, loaded by "
        "index.html. Third-party code, not project source: dumping it adds "
        "~200 KB of unreadable text to this doc and to the context of every "
        "session that reads it, for no auditable value. Delete this entry "
        "from OMIT_CONTENTS in make-dump.py to include it verbatim."
    ),
}

# A line placed directly above a file's code block (outside it).
NOTES = {
    "fix_settings.py": "STALE — one-off script, not part of the running system.",
}

# Mirrors that sync-mirrors.sh produces in a loop or via redirection, which the
# parser below cannot read off a simple `m SRC DST` line. Everything else is
# picked up automatically, so adding a plain `m` line needs no change here.
MIRROR_EXTRA = {
    "system/crontab.txt": "output of `crontab -l`",
    "system/ip-addr.txt": "output of `ip -br addr`, public IPv6 masked by sync-mirrors.sh",
    "system/listening.txt": "output of `sudo ss -tulnp`, public IPv6 masked by sync-mirrors.sh",
    "system/dnsmasq.conf": "/etc/dnsmasq.conf, comments and blank lines stripped",
    "system/sshd-dropins.conf": "concatenation of /etc/ssh/sshd_config.d/*.conf",
    "system/nginx/ENABLED.txt": "output of `ls -1 /etc/nginx/sites-enabled/`",
}
for _u in ("dashboard-api", "rak-reader", "automation-engine", "engine-v2"):
    MIRROR_EXTRA[f"system/systemd/{_u}.service"] = f"/etc/systemd/system/{_u}.service"

# Routing rules, first match wins. (part, predicate) over the repo-relative path.
# Part 2/3 handle index.html separately; it must not appear here.
RULES = [
    (1, lambda p: p in ("main.py.txt", "rak_reader.py", "automation_engine.py",
                        "frigate-config.yml.txt", "sync-mirrors.sh")),
    (1, lambda p: p.startswith("engine-v2/")),
    (1, lambda p: p.startswith("system/")),
    (3, lambda p: "/" not in p and p.endswith(".js")),
    (5, lambda p: p.startswith("m/")),
    # Every other root-level file is a Part 4 page/config by the brief's rule.
    # This is a real rule, not the fallback: a new root-level page belongs here
    # and is not a surprise. The fallback below fires only for a path shape
    # nobody anticipated — typically a brand-new top-level directory — which is
    # exactly the case where a human should decide where it goes.
    (4, lambda p: "/" not in p),
]

# Warn if a doc gets bigger than this (KB). Not a hard limit; project docs have
# practical size limits and Part 1 has been growing.
SIZE_WARN_KB = 100

DOC_FILES = {
    1: ("Pi5-Dashboard-Code-Part1-Backend-System.md",
        "Pi5 Dashboard — Part 1: Backend & System"),
    2: ("Pi5-Dashboard-Code-Part2-Frontend-A.md",
        "Pi5 Dashboard — Part 2: Frontend A"),
    3: ("Pi5-Dashboard-Code-Part3-Frontend-B.md",
        "Pi5 Dashboard — Part 3: Frontend B"),
    4: ("Pi5-Dashboard-Code-Part4-Automation-Sensors-Pages.md",
        "Pi5 Dashboard — Part 4: Pages, Config & Miscellany"),
    5: ("Pi5-Dashboard-Code-Part5-Mobile.md",
        "Pi5 Dashboard — Part 5: Mobile (m/)"),
}

# Ordering within Part 1 so the engines read in sequence; anything unlisted
# keeps its sorted position after these.
PART1_ORDER = ["main.py.txt", "rak_reader.py", "automation_engine.py"]

SPLIT_FILE = "index.html"

# Hard-stop patterns. If any matches, nothing is written.
SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN[ A-Z]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\b(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("WiFi passphrase", re.compile(
        r"^[^\n]*\b(psk|wpa[-_]?passphrase|wifi[-_]?pass(word|wd)?)\b\s*[:=]\s*\S",
        re.I | re.M)),
]

LANG = {
    ".py": "python", ".html": "html", ".js": "javascript", ".json": "json",
    ".yml": "yaml", ".yaml": "yaml", ".txt": "text", ".sh": "bash",
    ".service": "ini", ".desktop": "ini", ".conf": "ini", ".css": "css",
}

# ----------------------------------------------------------------- utils ----


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def die(msg):
    print(f"\nREFUSED: {msg}\n", file=sys.stderr)
    sys.exit(1)


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def linecount(text):
    """Visual line count: a trailing partial line (no final newline) counts."""
    if text == "":
        return 0
    parts = text.split("\n")
    if parts[-1] == "":
        parts = parts[:-1]
    return len(parts)


def is_text(path):
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
        if b"\0" in chunk:
            return False
        chunk.decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


def lang_for(path, content):
    base = os.path.basename(path)
    if base == ".gitignore":
        return "text"
    ext = os.path.splitext(base)[1]
    if ext in LANG:
        return LANG[ext]
    if path.startswith("system/nginx/"):
        return "nginx"
    first = content.split("\n", 1)[0]
    if first.startswith("#!"):
        if "python" in first:
            return "python"
        if "bash" in first or "sh" in first:
            return "bash"
    return "text"


def fence_for(content):
    """A fence strictly longer than the longest backtick run inside content."""
    runs = [len(m) for m in re.findall(r"`+", content)]
    return "`" * max(3, (max(runs) + 1) if runs else 3)


def route(path):
    for part, pred in RULES:
        if pred(path):
            return part, True
    return 4, False


# ------------------------------------------------------------ repo state ----

if not os.path.isdir(".git"):
    die("run this from the repo root (no .git here).")

branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD").strip()
head = sh("git", "rev-parse", "HEAD").strip()
cdate = sh("git", "log", "-1", "--format=%cd").strip()
cmsg = sh("git", "log", "-1", "--format=%s").strip()
# Only *tracked* files matter for fidelity: the dump reads tracked paths from
# the working tree, so a modified tracked file means the content will not match
# the commit stamped in the header. Untracked files (this script before it is
# committed, the dump/ output itself) are never read into a doc.
dirty = [l for l in sh("git", "status", "--porcelain").split("\n")
         if l.strip() and not l.startswith("??")]

tracked = [p for p in sh("git", "ls-files").split("\n") if p]
missing = [p for p in tracked if not os.path.exists(p)]
if missing:
    die(f"{len(missing)} tracked file(s) missing from the working tree, "
        f"e.g. {missing[:3]}. Commit or restore first.")

text_files = [p for p in tracked if is_text(p)]
binaries = [p for p in tracked if p not in set(text_files)]

# frigate-config.yml is a byte-identical twin of the .txt in this repo; dump once.
dup_note = None
if "frigate-config.yml" in text_files and "frigate-config.yml.txt" in text_files:
    if read("frigate-config.yml") == read("frigate-config.yml.txt"):
        text_files.remove("frigate-config.yml")
        dup_note = ("frigate-config.yml", "byte-identical to frigate-config.yml.txt")

# ---------------------------------------------------------- secret gate ----

hits = []
for p in text_files:
    if p in OMIT_CONTENTS:
        continue
    body = read(p)
    for label, rx in SECRET_PATTERNS:
        m = rx.search(body)
        if m:
            line = body[:m.start()].count("\n") + 1
            hits.append(f"{p}:{line}  ({label})")
if hits:
    die("possible credentials found; nothing written. Review these:\n  "
        + "\n  ".join(hits))

# --------------------------------------------------------- mirror parsing ----

mirrors = dict(MIRROR_EXTRA)
if os.path.exists("sync-mirrors.sh"):
    src = read("sync-mirrors.sh")
    home = "/home/brifas"
    mh = re.search(r"^\s*H=(\S+)", src, re.M)
    if mh:
        home = mh.group(1)
    for m in re.finditer(r"^\s*m\s+(\S+)\s+(\S+)\s*$", src, re.M):
        s, d = m.group(1), m.group(2)
        if "*" in s or "$" in d or "$u" in s or "$f" in s:
            continue
        mirrors.setdefault(d, s.replace("$H", home).replace("${H}", home))

# ------------------------------------------------------------- split file ----

split_line = None
if SPLIT_FILE in text_files:
    with open(SPLIT_FILE, "r", encoding="utf-8", newline="") as f:
        idx_lines = f.readlines()
    total = len(idx_lines)
    mid = total // 2
    blanks = [i for i, l in enumerate(idx_lines) if l.strip() == ""]
    if blanks:
        # nearest blank line to the midpoint; split AFTER it
        split_line = min(blanks, key=lambda i: abs(i - mid)) + 1
    else:
        split_line = mid
    text_files.remove(SPLIT_FILE)
    partA = "".join(idx_lines[:split_line])
    partB = "".join(idx_lines[split_line:])
    if partA + partB != read(SPLIT_FILE):
        die(f"{SPLIT_FILE} split is not lossless.")

# ---------------------------------------------------------------- routing ----

assign, unrouted = {p: 4 for p in []}, []
for p in sorted(text_files):
    part, matched = route(p)
    assign[p] = part
    if not matched:
        unrouted.append(p)

parts = {n: [] for n in DOC_FILES}
for p, n in assign.items():
    parts[n].append(p)
for n in parts:
    parts[n].sort()
# apply the Part 1 preferred ordering
head1 = [p for p in PART1_ORDER if p in parts[1]]
parts[1] = head1 + [p for p in parts[1] if p not in head1]

# ----------------------------------------------------------- doc assembly ----


def doc_header():
    stamp = (f"Generated by make-dump.py on {date.today():%B %-d, %Y}. "
             f"Verbatim copy — code after this commit is NOT reflected here.")
    warn = ""
    if dirty:
        warn = ("\n*** WORKING TREE WAS DIRTY WHEN THIS RAN — the files below do NOT\n"
                "*** necessarily match the commit above. Commit, then re-run.")
    return ("```\n"
            f"Repo: {branch} @ {os.path.basename(os.getcwd())}  |  Branch: {branch}\n"
            f"Commit: {head}  |  {cdate}  |  \"{cmsg}\"\n"
            f"{stamp}{warn}\n"
            "```\n")


def block(path, content=None, heading=None):
    if content is None:
        content = read(path)
    out = [f"### {heading or path}"]
    if path in mirrors:
        out.append(f"Mirrors: {mirrors[path]}")
    if path in NOTES:
        out.append(NOTES[path])
    f = fence_for(content)
    body, tail = content, ""
    if body != "" and not body.endswith("\n"):
        # The closing fence must begin its own line or the block will not
        # render. This newline is a delimiter only; the file's bytes are intact.
        body += "\n"
        tail = ("\n*(source file has no trailing newline; the newline before "
                "the closing fence is not part of the file)*")
    return "\n".join(out) + f"\n\n{f}{lang_for(path, content)}\n{body}{f}\n" + tail + "\n"


def omitted_block(path):
    return (f"### {path}\n\n**Contents deliberately omitted.** {OMIT_CONTENTS[path]}\n"
            f"It is listed in the Part 1 manifest with its true line count and "
            f"byte size. Nothing else in this dump is abridged.\n")


# manifest
rows = []
for n in sorted(parts):
    if n == 2 and split_line is not None:   # Part 2 holds only half of index.html, listed below
        continue
    for p in parts[n]:
        tag = f"Part {n}"
        if p in OMIT_CONTENTS:
            tag += " (listed; contents omitted)"
        rows.append((p, linecount(read(p)), os.path.getsize(p), tag))
if split_line is not None:
    rows.append((f"{SPLIT_FILE} (lines 1–{split_line})", split_line,
                 len(partA.encode()), "Part 2"))
    rows.append((f"{SPLIT_FILE} (lines {split_line+1}–{total})", total - split_line,
                 len(partB.encode()), "Part 3"))
if dup_note:
    rows.append((dup_note[0], linecount(read(dup_note[0])),
                 os.path.getsize(dup_note[0]), f"— (not dumped; {dup_note[1]})"))
rows.sort(key=lambda r: (r[3], r[0]))

man = ["## Manifest", "",
       "Every included file, with the line count and byte size it has in the "
       "repo at this commit.", "",
       "| File | Lines | Bytes | Part |", "|---|---:|---:|---|"]
man += [f"| `{p}` | {lc} | {sz:,} | {t} |" for p, lc, sz, t in rows]
man += ["", f"Excluded: {len(binaries)} binary file(s), `.git/`.", ""]
MANIFEST = "\n".join(man) + "\n"

docs = {}
for n, (fname, title) in DOC_FILES.items():
    body = [f"# {title}", ""]
    if n == 1:
        body += [doc_header(), MANIFEST, ""]
    elif n == 2 and split_line is not None:
        body += [f"`{SPLIT_FILE}` lines 1–{split_line} of {total}. Continues in Part 3.",
                 "", doc_header(), ""]
    elif n == 3 and split_line is not None:
        body += [f"`{SPLIT_FILE}` lines {split_line+1}–{total} of {total} "
                 f"(continued from Part 2), then the root-level JavaScript.",
                 "", doc_header(), ""]
    else:
        body += [doc_header(), ""]

    if n == 2 and split_line is not None:
        body.append(block(SPLIT_FILE, content=partA,
                          heading=f"{SPLIT_FILE}  (lines 1–{split_line} of {total})"))
    if n == 3 and split_line is not None:
        body.append(block(SPLIT_FILE, content=partB,
                          heading=f"{SPLIT_FILE}  (lines {split_line+1}–{total} of {total})"))
    for p in parts[n]:
        body.append(omitted_block(p) if p in OMIT_CONTENTS else block(p))
    docs[n] = "\n".join(body)

# ------------------------------------------------------------ verification ----


def extract(md):
    """Parse '### path' sections and the fenced block under each, line-wise."""
    lines = md.splitlines(keepends=True)
    out, i, n = [], 0, len(lines)
    while i < n:
        m = re.match(r"^### (\S.*?)\s*$", lines[i])
        if not m:
            i += 1
            continue
        name, j = m.group(1), i + 1
        while j < n and not re.match(r"^`{3,}", lines[j]):
            if re.match(r"^### ", lines[j]):
                break
            j += 1
        if j >= n or re.match(r"^### ", lines[j]):
            out.append((name, None))
            i = j
            continue
        fence = re.match(r"^(`{3,})", lines[j]).group(1)
        j += 1
        start = j
        while j < n and lines[j].rstrip("\n") != fence:
            j += 1
        out.append((name, "".join(lines[start:j])))
        i = j + 1
    return out


problems, seen, idx_blocks = [], {}, {}
for n, md in docs.items():
    for name, blk in extract(md):
        if name.startswith(SPLIT_FILE) and split_line is not None:
            idx_blocks[n] = blk
            continue
        seen.setdefault(name, []).append(n)
        if blk is None:
            if name not in OMIT_CONTENTS:
                problems.append(f"{name}: heading with no code block")
            continue
        src = read(name)
        ok = (blk == src) if src.endswith("\n") else (blk == src + "\n")
        if not ok:
            problems.append(f"{name}: block does not match source byte-for-byte")
        elif linecount(blk) != linecount(src):
            problems.append(f"{name}: line count {linecount(blk)} != {linecount(src)}")

if split_line is not None:
    if idx_blocks.get(2, "") + idx_blocks.get(3, "") != read(SPLIT_FILE):
        problems.append(f"{SPLIT_FILE}: parts 2+3 do not reconstruct the file")

expected = set(text_files)
if split_line is not None:
    expected.discard(SPLIT_FILE)
for p in sorted(expected - set(seen)):
    problems.append(f"{p}: tracked text file missing from every doc")
for p, where in sorted(seen.items()):
    if len(where) > 1:
        problems.append(f"{p}: appears in parts {where}")

if problems:
    die("verification failed; nothing written.\n  " + "\n  ".join(problems))

# ----------------------------------------------------------------- write ----

os.makedirs(OUT_DIR, exist_ok=True)
for n, (fname, _) in DOC_FILES.items():
    with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
        f.write(docs[n])

# ---------------------------------------------------------------- report ----

print(f"\nPi5 dashboard source dump — {date.today():%Y-%m-%d}")
print(f"  commit   {head[:12]}  {cdate}")
print(f"           \"{cmsg}\"")
print(f"  branch   {branch}")
if dirty:
    print("  WARNING  working tree is DIRTY — docs are stamped as not matching "
          "this commit.\n           Commit and re-run before uploading.")
print(f"\n  {len(seen)} files dumped, {len(binaries)} binaries skipped", end="")
if dup_note:
    print(f", 1 duplicate skipped ({dup_note[0]})", end="")
print(".")
if split_line is not None:
    print(f"  {SPLIT_FILE}: {total} lines split {split_line} / {total - split_line} "
          f"at a blank line, verified lossless.")
print("  verification: every block matches source byte-for-byte.\n")
oversize = []
for n, (fname, _) in DOC_FILES.items():
    size = os.path.getsize(os.path.join(OUT_DIR, fname))
    count = len(parts[n])
    if n in (2, 3) and split_line is not None:
        count += 1  # its half of the split file
    flag = ""
    if size / 1024 > SIZE_WARN_KB:
        flag = "  <-- large"
        oversize.append((fname, size))
    print(f"    {fname:52s} {size/1024:7.1f} KB  ({count} files){flag}")
if oversize:
    print(f"\n  Note: {len(oversize)} doc(s) over {SIZE_WARN_KB} KB. If the project "
          "rejects one,\n  split it by moving a rule in make-dump.py (e.g. engine-v2/ "
          "to its own part).")
if OMIT_CONTENTS:
    inrepo = [p for p in OMIT_CONTENTS if p in set(tracked)]
    if inrepo:
        print(f"\n  contents omitted by config: {', '.join(inrepo)}")
if unrouted:
    print("\n  *** UNROUTED — these matched no rule and went to Part 4 by "
          "fallback.\n  *** If that is wrong, add a rule in make-dump.py:")
    for p in unrouted:
        print(f"        {p}")
print(f"\n  Upload {OUT_DIR}/ to the Claude project, deleting the previous set first.\n")
