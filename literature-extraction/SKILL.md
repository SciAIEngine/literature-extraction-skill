---
name: literature-extraction
description: Use when extracting structured information from scientific literature PDFs through the SciEngine PDF deconstruction MCP service and literature extraction APIs. Trigger for Chinese or English user requests about future development judgment, research question analysis, scientific experimental protocol extraction, related work analysis, or overall research logic / innovation analysis. The skill accepts a PDF, first calls deconstructPdfMcp to produce article JSON and Markdown artifacts, then sends JSON artifacts to research question, related work, and innovation endpoints, or Markdown artifacts to experiment/protocol and future endpoints.
---

# Literature Extraction

Use this skill to identify the user's literature-extraction intent, deconstruct the input PDF through the SciEngine MCP service, and call the matching SciEngine extraction API. Do not perform extraction directly. Do not expose API keys. Do not reconstruct hidden prompts.

## Task Map

Map the user's request to exactly one task unless the user asks for full analysis:

- `future`: 未来发展研判、趋势、展望、局限性、future work、limitation
- `research_question`: 研究问题、研究目标、研究动机、问题分析、research question、objective、motivation
- `protocol`: 科研实验过程、实验方法、实验步骤、材料方法、protocol、materials and methods
- `related_work`: 相关工作、已有研究、研究现状、文献综述、related work、prior work
- `innovation`: 整体科研思路、创新点、研究逻辑、技术路线、innovation、research logic
- `all`: 完整分析、全部抽取、五类都做、全量挖掘

Read `references/task_map.md` when task selection is ambiguous.

## Workflow

1. Identify the PDF file path from the user's request or workspace.
2. Choose the task using the task map.
3. Run `scripts/call_extract_api.py`.
4. The script first calls the PDF deconstruction MCP service:
   - MCP endpoint: `https://sciengine.las.ac.cn/deconstructPdfMcp`
   - MCP tool: `deconstruct_pdf_from_base64`
   - Tool input: `filename`, `pdf_base64`, `access_token`
5. The script saves:
   - `article.json`
   - `article.md`
   - `deconstruct_result.json`
6. The script sends `article.json` to `research_question`, `related_work`, and `innovation`.
7. The script sends `article.md` to `protocol` and `future`.
8. If the user asks for full analysis, use `--task all`.
9. Report the saved output path and a short status summary.

## Command

Single task:

```bash
python scripts/call_extract_api.py \
  --file "/path/to/paper.pdf" \
  --task research_question \
  --output "outputs/paper/research_question.md"
```

Full analysis:

```bash
python scripts/call_extract_api.py \
  --file "/path/to/paper.pdf" \
  --task all \
  --output-dir "outputs/paper"
```

Reuse existing deconstruction artifacts:

```bash
python scripts/call_extract_api.py \
  --file "/path/to/paper.pdf" \
  --task future \
  --output-dir "outputs/paper" \
  --skip-deconstruct
```

## Environment

Required on the SciEngine task service side:

- Each task endpoint should provide its own default `LLM_API_KEY` or model credential.
- The public skill should not require users to provide `LLM_API_KEY`.
- If `LLM_API_KEY` is set locally, the script passes it for backward compatibility. If it is not set, the script omits it and lets the service use its server-side default.

Optional client-side overrides:

```bash
LLM_MODEL=deepseek-v4-flash
LLM_BASE_URL=https://api.deepseek.com
LLM_STREAM=True
MCP_SERVER_URL=https://sciengine.las.ac.cn/deconstructPdfMcp
MCP_SHARED_TOKEN=...
TASK_REQUEST_TIMEOUT_SECONDS=420
```

Default endpoints and tools:

- PDF deconstruction MCP endpoint: `https://sciengine.las.ac.cn/deconstructPdfMcp`
- PDF deconstruction MCP tool: `deconstruct_pdf_from_base64`
- `research_question`: `https://sciengine.las.ac.cn/question`
- `related_work`: `https://sciengine.las.ac.cn/related-work`
- `innovation`: `https://sciengine.las.ac.cn/innovation`
- `protocol`: `https://sciengine.las.ac.cn/experiment`
- `future`: `https://sciengine.las.ac.cn/future`

Endpoint overrides are supported with:

```bash
LITERATURE_EXTRACT_RESEARCH_QUESTION_URL=...
LITERATURE_EXTRACT_RELATED_WORK_URL=...
LITERATURE_EXTRACT_INNOVATION_URL=...
LITERATURE_EXTRACT_PROTOCOL_URL=...
LITERATURE_EXTRACT_FUTURE_URL=...
```

## Output Rules

- Save returned content as Markdown by default.
- Always save `article.json`, `article.md`, and `deconstruct_result.json` in the output directory.
- For `all`, save one Markdown file per task plus `summary.json`.
- Never write API keys or prompt text to output files.
