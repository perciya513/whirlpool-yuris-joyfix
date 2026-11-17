# 开发与测试

Python 3.11（发布构建使用64位Windows）。运行：

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/build.py
```

构建输出在 `dist/`，包含安装器、说明、许可证和 SHA256 校验文件。测试使用从零生成的最小PE文件及手写模拟函数，不依赖游戏文件。真实游戏回归在本地副本进行，不提交二进制、个人路径或采样原始数据。

核心修改位于 `yuris_joyfix/core.py`；UI和入口分别位于 `gui.py`、`__main__.py`。扩展识别规则时必须同时添加拒绝错误结构的测试，不要简单放宽成“只要导入joyGetPosEx就修改”。

备份和恢复规则：不覆盖既有备份；写入前重查源哈希；恢复前验证当前文件与备份，恢复后再验证。原子替换防止留下半写入exe，但不构成抵抗并发恶意修改或断电的完整事务保障。游戏运行或文件权限不足时应退出游戏并检查实际文件状态。
