# Input And Output

## Input

The user provides a PDF file path that is readable from the machine where `scripts/call_extract_api.py` runs.

Example:

```text
/data3/SciAIEngine3.0/projects/sunxi/Chain of Thought.pdf
```

## Pipeline

The script runs two stages:

1. PDF deconstruction: call the MCP endpoint `https://sciengine.las.ac.cn/deconstructPdfMcp`.
2. Task extraction: send the deconstruction artifact to the selected task endpoint.

The deconstruction call uses the MCP tool:

```text
deconstruct_pdf_from_base64
```

Tool arguments:

```text
filename
pdf_base64
access_token
```

The deconstruction stage writes:

```text
deconstruct_result.json
article.json
article.md
```

## Task Input Format

| Task | Input sent to task endpoint |
|---|---|
| `research_question` | `article.json` |
| `related_work` | `article.json` |
| `innovation` | `article.json` |
| `protocol` | `article.md` |
| `future` | `article.md` |

## Form Fields

The task extraction stage sends multipart form requests with:

- `LLM_MODEL`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `Stream`
- `extra_input`
- `file`

## Task Endpoints

| Task | Endpoint |
|---|---|
| PDF deconstruction | `https://sciengine.las.ac.cn/deconstructPdfMcp` |
| `research_question` | `https://sciengine.las.ac.cn/question` |
| `related_work` | `https://sciengine.las.ac.cn/related-work` |
| `innovation` | `https://sciengine.las.ac.cn/innovation` |
| `protocol` | `https://sciengine.las.ac.cn/experiment` |
| `future` | `https://sciengine.las.ac.cn/future` |

## Output

The API returns streamed text or normal response text. The script writes the returned content to Markdown files.

For a single task:

```text
outputs/<pdf-stem>/<task>.md
```

For `all`:

```text
outputs/<pdf-stem>/deconstruct_result.json
outputs/<pdf-stem>/article.json
outputs/<pdf-stem>/article.md
outputs/<pdf-stem>/research_question.md
outputs/<pdf-stem>/related_work.md
outputs/<pdf-stem>/innovation.md
outputs/<pdf-stem>/protocol.md
outputs/<pdf-stem>/future.md
outputs/<pdf-stem>/summary.json
```
