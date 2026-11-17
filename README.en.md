# Whirlpool YU-RIS JoyFix

[中文说明](README.md)

A Windows compatibility patcher developed for selected **Whirlpool visual novels using older 32-bit YU-RIS engines**. It replaces one recognized `winmm!joyGetPosEx` call with a neutral, successful joystick response. This may resolve sustained stutter caused by repeated device queries on affected systems.

This project is solely a personal research and learning project.

**This project was implemented entirely through vibe coding. It has not undergone rigorous, comprehensive testing. Use it at your own risk and independently verify the results. Before making any changes, you must create your own backups of the original game executable and save files. Automatic backups are not a substitute for independent backups.**

This is a community tool, not an official Whirlpool or YU-RIS patch. Compatibility with all Whirlpool titles or other publishers is not promised.

This is **not a universal YU-RIS performance fix**. Controller input through the patched path is disabled. The current GUI and errors are in Chinese.

Download the Windows x64 ZIP from Releases, close the game, select its executable, check compatibility, then install. No Python or driver installation is required for the packaged app. Keep the adjacent `.joyfix-original.bak` and `.joyfix.json` files for restoration.

Runtime improvement was confirmed for the Chinese `pieces_chs.exe` prototype. `pieces_canary.exe` and `drapri.exe` passed structural checks and byte-perfect install/restore testing, but have not yet been runtime-validated. See [technical notes](docs/TECHNICAL.md).

Source: Python 3.11, `pip install -r requirements.txt`, then `python -m yuris_joyfix`. MIT licensed; no game executables, assets or saves are distributed.
