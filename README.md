# Online2DIrregularBPP
 My implementation of online 2D irregular BPP algorithm with state-of-the-art picking policy minimal surrounding waste.



**Licence**: The software as a whole is licenced under **GPL v3** because I'm using GPL v3-licenced library [libnfporb](https://github.com/kallaballa/libnfporb/), but for the everything except repository `source/nfp_interface` I'm granting **MIT** licence.  
+I would be happy if you wrote to me when you use my project because I'm curious if this will be useful for someone :)

**Note**: If you want to replace *libnfporb* library with your own implementation of No-fit polygon and Inner-fit polygon calculation, then you need to modify only the `geometry_tools.py` file (call your own functions, maybe modify error handling, ...) to make it work.

**Build**: see `Requirements.md` for instructions.

**Usage**:  run `run_tests.py` for a sample computation. If you choose `best_run`, then it runs on dataset generators  from `SFG_competition` using specified parameters. `euro_datasets` loads and runs specified datasets from `.csv` files.

**Versions**:  
Current version uses last version of `libnfporb` (the library was archived on 8th March 2023) with my modifications and requires `boost` version 1.76.0. It's more robust than older version => less errors in NPF computations => very slightly different results and significantly faster times on some of the EURO datasets (those with a lot of NFP computation errors).     
For latest version that uses original `libnfporb` library with `boost` version 1.65.0, see tag `last-boost-1.65.0`. Results included in `results` folder should be reproducible with this version, at least on Windows. 

**Performance note**: it seems that when building the `libnfprob` with `cmake` (at least on Linux), there is a big (around 10x) performance penalty compared to building with Visual Studio (with average time to place 1 shape (using tests in `run_test.py`) around +- 1 second). If you figure out how to compile it more effectively, please let me know.  

**References**: My [Bachelor thesis](https://dspace.cuni.cz/bitstream/handle/20.500.11956/148383/130316114.pdf) (written in Czech).
