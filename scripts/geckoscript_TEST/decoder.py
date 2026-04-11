"""
THIS IS AN EDITED VERSION OF 'pyiiasmh_cli.py' FROM https://github.com/JoshuaMKW/pyiiasmh/
I edited it to allow a function return instead of a CLI.
All thanks to JoshuaMKW.
"""

#!/usr/bin/env python3

#  PyiiASMH 3 (pyiiasmh_cli.py)
#  Copyright (c) 2011, 2012, Sean Power
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#      * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#      * Neither the names of the authors nor the
#        names of its contributors may be used to endorse or promote products
#        derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL SEAN POWER BE LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import binascii
import re
import shutil
import sys
import tempfile
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional, Tuple, Union

from pyiiasmh.errors import UnsupportedOSError, CodetypeError
from pyiiasmh.ppctools import PpcFormatter

class Decoder(PpcFormatter):

    def __init__(self):
        super().__init__()

        self.opcodes = None
        self.geckocodes = None
        self.bapo = None
        self.xor = None
        self.chksum = None
        self.codetype = None

    def assemble(self, inputasm: str, outputfile: Optional[Union[str, Path]] = None, filetype: str = "text") -> str:
        tmpdir = Path(tempfile.mkdtemp(prefix="pyiiasmh-"))

        if filetype is None:
            try:
                Path(tmpdir, "code.txt").write_text(inputasm)
                inputasm = None
            except IOError:
                self.log.exception("Failed to open input file.")
                shutil.rmtree(tmpdir)
                return None

        try:
            toReturn = ""
            machine_code = self.asm_opcodes(tmpdir, inputasm)
        except UnsupportedOSError as e:
            self.log.exception(e)
            toReturn = (
                f"Your OS \"{sys.platform}\" is not supported. See \"error.log\" for details and also read the README.")
        except IOError as e:
            self.log.exception(e)
            toReturn = f"Error: {str(e)}"
        except RuntimeError as e:
            self.log.exception(e)
            toReturn = str(e)
        else:
            if self.bapo is not None:
                if self.bapo[0] not in ("8", "0") or self.bapo[1] not in ("0", "1"):
                    return f"Invalid ba/po: {self.bapo}"
                elif int(self.bapo[2], 16) > 7 and self.bapo[1] == "1":
                    return f"Invalid ba/po: {self.bapo}"

            toReturn = self.construct_code(
                machine_code, self.bapo, self.xor, self.chksum, self.codetype)
            if outputfile is not None:
                if isinstance(outputfile, str):
                    outputfile = Path(outputfile)

                if filetype == "text":
                    outputfile.write_text(toReturn)
                elif filetype == "bin":
                    outputfile.write_bytes(bytes.fromhex(
                        toReturn.replace("\n", "").replace(" ", "")))
                else:
                    outputfile.write_text(toReturn)

        shutil.rmtree(tmpdir, ignore_errors=True)
        return toReturn
        
    def split_gecko_blocks(self, code: str) -> list[str]:
        blocks = []
        current_block = []

        codetypes = ("04", "14", "05", "15", "06", "07", "16", "17", "C0", "C2", "C3", "D2", "D3", "F2", "F3", "F4", "F5")

        for line in code.strip().splitlines():
            if line[:2] in codetypes and current_block:
                blocks.append("\n".join(current_block))
                current_block = []
            current_block.append(line)

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def disassemble(self,
                    inputfile,
                    outputfile: Optional[Union[str, Path]] = None,
                    filetype: str = "text",
                    cFooter: bool = True,
                    formalNames: bool = False) -> Tuple[str, Tuple[Any, Any, Any, Any]]:
        tmpdir = tempfile.mkdtemp(prefix="pyiiasmh-")
        codes = None

        if filetype == "bin":
            access = "rb"
        else:
            access = "r"

        if filetype is None:
            codes = inputfile
        else:
            try:
                with open(inputfile, access) as f:
                    codes = "".join(f.readlines())
                    if filetype == "bin":
                        codes = binascii.b2a_hex(codes).upper()
            except IOError as e:
                self.log.exception("Failed to open input file.")
                shutil.rmtree(tmpdir)
                return [f"Error: {str(e)}", (None, None, None, None)]
            
        blocks = self.split_gecko_blocks(codes)
        print(blocks)
        rawcodes = []
        for block in blocks:
            print(block)
            rawcode = self.deconstruct_code(codes, cFooter)
            rawcodes.append(rawcode)
        return rawcodes

        """
        try:
            with Path(tmpdir, "code.bin").open("wb") as f:
                rawhex = "".join("".join(rawcodes[0].split("\n")).split(" "))
                try:
                    f.write(binascii.a2b_hex(rawhex))
                except binascii.Error:
                    f.write(b"")
        except IOError:
            self.log.exception("Failed to open temp file.")

        try:
            toReturn = ["", (None, None, None, None)]
            opcodes = self.dsm_geckocodes(tmpdir, outputfile)
        except UnsupportedOSError:
            self.log.exception("")
            toReturn = [(f"Your OS \"{sys.platform}\" is not supported. " +
                         "See \"error.log\" for details and also read the README."),
                        (None, None, None, None)]
        except IOError as e:
            self.log.exception(e)
            toReturn = ["Error: " + str(e), (None, None, None, None)]
        except RuntimeError as e:
            self.log.exception(e)
            toReturn = [str(e), (None, None, None, None)]
        else:
            toReturn = [opcodes + "\n", rawcodes[1:]]

        if formalNames:
            opcodes = []
            for line in toReturn[0].split("\n"):
                values = re.sub(r"(?<!c)r1(?![0-9])", "sp", line)
                values = re.sub(r"(?<!c)r2(?![0-9])", "rtoc", values)
                opcodes.append(values)
            toReturn[0] = "\n".join(opcodes)

        shutil.rmtree(tmpdir)

        return toReturn
    """

    def run(self, type: str, path: str, filetype: str = "text"):
        if type == "gecko":
            return self.disassemble(path, None, filetype=filetype)
        elif type == "asm":
            return self.assemble(path, None, filetype=filetype)
