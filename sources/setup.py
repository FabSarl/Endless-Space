from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="Endless Space",
      version ="alpha 0.3",
      description = "Space Shooter",
      executables=[Executable("endless-space.pyw", base=base)])
