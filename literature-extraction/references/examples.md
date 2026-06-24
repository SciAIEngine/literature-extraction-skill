# Examples

## Research Question

User:

```text
请帮我抽取这篇论文的研究问题：./paper.pdf
```

Command:

```bash
python scripts/call_extract_api.py --file "./paper.pdf" --task research_question --output-dir "outputs/paper"
```

The command first creates `outputs/paper/article.json` and `outputs/paper/article.md`, then sends the JSON artifact to the research-question endpoint.

## Related Work

User:

```text
请帮我分析这篇论文的相关工作：./paper.pdf
```

Task:

```text
related_work
```

## Innovation

User:

```text
请提取这篇论文的整体科研思路和创新点：./paper.pdf
```

Task:

```text
innovation
```

## Protocol

User:

```text
请抽取论文中的科研实验过程：./paper.pdf
```

Task:

```text
protocol
```

This task uses the Markdown deconstruction artifact as input.

## Future

User:

```text
请研判这篇论文的未来发展方向：./paper.pdf
```

Task:

```text
future
```

This task uses the Markdown deconstruction artifact as input.

## Full Analysis

User:

```text
请对这篇论文做完整科技文献抽取：./paper.pdf
```

Task:

```text
all
```

## Reuse PDF Deconstruction

If `outputs/paper/article.json` and `outputs/paper/article.md` already exist, skip the PDF deconstruction MCP call:

```bash
python scripts/call_extract_api.py --file "./paper.pdf" --task future --output-dir "outputs/paper" --skip-deconstruct
```
