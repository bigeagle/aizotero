# TODO.md

## 开发计划

- [ ] **ArXiv API 集成优化**: 使用官方 API 获取论文元数据
  - 当前实现：直接从 `https://arxiv.org/pdf/{id}.pdf` 拼接 URL
  - 目标实现：使用 `https://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1` 获取完整元数据
  - 原因：使用官方 API 获取准确的 PDF URL 和其他元数据，避免硬编码 URL 格式，支持更多数据字段

- [ ] **添加论文前搜索**: add_arxiv 时先在 Zotero 库中搜索
  - 当前实现：直接添加论文到库中
  - 目标实现：添加前先搜索 Zotero 库(通过标题搜索、再用 url 检测)，避免重复添加
  - 原因：防止重复论文，提升用户体验

- [ ] **PDF URL 阅读支持**: 支持直接添加 PDF URL 阅读
  - 当前实现：仅支持 ArXiv 论文
  - 目标实现：支持任意 PDF URL，用 LLM 提取元数据并添加到 Zotero
  - 原因：扩展支持范围，提升灵活性


## 技术债务
- [ ] 完善错误处理机制
- [ ] 增加单元测试覆盖率

## 更新记录
- 2025-08-03: 创建 TODO.md，添加 ArXiv PDF 获取优化任务
