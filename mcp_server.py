"""
SAP FI/TR Knowledge Base — MCP Server
========================================
Model Context Protocol 서버 구현체.
로컬 knowledge-base/ 폴더를 MCP 도구로 노출하여
AI 에이전트가 실시간으로 업무 노트를 검색할 수 있도록 합니다.

실행 방법:
  python mcp_server.py
  python mcp_server.py --kb-path ./knowledge-base --port 8765
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# ── MCP SDK import (graceful fallback) ───────────────────────────────────────
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("[WARNING] mcp 패키지가 설치되지 않았습니다. pip install mcp 실행 후 재시작하세요.", file=sys.stderr)

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_KB_PATH = Path(__file__).parent / "knowledge-base"
SERVER_NAME = "sap-fi-tr-knowledge-base"
SERVER_VERSION = "1.0.0"


# ──────────────────────────────────────────────────────────────────────────────
# Knowledge Base Utilities
# ──────────────────────────────────────────────────────────────────────────────

def load_documents(kb_path: Path) -> dict[str, str]:
    """지정 경로의 .md / .txt 파일 로드"""
    docs: dict[str, str] = {}
    for ext in ("*.md", "*.txt"):
        for fp in sorted(kb_path.glob(ext)):
            try:
                docs[fp.name] = fp.read_text(encoding="utf-8")
            except Exception as e:
                docs[fp.name] = f"[읽기 오류: {e}]"
    return docs


def keyword_search(
    query: str,
    docs: dict[str, str],
    top_k: int = 5,
    min_score: float = 0.05,
) -> list[dict[str, Any]]:
    """키워드 기반 관련도 검색"""
    query_tokens = set(re.findall(r"[가-힣a-zA-Z0-9_/]{2,}", query.lower()))
    if not query_tokens:
        return []

    results: list[tuple[float, str, str]] = []
    for name, content in docs.items():
        content_lower = content.lower()
        # 단어 빈도 + 위치 보너스
        token_scores: list[float] = []
        for token in query_tokens:
            count = content_lower.count(token)
            score = min(count * 0.2, 1.0)  # 최대 1.0
            token_scores.append(score)
        avg_score = sum(token_scores) / len(token_scores) if token_scores else 0
        if avg_score >= min_score:
            results.append((avg_score, name, content))

    results.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "filename": name,
            "score": round(score, 4),
            "content": content,
            "excerpt": _extract_excerpt(content, query_tokens),
            "char_count": len(content),
        }
        for score, name, content in results[:top_k]
    ]


def _extract_excerpt(content: str, query_tokens: set[str], window: int = 300) -> str:
    """쿼리 토큰 근처의 문맥 발췌"""
    content_lower = content.lower()
    best_pos = 0
    best_count = 0

    for i in range(0, len(content) - window, 50):
        chunk = content_lower[i : i + window]
        count = sum(1 for t in query_tokens if t in chunk)
        if count > best_count:
            best_count = count
            best_pos = i

    excerpt = content[best_pos : best_pos + window]
    return excerpt.strip()


def list_documents(kb_path: Path) -> list[dict[str, Any]]:
    """지식베이스 문서 목록 반환"""
    docs = []
    for ext in ("*.md", "*.txt"):
        for fp in sorted(kb_path.glob(ext)):
            stat = fp.stat()
            docs.append({
                "filename": fp.name,
                "extension": fp.suffix,
                "size_bytes": stat.st_size,
                "modified": stat.st_mtime,
            })
    return docs


def read_document(filename: str, kb_path: Path) -> dict[str, Any]:
    """특정 문서 전문 반환"""
    fp = kb_path / filename
    # 경로 탈출 방지 (보안)
    try:
        fp.resolve().relative_to(kb_path.resolve())
    except ValueError:
        return {"error": "잘못된 파일 경로입니다."}

    if not fp.exists():
        return {"error": f"파일을 찾을 수 없습니다: {filename}"}
    if fp.suffix not in (".md", ".txt"):
        return {"error": "지원하지 않는 파일 형식입니다 (.md, .txt만 허용)."}

    try:
        content = fp.read_text(encoding="utf-8")
        return {
            "filename": fp.name,
            "content": content,
            "char_count": len(content),
        }
    except Exception as e:
        return {"error": f"파일 읽기 오류: {e}"}


def write_document(filename: str, content: str, kb_path: Path) -> dict[str, Any]:
    """새 문서 저장 (보안: .md / .txt 확장자만 허용)"""
    if not filename.endswith((".md", ".txt")):
        filename += ".md"

    # 경로 탈출 방지
    fp = kb_path / Path(filename).name  # 디렉토리 트래버설 차단
    try:
        kb_path.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return {"success": True, "filename": fp.name, "bytes_written": len(content.encode("utf-8"))}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ──────────────────────────────────────────────────────────────────────────────
# MCP Server Definition
# ──────────────────────────────────────────────────────────────────────────────

def create_server(kb_path: Path) -> "Server":
    """MCP Server 인스턴스 생성 및 도구 등록"""
    server = Server(SERVER_NAME)

    # ── Tool: search_knowledge_base ──────────────────────────────────────────
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="search_knowledge_base",
                description=(
                    "SAP FI/TR 업무 노트 지식베이스에서 관련 문서를 검색합니다. "
                    "질문에 관련된 문서와 발췌문을 반환합니다."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "검색할 키워드 또는 질문",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "반환할 최대 문서 수 (기본: 3, 최대: 10)",
                            "default": 3,
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="list_documents",
                description="지식베이스의 모든 문서 목록을 반환합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="read_document",
                description="지식베이스에서 특정 문서의 전체 내용을 읽습니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "읽을 파일명 (예: fi_gl_process.md)",
                        },
                    },
                    "required": ["filename"],
                },
            ),
            types.Tool(
                name="write_document",
                description="지식베이스에 새 문서를 저장하거나 기존 문서를 업데이트합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "저장할 파일명 (예: new_note.md)",
                        },
                        "content": {
                            "type": "string",
                            "description": "저장할 내용 (Markdown 형식 권장)",
                        },
                    },
                    "required": ["filename", "content"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        docs = load_documents(kb_path)

        if name == "search_knowledge_base":
            query = arguments.get("query", "")
            top_k = min(int(arguments.get("top_k", 3)), 10)
            results = keyword_search(query, docs, top_k=top_k)

            if not results:
                text = f"'{query}'에 관련된 문서를 찾지 못했습니다. 지식베이스에 관련 노트를 추가해주세요."
            else:
                lines = [f"## 검색 결과: '{query}' ({len(results)}건)\n"]
                for i, r in enumerate(results, 1):
                    lines.append(
                        f"### [{i}] {r['filename']} (관련도: {r['score']})\n"
                        f"**발췌:**\n```\n{r['excerpt']}\n```\n"
                    )
                text = "\n".join(lines)

            return [types.TextContent(type="text", text=text)]

        elif name == "list_documents":
            doc_list = list_documents(kb_path)
            if not doc_list:
                text = "지식베이스가 비어 있습니다. knowledge-base/ 폴더에 .md 또는 .txt 파일을 추가하세요."
            else:
                lines = [f"## 지식베이스 문서 목록 ({len(doc_list)}개)\n"]
                for d in doc_list:
                    size_kb = d["size_bytes"] / 1024
                    lines.append(f"- **{d['filename']}** ({size_kb:.1f} KB)")
                text = "\n".join(lines)
            return [types.TextContent(type="text", text=text)]

        elif name == "read_document":
            filename = arguments.get("filename", "")
            result = read_document(filename, kb_path)
            if "error" in result:
                text = f"❌ 오류: {result['error']}"
            else:
                text = f"## {result['filename']}\n\n{result['content']}"
            return [types.TextContent(type="text", text=text)]

        elif name == "write_document":
            filename = arguments.get("filename", "")
            content = arguments.get("content", "")
            result = write_document(filename, content, kb_path)
            if result.get("success"):
                text = f"✅ '{result['filename']}' 저장 완료 ({result['bytes_written']} bytes)"
            else:
                text = f"❌ 저장 오류: {result.get('error', '알 수 없는 오류')}"
            return [types.TextContent(type="text", text=text)]

        else:
            return [types.TextContent(type="text", text=f"알 수 없는 도구: {name}")]

    return server


# ──────────────────────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────────────────────

async def main(kb_path: Path):
    if not MCP_AVAILABLE:
        print("❌ mcp 패키지가 없어 서버를 시작할 수 없습니다.", file=sys.stderr)
        print("   pip install mcp 실행 후 재시작하세요.", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 SAP FI/TR Knowledge Base MCP Server v{SERVER_VERSION} 시작", file=sys.stderr)
    print(f"📂 지식베이스 경로: {kb_path.resolve()}", file=sys.stderr)

    docs = load_documents(kb_path)
    print(f"📄 로드된 문서: {len(docs)}개", file=sys.stderr)

    server = create_server(kb_path)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="SAP FI/TR Knowledge Base MCP Server")
    parser.add_argument(
        "--kb-path",
        type=Path,
        default=DEFAULT_KB_PATH,
        help="지식베이스 폴더 경로 (기본: ./knowledge-base)",
    )
    args = parser.parse_args()

    kb_path = args.kb_path
    kb_path.mkdir(parents=True, exist_ok=True)

    asyncio.run(main(kb_path))
