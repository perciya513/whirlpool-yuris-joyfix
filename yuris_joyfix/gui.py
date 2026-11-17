"""Tk user interface. Importing core never opens windows."""

import pathlib
from .core import scan, install, restore
from . import __version__ as VERSION


def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title("Whirlpool YU-RIS 手柄模拟补丁 " + VERSION)
    root.geometry("680x440")
    root.resizable(False, False)
    path = tk.StringVar()
    tk.Label(
        root,
        text="选择游戏主程序（.exe），请先退出游戏。",
        font=("Microsoft YaHei", 12),
    ).pack(pady=15)
    row = tk.Frame(root)
    row.pack(fill="x", padx=20)
    tk.Entry(row, textvariable=path, width=65).pack(side="left")
    tk.Button(
        row,
        text="选择…",
        command=lambda: path.set(
            filedialog.askopenfilename(filetypes=[("游戏程序", "*.exe")]) or path.get()
        ),
    ).pack(side="right")
    tk.Label(
        root,
        text="模拟已连接且无输入的手柄；不安装驱动。\n真实手柄输入将不再通过这一查询路径生效。\n面向漩涡社部分旧版 YU-RIS 游戏，不保证全部兼容。\n安装会备份原程序；恢复会校验文件后撤销修改。",
        justify="left",
        font=("Microsoft YaHei", 10),
    ).pack(pady=18)

    tk.Label(
        root,
        text="本项目全部由 vibe coding 实现，0.1.0 尚未经过严谨测试。\n请注意使用风险并自行验证结果。\n开始前务必独立备份游戏原程序和存档。",
        justify="left",
        fg="#a52a2a",
        font=("Microsoft YaHei", 10),
        wraplength=630,
    ).pack(pady=8)

    def run(action):
        try:
            exe = pathlib.Path(path.get())
            if not exe.is_file():
                raise ValueError("请先选择游戏主程序。")
            if action == install and not messagebox.askyesno(
                "安装确认",
                "本项目全部由 vibe coding 实现，请自行验证结果。\n开始前务必独立备份游戏原程序和存档。\n\n已完成备份，并继续修改所选程序？",
            ):
                return
            messagebox.showinfo("结果", action(exe))
        except Exception as e:
            messagebox.showerror(
                "未完成", str(e) + "\n\n若文件正在使用，请退出游戏后重试。"
            )

    bar = tk.Frame(root)
    bar.pack()
    for title, action in [
        ("只检查兼容性", scan),
        ("安装补丁", install),
        ("恢复原程序", restore),
    ]:
        tk.Button(bar, text=title, command=lambda a=action: run(a), width=18).pack(
            side="left", padx=5
        )
    root.mainloop()
