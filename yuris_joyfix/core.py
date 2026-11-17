"""Local YU-RIS joystick compatibility patch installer; no driver or DLL injection."""

import pathlib, struct, hashlib, json, re, os, tempfile
import pefile, capstone
from . import __version__ as VERSION

SIGNATURE = [
    "test eax, eax",
    "jne IMAGE",
    "mov edx, dword ptr [esp + 0x10]",
    "mov byte ptr [edx + IMAGE], 1",
    "mov edi, dword ptr [ebx + IMAGE]",
    "mov ebp, dword ptr [esp + 0x10]",
    "lea esi, [ebp + ebp]",
    "add esi, esi",
    "lea ebp, [esi + esi*8]",
    "cmp edi, 0x7fff",
    "mov edx, 0",
    "setb dl",
    "shl edx, 7",
    "mov byte ptr [esi + esi*8 + IMAGE], dl",
    "cmp edi, 0x7fff",
    "mov ecx, 0",
    "seta cl",
    "shl ecx, 7",
    "mov byte ptr [esi + esi*8 + IMAGE], cl",
    "mov edx, dword ptr [ebx + IMAGE]",
    "cmp edx, 0x7fff",
    "mov eax, 0",
    "setb al",
    "shl eax, 7",
    "mov byte ptr [esi + esi*8 + IMAGE], al",
    "cmp edx, 0x7fff",
    "mov edx, 0",
    "seta dl",
    "shl edx, 7",
    "mov byte ptr [esi + esi*8 + IMAGE], dl",
    "xor ecx, ecx",
    "mov edx, dword ptr [ebx + IMAGE]",
    "test dword ptr [ecx*4 + IMAGE], edx",
    "mov eax, 0",
    "setne al",
    "shl eax, 7",
    "mov byte ptr [ebp + ecx + IMAGE], al",
    "inc ecx",
    "cmp ecx, 0x20",
    "jl IMAGE",
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(code, addr):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    result = []
    for i in md.disasm(code, addr):
        operands = re.sub(
            r"0x[0-9a-f]+",
            lambda m: "IMAGE" if int(m[0], 16) >= 0x400000 else m[0],
            i.op_str,
        )
        result.append(i.mnemonic + " " + operands)
        if len(result) == 40:
            break
    return result


def inspect(data):
    pe = pefile.PE(data=data)
    if pe.OPTIONAL_HEADER.ImageBase != 0x400000:
        raise ValueError("当前版本只支持基址为0x400000的已匹配引擎。")
    if pe.FILE_HEADER.Machine != 0x14C or pe.OPTIONAL_HEADER.Magic != 0x10B:
        raise ValueError("只支持32位 x86 游戏程序。")
    if "YU-RIS Script Engine".encode("utf-16le") not in data:
        raise ValueError("未识别为支持的 YU-RIS 程序。")
    if any(s.Name.rstrip(b"\0") == b".joyfix" for s in pe.sections):
        raise ValueError("程序已经含有手柄补丁，请勿重复安装。")
    if pe.OPTIONAL_HEADER.DATA_DIRECTORY[4].Size:
        raise ValueError("此程序带有数字签名，当前版本不修改。")
    imports = [
        i
        for d in pe.DIRECTORY_ENTRY_IMPORT
        if d.dll.lower() == b"winmm.dll"
        for i in d.imports
        if i.name == b"joyGetPosEx"
    ]
    if len(imports) != 1:
        raise ValueError("没有找到唯一的 WINMM!joyGetPosEx 导入。")
    needle = b"\xff\x15" + struct.pack("<I", imports[0].address)
    sites = []
    for s in pe.sections:
        if not s.Characteristics & 0x20000000:
            continue
        start = s.PointerToRawData
        end = start + s.SizeOfRawData
        p = data.find(needle, start, end)
        while p != -1:
            sites.append(p)
            p = data.find(needle, p + 1, end)
    if len(sites) != 1:
        raise ValueError("手柄调用不是唯一位置，停止自动修改。")
    site = sites[0]
    if data[site - 6 : site] != bytes.fromhex("528b4c241451"):
        raise ValueError("手柄参数传递代码不匹配。")
    rva = pe.get_rva_from_offset(site)
    if (
        norm(data[site + 6 : site + 400], pe.OPTIONAL_HEADER.ImageBase + rva + 6)
        != SIGNATURE
    ):
        raise ValueError("周边输入处理代码不匹配，不能安全自动安装。")
    header = pe.sections[-1].get_file_offset() + 40
    if (
        header + 40 > pe.OPTIONAL_HEADER.SizeOfHeaders
        or data[header : header + 40] != b"\0" * 40
    ):
        raise ValueError("程序没有足够的节表空间，停止修改。")
    return pe, site, rva, header


def patch(data):
    pe, site, callrva, header = inspect(data)
    stub = bytearray.fromhex("8b4c2408")
    for offset, value in [(x, 0x7FFF) for x in (8, 12, 16, 20, 24, 28)] + [
        (32, 0),
        (36, 0),
        (40, 0xFFFF),
        (44, 0),
        (48, 0),
    ]:
        stub += b"\xc7\x41" + bytes([offset]) + struct.pack("<I", value)
    stub += bytes.fromhex("31c0c20800")
    align = lambda n, a: (n + a - 1) // a * a
    rva = align(
        max(
            s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData)
            for s in pe.sections
        ),
        pe.OPTIONAL_HEADER.SectionAlignment,
    )
    raw = align(len(data), pe.OPTIONAL_HEADER.FileAlignment)
    size = align(len(stub), pe.OPTIONAL_HEADER.FileAlignment)
    result = bytearray(data)
    result.extend(b"\0" * (raw + size - len(result)))
    result[raw : raw + len(stub)] = stub
    result[header : header + 40] = struct.pack(
        "<8sIIIIIIHHI", b".joyfix\0", len(stub), rva, size, raw, 0, 0, 0, 0, 0x60000020
    )
    struct.pack_into(
        "<H",
        result,
        pe.FILE_HEADER.get_field_absolute_offset("NumberOfSections"),
        pe.FILE_HEADER.NumberOfSections + 1,
    )
    struct.pack_into(
        "<I",
        result,
        pe.OPTIONAL_HEADER.get_field_absolute_offset("SizeOfImage"),
        align(rva + len(stub), pe.OPTIONAL_HEADER.SectionAlignment),
    )
    struct.pack_into(
        "<I",
        result,
        pe.OPTIONAL_HEADER.get_field_absolute_offset("SizeOfCode"),
        pe.OPTIONAL_HEADER.SizeOfCode + size,
    )
    result[site : site + 6] = b"\xe8" + struct.pack("<i", rva - callrva - 5) + b"\x90"
    struct.pack_into(
        "<I",
        result,
        pe.OPTIONAL_HEADER.get_field_absolute_offset("CheckSum"),
        pefile.PE(data=bytes(result)).generate_checksum(),
    )
    return bytes(result), {
        "version": VERSION,
        "original_sha256": sha(data),
        "patched_sha256": sha(result),
        "call_rva": hex(callrva),
        "stub_rva": hex(rva),
    }


def paths(exe):
    return exe.with_name(exe.name + ".joyfix-original.bak"), exe.with_name(
        exe.name + ".joyfix.json"
    )


def replace(exe, data):
    fd, tmp = tempfile.mkstemp(prefix=".joyfix-", suffix=".tmp", dir=str(exe.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, exe)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def install(exe):
    original = exe.read_bytes()
    result, record = patch(original)
    backup, manifest = paths(exe)
    if backup.exists() or manifest.exists():
        raise ValueError("备份或安装记录已存在。请先检查或恢复，工具不会覆盖旧备份。")
    # Prepare recoverable backup and record before changing the executable.
    with backup.open("xb") as f:
        f.write(original)
    if sha(backup.read_bytes()) != sha(original):
        raise ValueError("备份校验失败，未修改程序。")
    with manifest.open("x", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    if sha(exe.read_bytes()) != record["original_sha256"]:
        raise ValueError("文件在准备期间发生变化，未覆盖。")
    replace(exe, result)
    if sha(exe.read_bytes()) != record["patched_sha256"]:
        raise ValueError("写入后的校验未通过，请使用恢复功能。")
    return "安装成功。请重新启动游戏。原程序备份：\n" + str(backup)


def restore(exe):
    backup, manifest = paths(exe)
    if not backup.is_file() or not manifest.is_file():
        raise ValueError("没有找到本工具生成的备份和安装记录。")
    record = json.loads(manifest.read_text(encoding="utf-8"))
    data = backup.read_bytes()
    if sha(data) != record["original_sha256"]:
        raise ValueError("备份校验不匹配，停止恢复。")
    if sha(exe.read_bytes()) not in (
        record["original_sha256"],
        record["patched_sha256"],
    ):
        raise ValueError("程序已被更新或另一个补丁修改，停止覆盖。")
    replace(exe, data)
    if sha(exe.read_bytes()) != record["original_sha256"]:
        raise ValueError("恢复校验失败，保留备份。")
    backup.unlink()
    manifest.unlink()
    return "已恢复安装前的原程序，存档和配置未改动。"


def scan(exe):
    pe, site, rva, header = inspect(exe.read_bytes())
    return (
        "结构检查通过，可安装手柄模拟补丁。\n程序："
        + str(exe)
        + "\n查询位置 RVA："
        + hex(rva)
        + "\n尚未验证此游戏的实际运行效果。"
    )
