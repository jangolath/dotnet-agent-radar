# dotnet-agent-radar

**Which Roslyn MCP server should your coding agent use? Which SQL Server MCP server is read-only by default? Which T-SQL linter is still maintained?**

This is a short, hand-reviewed list of tools for people building .NET, SQL Server and Azure software with AI agents. Every entry carries a verdict (**use**, **watch** or **avoid**), the honest reason, the license and the last-push date, so you can pick in minutes instead of reading dozens of READMEs.

- **Opinionated on purpose.** Each entry says why, including the caveats.
- **Small on purpose.** About two dozen entries, not hundreds.
- **No composite score.** Stars and rankings move weekly and are not quality. You get facts plus a reviewer's judgment.
- **Kept honest by a script.** A weekly workflow compares each entry with live GitHub data and opens an issue when something drifts. It never edits a verdict by itself.

Full list with reasons: [ENTRIES.md](ENTRIES.md), including side-by-side tables for the Roslyn and SQL Server servers.

## Top 5 starting points

<!-- radar:top5:start -->
- [.NET Agent Skills (official)](https://github.com/dotnet/skills) (use): pick it if you want a baseline set of .NET skills from the people who ship the SDK.
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) (use): pick it if you are building your own agents on .NET and want the vendor-supported route.
- [Microsoft MCP servers (Azure, Fabric)](https://github.com/microsoft/mcp) (use): pick it if your agent needs to work with Azure resources or Fabric.
- [RoslynMcp (MadQ)](https://github.com/MadQ/RoslynMcp) (use): pick it if you want one Roslyn server for navigation plus careful rename, and you are on a current SDK.
- [mssql_mcp_server (RichardHan)](https://github.com/RichardHan/mssql_mcp_server) (use): pick it if you want agents to read from SQL Server with a safe default and do not need DBA diagnostics.
<!-- radar:top5:end -->

## Why this exists

I build a large .NET API ("Project A (.NET API)") with AI coding agents. Every new tool in that workflow raised the same question: is this one trustworthy, maintained and safe to point at my code or my database? I could not find a short, opinionated answer for the .NET and SQL Server corner, so I started writing the list I wanted. This repo is that list, with a script to stop it rotting. If it saves you an afternoon, it did its job.

## How entries are chosen

An entry gets in when it is relevant to .NET, SQL Server or Azure agent work, is public on GitHub, and I have read its README and repository metadata. Entries I would warn people off are included too, so you can recognize them. The bar for adding one is in [CONTRIBUTING.md](CONTRIBUTING.md).

## How to read verdicts

| Verdict | Meaning |
|---|---|
| **use** | A reasonable default for its job today, based on docs and metadata. Read the caveats first. |
| **watch** | Promising, narrow, young or carrying a risk worth knowing. Try it, but do not standardize on it yet. |
| **avoid** | Archived, abandoned, unlicensed or unsafe by default. Do not start new work on it. |

Each entry also shows `last push`, whether the repo is archived and the license as GitHub reports it. These are recorded at review time; the weekly job reports drift.

## Limitations

- I read READMEs and repository metadata. I did **not** run or security-audit these tools. Review anything that touches your code or database yourself, and use least-privilege credentials.
- Tool counts and feature lists are the projects' own claims.
- GitHub only. Last push is a weak signal (a push is not a release).
- A verdict is a snapshot of one reviewer's judgment, dated in the file.
- Not legal advice: "license" is what GitHub detects; check the LICENSE file before depending on a project.

## How the automation works

`scripts/radar.py` (Python standard library only, no telemetry) powers everything:

- `python scripts/radar.py render` regenerates `ENTRIES.md` and the top-5 block above from `data/entries.json`.
- `python scripts/radar.py check` compares each entry with live GitHub metadata and link-checks the URLs.
- The weekly workflow ([freshness.yml](.github/workflows/freshness.yml)) runs `check` with `contents: read` and `issues: write` only, and opens or updates one issue. CI runs the tests and verifies the generated files are current.
- Filling a profile README's top 5 is documented in [docs/PROFILE-README.md](docs/PROFILE-README.md) and is **not enabled**.

## Contributing

Suggestions and stale reports are welcome: use the issue templates, or read [CONTRIBUTING.md](CONTRIBUTING.md). Security concerns: [SECURITY.md](SECURITY.md). Licensed under the [MIT License](LICENSE).
