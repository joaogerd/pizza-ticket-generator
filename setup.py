import cx_Freeze
import sys
import os
import math
from fpdf import FPDF

base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("geraTickets.py", base=base)]

cx_Freeze.setup(
    name="geraTickets",
    options={
        "build_exe": {
            "packages": ["PyQt5.QtWidgets", "sys", "math", "fpdf"],
            "zip_include_packages": "*",
            "zip_exclude_packages": [],
            "include_files": [("data/pizza.png", "data/pizza.png"), 
                              ("data/Helvetica-Bold.ttf", "data/Helvetica-Bold.ttf")],
        }
    },
    version="0.01",
    author="João Gerd Zell de Mattos",
    description="Gui para gerar tickets de pizza",
    executables=executables,
)

