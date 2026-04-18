# MCP Servers

Thư mục này chứa các MCP (Model Context Protocol) Servers giúp AI Agent tương tác với các dịch vụ bên ngoài.

## Danh sách MCP Servers

| Server | File | Mục đích | Nguồn |
|--------|------|---------|-------|
| **GitHub MCP** | `github_mcp.py` | Tạo branch, commit, push, tạo PR | Custom Python |
| **Notion MCP** | `notion_mcp.py` | Đọc requirements từ Notion | `@notionhq/notion-mcp-server` |
| **Jira MCP** | `jira_mcp.py` | Đọc tasks từ Jira | `@sooperset/mcp-atlassian` |

## Cài đặt

### GitHub MCP (Custom Python)

```bash
pip install mcp httpx
python mcp_servers/github_mcp.py
```

### Notion MCP (NPX)

```bash
# Không cần cài đặt, chạy trực tiếp qua npx
npx -y @notionhq/notion-mcp-server
```

### Jira MCP (NPX)

```bash
# Không cần cài đặt, chạy trực tiếp qua npx
npx -y @sooperset/mcp-atlassian
```

## Cấu hình trong ZeroClaw config.yaml

```toml
[mcp_servers.github]
command = "python3"
args = ["./mcp_servers/github_mcp.py"]
env = { GITHUB_TOKEN = "${GITHUB_TOKEN}" }

[mcp_servers.notion]
command = "npx"
args = ["-y", "@notionhq/notion-mcp-server"]
env = { OPENAPI_MCP_HEADERS = '{"Authorization": "Bearer ${NOTION_TOKEN}", "Notion-Version": "2022-06-28"}' }

[mcp_servers.jira]
command = "npx"
args = ["-y", "@sooperset/mcp-atlassian"]
env = { JIRA_URL = "${JIRA_URL}", JIRA_USERNAME = "${JIRA_USERNAME}", JIRA_API_TOKEN = "${JIRA_API_TOKEN}" }
```

## Xem chi tiết từng server

- `github_mcp.py` - GitHub integration (tạo branch, commit, PR)
- `notion_mcp.py` - Notion integration (đọc pages, databases)
- `jira_mcp.py` - Jira integration (đọc issues, projects)
