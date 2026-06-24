# Literature Extraction Skill

This repository provides a Codex skill for scientific literature extraction from PDF papers.

The skill lets a user ask natural-language questions such as "抽取这篇论文的研究问题" or "对这篇论文做完整科技文献抽取". Codex identifies the target task, deconstructs the PDF, calls the matching SciEngine extraction service, and returns structured Markdown/JSON outputs.

## Capabilities

| User need | Task |
|---|---|
| 研究问题、研究目标、研究动机 | `research_question` |
| 相关工作、已有研究、研究现状 | `related_work` |
| 整体科研思路、创新点、技术路线 | `innovation` |
| 科研实验过程、实验方法、实验步骤 | `protocol` |
| 未来发展研判、趋势、展望、局限性 | `future` |
| 五类任务全部抽取 | `all` |

## Processing Flow

```text
PDF paper
  -> PDF deconstruction MCP service
  -> article.json / article.md
  -> task routing
  -> SciEngine extraction endpoint
  -> Markdown / JSON outputs
```

`research_question`, `related_work`, and `innovation` use `article.json`.

`protocol` and `future` use `article.md`.

Each task extraction request waits up to 420 seconds by default. Set `TASK_REQUEST_TIMEOUT_SECONDS` to override it.

## Environment

Install runtime dependencies on the machine that executes the script:

```bash
pip install requests "mcp[cli]"
```

Do not commit API keys. The public skill does not require users to provide `LLM_API_KEY` if task endpoints use server-side default credentials. Local environment values can still override defaults for testing:

```bash
LLM_MODEL=deepseek-v4-flash
LLM_BASE_URL=https://api.deepseek.com
MCP_SERVER_URL=https://sciengine.las.ac.cn/deconstructPdfMcp
TASK_REQUEST_TIMEOUT_SECONDS=420
```

## User Example

After installing the skill, ask Codex:

```text
请使用 literature-extraction skill，帮我抽取这篇 PDF 的研究问题：

./paper.pdf
```

For full extraction:

```text
请使用 literature-extraction skill，对这篇 PDF 做完整科技文献抽取：

./paper.pdf
```

The skill writes outputs under `outputs/<pdf-stem>/` unless the user specifies another output directory.

## Codex Install From GitHub

Install the skill with the Codex skill installer:

```text
$skill-installer install https://github.com/SciAIEngine/literature-extraction-skill/tree/main/literature-extraction
```

Restart Codex after installation.
