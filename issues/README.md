# Definicje tasków
`tasks.json` to źródło prawdy dla Issues. Pola: `key`, `zestaw`, `title`, `points`, `description`,
`acceptance`, `depends_on` (twarde – blokuje, label `blocked`), `soft_depends` (opcjonalne), `source`, `labels`.

Dodawanie zestawów 4–6: dopisz taski na końcu pliku (zależności muszą być *wcześniej* w pliku),
uruchom `python scripts/create_issues.py --repo ORG/REPO --dry-run`.
Ręczne pojedyncze taski: szablon „Zadanie z zestawu” w zakładce New issue.

## Graf zależności
```
Z0 ─► Z1.1 ─┬─► Z1.2
            ├─► Z1.3 ──────────────┐
            ├─► Z2.1 ─┬─► Z2.4     │
            │         └─► Z2.5     ├─► Z3.1 ─┬─► Z3.2 ─► Z3.3 ─► Z3.4
            ├─► Z2.2 ──► Z2.4, Z2.5│         └─► Z3.5
            ├─► Z2.3 ──► Z2.4 ─────┘ (Z2.3 → Z3.1)
            └─► Z2.6
```
Tabela: Z2.4 ← {Z2.1, Z2.2, Z2.3}; Z2.5 ← {Z2.1, Z2.2}; Z3.1 ← {Z1.3, Z2.3}; Z3.2 ← Z3.1; Z3.3 ← Z3.2; Z3.4 ← Z3.3; Z3.5 ← Z3.1.
