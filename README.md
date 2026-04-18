# Enterprise AI Workflow

Hệ thống AI Agent (ZeroClaw) được thiết kế riêng cho môi trường Multi-Project, tương tác qua Slack Chat, và tích hợp với GitHub/Jenkins.

## 🌟 Tính năng chính

- **Chat-based**: Tương tác tự nhiên qua Slack, không cần slash commands.
- **Multi-Project**: Hỗ trợ nhiều dự án với pattern khác nhau thông qua thư mục `.agent/`.
- **Smart Questions**: AI tự động hỏi về UI changes và business logic.
- **Plan Approval**: Duyệt kế hoạch trước khi AI code.
- **Auto Git**: Tự động tạo branch, commit, push lên GitHub.
- **Jenkins Ready**: Báo cáo hoàn thành, Jenkins tự động trigger.
- **Context Memory**: AI nhớ lại context từ `.agent/` folder của mỗi project.

## 📁 Cấu trúc Repository

```text
enterprise-ai-workflow/
├── .agent/                 # Thư mục chứa context cho AI (copy vào từng project)
│   ├── ARCHITECTURE.md     # Kiến trúc cụ thể của dự án
│   ├── RULES.md            # Coding standards của dự án
│   └── SKILL.md            # Các kỹ năng đặc thù
├── mcp_servers/            # Các MCP Servers (GitHub, Notion, Jira)
├── config.yaml             # Cấu hình mẫu cho ZeroClaw
└── README.md               # Tài liệu hướng dẫn
```

## 🚀 Hướng dẫn Triển khai

### 1. Cài đặt MCP Servers

Hệ thống sử dụng các MCP Servers để tương tác với các dịch vụ bên ngoài:

- **GitHub MCP**: Tự động tạo branch, commit, push.
- **Notion MCP**: Đọc requirements từ Notion.
- **Jira MCP**: Đọc tasks từ Jira.

Xem chi tiết trong thư mục `mcp_servers/`.

### 2. Cấu hình ZeroClaw

Cập nhật file `config.yaml` của ZeroClaw với các thông tin:
- API Keys (Anthropic, GitHub, Slack)
- MCP Servers configuration
- Slack channel configuration

### 3. Setup Dự án Con (Multi-Project)

Để AI hỗ trợ một dự án mới:
1. Copy thư mục `.agent/` từ repository này vào thư mục gốc của dự án con.
2. Chỉnh sửa các file `ARCHITECTURE.md`, `RULES.md`, `SKILL.md` cho phù hợp với dự án đó.
3. Commit và push thư mục `.agent/` lên repository của dự án con.

### 4. Luồng Làm Việc (Workflow)

1. **Giao Task**: Gửi link Notion/Jira vào channel Slack của AI.
2. **Phân tích & Hỏi đáp**: AI đọc link, phân tích context dự án, và chủ động hỏi lại các thông tin còn thiếu.
3. **Lập Kế hoạch**: AI tạo file `plan.md` và gửi lên Slack để review.
4. **Duyệt Kế hoạch**: Comment "approved" trên Slack.
5. **Thực thi**: AI tự động tạo branch mới, viết code, commit và push lên GitHub.
6. **Báo cáo**: AI báo cáo lại trên Slack kèm link branch/PR.

---
*Developed by Kiet Le & Manus AI*
