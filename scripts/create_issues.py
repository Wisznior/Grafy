#!/usr/bin/env python3
"""Zakłada na GitHubie labele, Issues z issues/tasks.json (z zależnościami) i issue-śledzące per zestaw.

Wymaga: GitHub CLI (`gh auth login`).
Użycie:
    python scripts/create_issues.py --repo ORG/REPO --dry-run
    python scripts/create_issues.py --repo ORG/REPO
Zadania są tworzone w kolejności z tasks.json (zależności zawsze wcześniej), więc w treści
issue da się wstawić prawdziwe numery: `- [ ] #12 – tytuł`. Taski z zależnościami dostają label `blocked`.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = {
    "zadanie": "0e8a16", "blocked": "d93f0b", "setup": "5319e7", "prezentacja": "fbca04",
    "tracking": "1d76db", "bug": "b60205",
    **{f"zestaw-{i}": c for i, c in zip(range(1, 7), ["c5def5", "bfd4f2", "d4c5f9", "f9d0c4", "fef2c0", "c2e0c6"])},
}


def gh(args, dry, stdin=None):
    cmd = ["gh", *args]
    if dry:
        print("DRY>", " ".join(cmd))
        return "https://github.com/DRY/RUN/issues/0"
    return subprocess.run(cmd, input=stdin, text=True, capture_output=True, check=True).stdout.strip()


def body(task, num):
    def ref(k):
        t = next(x for x in task_index.values() if x["key"] == k)
        return f"- [ ] #{num[k]} – {t['title']}" if k in num else f"- [ ] {k}"
    parts = [f"**Punkty:** {task['points']}", "", "## Opis", task["description"], ""]
    if task["depends_on"]:
        parts += ["## ⛔ Zależy od (blokuje)", "Nie zaczynaj, dopóki te taski nie są zamknięte:",
                  *map(ref, task["depends_on"]), ""]
    else:
        parts += ["## Zależności", "Brak – można zaczynać.", ""]
    if task["soft_depends"]:
        parts += ["## Przydatne (opcjonalnie)", *map(ref, task["soft_depends"]), ""]
    parts += ["## Kryteria akceptacji", *[f"- [ ] {a}" for a in task["acceptance"]], ""]
    if task["source"]:
        parts += ["## Źródło algorytmu", f"{task['source']}  \n(dopisz do `docs/ZRODLA.md`)", ""]
    parts += ["## Definition of Done",
              "- [ ] Algorytm napisany samodzielnie", "- [ ] Testy (zdjęty `@todo`)",
              "- [ ] Komenda CLI do demo", "- [ ] PR zreviewowany przez drugą osobę"]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    tasks = json.loads((ROOT / "issues" / "tasks.json").read_text())
    global task_index
    task_index = {t["key"]: t for t in tasks}

    for name, color in LABELS.items():
        gh(["label", "create", name, "--color", color, "--force", "--repo", a.repo], a.dry_run)

    num = {}
    for t in tasks:
        labels = ["zadanie", *t["labels"], *(["blocked"] if t["depends_on"] else [])]
        args = ["issue", "create", "--repo", a.repo, "--title", t["title"], "--body-file", "-"]
        for l in labels:
            args += ["--label", l]
        url = gh(args, a.dry_run, stdin=body(t, num))
        num[t["key"]] = int(re.search(r"/(\d+)$", url).group(1))
        print(f"{t['key']:5} -> #{num[t['key']]}")

    for z in sorted({t["zestaw"] for t in tasks if t["zestaw"]}):
        items = [t for t in tasks if t["zestaw"] == z]
        text = f"Śledzenie postępu zestawu {z}. Treść: `docs/zestawy/zestaw{z}.md`.\n\n" + \
               "\n".join(f"- [ ] #{num[t['key']]} {t['title']}" for t in items)
        gh(["issue", "create", "--repo", a.repo, "--title", f"[ZESTAW {z}] Tracking",
            "--body-file", "-", "--label", "tracking", "--label", f"zestaw-{z}"], a.dry_run, stdin=text)


if __name__ == "__main__":
    main()
