What you need in order to run this project:

`Python` (personally using 3.6, higher version might be also ok) and the libraries:  
-`shapely` (personally using 1.7.1)  
-`matplotlib` (personally using 3.3.2)  
-`descartes` (for graph drawing) (personally using 1.1.0)  
-optionally `pandas` (used for processing datasets) (personally using 1.1.2)  
-very optionally `svg.path` (personally using 4.1) and `dxfwrite` (personally using 1.2.2) - they are used for processing datasets to convert them to other file formats to run benchmarks on offline implementations

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

Then you need to make sure that you have `cmake` (download from https://cmake.org/download/, don't forget to add it to `PATH` during installation (on Windows at least)).

Note: if you get error `Python.h: No such file or directory`, then you can directly add path of directory with `Python.h` to `source/nfp_interface/CmakeList.txt`. 
E.g. location is `/usr/include/python3.6/Python.h`, then add `include_directories(/usr/include/python3.6)`.

Then you need to follow *Visual Studio (Windows)* or *Any platform* steps.

### Visual Studio (Windows)

For Windows users, there is a `build.bat` script in `source/nfp_interface`.

To run it, you need to have Visual Studio 2017 or 2019 with "Desktop development with C++" tools installed (open Visual Studio -> Tools -> Get Tools and Features).

Then you have to make sure that you have `pybind11` (other one than Python library) installed.

My way of installation: go to some repository where you want to install `vcpkg` (e.g. `C:\local\`), open PowerShell, run following commands:  
`git clone https://github.com/Microsoft/vcpkg.git`  
`.\vcpkg\bootstrap-vcpkg.bat`  
`.\vcpkg\vcpkg.exe install pybind11:x64-windows ` (be patient while it downloads and installs)  
`.\vcpkg\vcpkg.exe integrate install`

Then, in `source/nfp_interface/CmakeList.txt`, uncomment `# set(CMAKE_CXX_FLAGS "/MD /EHsc") #Microsoft Visual C++ compiler` and comment `set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC") #Linux with GCC or Clang`.

It should be enough to just run `build.bat` by doubleclicking the file and it will launch Developer Command Prompt for Visual Studio. If not, then run the file from Developer PowerShell from Visual Studio.

If you manage to get to the point when it generates `libnfporb_interface.pyd` file, but when you try to run e.g. `run_tests.py` and it says `DLL load failed: The specified module could not be found`, then you have 2 options (hopefully at least one of them will work):

A)  
-install Python 3.6 (3.6.8 if possible) and all required Python libraries (shapely, matplotlib, ...)  
-delete `libnfporb_interface.pyd` file (in `/source/nfp_interface/`)  
-rename `libnfporb_interface_rescue.pyd` to `libnfporb_interface.pyd`  
-run `run_tests.py` using Python 3.6.

B)  
-open Developer Command prompt for VS 201x (Windows key -> scroll to "Visual Studio 201x" folder -> you can find it inside the folder)  
-change directory (`cd <location>`) to `<location of this project>\source\nfp_interface`  
-run following command `dumpbin /dependents libnfporb_interface.pyd`. This will show the requirements of the DLL/PYD for the Python version (e.g. "python39.dll" means it needs Python 3.9).  
-change environment variable %PYTHONPATH% to the folder containing required version of Python.  
If you think that you don't have this required version installed/available, then download and install it (reboot maybe required).  
-(maybe needed) check (in Developer Command prompt for VS 201x) that the Python version used in command prompt is the required version (run `python --version`). If it isn't, then maybe try to modify %Path% environment variable so that the entries with required Python version are above entries with other Python versions and restart the command prompt.  
-rebuild `libnfporb_interface.pyd` (delete `build` folder and `libnfporb_interface.pyd`, then run `build.bat`)  
-run `run_tests.py` with required Python version (and, of course, installed required libraries (shapely, matplotlib, ...) for this version)  

### Any platform
First, you have to adjust CMake flags in `CmakeLists.txt` file provided depending on the platform/compiler. Use `set(CMAKE_CXX_FLAGS "/MD /EHsc")` while using Microsoft Visual C++ compiler or `set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")` on Linux with GCC or Clang.

Use `cmake` to generate the project for your compiler with the
`CmakeLists.txt` file. In the `source/nfp_interface`
folder, run:

``` {.cmd}
mkdir build
cd build
cmake .. -G <your generator>
```

Then, build it with your compiler (e.g. `make`). After that, you need to place the build `libnfporb_interface.so` into the `source/nfp_interface` folder.

Also, you will most probably need to have `pybind11` installed (other one than Python library).
