# Literature Extraction Skill

This repository contains a Codex skill for SciEngine scientific literature extraction.

The skill maps natural-language literature-mining requests to five task endpoints:

| Task | Endpoint |
|---|---|
| `research_question` | `https://sciengine.las.ac.cn/question` |
| `related_work` | `https://sciengine.las.ac.cn/related-work` |
| `innovation` | `https://sciengine.las.ac.cn/innovation` |
| `protocol` | `https://sciengine.las.ac.cn/experiment` |
| `future` | `https://sciengine.las.ac.cn/future` |

## Skill Path

The skill folder is:

```text
literature-extraction/
```

## Environment

Do not commit API keys. Configure them locally:

```bash
LLM_API_KEY=...
LLM_MODEL=deepseek-v4-flash
LLM_BASE_URL=https://api.deepseek.com
```

## Example

```bash
python literature-extraction/scripts/call_extract_api.py \
  --file "/path/to/paper.pdf" \
  --task research_question \
  --output "outputs/paper/research_question.md"
```

## Codex Install From GitHub

After publishing this repository to GitHub, install with the skill installer:

```text
$skill-installer install https://github.com/<owner>/<repo>/tree/main/literature-extraction
```

Restart Codex after installation.
