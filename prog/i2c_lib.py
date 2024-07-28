from time import sleep
from typing import List, Sequence

from smbus2 import SMBus


class i2c_device:
  def __init__(self, addr: int, port: int=0) -> None:
    self.addr = addr
    self.bus = SMBus(port)

  # Write a single command
  def write_cmd(self, cmd: int) -> None:
    self.bus.write_byte(self.addr, cmd)
    sleep(0.0001)

  # Write a command and argument
  def write_cmd_arg(self, cmd: int, data: int) -> None:
    self.bus.write_byte_data(self.addr, cmd, data)
    sleep(0.0001)

  # Write a block of data
  def write_block_data(self, cmd: int, data: Sequence[int]) -> None:
    self.bus.write_block_data(self.addr, cmd, data)
    sleep(0.0001)

  # Read a single byte
  def read(self) -> int:
    return self.bus.read_byte(self.addr)

  # Read
  def read_data(self, cmd: int) -> int:
    return self.bus.read_byte_data(self.addr, cmd)

  # Read a block of data
  def read_block_data(self, cmd: int) -> List[int]:
    return self.bus.read_block_data(self.addr, cmd)

