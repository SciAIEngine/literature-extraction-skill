import argparse
import asyncio
import base64
import json
import os
from io import BytesIO
from pathlib import Path
from typing import Any

import requests


TASKS = ("research_question", "related_work", "innovation", "protocol", "future")
TASK_CHOICES = set(TASKS) | {"all"}

DECONSTRUCT_MCP_URL = "https://sciengine.las.ac.cn/deconstructPdfMcp"
DECONSTRUCT_TOOL_NAME = "deconstruct_pdf_from_base64"
TASK_ENDPOINTS = {
    "research_question": "https://sciengine.las.ac.cn/question",
    "related_work": "https://sciengine.las.ac.cn/related-work",
    "innovation": "https://sciengine.las.ac.cn/innovation",
    "protocol": "https://sciengine.las.ac.cn/experiment",
    "future": "https://sciengine.las.ac.cn/future",
}
TASK_INPUT_KIND = {
    "research_question": "json",
    "related_work": "json",
    "innovation": "json",
    "protocol": "md",
    "future": "md",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run PDF deconstruction MCP and literature extraction tasks.")
    parser.add_argument("--file", required=True, help="Input PDF path.")
    parser.add_argument("--task", required=True, choices=sorted(TASK_CHOICES), help="Extraction task.")
    parser.add_argument("--output", help="Output path for a single task.")
    parser.add_argument("--output-dir", help="Output directory for --task all or default single-task output.")
    parser.add_argument("--extra-input", default=os.environ.get("EXTRA_INPUT", ""), help="Optional extra input for task APIs.")
    parser.add_argument(
        "--skip-deconstruct",
        action="store_true",
        help="Use existing article.json/article.md in output-dir instead of calling the PDF deconstruction MCP.",
    )
    return parser.parse_args()


def api_config():
    api_key = os.environ.get("LLM_API_KEY")
    return {
        "llm_model": os.environ.get("LLM_MODEL", "deepseek-v4-flash"),
        "llm_api_key": api_key,
        "llm_base_url": os.environ.get("LLM_BASE_URL", "https://api.deepseek.com"),
        "stream": os.environ.get("LLM_STREAM", os.environ.get("LITERATURE_EXTRACT_STREAM", "True")),
        "mcp_access_token": os.environ.get("MCP_SHARED_TOKEN", ""),
        "task_timeout": int(os.environ.get("TASK_REQUEST_TIMEOUT_SECONDS", "420")),
    }


def mcp_url():
    return os.environ.get("MCP_SERVER_URL", os.environ.get("LITERATURE_DECONSTRUCT_PDF_URL", DECONSTRUCT_MCP_URL))


def task_endpoint_for(task):
    env_key = f"LITERATURE_EXTRACT_{task.upper()}_URL"
    return os.environ.get(env_key, TASK_ENDPOINTS[task])


def output_base_dir(pdf_path, output_dir=None):
    return Path(output_dir) if output_dir else Path("outputs") / pdf_path.stem


def output_path_for(pdf_path, task, output=None, output_dir=None):
    if output:
        return Path(output)
    return output_base_dir(pdf_path, output_dir) / f"{task}.md"


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def save_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def encode_pdf_to_base64(pdf_path):
    return base64.b64encode(pdf_path.read_bytes()).decode("ascii")


def parse_mcp_tool_result(result: Any) -> dict:
    structured = getattr(result, "structured_content", None)
    if isinstance(structured, dict):
        return structured

    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        return structured

    content = getattr(result, "content", None)
    if content:
        first = content[0]
        text = getattr(first, "text", None)
        if isinstance(text, str) and text.strip():
            return json.loads(text)

    if isinstance(result, dict):
        return result

    raise RuntimeError(f"Cannot parse MCP tool result: {result!r}")


def unwrap_mcp_result(parsed):
    if isinstance(parsed, dict) and "result" in parsed and isinstance(parsed["result"], dict):
        parsed = parsed["result"]

    if isinstance(parsed, dict) and "result" in parsed and isinstance(parsed["result"], str):
        try:
            nested = json.loads(parsed["result"])
        except json.JSONDecodeError:
            nested = None
        if isinstance(nested, dict):
            parsed = nested

    return parsed


async def call_pdf_deconstruct_mcp(pdf_path, work_dir, config):
    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client
    except ImportError as exc:
        raise RuntimeError('Missing dependency. Install with: pip install "mcp[cli]"') from exc

    pdf_base64 = encode_pdf_to_base64(pdf_path)
    async with streamable_http_client(mcp_url()) as streams:
        read_stream = streams[0]
        write_stream = streams[1]
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(
                DECONSTRUCT_TOOL_NAME,
                {
                    "filename": pdf_path.name,
                    "pdf_base64": pdf_base64,
                    "access_token": config["mcp_access_token"],
                },
            )

    parsed = unwrap_mcp_result(parse_mcp_tool_result(result))
    if "article_json" not in parsed or "article_md" not in parsed:
        raise RuntimeError(f"PDF deconstruction result is missing article_json or article_md. Keys: {list(parsed.keys())}")

    article_json = parsed["article_json"]
    article_md = parsed["article_md"] or ""

    article_json_path = work_dir / "article.json"
    article_md_path = work_dir / "article.md"
    raw_path = work_dir / "deconstruct_result.json"

    save_json(article_json_path, article_json)
    save_text(article_md_path, article_md)
    save_json(raw_path, parsed)

    return {
        "json": article_json_path,
        "md": article_md_path,
        "raw": raw_path,
    }


def existing_deconstruction(work_dir):
    json_path = work_dir / "article.json"
    md_path = work_dir / "article.md"
    missing = [str(path) for path in (json_path, md_path) if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing deconstruction artifacts: {', '.join(missing)}")
    return {"json": json_path, "md": md_path, "raw": work_dir / "deconstruct_result.json"}


def task_input_path(task, artifacts):
    return artifacts[TASK_INPUT_KIND[task]]


def build_upload_file(task, input_path):
    input_type = TASK_INPUT_KIND[task]
    if input_type == "json":
        content = input_path.read_text(encoding="utf-8").encode("utf-8")
        return ("article.json", BytesIO(content), "application/json")

    content = input_path.read_text(encoding="utf-8").encode("utf-8")
    return ("article.md", BytesIO(content), "text/markdown")


def parse_task_response(response):
    content_type = response.headers.get("Content-Type", "").lower()
    text = response.text or ""
    if "json" in content_type:
        try:
            return response.json()
        except json.JSONDecodeError:
            return text

    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return text
    return text


def save_task_result(output_path, result):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(result, (dict, list)):
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        output_path.write_text(str(result), encoding="utf-8")


def call_one_task(task, input_path, output_path, extra_input, config):
    data = {
        "LLM_MODEL": config["llm_model"],
        "LLM_BASE_URL": config["llm_base_url"],
        "Stream": config["stream"],
        "extra_input": extra_input,
    }
    if config["llm_api_key"]:
        data["LLM_API_KEY"] = config["llm_api_key"]

    files = {"file": build_upload_file(task, input_path)}
    response = requests.post(
        task_endpoint_for(task),
        data=data,
        files=files,
        timeout=config["task_timeout"],
    )
    response.raise_for_status()
    result = parse_task_response(response)
    save_task_result(output_path, result)
    return {
        "task": task,
        "input": str(input_path),
        "input_kind": TASK_INPUT_KIND[task],
        "output": str(output_path),
        "status": "ok",
    }


async def run(args):
    pdf_path = Path(args.file)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {pdf_path}")
    if args.task == "all" and args.output:
        raise ValueError("--output cannot be used with --task all; use --output-dir instead.")

    config = api_config()
    base_dir = output_base_dir(pdf_path, args.output_dir)
    artifacts = existing_deconstruction(base_dir) if args.skip_deconstruct else await call_pdf_deconstruct_mcp(
        pdf_path,
        base_dir,
        config,
    )

    tasks = TASKS if args.task == "all" else (args.task,)
    results = []
    for task in tasks:
        output_path = output_path_for(
            pdf_path,
            task,
            output=args.output if args.task != "all" else None,
            output_dir=args.output_dir,
        )
        results.append(call_one_task(task, task_input_path(task, artifacts), output_path, args.extra_input, config))

    summary_path = base_dir / "summary.json"
    save_json(
        summary_path,
        {
            "status": "ok",
            "file": str(pdf_path),
            "mcp_url": mcp_url(),
            "deconstruction": {key: str(value) for key, value in artifacts.items()},
            "results": results,
        },
    )
    print(f"Saved summary to: {summary_path}")


def main():
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
