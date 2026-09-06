# 如何复核

在仓库根目录运行。小游戏本身是独立 HTML，以下依赖只用于自动检查。

## 游戏规则

安装 Node.js 后运行：

```powershell
node tests/snake.test.cjs
```

覆盖手动规则、暂停、碰撞、AI 连吃 15 个（1000 组种子）及满棋盘（20 组）。

## 浏览器行为

需要 Microsoft Edge 和 Playwright：

```powershell
npm install --no-save --package-lock=false playwright@1.62.1
node tests/browser-smoke.cjs
node tests/browser-history.cjs
```

检查双击本地 HTML、键盘、方向按钮、滑动、暂停继续、主题刷新保留、AI 自动达标、320/390px 手机布局，以及战绩新增、10 局上限、展开、持久化和清空。截图写入 `tmp/`。测试使用独立浏览器上下文，不读取个人浏览器资料。

## 真实 AI 代码错误复现

配置好 README 中的 Python 环境后：

```powershell
.\.venv-circuits\Scripts\python.exe tests/pyspice-save-repro.py
```

先显示原 AI 代码的 TypeError，再打印 PySpice 1.5 源码依据并确认正确调用通过。这个小复现实验无需 Ngspice DLL。

三个完整电路的运行与理论对照见根目录 README。
