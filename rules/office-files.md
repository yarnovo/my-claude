# Office 文件自动处理规则

当需要读取以下类型的 Office 文件时，自动调用相应的技能进行转换：

| 文件类型 | 扩展名 | 技能 |
|---------|--------|------|
| PDF 文档 | `.pdf` | pdf |
| Word 文档 | `.docx` | docx |
| Excel 表格 | `.xlsx`, `.xls` | xlsx |
| PowerPoint | `.pptx`, `.ppt` | pptx |

## 工作流程

1. **检测文件类型**：根据扩展名判断
2. **调用技能**：使用相应技能转换文件
3. **读取转换结果**：
   - `<file>.claude/content.md` - Markdown 内容
   - `<file>.claude/images/` - Word 内嵌图片
   - `<file>.claude/previews/` - PPTX 幻灯片预览图
   - `<file>.claude/pages/` - PDF 页面预览图

## 示例

用户请求：「帮我看看 report.docx 里写了什么」

执行步骤：
1. 调用 docx 转换 report.docx
2. 读取 report.docx.claude/content.md
3. 如有图片，读取 report.docx.claude/images/ 下的图片
4. 向用户展示内容

## 注意事项

- 转换结果缓存在原文件旁边的 `.claude` 目录中
- 如果 `.claude` 目录已存在且文件未更新，可以直接读取缓存
- 首次使用需要安装依赖：`cd ~/.claude/office-deps && uv sync`
