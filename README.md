# Whirlpool YU-RIS JoyFix

面向 **Whirlpool（漩涡社）旗下部分采用旧版 32 位 YU-RIS 引擎的游戏**开发的手柄轮询兼容性工具。将匹配的 `joyGetPosEx` 查询替换为立即返回中立手柄状态，缓解特定电脑上菜单、转场和画面持续卡顿的问题。

**本项目仅为个人研究学习项目，不是所有 YU-RIS 游戏的通用加速器。** 真实手柄输入会被这一查询路径的模拟替代。鼠标与键盘的处理不在修改范围内。

## 使用前必读

**本项目全部由 vibe coding 实现，尚未经过严谨、全面的测试。请注意使用风险，并自行验证结果。开始任何修改前，务必自行备份游戏原程序和存档；工具自动创建的备份不能替代你的独立备份。**

本项目以漩涡社游戏的实际问题为开发对象，不承诺覆盖该会社所有作品，也不承诺适用于其他厂商的 YU-RIS 游戏。它是个人研究学习工具，不是 Whirlpool 或 YU-RIS 官方补丁。

## 下载与使用

发布后请在本仓库的 **Releases** 中下载 `Whirlpool-YURIS-JoyFix-windows-x64.zip`，不要把 GitHub 自动生成的 Source code ZIP 当作安装器。

1. 退出目标游戏，**先独立备份游戏原程序和存档**，再解压安装器。
2. 运行 `Whirlpool-YURIS-JoyFix.exe`，选择游戏主程序 `.exe`。
3. 点击“只检查兼容性”，通过后点击“安装补丁”。
4. 正常启动游戏，验证菜单、转场、读档与音频。

无需另装 Python，不创建虚拟设备，不安装驱动，不联网。安装器需要 64 位 Windows，目标游戏须为匹配的 32 位程序。

## 兼容性与验证状态

| 游戏 / 程序 | 状态 |
|---|---|
| pieces / 候鸟的梦：`pieces_chs.exe` | 修复原型实机验证：菜单与转场恢复流畅，输入正常；整理版安装/恢复回归通过 |
| Pieces 揺り籠のカナリア：`pieces_canary.exe` | 代码匹配、安装和恢复验证通过；尚未实机确认效果 |
| Slobbish Dragon Princess：`drapri.exe` | 代码匹配、安装和恢复验证通过；尚未实机确认效果 |

版本可能不同，请以检测结果为准。检查通过代表代码结构匹配，**不代表完整剧情已测试**。不声称某个年份之前的全部游戏都有同一个缺陷。详见 [技术记录](docs/TECHNICAL.md)。

## 恢复

安装器在游戏旁保存 `游戏.exe.joyfix-original.bak` 和 `游戏.exe.joyfix.json`，请保留。退出游戏，选择同一个主程序，点击“恢复原程序”。恢复前后都会校验 SHA-256；游戏被更新或被其他补丁改动后，工具会拒绝覆盖。

早期单独发布的《候鸟的梦》修复exe没有本安装器记录，不能用本工具恢复；请使用当时保存的原程序备份。安装器会拒绝重复打补丁。

## 从源码运行

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m yuris_joyfix
# 或命令行
.venv\Scripts\python -m yuris_joyfix scan "D:\Games\Example\game.exe"
```

开发、测试和构建见 [CONTRIBUTING.md](CONTRIBUTING.md)。反馈请提供程序 SHA-256、游戏版本、系统版本与症状，**不要上传游戏exe、素材、存档或内存转储**。

项目代码采用 MIT 许可证，第三方依赖分别遵循其许可证。仓库不包含游戏程序或素材，与游戏厂商和引擎作者无隶属关系。
