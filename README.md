# Synacor Challenge

These are my solutions to the [Synacor Challenge](https://challenge.synacor.com/). 

Folders:

* `asm/` - transcription of the teleporter check in assembly. Needs to be reviewed, and of course still too slow.
* `bin/` - the binary file of the challange and other user-made binary files
* `info/` - VM specs, challange codes, and clues from the game
* `misc/` - notes, disassembly of the bin-file

Python Scripts:

* `dump_binary.py` - reads the bin file, and writes a disassembly. More features need to be added
* `opc_lookup.py` - a class providing information about the opcodes. Interactive opcode lookup if run as standalone file
* `orb_puzzle.py` - solution to the orb puzzle using the DFS method.
* `vm.py` - the virtual machine class for the synachor bin file. Includes routines to load a custum command buffer (see blow), patches for the loaded bin-file to avoid register checks and the teleporter check routine. Also contains a custom direct call to the teleporter check subrouting as well as a transcription as method. Finally a method is included to find the correct value of the 8th regiser. An additional method that decodes hidden text strings in the bin file may be used (and maybe included in the `dump_binary.py` file...)

Text Files:

* `input_buffer.txt` - text file containing keyboard inputs for the challange