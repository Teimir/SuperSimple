import struct
import tempfile
import unittest

from emulator.decoder import InstructionDecoder
from emulator.memory import Memory
from emulator.core import CPU


class MemoryTests(unittest.TestCase):
    def test_load_and_read(self):
        mem = Memory(size_words=4)
        data = struct.pack("<IIII", 1, 2, 3, 4)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(data)
            tmp.flush()
            mem.load_from_file(tmp.name)
        self.assertEqual(mem.read_word(0), 1)
        self.assertEqual(mem.read_word(3), 4)


class DecoderTests(unittest.TestCase):
    def test_decode_format_011(self):
        decoder = InstructionDecoder()
        # opcode=1 (add), format=011, dest=r2, src1=r1, src2=r0
        instr = (1 << 3) | (2 << 7) | (1 << 12) | (0 << 17) | 0b011
        decoded = decoder.decode(instr)
        self.assertEqual(decoded.opcode, 1)
        self.assertEqual(decoded.format_type, 0b011)
        self.assertEqual(decoded.dest_reg, 2)
        self.assertEqual(decoded.src1_reg, 1)
        self.assertEqual(decoded.src2_reg, 0)


class ExecutionTests(unittest.TestCase):
    def test_mov_add_halt(self):
        cpu = CPU()
        # mov r1, #5 (format 001)
        mov_instr = (0 << 3) | (1 << 7) | (5 << 12) | 0b001
        # add r2, r1, r0 (format 011)
        add_instr = (1 << 3) | (2 << 7) | (1 << 12) | (0 << 17) | 0b011
        # hlt literal
        hlt_instr = 5
        cpu.memory.data[0] = mov_instr
        cpu.memory.data[1] = add_instr
        cpu.memory.data[2] = hlt_instr
        cpu.running = True
        cpu.run(max_steps=10)
        self.assertEqual(cpu.read_reg(1), 5)
        self.assertEqual(cpu.read_reg(2), 5)
        self.assertFalse(cpu.running)


if __name__ == "__main__":
    unittest.main()
