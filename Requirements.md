What you need in order to run this project:

`Python` (recommended 3.6) and the libraries:  
-`shapely`  
-`matplotlib`  
-`descartes` (for graph drawing)  
-optionally `pandas` (used for processing datasets)  
-very optionally `svg.path` and `dxfwrite` (used for processing datasets to convert them to other file formats to run benchmarks on offline implementations)

And then a lot of things to build  `libnfporb` library.

Building libnfporb
------------------

You will need `boost` (https://www.boost.org/) (or at least `boost geometry`) version **1.65.0** or **earlier** (in later versions, there's a change that breaks libnforb functioning).

You can download it from here:  
https://sourceforge.net/projects/boost/files/boost/1.65.0/  
For Windows users, there are prebuild binaries here:  
https://sourceforge.net/projects/boost/files/boost-binaries/1.65.0/  
(I specifically installed https://sourceforge.net/projects/boost/files/boost-binaries/1.65.0/boost_1_65_0-msvc-14.1-64.exe/download)

Then you need to define following environment variables: `%PYTHONPATH%` (in my case `C:\Users\Damian\AppData\Local\Programs\Python\Python36\`) and `%BOOST_ROOT%` (in my case `C:\local\boost_1_65_0`).

Then you need to make sure that you have `cmake` (download from `https://cmake.org/download/`, don't forget to add it to PATH during installation (on Windows at least)).

Then you need to follow *Visual Studio (Windows)* or *Other systems* steps.

### Visual Studio (Windows)

For Windows users, there is a `build.bat` script in `source/nfp_interface`.

To run it, you need to have Visual Studio 2017 or 2019 with "Desktop development with C++" tools installed (open Visual Studio -> Tools -> Get Tools and Features).

Then you have to make sure that you have `pybind11` (other one than Python library) installed.

My way of installation: go to some repository where you want to install `vcpkg` (e.g. C:/local/), open PowerShell, run following commands:  
`git clone https://github.com/Microsoft/vcpkg.git`  
`.\vcpkg\bootstrap-vcpkg.bat`  
`\.vcpkg\vcpkg.exe install pybind11:x64-windows ` (be patient while it downloads and installs)  
`\.vcpkg\vcpkg.exe integrate install`

It should be enough to just run `build.bat` by doubleclicking the file and it will launch Developer Command Prompt for Visual Studio. If not, then run the file from Developer PowerShell from Visual Studio.

If you manage to get to the point when it generates `libnfporb_interface.pyd` file, but when you try to run e.g. `run_tests.py` and it says `[DLL load failed: The specified module could not be found]`, then try to delete this `libnfporb_interface.pyd` file and rename  `libnfporb_interface.pyd_rescue` to  `libnfporb_interface.pyd` . 

### Other Platforms
Use `cmake` to generate the project for your compiler with the
`CmakeLists.txt` file provided. In the `source/nfp_interface`
folder, run:

``` {.cmd}
mkdir build
cd build
cmake .. -G <your generator>
```

Then, build it with your compiler. After that, you need to
place the build `libnfporb_interface.dll` into the
`wasteoptimiser/nfp_interface` folder and rename it to
`libnfporb_interface.pyd`.

Also, you will most probably need to have `pybind11` installed (other one than Python library).
