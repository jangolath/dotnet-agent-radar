# Contributing

Thanks for helping keep the list short and trustworthy.

## Criteria for adding an entry

An entry must:

1. Be relevant to .NET, SQL Server or Azure work with AI agents (MCP servers, agent frameworks, agent skills/plugins, T-SQL tooling, remote/fleet agent tools).
2. Be public on GitHub with a license GitHub can detect, or be listed with that gap called out (unlicensed projects can be `watch` or `avoid`, never `use`).
3. Have been read by whoever proposes it: README plus repository metadata. Say whether you actually ran it.
4. Bring something the list does not already cover, or a better option in a category that already has entries.

Not accepted: promotion of your own tool without disclosure, entries with no verifiable facts, and anything requiring a composite score.

## How to propose

Open a "Suggest a tool" issue, or send a pull request that edits `data/entries.json` only. Required fields: `id`, `repo`, `name`, `category`, `verdict` (`use`/`watch`/`avoid`), `what`, `reason` (with honest caveats), `pick_if`, `license`, `last_push`, `archived`. Every fact must be checkable (README or API). Then run:

```
python scripts/radar.py render
python -m unittest discover -s tests
```

and commit the regenerated `ENTRIES.md` and `README.md`. CI fails if they are out of date.

## Verdict changes

Verdict changes are made by hand in a pull request, with the reason. The weekly job only reports drift.
