"""
Notion MCP Server for Enterprise AI Workflow

Sử dụng official Notion MCP Server từ Anthropic:
  npx -y @notionhq/notion-mcp-server

File này là wrapper/documentation hướng dẫn cách tích hợp Notion MCP.

Các tools được cung cấp bởi @notionhq/notion-mcp-server:
  - notion_retrieve_page       : Đọc nội dung một page theo ID
  - notion_query_database      : Query database theo filter
  - notion_retrieve_database   : Lấy thông tin database
  - notion_list_users          : Liệt kê users trong workspace
  - notion_search              : Tìm kiếm pages/databases

Setup:
  1. Tạo Notion Integration tại https://www.notion.so/my-integrations
  2. Copy Integration Token (secret_xxx...)
  3. Share các pages/databases cần AI đọc với Integration
  4. Thêm vào config.yaml của ZeroClaw (xem bên dưới)

Cấu hình trong config.yaml:
  [mcp_servers.notion]
  command = "npx"
  args = ["-y", "@notionhq/notion-mcp-server"]
  env = { OPENAPI_MCP_HEADERS = '{"Authorization": "Bearer secret_xxx", "Notion-Version": "2022-06-28"}' }

Cách AI sử dụng:
  Khi anh gửi link Notion: https://notion.so/workspace/page-id
  AI sẽ extract page ID và gọi notion_retrieve_page để đọc nội dung.

Ví dụ URL Notion:
  https://www.notion.so/My-Task-Title-abc123def456...
  Page ID = abc123def456... (phần cuối URL, bỏ dấu gạch ngang)
"""

# Đây là file documentation/wrapper.
# Actual MCP server chạy qua: npx -y @notionhq/notion-mcp-server
# Không cần chạy file Python này trực tiếp.

NOTION_MCP_CONFIG = {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": {
        "OPENAPI_MCP_HEADERS": '{"Authorization": "Bearer ${NOTION_TOKEN}", "Notion-Version": "2022-06-28"}'
    }
}

NOTION_SETUP_INSTRUCTIONS = """
=== Notion MCP Setup Instructions ===

1. Tạo Notion Integration:
   - Truy cập: https://www.notion.so/my-integrations
   - Click "New integration"
   - Đặt tên: "ZeroClaw AI Agent"
   - Chọn workspace
   - Copy "Internal Integration Secret" (dạng: secret_xxx...)

2. Share Pages với Integration:
   - Mở page/database cần AI đọc
   - Click "..." > "Connections" > Chọn "ZeroClaw AI Agent"
   - Lặp lại cho tất cả pages/databases cần thiết

3. Cập nhật .env:
   NOTION_TOKEN=secret_xxx...

4. Cập nhật config.yaml của ZeroClaw:
   [mcp_servers.notion]
   command = "npx"
   args = ["-y", "@notionhq/notion-mcp-server"]
   env = { OPENAPI_MCP_HEADERS = '{"Authorization": "Bearer secret_xxx", "Notion-Version": "2022-06-28"}' }

5. Test:
   Gửi link Notion vào Slack và xem AI có đọc được không.
"""

if __name__ == "__main__":
    print(NOTION_SETUP_INSTRUCTIONS)
