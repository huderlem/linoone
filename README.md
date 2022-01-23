# Linoone
Linoone is a static website generator for Pokémon decompilation projects (only [pokeemerald](https://github.com/pret/pokeemerald) is currently supported). Many projects add custom Pokémon, moves, and much more.  Sometimes, authors like to provide a reference website for the players, similar to Bulbapedia or Serebii. Linoone aims to automatically generate a reference website like that, based on the data from the project's source code.

***Linoone is in the very early development stage right now--it is not ready for actual use.***

## Setup

Linoone is built with Python 3. It has a few dependencies, which are listed in `requirements.txt` and can be installed using the following `pip` command.
```sh
pip install -r requirements.txt
```

Additionally, you must have [Graphviz](https://graphviz.org/download/) installed and available on your path.

Linoone uses `pycparser` to parse the project's C files. `pycparser` has a couple issues with parsing the vanilla pokeemerald source code.

In your pokeemerald repo, in `include/global.h`, stub out `__attribute__` at the top of the file.
```diff
@@ -1,6 +1,8 @@
 #ifndef GUARD_GLOBAL_H
 #define GUARD_GLOBAL_H

+#define __attribute__(x)
+
 #include <string.h>
 #include <limits.h>
 #include "config.h" // we need to define config before gba headers as print stuff needs the functions nulled before defines.
@@ -107,7 +109,7 @@
```

There is also a bug in `pycparser` which makes it choke on various unicode characters in the decomp files. You need to manually apply this fix to your local installation of `pycparser`: https://github.com/eliben/pycparser/issues/415

That's all--you should now be ready to run Linoone. See the Usage section below.

## Usage

Simply invoke `main.py`, while providing the filepath to the project's directory.
```sh
python main.py "D:\path\to\pokeemerald"
```

It will take awhile to run the first time (~30 seconds?) because parsing the C files is a slow process. Subsequent runs are very fast because the C files are cached into `.pickle` files in the same directory. If everything succeeds, you will see a `dist/` directory created with the resulting HTML files.
