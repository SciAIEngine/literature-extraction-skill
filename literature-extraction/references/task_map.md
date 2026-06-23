# Task Map

Use this table to map natural-language user requests to script `--task` values.

| User request | Script task |
|---|---|
| 未来发展、趋势研判、研究展望、局限性、future work、limitations | `future` |
| 研究问题、研究目标、研究动机、问题分析、objective、motivation、research question | `research_question` |
| 科研实验过程、实验方法、实验步骤、材料方法、protocol、materials and methods | `protocol` |
| 相关工作、已有研究、研究现状、文献综述、related work、prior work | `related_work` |
| 整体科研思路、创新点、研究逻辑、技术路线、innovation、research logic | `innovation` |
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

- If the user asks for "创新点", prefer `innovation`.
- If the user asks for "研究问题" or "研究动机", prefer `research_question`.
- If the user asks for "实验怎么做", prefer `protocol`.
- If the user asks for "别人做过什么", prefer `related_work`.
- If the user asks for "未来怎么发展", prefer `future`.
- If two or more tasks are requested, use `all` only when the user clearly wants complete extraction. Otherwise run the requested tasks separately.
