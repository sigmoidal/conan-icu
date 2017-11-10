[![Build status](https://ci.appveyor.com/api/projects/status/mm27s515gpx3io09/branch/testing/60.1?svg=true)](https://ci.appveyor.com/project/sigmoidal/conan-icu/branch/testing/60.1)
[![Build Status](https://travis-ci.org/sigmoidal/conan-icu.svg?branch=testing%2F60.1)](https://travis-ci.org/sigmoidal/conan-icu)
[![License LGPL](https://img.shields.io/badge/license-LGPL%202.1-yellow.svg)](https://shields.io/)

## Conan recipe for IBM ICU.

[Conan.io](https://conan.io) package for [IBM ICU](http://icu-project.org) project

The packages generated with this **conanfile** can be found in [Bintray](https://bintray.com/sigmoidal/public-conan/).

### Features

This recipe can be used to build ICU on Windows, Linux and MacOS.

On Windows, both shared (MD/MDd) and static(MT/MTd) runtimes are supported.

On Windows only MSVC binaries have been tested, using both MSYS2 and Cygwin as a toolset. Note, that these are MSVC binaries and are not linked against mingw or cygwin's runtimes.

On Linux it has been tested with GCC 5.x and 6.x.

On MacOS it has been tested with Apple's Clang.



## For Users: Use this package

### Basic setup

    $ conan install icu/60.1@sigmoidal/testing

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    icu/60.1@sigmoidal/testing

    [generators]
    txt

Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they shoudl not be added to the root of the project, nor committed to git.

### Package Options

This package has the following options useful for end-users: 

|Option Name     | Default Values   | Possible Value                  | Description
|----------------|------------------|---------------------------------|------------------------
|shared			 | False            | True/False                      | Use as a shared library or static library
|data_packaging	 | archive          | shared, static, files, archive  | See [ICU Data Packaging documentation](http://userguide.icu-project.org/packaging)


## For Packagers: Publish this Package

The example below shows the commands used to publish to sigmoidal conan repository. 
To publish to your own conan respository (for example, after forking this git repository), 
you will need to change the commands below accordingly.

## Build and package 

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  
This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method. 

    $ conan create sigmoidal/testing

## Add Remote

	$ conan remote add sigmoidal "https://api.bintray.com/conan/sigmoidal/public-conan"

## Upload

    $ conan upload icu/60.1@sigmoidal/testing --all -r sigmoidal

### License
[IBM ICU](http://www.unicode.org/copyright.html#License)
