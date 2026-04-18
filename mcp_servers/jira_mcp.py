"""
Jira MCP Server for Enterprise AI Workflow

Sử dụng opensource Jira MCP Server:
  npx -y @sooperset/mcp-atlassian

File này là wrapper/documentation hướng dẫn cách tích hợp Jira MCP.

Các tools được cung cấp bởi @sooperset/mcp-atlassian:
  - jira_get_issue           : Đọc chi tiết một issue theo key (ví dụ: PROJ-123)
  - jira_search_issues       : Tìm kiếm issues theo JQL query
  - jira_create_issue        : Tạo issue mới
  - jira_update_issue        : Cập nhật issue
  - jira_add_comment         : Thêm comment vào issue
  - jira_get_project         : Lấy thông tin project
  - jira_list_projects       : Liệt kê tất cả projects

Setup:
  1. Tạo Jira API Token tại https://id.atlassian.com/manage-profile/security/api-tokens
  2. Lấy Jira Cloud URL (ví dụ: https://your-company.atlassian.net)
  3. Thêm vào config.yaml của ZeroClaw (xem bên dưới)

Cấu hình trong config.yaml:
  [mcp_servers.jira]
  command = "npx"
  args = ["-y", "@sooperset/mcp-atlassian"]
  env = {
    JIRA_URL = "https://your-company.atlassian.net",
    JIRA_USERNAME = "your-email@company.com",
    JIRA_API_TOKEN = "your-api-token"
  }

Cách AI sử dụng:
  Khi anh gửi link Jira: https://your-company.atlassian.net/browse/PROJ-123
  AI sẽ extract issue key (PROJ-123) và gọi jira_get_issue để đọc nội dung.

Ví dụ URL Jira:
  https://blogic.atlassian.net/browse/FE-456
  Issue Key = FE-456
"""

JIRA_MCP_CONFIG = {
    "command": "npx",
    "args": ["-y", "@sooperset/mcp-atlassian"],
    "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_USERNAME": "${JIRA_USERNAME}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
    }
}

JIRA_SETUP_INSTRUCTIONS = """
=== Jira MCP Setup Instructions ===

1. Tạo Jira API Token:
   - Truy cập: https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Đặt tên: "ZeroClaw AI Agent"
   - Copy token

2. Lấy thông tin Jira:
   - Jira URL: https://your-company.atlassian.net
   - Username: email đăng nhập Jira

3. Cập nhật .env:
   JIRA_URL=https://your-company.atlassian.net
   JIRA_USERNAME=your-email@company.com
   JIRA_API_TOKEN=your-api-token

4. Cập nhật config.yaml của ZeroClaw:
   [mcp_servers.jira]
   command = "npx"
   args = ["-y", "@sooperset/mcp-atlassian"]
   env = {
     JIRA_URL = "https://your-company.atlassian.net",
     JIRA_USERNAME = "your-email@company.com",
     JIRA_API_TOKEN = "your-api-token"
   }

5. Test:
   Gửi link Jira vào Slack và xem AI có đọc được không.
"""

if __name__ == "__main__":
    print(JIRA_SETUP_INSTRUCTIONS)
