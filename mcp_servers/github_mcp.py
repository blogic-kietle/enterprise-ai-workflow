"""
GitHub MCP Server for Enterprise AI Workflow
Cung cấp các tools để AI Agent tương tác với GitHub:
- Tạo branch mới
- Đọc/ghi file
- Commit và push code
- Tạo Pull Request
- Đọc nội dung repository
"""

import asyncio
import json
import os
import base64
from typing import Any
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ─── Configuration ────────────────────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API_BASE = "https://api.github.com"

app = Server("github-mcp")

# ─── HTTP Client ──────────────────────────────────────────────────────────────
def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def github_request(method: str, path: str, **kwargs) -> dict:
    url = f"{GITHUB_API_BASE}{path}"
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method, url, headers=get_headers(), timeout=30, **kwargs
        )
        response.raise_for_status()
        return response.json() if response.content else {}


# ─── Tools ────────────────────────────────────────────────────────────────────
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="github_get_repo",
            description="Lấy thông tin repository GitHub",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Owner của repository"},
                    "repo": {"type": "string", "description": "Tên repository"},
                },
                "required": ["owner", "repo"],
            },
        ),
        Tool(
            name="github_list_branches",
            description="Liệt kê tất cả branches của repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                },
                "required": ["owner", "repo"],
            },
        ),
        Tool(
            name="github_create_branch",
            description="Tạo branch mới từ một branch hoặc commit SHA",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "branch_name": {"type": "string", "description": "Tên branch mới (ví dụ: feature/PROJ-123-add-user-list)"},
                    "from_branch": {"type": "string", "description": "Branch gốc để tạo từ (mặc định: main)", "default": "main"},
                },
                "required": ["owner", "repo", "branch_name"],
            },
        ),
        Tool(
            name="github_get_file",
            description="Đọc nội dung một file trong repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "path": {"type": "string", "description": "Đường dẫn file trong repository"},
                    "branch": {"type": "string", "description": "Branch để đọc (mặc định: main)", "default": "main"},
                },
                "required": ["owner", "repo", "path"],
            },
        ),
        Tool(
            name="github_create_or_update_file",
            description="Tạo mới hoặc cập nhật một file trong repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "path": {"type": "string", "description": "Đường dẫn file"},
                    "content": {"type": "string", "description": "Nội dung file (plain text)"},
                    "message": {"type": "string", "description": "Commit message"},
                    "branch": {"type": "string", "description": "Branch để commit"},
                },
                "required": ["owner", "repo", "path", "content", "message", "branch"],
            },
        ),
        Tool(
            name="github_create_pull_request",
            description="Tạo Pull Request mới",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "title": {"type": "string", "description": "Tiêu đề PR"},
                    "body": {"type": "string", "description": "Mô tả PR"},
                    "head": {"type": "string", "description": "Branch nguồn (feature branch)"},
                    "base": {"type": "string", "description": "Branch đích (thường là main hoặc develop)", "default": "main"},
                },
                "required": ["owner", "repo", "title", "body", "head"],
            },
        ),
        Tool(
            name="github_list_files",
            description="Liệt kê tất cả files trong một thư mục của repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "path": {"type": "string", "description": "Đường dẫn thư mục (để trống để xem root)", "default": ""},
                    "branch": {"type": "string", "description": "Branch", "default": "main"},
                },
                "required": ["owner", "repo"],
            },
        ),
        Tool(
            name="github_read_agent_context",
            description="Đọc toàn bộ context từ thư mục .agent/ của repository (ARCHITECTURE.md, RULES.md, SKILL.md)",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string"},
                    "repo": {"type": "string"},
                    "branch": {"type": "string", "default": "main"},
                },
                "required": ["owner", "repo"],
            },
        ),
    ]


# ─── Tool Handlers ─────────────────────────────────────────────────────────────
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "github_get_repo":
            result = await github_request("GET", f"/repos/{arguments['owner']}/{arguments['repo']}")
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "github_list_branches":
            result = await github_request("GET", f"/repos/{arguments['owner']}/{arguments['repo']}/branches")
            branches = [b["name"] for b in result]
            return [TextContent(type="text", text=f"Branches: {json.dumps(branches, indent=2)}")]

        elif name == "github_create_branch":
            owner, repo = arguments["owner"], arguments["repo"]
            from_branch = arguments.get("from_branch", "main")

            # Lấy SHA của branch gốc
            ref_data = await github_request("GET", f"/repos/{owner}/{repo}/git/ref/heads/{from_branch}")
            sha = ref_data["object"]["sha"]

            # Tạo branch mới
            result = await github_request(
                "POST",
                f"/repos/{owner}/{repo}/git/refs",
                json={"ref": f"refs/heads/{arguments['branch_name']}", "sha": sha},
            )
            return [TextContent(type="text", text=f"Branch '{arguments['branch_name']}' created successfully from '{from_branch}'.\nSHA: {sha}")]

        elif name == "github_get_file":
            owner, repo = arguments["owner"], arguments["repo"]
            path = arguments["path"]
            branch = arguments.get("branch", "main")
            result = await github_request("GET", f"/repos/{owner}/{repo}/contents/{path}", params={"ref": branch})
            content = base64.b64decode(result["content"]).decode("utf-8")
            return [TextContent(type="text", text=f"File: {path}\n\n{content}")]

        elif name == "github_create_or_update_file":
            owner, repo = arguments["owner"], arguments["repo"]
            path = arguments["path"]
            branch = arguments["branch"]
            encoded_content = base64.b64encode(arguments["content"].encode("utf-8")).decode("utf-8")

            # Kiểm tra file đã tồn tại chưa để lấy SHA
            payload: dict[str, Any] = {
                "message": arguments["message"],
                "content": encoded_content,
                "branch": branch,
            }
            try:
                existing = await github_request("GET", f"/repos/{owner}/{repo}/contents/{path}", params={"ref": branch})
                payload["sha"] = existing["sha"]
                action = "updated"
            except httpx.HTTPStatusError:
                action = "created"

            result = await github_request("PUT", f"/repos/{owner}/{repo}/contents/{path}", json=payload)
            commit_sha = result["commit"]["sha"]
            return [TextContent(type="text", text=f"File '{path}' {action} successfully.\nCommit SHA: {commit_sha}")]

        elif name == "github_create_pull_request":
            owner, repo = arguments["owner"], arguments["repo"]
            result = await github_request(
                "POST",
                f"/repos/{owner}/{repo}/pulls",
                json={
                    "title": arguments["title"],
                    "body": arguments["body"],
                    "head": arguments["head"],
                    "base": arguments.get("base", "main"),
                },
            )
            return [TextContent(type="text", text=f"Pull Request created!\nURL: {result['html_url']}\nNumber: #{result['number']}")]

        elif name == "github_list_files":
            owner, repo = arguments["owner"], arguments["repo"]
            path = arguments.get("path", "")
            branch = arguments.get("branch", "main")
            result = await github_request("GET", f"/repos/{owner}/{repo}/contents/{path}", params={"ref": branch})
            files = [{"name": f["name"], "type": f["type"], "path": f["path"]} for f in result]
            return [TextContent(type="text", text=json.dumps(files, indent=2))]

        elif name == "github_read_agent_context":
            owner, repo = arguments["owner"], arguments["repo"]
            branch = arguments.get("branch", "main")
            context_parts = []
            for filename in ["ARCHITECTURE.md", "RULES.md", "SKILL.md"]:
                try:
                    result = await github_request("GET", f"/repos/{owner}/{repo}/contents/.agent/{filename}", params={"ref": branch})
                    content = base64.b64decode(result["content"]).decode("utf-8")
                    context_parts.append(f"=== .agent/{filename} ===\n{content}\n")
                except httpx.HTTPStatusError:
                    context_parts.append(f"=== .agent/{filename} === [NOT FOUND]\n")
            return [TextContent(type="text", text="\n".join(context_parts))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"GitHub API Error: {e.response.status_code} - {e.response.text}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ─── Main ──────────────────────────────────────────────────────────────────────
async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
