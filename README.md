# MFGTool_PyQt5 — 工厂测试工装（MFG Test Tool）

基于 **PyQt5** 的产线测试站上位机框架，通过扫描枪触发测试流程，覆盖 PT / FT / RunIn 等站点，支持多产品 SKU 分发、测试结果表格化显示、SFC 路由检查挂载点、Pass/Fail 计数与 FPY 统计。

> 环境搭建与踩坑记录见 [AGENTS.md](AGENTS.md)（venv 必须放在纯 ASCII 路径等关键约束）。

---

## 功能特性

### 测试主流程
- **扫描枪 SN 触发测试**：全局键盘钩子式监听（回车结尾），校验 SN 长度后自动进入测试流程
- **测试状态机**：`StandBy / BootUp / Run / Pass / Fail / ReTest / WaitSFC` 七态流转，状态灯与 LCD 计时器联动
- **测试结果表格**：Index / Test Item / Test Value / Low Spec / High Spec / Result 六列，PASS 绿底、FAIL 红底，支持排序
- **多日志面板**：Test Log、SFIS Log、DUT Log、SFC Log 四个输出区
- **Pass/Fail 计数与 FPY**：结果实时写回 `cfg.tab`，重启不丢失

### 站点与产线管理
- 项目名标题栏**右键菜单切换站点**（站点列表来自 `cfg.tab` 的 `stationlist`），切换后写回配置
- SAMPLE / SFIS ON / SFIS OFF 三种模式切换（SFIS = 车间信息系统，开启后走 SFC 路由检查流程）
- Connector / RF Probe 使用次数计数，达到上限（`conmax`/`antmax`）提示更换治具

### 硬件与工具
- **串口管理**：FIX COM / DUT COM 下拉选择，选通后建立线程化串口连接（绿色标识，失败红色）
- **快捷工具按钮**：打开配置文件、设备管理器、远程桌面(mstsc)、注册表编辑器、CMD 窗口、Ping 测试、屏幕键盘——均已做"窗口已存在则置顶"处理
- PC 信息面板：主机名、IP、Total PASS/FAIL、F.P.Y、测试周期、治具计数

---

## 开发思路（架构设计）

```
┌─────────────────────────────────────────────┐
│  main_MFGWind.py  (MFGWindow 业务层)          │
│  信号槽通信 · 测试流程 · 状态机 · 线程调度       │
├─────────────────────────────────────────────┤
│  myUI.py  (Ui_MainWindow 界面层, Designer生成) │
├─────────────────────────────────────────────┤
│  package/  (基础能力层)                       │
│  串口三层通信 · WMI硬件信息 · ADB/Telnet       │
│  管道命令 · 窗口句柄 · 错误码 · 全局结构体      │
├─────────────────────────────────────────────┤
│  cfg.tab  (配置层, configparser 读写)         │
└─────────────────────────────────────────────┘
```

几个贯穿全局的设计约定：

1. **界面与业务分离**：`myUI.py` 由 Qt Designer 从 `myUI.ui` 生成，不手改；业务全部在 `main_MFGWind.py` 的 `MFGWindow` 中。
2. **跨线程只走信号槽**：测试在后台 `Thread` 中执行，所有 UI 更新通过 `pyqtSignal` 发回主线程（`signal_addtestLog`、`signal_testResultInsert`、`signal_showStatus` 等），避免 Qt 跨线程操作控件。
3. **枚举驱动的状态机**：`DUTStatusMode` 枚举 + `Slot_ShowStatus()` 统一处理状态切换时的 UI 与计数逻辑。
4. **串口三层封装**（`SerialCom_Class.py` 注释原文：base 底层 / application 应用层 / user_api 客户层）：`ComBasic` 为 TTL 底层类，收发各占一个线程 + 队列，其他协议直接继承。
5. **配置驱动**：站点列表、SN 长度、治具上限、数据库/日志服务器、RF 仪器路径损耗等全部从 `cfg.tab` 读取，现场改配置不改代码。
6. **多项目 SKU 分发**：`beginTestThread()` 按 `productname` + `stationname` 分发到对应测试函数，新项目只需加分支。
7. **错误码统一**：`package/errorCode.py` 枚举集中定义（如 `SNLEN0` SN 长度错、`CMDTIM` 命令超时），格式 `[CODE] MSG`。

---

## 环境要求与安装

- Windows x64（依赖 pywin32/WMI）
- [uv](https://docs.astral.sh/uv/) 包管理器
- Python 3.11~3.12（**不能用 3.13**：`package/telnet_Class.py` 依赖的 `telnetlib` 已被移除）

首次同步环境（venv 固定安装在纯 ASCII 路径，原因见 AGENTS.md）：

```bat
set UV_PROJECT_ENVIRONMENT=C:/Users/Jason.Fan/.venvs/MFGTool_PyQt5
uv sync
```

## 运行方式

| 方式 | 命令 |
|---|---|
| 一键启动（推荐） | 双击 `run.bat` |
| 命令行 | `uv run --env-file .env main_MFGWind.py` |
| ❌ 禁止 | `uv run main_MFGWind.py`（裸跑会在中文路径重建 .venv，Qt 插件加载失败） |

### 典型操作流
1. 启动后确认 PC 信息面板；在 FIX COM / DUT COM 下拉框选择串口完成治具连接
2. 标题栏右键可切换站点（PT/FT/CS1...）
3. 扫描枪扫 SN（长度须等于 `cfg.tab` 的 `snlength`）或点 ▶ 按钮开始测试
4. 测试项逐条出现在结果表格，状态灯变绿/红，Pass/Fail 自动累计

---

## 配置文件 cfg.tab 主要节

| 节 | 关键键 | 说明 |
|---|---|---|
| `General` | `stationlist` `productname` `stationname` `snlength` `isdialogbeforetest` | 站点列表、SKU 名、SN 长度等 |
| `Result` | `pass` `fail` | 累计产量（程序自动维护） |
| `Cable` | `conmax` `antmax` `concounter` `antcounter` | 治具寿命管理 |
| `DEVLIST` | `devname1/2` | 挂载的设备名 |
| `MACRange` / `IMEIRange` | `macbegin/end/current` 等 | 号段管理（预留） |
| `DataBase` | `isoracledb` `serverip` ... | Oracle 数据库（预留） |
| `SAVELOG` | 本地/服务器日志路径 | 测试日志归档（预留） |
| `IQ2011` | `isoniq2011` `pathloss_*` | RF 综测仪路径损耗补偿 |

---

## 项目结构

```
MFGTool_PyQt5/
├── main_MFGWind.py        # 主程序：MFGWindow 业务类 + 入口
├── myUI.py / myUI.ui      # 界面层（Designer 生成）
├── package/               # 基础能力层
│   ├── structural_var.py  #   全局变量/枚举/数据结构(TabParam/TabDUTInfo/TabInstrument...)
│   ├── SerialCom_Class.py #   ComBasic 串口三层封装(线程收发+队列)
│   ├── hardwareInfo.py    #   WMI 获取 PC 信息 / 枚举串口
│   ├── windowHandlerCtrl.py#  按标题查找窗口并置顶
│   ├── errorCode.py       #   错误码枚举
│   ├── adb_Class.py / telnet_Class.py / PipeCmd_Class.py / superFunc.py
├── cfg.tab                # 运行配置
├── gif/ icon/ pyres.qrc   # 界面资源
├── pyproject.toml / uv.lock / .env   # uv 环境定义
├── run.bat                # 一键启动
└── AGENTS.md              # 环境踩坑记录(务必先读)
```

---

## 二次开发指导

### 1. 接入一个新产品 SKU
`beginTestThread()` 中已有分发模板：

```python
if self.sTabParam.Tab_chrProductName == 'SBB-115':
    if self.sTabParam.Tab_chrStationName == 'PT' and not self.PTTest_ProjectName(): ...
elif self.sTabParam.Tab_chrProductName == 'XXXXXX':
    pass          # ← 新项目在这里加分支
```

再把 `PTTest_ProjectName()` 等函数改名为对应项目的实现，内部逐项调用测试并 `signal_testResultInsert.emit([...])` 上报结果。

### 2. 新增一个测试项
```python
def MyNewTestItem(self):
    value = ...                                   # 采集
    ok = (lo <= value <= hi)
    self.signal_testResultInsert.emit(
        [SVAR.CurrentTestItemRow, 'MyTest', value, lo, hi, 'PASS' if ok else 'FAIL'])
    if not ok:
        self.sTabDUTInfo.chrErrorCode = '[CODE] MSG'   # 用 errorCode.py 的枚举
    return ok
```

### 3. 接入新仪器 / 新协议
- 串口类设备：继承 `package/SerialCom_Class.py` 的 `ComBasic`，应用层实现命令收发
- 网口仪器：参考 `package/telnet_Class.py`，或用 `Pipe_SendCmdExpectStr()` 做命令行交互
- 仪器参数结构体加到 `structural_var.py` 的 `TabInstrument`，对应节加进 `getCfgSetting()`

### 4. 打包发布
```bat
uv add --dev pyinstaller
uv run pyinstaller -F -w main_MFGWind.py
```
将 `dist/` 中的 exe 与 `cfg.tab`、`gif/`、`icon/` 放同级目录分发。

### 5. 环境变更注意
- 升级 Python / 增删依赖后：`uv sync`（记得带 `UV_PROJECT_ENVIRONMENT`）
- **不要**在项目目录手动创建 `.venv`；误建后删除即可
- 修改界面：用 Qt Designer 编辑 `myUI.ui` 后重新生成 `myUI.py`（`pyuic5 myUI.ui -o myUI.py`）

---

## 已知问题与限制

- `Slot_SFCRoutingCheck`、Oracle 数据库、服务器日志归档为预留挂载点，尚未实现
- 管理员功能（清零计数）密码硬编码在 `structural_var.py` 的 `AdminPWD`
- 环境相关坑（Qt 5.15.2 中文路径崩溃、uv `.env` 加载等）统一记录在 [AGENTS.md](AGENTS.md)

## 作者

JASON.FAN · Ver 4.1.2
"# MFGTool_PyQt5" 
