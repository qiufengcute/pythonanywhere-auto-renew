# PythonAnywhere 自动续期工具

这个项目用于自动点击 PythonAnywhere 网页上的 "Run until 1 months from today" 按钮，确保免费网站保持运行状态。

## 功能特点

- 🤖 自动化登录 PythonAnywhere
- 🔄 自动点击续期按钮
- ⏰ 每个月自动执行两次（通过 GitHub Actions）
- 🔒 使用 GitHub Secrets 安全存储凭证
- 📸 失败时自动保存截图用于调试

## 执行计划

脚本会在每个月 1 号及 20 号自动执行

你也可以在 GitHub Actions 页面手动触发执行。

## 故障排除

如果脚本执行失败：

1. 检查 GitHub Actions 日志
2. 查看自动上传的错误截图和页面源码
3. 确认 PythonAnywhere 网站结构是否有变化
4. 验证凭证是否正确

## 工作原理

脚本会：
1. **优先尝试API方式**：尝试通过HTTP请求直接调用续期接口（更快更稳定）
2. **回退到浏览器自动化**：如果API不可用，使用Playwright自动点击按钮
3. **自动检测API**：浏览器模式下会监听网络请求，如果发现API端点会自动记录

## 注意事项

- ⚠️ 免费账户需要每个月至少登录一次，此脚本每个月执行两次以确保安全
- ⚠️ 脚本会自动根据用户名构建webapp ID（格式：`{username}_pythonanywhere_com`）
- ⚠️ 如果API方式可用，脚本会自动使用API，无需浏览器，执行更快

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

