# not found

[![travis Status](https://travis-ci.org/not found/not found.svg?branch=master)](https://travis-ci.org/not found/not found) [![Appveyor Status](https://ci.appveyor.com/api/projects/status/not found/not found/not found?branch=master&svg=true)](https://ci.appveyor.com/project/not found/not found) [![Go Report Card](https://goreportcard.com/badge/not found/not found/not found)](https://goreportcard.com/report/not found/not found/not found) [![GoDoc](https://godoc.org/not found/not found/not found?status.svg)](http://godoc.org/not found/not found/not found) [![<nil> License](http://img.shields.io/badge/License-<nil>-blue.svg)](LICENSE)


foo

master

not found
not found
not found
not found
not found
not found
master

[![Go Report Card](https://goreportcard.com/badge/not found/not found/not found)](https://goreportcard.com/report/not found/not found/not found) [![GoDoc](https://godoc.org/not found/not found/not found?status.svg)](http://godoc.org/not found/not found/not found)



# TOC
- [Install](#install)
  - [go](#go)
- [Conan recipe for IBM ICU.](#conan-recipe-for-ibm-icu)
  - [Features](#features)
- [For Users: Use this package](#for-users-use-this-package)
  - [Basic setup](#basic-setup)
  - [Project setup](#project-setup)
  - [Package Options](#package-options)
- [For Packagers: Publish this Package](#for-packagers-publish-this-package)
- [Build and package ](#build-and-package-)
- [Add Remote](#add-remote)
- [Upload](#upload)
  - [License](#license)

# Install

Check the [release page](https://not found/releases)!

#### go
```sh
go get not found/not found/not found
```



[![Build status](https://ci.appveyor.com/api/projects/status/mm27s515gpx3io09/branch/stable/60.1?svg=true)](https://ci.appveyor.com/project/sigmoidal/conan-icu/branch/stable/60.1)
[![Build Status](https://travis-ci.org/sigmoidal/conan-icu.svg?branch=stable%2F60.1)](https://travis-ci.org/sigmoidal/conan-icu)
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


not found

## For Users: Use this package

### Basic setup

    $ conan install icu/60.1@sigmoidal/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    icu/60.1@sigmoidal/stable

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

    $ conan create sigmoidal/stable

## Add Remote

	$ conan remote add sigmoidal "https://api.bintray.com/conan/sigmoidal/public-conan"

## Upload

    $ conan upload icu/60.1@sigmoidal/stable --all -r sigmoidal

### License
[IBM ICU](http://www.unicode.org/copyright.html#License)
