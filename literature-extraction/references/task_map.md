# Task Map

Use this table to map natural-language user requests to script `--task` values.

| User request | Script task |
|---|---|
| 未来发展、趋势研判、研究展望、局限性 | `future` |
| 研究问题、研究目标、研究动机、问题分析 | `research_question` |
| 科研实验过程、实验方法、实验步骤、材料方法 | `protocol` |
| 相关工作、已有研究、研究现状、文献综述 | `related_work` |
| 整体科研思路、创新点、研究逻辑、技术路线 | `innovation` |
| 完整分析、全部抽取、五类都做、全量挖掘 | `all` |

## Input Artifact Routing

The user always provides a PDF. The skill script first calls the PDF deconstruction MCP service and saves `article.json` and `article.md`.

Then route artifacts as follows:

| Script task | Artifact |
|---|---|
| `research_question` | `article.json` |
| `related_work` | `article.json` |
| `innovation` | `article.json` |
| `protocol` | `article.md` |
| `future` | `article.md` |

## Disambiguation

- 用户问“这篇论文解决什么问题、研究目标是什么、为什么做”，选择 `research_question`。
- 用户问“别人做过什么、已有研究有哪些、研究现状如何”，选择 `related_work`。
- 用户问“论文有什么创新、整体思路是什么、技术路线是什么”，选择 `innovation`。
- 用户问“实验怎么做、用了什么方法、步骤是什么”，选择 `protocol`。
- 用户问“未来怎么发展、局限和展望是什么”，选择 `future`。
- 用户明确要求“五类全部、完整抽取、全量分析”时，选择 `all`。
- 如果用户同时提出多个但不是全部任务，分别运行对应任务；不要默认扩大为 `all`。
