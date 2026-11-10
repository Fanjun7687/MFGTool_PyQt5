# AGENTS.md — MFGTool_PyQt5 项目参考

> 本文件记录 2026-11 梳理本项目、构建 uv 环境并成功运行界面的完整过程与踩坑记录，供以后参考。

## 项目简介

基于 PyQt5 的工厂测试工装（MFG Test Tool），主窗口类 `MFGWindow`，通过扫描 SN 触发 PT/FT/RunIn 等站点测试流程。

## 项目结构

| 文件/目录 | 作用 |
|---|---|
| `main_MFGWind.py` | 主程序入口，`MFGWindow` 主窗口类（信号槽、测试线程、子进程调用） |
| `myUI.py` / `myUI.ui` | Qt Designer 生成的界面代码 |
| `package/` | 业务模块：`SerialCom_Class`(串口)、`hardwareInfo`(WMI/COM口)、`adb_Class`、`telnet_Class`、`windowHandlerCtrl`(窗口句柄)、`errorCode`、`structural_var`(全局结构体) |
| `cfg.tab` | 运行配置（**启动必需**，以相对路径 `./cfg.tab` 读取） |
| `gif/`、`icon/`、`pyres.qrc` | 界面资源，样式表里用相对路径 `url(gif/*.gif)` 引用 |
| `pyproject.toml` / `uv.lock` | uv 项目定义与锁文件 |
| `.env` | 指定 venv 路径（见下文关键约束） |
| `run.bat` | 一键启动脚本（双击即可） |

## 依赖（pyproject.toml 已声明）

- `pyqt5`（Windows 轮子只带 Qt 5.15.2）、`pywin32`、`pygame`（仅用于延迟函数）、`keyboard`、`mouse`、`WMI`、`pyserial`
- Python 版本固定 `>=3.11,<3.13`：`package/telnet_Class.py` 依赖标准库 `telnetlib`，**Python 3.13 已移除该模块**，实际使用 CPython 3.12.7（uv 自动选择）

## ⚠️ 关键约束：venv 必须放在纯 ASCII 路径

本项目路径 `D:\工作代码\Python\...` **含中文字符**，而 PyQt5 官方 Windows 轮子捆绑的 Qt 5.15.2 在非 ASCII 路径下会初始化失败（无法加载 `qwindows` 平台插件，甚至 Qt5Core.dll 直接崩溃 0xC0000409）。因此虚拟环境固定放在：

```
C:\Users\Jason.Fan\.venvs\MFGTool_PyQt5
```

通过 `UV_PROJECT_ENVIRONMENT` 环境变量指定（uv 没有在 pyproject.toml 里配置 venv 路径的选项）。**不要删除该目录**，否则界面无法启动。

## 启动方式

| 命令 | 结果 |
|---|---|
| `run.bat`（双击或命令行） | ✅ 推荐，内部先设置 `UV_PROJECT_ENVIRONMENT` 再 `uv run` |
| `uv run --env-file .env main_MFGWind.py` | ✅ 可用 |
| `uv run main_MFGWind.py`（裸跑） | ❌ 会在项目目录自动重建 `.venv`（中文路径），报 `Could not find the Qt platform plugin "windows" in ""` |

首次同步环境：

```bat
set UV_PROJECT_ENVIRONMENT=C:\Users\Jason.Fan\.venvs\MFGTool_PyQt5
uv sync
```

## 踩坑记录（原因与解法）

1. **`pyqt5-qt5==5.15.19` 没有 Windows 轮子**：解析器默认选了最新版导致安装失败。解法：`[tool.uv]` 中加 `required-environments = ["sys_platform == 'win32' and platform_machine == 'AMD64'"]`，自动回落到有 Windows 轮子的 5.15.2。

2. **Qt 5.15.2 中文路径崩溃/插件加载失败**：现象有两种——Qt5Core.dll 0xC0000409 无提示退出（查 Windows 事件日志可见崩溃模块），或 `Could not find the Qt platform plugin "windows" in ""`。根因相同。解法：venv 放纯 ASCII 路径（见上）。注意项目工作目录（cwd）含中文没关系，只有 venv/Qt 库文件所在路径不能含中文。

3. **本机 `socket.gethostbyname(socket.getfqdn(...))` 抛 `gaierror 11001`**：主机名无法解析（无 DNS/离线）。已修复：`main_MFGWind.py` `Var_Defined()` 中 try/except 回退 `127.0.0.1`。

4. **本机 PATH 无 `adb.exe`**：点 Run 触发演示测试时 `subprocess.Popen` 抛 `FileNotFoundError`。已修复：`main_MFGWind.py` `Pipe_SendCmdGetRetStr()` 捕获异常写入测试日志 `[CMD ERROR]`，不再抛线程异常。若需要 adb 功能，安装 Android platform-tools 并加入 PATH。

5. **uv 0.10.10 不会自动加载项目根目录 `.env`**：必须显式 `uv run --env-file .env ...`。

6. **uv 的 dotenv 解析器把 `\U`（如 `C:\Users`）当 unicode 转义**：`.env` 里的 Windows 反斜杠路径会报 `Failed to parse environment file at position 3`。解法：`.env` 中用正斜杠 `C:/Users/Jason.Fan/.venvs/MFGTool_PyQt5`。另外 `.env` 内容须为纯 ASCII（含中文注释也会解析失败）。

7. **bat 文件不能用 UTF-8 中文注释**：cmd.exe 按 GBK 解析批处理，UTF-8 中文注释会被切碎当成命令执行（报"不是内部或外部命令"）。`run.bat` 因此用纯英文注释。

8. **PowerShell 下 uv 的 stderr 横幅会被标成 NativeCommandError**：属显示噪音，非真实错误。

## 对源码的修改记录

仅 `main_MFGWind.py` 两处容错（不影响原逻辑）：
- `Var_Defined()`：IP 获取失败回退 `127.0.0.1`
- `Pipe_SendCmdGetRetStr()`：Popen 失败写测试日志并返回空列表

## 其他备忘

- 打包 exe：`pyinstaller -F -w main_MFGWind.py`（在 uv 环境下执行，需将 `cfg.tab`、`gif/`、`icon/` 拷到 dist 同级目录）
- 真实测试逻辑挂载点：`Slot_SFCRoutingCheck`（SFC 路由检查）、`PTTest_ProjectName`/`FTTest_ProjectName`/`RunInTest_ProjectName`、`beginTestThread` 中按产品 SKU 分发
- 菜单 About 显示版本号来自 `package/structural_var.py` 的 `Version`
