# Tutorial: Thiết lập Enterprise AI Workflow

Hướng dẫn từng bước để thiết lập hệ thống AI Agent (ZeroClaw) cho môi trường Multi-Project với Slack, GitHub, Notion và Jira.

---

## Tổng quan Kiến trúc

```text
Slack Chat
    │
    ▼
ZeroClaw AI Agent (config.yaml + System Prompt)
    │
    ├── GitHub MCP     → Tạo branch, commit, push, PR
    ├── Notion MCP     → Đọc requirements từ Notion pages
    └── Jira MCP       → Đọc tasks từ Jira issues
```

**Luồng làm việc:**

```text
[Anh Kiệt] Gửi link Notion/Jira vào Slack
    ↓
[ZeroClaw] Đọc requirement + đọc .agent/ context của dự án
    ↓
[ZeroClaw] Hỏi: "UI changes? Business logic?"
    ↓
[Anh Kiệt] Trả lời trên Slack
    ↓
[ZeroClaw] Tạo plan.md → Gửi lên Slack để review
    ↓
[Anh Kiệt] Comment "approved"
    ↓
[ZeroClaw] Tạo branch → Viết code → Commit → Push GitHub
    ↓
[ZeroClaw] Báo cáo: "Done! Branch: feature/xxx"
    ↓
[Jenkins] Tự động build/deploy (nếu đã cấu hình)
```

---

## Bước 1: Chuẩn bị API Keys

### 1.1. Anthropic API Key

1. Truy cập [https://console.anthropic.com](https://console.anthropic.com)
2. Vào **API Keys** → **Create Key**
3. Copy key (dạng `sk-ant-...`)

### 1.2. GitHub Personal Access Token

1. Truy cập [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Chọn scopes: `repo`, `workflow`, `admin:repo_hook`
4. Copy token (dạng `ghp_...`)

### 1.3. Slack App Tokens

1. Truy cập [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Đặt tên **"ZeroClaw"**, chọn workspace
4. Vào **Socket Mode** → Bật Socket Mode → Tạo App-Level Token → Copy `xapp-...`
5. Vào **OAuth & Permissions** → Thêm scopes: `chat:write`, `app_mentions:read`, `channels:history`
6. Click **Install to Workspace** → Copy Bot Token `xoxb-...`

### 1.4. Notion Integration Token

1. Truy cập [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **New integration** → Đặt tên **"ZeroClaw AI"**
3. Copy **Internal Integration Secret** (dạng `secret_...`)
4. **Quan trọng**: Mở từng page/database cần AI đọc → Click **"..."** → **Connections** → Chọn **"ZeroClaw AI"**

### 1.5. Jira API Token

1. Truy cập [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token** → Đặt tên **"ZeroClaw AI"**
3. Copy token

---

## Bước 2: Cài đặt Dependencies

```bash
# Python dependencies (cho GitHub MCP)
pip install mcp httpx
# hoặc
pip install -r requirements.txt

# Node.js (cho Notion và Jira MCP)
# Đảm bảo Node.js >= 18 đã được cài đặt
node --version

# Test Notion MCP
npx -y @notionhq/notion-mcp-server --help

# Test Jira MCP (cần cài đặt uv trước: pip install uv)
uvx mcp-atlassian --help
```

---

## Bước 3: Cấu hình Environment Variables

```bash
# Copy file mẫu
cp .env.example .env

# Mở và điền các giá trị
nano .env
```

Nội dung `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
NOTION_TOKEN=secret_...
JIRA_URL=https://blogicsystems.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=...
```

---

## Bước 4: Cập nhật config.yaml của ZeroClaw

Mở file `config.yaml` của ZeroClaw (thường ở `~/.zeroclaw/config.yaml`) và thêm/cập nhật các phần sau:

### 4.1. Tăng Context Tokens

```toml
[agent]
max_context_tokens = 128000
context_aware_tools = true
```

### 4.2. Bật Skills

```toml
[skills]
open_skills_enabled = true
allow_scripts = true
```

### 4.3. Thêm MCP Servers

```toml
[mcp_servers.github]
command = "python3"
args = ["/path/to/enterprise-ai-workflow/mcp_servers/github_mcp.py"]
env = { GITHUB_TOKEN = "ghp_..." }

[mcp_servers.notion]
command = "npx"
args = ["-y", "@notionhq/notion-mcp-server"]
env = { OPENAPI_MCP_HEADERS = '{"Authorization": "Bearer secret_...", "Notion-Version": "2022-06-28"}' }

[mcp_servers.jira]
command = "uvx"
args = ["mcp-atlassian"]
env = { JIRA_URL = "https://blogicsystems.atlassian.net", JIRA_USERNAME = "email@company.com", JIRA_API_TOKEN = "..." }
```

### 4.4. Thêm System Prompt

Xem nội dung System Prompt trong file `config.yaml` của repository này và copy vào cấu hình ZeroClaw.

---

## Bước 5: Setup Dự án Con (Multi-Project)

Để AI hỗ trợ một dự án mới, thực hiện các bước sau trong repository của dự án đó:

```bash
# 1. Clone repository dự án
git clone https://github.com/your-org/your-project.git
cd your-project

# 2. Tạo thư mục .agent
mkdir -p .agent

# 3. Copy templates từ enterprise-ai-workflow
cp /path/to/enterprise-ai-workflow/.agent/ARCHITECTURE.md .agent/
cp /path/to/enterprise-ai-workflow/.agent/RULES.md .agent/
cp /path/to/enterprise-ai-workflow/.agent/SKILL.md .agent/

# 4. Chỉnh sửa từng file cho phù hợp với dự án
nano .agent/ARCHITECTURE.md
nano .agent/RULES.md
nano .agent/SKILL.md

# 5. Commit và push
git add .agent/
git commit -m "chore: add AI agent context files"
git push origin main
```

### Những gì cần điền trong từng file:

**`.agent/ARCHITECTURE.md`**: Mô tả kiến trúc cụ thể của dự án (folder structure, component patterns, routing, state management).

**`.agent/RULES.md`**: Coding standards (naming conventions, component rules, RxJS patterns, testing requirements).

**`.agent/SKILL.md`**: Tools và workflows cụ thể (libraries, API endpoints, build commands, deployment process).

---

## Bước 6: Test Workflow

### 6.1. Test GitHub MCP

```bash
# Chạy GitHub MCP server
GITHUB_TOKEN=ghp_... python3 mcp_servers/github_mcp.py

# Trong terminal khác, test tool
# Gọi github_get_repo với owner và repo
```

### 6.2. Test Notion MCP

```bash
# Test đọc một Notion page
OPENAPI_MCP_HEADERS='{"Authorization": "Bearer secret_...", "Notion-Version": "2022-06-28"}' \
  npx -y @notionhq/notion-mcp-server
```

### 6.3. Test Jira MCP

```bash
# Test đọc một Jira issue
JIRA_URL=https://blogicsystems.atlassian.net \
JIRA_USERNAME=email@company.com \
JIRA_API_TOKEN=... \
  uvx mcp-atlassian
```

### 6.4. Test End-to-End Workflow

1. Mở Slack, vào channel của ZeroClaw
2. Gửi tin nhắn:
   ```
   Làm giúp anh task này nhé: https://notion.so/workspace/task-id
   Dự án: your-project
   ```
3. Kiểm tra ZeroClaw có hỏi lại về UI changes và business logic không
4. Trả lời các câu hỏi
5. Kiểm tra ZeroClaw có gửi plan.md không
6. Comment "approved"
7. Kiểm tra GitHub có branch mới không
8. Kiểm tra Slack có báo cáo hoàn thành không

---

## Bước 7: Cải tiến Hàng ngày

Sau mỗi task, hãy cập nhật các file trong `.agent/` để AI ngày càng hiểu dự án tốt hơn:

- **Thêm rule mới**: Nếu AI sinh code sai pattern, thêm rule vào `.agent/RULES.md`
- **Cập nhật architecture**: Nếu dự án có thay đổi cấu trúc, cập nhật `.agent/ARCHITECTURE.md`
- **Thêm known issues**: Nếu có vấn đề thường gặp, thêm vào `.agent/SKILL.md`

---

## Troubleshooting

### Lỗi: GitHub MCP không tạo được branch

**Nguyên nhân**: GitHub token không có đủ quyền.

**Giải pháp**: Tạo lại token với scopes: `repo`, `workflow`, `admin:repo_hook`.

### Lỗi: Notion MCP không đọc được page

**Nguyên nhân**: Integration chưa được share với page đó.

**Giải pháp**: Mở page → Click "..." → "Connections" → Chọn integration.

### Lỗi: Jira MCP không kết nối được

**Nguyên nhân**: URL hoặc credentials sai.

**Giải pháp**: Kiểm tra `JIRA_URL` (phải có `https://`), `JIRA_USERNAME` (email), `JIRA_API_TOKEN`.

### AI không đọc được `.agent/` context

**Nguyên nhân**: `max_context_tokens` quá thấp hoặc `context_aware_tools` chưa bật.

**Giải pháp**: Cập nhật config.yaml theo Bước 4.1.

---

## Tài liệu Tham khảo

- [ZeroClaw Documentation](https://zeroclaw.dev/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Notion MCP Server](https://github.com/notionhq/notion-mcp-server)
- [Jira MCP Server](https://github.com/sooperset/mcp-atlassian)
- [GitHub REST API](https://docs.github.com/en/rest)
