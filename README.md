# 大一招新考核

**个人网站： [https://andy-bit-sys.github.io/kaohe/](https://andy-bit-sys.github.io/kaohe/)**

本仓库用于逐步完成协会招新考核，保存个人网站、个人简介 PDF、小游戏、进阶项目及开发记录。

## 当前进度

- [x] 准备 Git、VS Code 和 AI 编程工具 Codex
- [x] 登录 GitHub
- [x] 完成个人简介 PDF
- [x] 完成个人网站
- [ ] 完成小游戏的手动操作和 AI 自动演示
- [ ] 完成进阶挑战
- [ ] 补齐验证结果、提示词迭代记录和代码逻辑说明

## 开发记录

### 个人网站

- 页面代码：[index.html](index.html)，使用原生 HTML/CSS，无需安装框架或运行构建命令。
- 本地预览：双击 `index.html`；下载个人简介时需保留 `output/pdf/` 目录。
- 内容：自我介绍、兴趣爱好、大学期待、个人简介 PDF 下载与 GitHub 入口。
- 验证：使用浏览器检查桌面、390px 和 320px 手机宽度；检查导航跳转、PDF 文件路径和页面错误。
- 在线访问：[刘锦桉的个人主页](https://andy-bit-sys.github.io/kaohe/)。
- GitHub Pages 从 `main` 分支根目录发布；修改并推送网站文件后会自动更新。

### 个人简介 PDF

- 已完成：[刘锦桉的个人简介（详细版）](output/pdf/刘锦桉_个人简介_详细版.pdf)。
- 内容涵盖个人背景、项目兴趣、足球爱好和大学期待，采用一页蓝白排版。
- 验证：检查 PDF 为单页，核对姓名、籍贯、年级班级，并渲染检查中文显示和排版。

### 环境准备

- Git：2.53.0.windows.3
- VS Code：1.136.1
- AI 编程工具：Codex
- 本次使用 Codex 检查开发环境并初始化仓库；后续实现与验证过程会随开发进度记录。

## 待完善的提交材料

网站访问地址、各项目运行方法、阶段一与阶段二验证过程、功能修改及原因、问题排查记录、AI 生成与人工调整说明、关键提示词原文及迭代、两处关键代码逻辑解释、AI 信息查证记录、许可证选择原因。

分支是在不影响主线的情况下独立开发功能，合并是把分支上完成的改动整合回主线或其他分支

## 常用命令

| 命令 | 用途 |
| --- | --- |
| `cd 路径` | 切换当前目录 |
| `ls` | 列出当前目录内容（PowerShell 中也可用） |
| `mkdir 目录名` | 创建目录 |
| `git status` | 查看文件修改和暂存状态 |
| `git add 文件名` | 把指定文件的修改加入暂存区 |
| `git commit -m "说明"` | 保存一次有说明的提交 |
| `git log --oneline` | 查看简洁的提交历史 |
| `git push` | 将本地提交上传到远程仓库 |

提交对应真实开发阶段，随实际进度逐步记录。

## 命令说明查证：ls 的用途

针对“ls 用于显示大小、权限、修改日期”这一说法，本次结合官方文档和本机环境进行了核对。

- 查证过程：查阅 GNU 的 `ls` 文档和 Microsoft 的 `Get-ChildItem` 文档，并在本机 PowerShell 中运行 `Get-Alias ls`，结果显示 `ls` 是 `Get-ChildItem` 的别名。
- 查证结论：`ls` 的基本用途是列出目录中的文件和子目录；不指定路径时，通常列出当前目录内容。GNU `ls` 默认列出名称，使用 `ls -l` 才显示权限、大小、修改时间等详细信息；Windows PowerShell 中的 `ls` 默认就会显示模式（文件属性）、修改时间、大小和名称，其中模式不等同于完整的访问权限。
- 这次核对说明：解释命令时需要说明使用环境和参数，不能把某一种环境下的输出当成通用规则。本条记录实际查证结果，不将本次聊天中未出现的解释冒充为 AI 原话。

参考：[GNU ls 文档](https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html)、[GNU 详细输出格式](https://www.gnu.org/software/coreutils/manual/html_node/General-output-formatting.html)、[Microsoft Get-ChildItem 文档](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-7.5)。
