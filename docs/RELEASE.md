# 首次公开发布建议

建议仓库：`perciya513/whirlpool-yuris-joyfix`，公开；描述：`Joystick polling fix for selected Whirlpool games using older YU-RIS engines.`

发布标签：`v0.1.0`。

1. 将本目录作为仓库根目录，确认MIT授权选择后提交源码。不要上传原聊天outputs目录或游戏文件。
2. 等待Checks工作流通过。该工作流只运行测试，不发布内容。
3. 在Windows运行 `python scripts/build.py`，使用本次源码新生成的安装包；不要复用早期1.0安装器。
4. 在GitHub Releases创建草稿，标签指向已验证提交，附上 `Whirlpool-YURIS-JoyFix-windows-x64.zip` 和 `SHA256SUMS.txt`。
5. 使用下方发布说明发布。不要声称有数字签名或已通过平台认证。

## 可直接使用的发布说明

v0.1.0 面向漩涡社部分使用旧版32位YU-RIS的游戏，尝试缓解手柄查询导致的持续卡顿。

本项目仅为个人研究学习项目。

**本项目全部由 vibe coding 实现，尚未经过严谨、全面测试。请注意使用风险并自行验证结果，开始前务必独立备份游戏原程序和存档。**

- 自动检查代码特征，匹配后模拟“已连接、无输入”的手柄状态。
- 自动备份和SHA-256校验恢复；无驱动安装，无网络访问。
- 候鸟的梦原型已实机确认改善；摇篮的金丝雀和Slobbish Dragon Princess仅完成结构与安装/恢复验证，欢迎反馈。
- 这一输入路径的真实手柄支持会被替代；不适用于所有YU-RIS版本。

下载Windows x64 ZIP，解压后运行安装器。请先退出游戏。保留游戏旁的备份和安装记录。

GitHub说明：[管理Release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)。
