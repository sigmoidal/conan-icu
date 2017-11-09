[![Build status](https://ci.appveyor.com/api/projects/status/mm27s515gpx3io09/branch/testing/60.1?svg=true)](https://ci.appveyor.com/project/sigmoidal/conan-icu/branch/testing/60.1)
[![Build Status](https://travis-ci.org/sigmoidal/conan-icu.svg?branch=testing%2F60.1)](https://travis-ci.org/sigmoidal/conan-icu)
[![License LGPL](https://img.shields.io/badge/license-LGPL%202.1-yellow.svg)](https://shields.io/)

## Conan recipe for IBM ICU.

[Conan.io](https://conan.io) package for [IBM ICU](http://icu-project.org) project

### Features

This recipe can be used to build ICU on Windows, Linux and MacOS.

On Windows, both shared (MD/MDd) and static(MT/MTd) runtimes are supported.

On Windows only MSVC binaries have been tested, using both MSYS2 and Cygwin as a toolset. Note, that these are MSVC binaries and are not linked against mingw or cygwin's runtimes.

On Linux it has been tested with GCC 5.x and 6.x.

On MacOS it has been tested with Apple's Clang.
