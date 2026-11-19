# 机制与证据

识别条件：PE32/x86、基址0x400000、YU-RIS产品标记、唯一WINMM!joyGetPosEx导入及唯一直接调用、调用前参数构造及调用后40条指令匹配、节表空间充足、无数字签名、未含.joyfix节。当前归一化规则将大于等于0x400000的地址替换为IMAGE；它是结构特征，不是形式化语义证明。

添加只读可执行的 `.joyfix` 节，放入86字节stdcall函数；改写6字节调用为相对CALL加NOP。保留JOYINFOEX的size/flags，将六轴设为0x7fff、按钮设为0、POV设为0xffff、保留字段清零，返回0并弹出8字节参数。中心值来自目标代码的实际比较常量。原入口、导入和其他逻辑保留；不修改存档。

说人话：往游戏的手柄轮询接口传入固定参数，让游戏自以为手柄已连接，从而停止大量占用运行资源去轮询检查

## 本地观察（2026-11-17）

约3秒采样中，候鸟旧程序内核CPU时间2.16–2.47秒，新作Relirium约0.17秒。旧作栈样本反复出现WINMM、DINPUT和设备枚举代码。手柄模拟补丁后内核CPU时间约0.109秒，用户确认菜单和转场恢复流畅、输入正常。

这些是特定电脑和标题场景的短时观察，不是普遍帧率保证。早期栈调查使用上下文和栈中返回地址候选采样，不是完整符号化堆栈；新作的配置、场景及附加模块不同。因此不将现象直接归因于所有旧引擎的统一缺陷，也不声称某款驱动必然有故障。

## 已检查版本（安装前SHA-256）

| 程序 | SHA-256 | 查询RVA |
|---|---|---|
| pieces_chs.exe | a3e4b57d604e13e9d4c5eb55af5dbcd02c303993bbaeebdcb7ba7ad051606122 | 0x1034f |
| pieces_canary.exe | 42b9df5a0e57334267528ebb5f86f62a84a50aa2e8c530cfc9179996b4624945 | 0x1034f |
| drapri.exe | 31780f69730d92eff6cc76d88f2a6fd830653aa0c37a3cf1ef624cdbea904289 | 0x1037f |

接口定义：[Microsoft joyGetPosEx](https://learn.microsoft.com/en-us/windows/win32/api/joystickapi/nf-joystickapi-joygetposex)。
