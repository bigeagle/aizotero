# AI论文助手 - AIZotero

一个基于Zotero的AI论文阅读助手，通过Web界面帮助用户快速理解和管理研究论文。

## 功能特点

- Zotero集成：直接连接本地Zotero库，无需手动导入
- AI驱动：智能分析论文内容，提供深度见解
- 对话式学习：边看论文边与AI讨论
- Web界面：现代化的响应式设计

## 快速开始

### 环境要求
- Python 3.13+
- Node.js 18+
- Zotero（已安装并配置）

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd aizotero

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖（使用pnpm）
cd frontend && pnpm install
```

### 启动服务

```bash
# 启动后端（端口8000）
uvicorn app.main:app --reload

# 启动前端（端口5173）
cd frontend && pnpm dev
```

访问 http://localhost:5173 开始使用

## 使用指南

1. 连接Zotero：首次使用时会自动检测本地Zotero
2. 浏览论文：在列表页面查看所有论文
3. 开始阅读：点击论文进入阅读界面
4. AI对话：在右侧与AI讨论论文内容

## 开发

### 项目结构
```
aizotero/
├── app/           # FastAPI后端
├── frontend/      # Vue.js前端
├── docs/          # 设计文档
└── tests/         # 测试文件
```

### 常用命令
```bash
# 运行测试
python -m pytest

# 代码格式化
black .
ruff check .

# 前端检查
cd frontend && pnpm lint
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License