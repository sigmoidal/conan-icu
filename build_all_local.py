from subprocess import call
import os, sys

# python build_all.py > build_all.log
#
# MSVC++ 4.x  _MSC_VER == 1000
# MSVC++ 5.0  _MSC_VER == 1100
# MSVC++ 6.0  _MSC_VER == 1200
# MSVC++ 7.0  _MSC_VER == 1300
# MSVC++ 7.1  _MSC_VER == 1310 (Visual Studio 2003)
# MSVC++ 8.0  _MSC_VER == 1400 (Visual Studio 2005)
# MSVC++ 9.0  _MSC_VER == 1500 (Visual Studio 2008)
# MSVC++ 10.0 _MSC_VER == 1600 (Visual Studio 2010)
# MSVC++ 11.0 _MSC_VER == 1700 (Visual Studio 2012)
# MSVC++ 12.0 _MSC_VER == 1800 (Visual Studio 2013)
# MSVC++ 14.0 _MSC_VER == 1900 (Visual Studio 2015)
# MSVC++ 14.1 _MSC_VER >= 1910 (Visual Studio 2017)
#  

def main(target_os):
    name = "icu"
    version = "59.1"
    channel = "bincrafters/testing"
    archs = [ "x86", "x86_64" ]
    build_types = [ "Release", "Debug" ]
    links = [ True, False ]
    compiler_versions = [ "15", "14" ]
    msvc_platforms = { "msys": 'MSYS_ROOT=D:\dev\msys64',
                      "cygwin": 'CYGWIN_ROOT=D:\PortableApps\CygwinPortable\App\Cygwin' }
    
    if target_os == 'win':
        # process arguments
        for arch in archs:
            for compiler_version in compiler_versions:
                for build_type in build_types:
                    for link in links:
                        for msvc_platform in msvc_platforms:
                            cmd = 'conan create {channel} -k \
                                   -s arch={arch} \
                                   -s build_type={build_type} \
                                   -s compiler.version={compiler} \
                                   -o icu:msvc_platform={msvc_platform} \
                                   -o icu:shared={link} \
                                   -e {build_env} > {name}-{version}-{arch}-{build_type}-{link}-{msvc_platform}-{used_compiler}.log'.format(name=name,
                                                                                                                                            version=version,
                                                                                                                                            channel=channel, 
                                                                                                                                            arch=arch, 
                                                                                                                                            compiler=compiler_version,
                                                                                                                                            used_compiler="vs2017" if compiler_version == "15" else "vs2015",
                                                                                                                                            build_type=build_type,
                                                                                                                                            link=str(link),
                                                                                                                                            msvc_platform=msvc_platform,
                                                                                                                                            build_env=msvc_platforms[msvc_platform])
                            print("[*] " + " ".join(cmd.split()))
                            os.system( cmd )
    elif target_os == 'linux':
    
        compiler_versions = [ "5.4", "6.3" ]
    
        # process arguments
        for arch in archs:
            for compiler_version in compiler_versions:
                for build_type in build_types:
                    for link in links:
                        for msvc_platform in msvc_platforms:
                            cmd = 'conan create {channel} -k \
                                   -s arch={arch} \
                                   -s build_type={build_type} \
                                   -s compiler=gcc \
                                   -s compiler.version={compiler} \
                                   -o icu:shared={link} 2>&1 | tee {name}-{version}-{arch}-{build_type}-{link}-{used_compiler}.log'.format(name=name,
                                                                                                                                           version=version,
                                                                                                                                           channel=channel, 
                                                                                                                                           arch=arch, 
                                                                                                                                           compiler=compiler_version,
                                                                                                                                           used_compiler="gcc" + compiler_version,
                                                                                                                                           build_type=build_type,
                                                                                                                                           link=str(link))
                            print("[*] " + " ".join(cmd.split()))
                            os.system( cmd )

    os.system("conan search {name}/{version}@{channel} --table=file.html".format(name=name, version=version, channel=channel) )

def usage():
    print("Usage: %s [win | linux | macosx]" % sys.argv)
    
if len(sys.argv) < 2:
    usage()
    exit(1)

target_os=sys.argv[1]

if target_os == 'win' or target_os == 'linux' or target_os == 'macosx':
    main(target_os)
else:
    usage()