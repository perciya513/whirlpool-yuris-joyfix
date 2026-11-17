"""Synthetic PE fixtures: no commercial game binary is needed or included."""

import pathlib
import struct
import tempfile
import unittest
from unittest.mock import patch as mock_patch

import keystone
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import (
    UC_X86_REG_EAX,
    UC_X86_REG_ESP,
    UC_X86_REG_EBX,
    UC_X86_REG_ESI,
    UC_X86_REG_EDI,
    UC_X86_REG_EBP,
)
from yuris_joyfix import core


def fixture():
    data = bytearray(0x600)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 0x84, 0x14C, 2, 0, 0, 0, 224, 0x102)
    opt = 0x98
    struct.pack_into("<H", data, opt, 0x10B)
    for offset, value in {
        4: 0x200,
        8: 0x200,
        16: 0x1000,
        20: 0x1000,
        24: 0x2000,
        28: 0x400000,
        32: 0x1000,
        36: 0x200,
        56: 0x3000,
        60: 0x200,
        72: 0x100000,
        76: 0x1000,
        80: 0x100000,
        84: 0x1000,
        92: 16,
        104: 0x2000,
        108: 40,
    }.items():
        struct.pack_into("<I", data, opt + offset, value)
    struct.pack_into("<H", data, opt + 68, 2)
    for index, (name, rva, raw, flags) in enumerate(
        [
            (b".text", 0x1000, 0x200, 0x60000020),
            (b".rdata", 0x2000, 0x400, 0x40000040),
        ]
    ):
        struct.pack_into(
            "<8sIIIIIIHHI",
            data,
            0x178 + index * 40,
            name,
            0x200,
            rva,
            0x200,
            raw,
            0,
            0,
            0,
            0,
            flags,
        )
    assembly = "; ".join(line.replace("IMAGE", "0x402180") for line in core.SIGNATURE)
    code, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(
        assembly, 0x40100C
    )
    prefix = bytes.fromhex("528b4c241451ff1550204000")
    data[0x200 : 0x200 + len(prefix) + len(code)] = prefix + bytes(code)
    struct.pack_into("<IIIII", data, 0x400, 0x2040, 0, 0, 0x2060, 0x2050)
    struct.pack_into("<II", data, 0x440, 0x2080, 0)
    struct.pack_into("<II", data, 0x450, 0x2080, 0)
    data[0x460:0x46A] = b"WINMM.dll\0"
    data[0x480:0x48E] = b"\0\0joyGetPosEx\0"
    marker = "YU-RIS Script Engine".encode("utf-16le")
    data[0x4C0 : 0x4C0 + len(marker)] = marker
    return bytes(data)


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.exe = pathlib.Path(self.tmp.name) / "game.exe"
        self.original = fixture()
        self.exe.write_bytes(self.original)

    def test_roundtrip_and_repeat_rejected(self):
        core.scan(self.exe)
        core.install(self.exe)
        self.assertNotEqual(self.exe.read_bytes(), self.original)
        with self.assertRaises(ValueError):
            core.install(self.exe)
        core.restore(self.exe)
        self.assertEqual(self.exe.read_bytes(), self.original)
        self.assertFalse(core.paths(self.exe)[0].exists())

    def test_changed_program_not_overwritten_on_restore(self):
        core.install(self.exe)
        self.exe.write_bytes(self.exe.read_bytes() + b"updated")
        with self.assertRaises(ValueError):
            core.restore(self.exe)
        self.assertTrue(core.paths(self.exe)[0].exists())

    def test_corrupt_backup_refused(self):
        core.install(self.exe)
        core.paths(self.exe)[0].write_bytes(b"corrupt")
        with self.assertRaises(ValueError):
            core.restore(self.exe)

    def test_failed_replace_recoverable(self):
        with mock_patch.object(
            core.os, "replace", side_effect=PermissionError("locked")
        ):
            with self.assertRaises(PermissionError):
                core.install(self.exe)
        self.assertEqual(self.exe.read_bytes(), self.original)
        core.restore(self.exe)
        self.assertEqual(self.exe.read_bytes(), self.original)

    def test_bad_signature_and_arguments_rejected(self):
        for offset in (0x200, 0x20C):
            data = bytearray(self.original)
            data[offset] = 0x90
            with self.assertRaises(ValueError):
                core.inspect(bytes(data))

    def test_wrong_arch_and_signature_rejected(self):
        data = bytearray(self.original)
        struct.pack_into("<H", data, 0x84, 0x8664)
        with self.assertRaises(ValueError):
            core.inspect(bytes(data))
        data = bytearray(self.original)
        struct.pack_into("<II", data, 0x98 + 128, 0x500, 8)
        with self.assertRaises(ValueError):
            core.inspect(bytes(data))

    def test_machine_code_neutral_state_and_stack(self):
        patched, record = core.patch(self.original)
        pe = pefile.PE(data=patched)
        rva = int(record["stub_rva"], 16)
        code = pe.get_data(rva, 86)
        for device in (0, 1, 15):
            u = Uc(UC_ARCH_X86, UC_MODE_32)
            for addr in (0x10000, 0x20000, 0x30000):
                u.mem_map(addr, 0x1000)
            u.mem_write(0x10000, code)
            u.mem_write(0x20000, b"\xa5" * 128)
            u.mem_write(0x20010, struct.pack("<13I", 52, 255, *([123] * 11)))
            u.mem_write(0x30800, struct.pack("<III", 0x10100, device, 0x20010))
            u.reg_write(UC_X86_REG_ESP, 0x30800)
            regs = (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP)
            for reg in regs:
                u.reg_write(reg, 0x12345678)
            u.emu_start(0x10000, 0x10100, count=100)
            self.assertEqual(u.reg_read(UC_X86_REG_EAX), 0)
            self.assertEqual(u.reg_read(UC_X86_REG_ESP), 0x3080C)
            self.assertEqual(
                struct.unpack("<13I", u.mem_read(0x20010, 52)),
                (52, 255, *([0x7FFF] * 6), 0, 0, 0xFFFF, 0, 0),
            )
            for reg in regs:
                self.assertEqual(u.reg_read(reg), 0x12345678)
            self.assertEqual(bytes(u.mem_read(0x20000, 16)), b"\xa5" * 16)
            self.assertEqual(bytes(u.mem_read(0x20044, 16)), b"\xa5" * 16)


if __name__ == "__main__":
    unittest.main()
