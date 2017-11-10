import subprocess, os, sys

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

def usage():
    print("Usage: %s [win | linux | macosx]" % sys.argv[0]) 
    
def main(target_os):
    name = "icu"
    version = "60.1"
    channel = "sigmoidal/stable"
    archs = [ "x86", "x86_64" ]
    build_types = ["Release", "Debug"]
    shared = [ True, False ]
    compiler_versions = [ "15", "14" ]
    msvc_platforms = [ "msys", "cygwin" ]

    os.system('conan remote add sigmoidal "https://api.bintray.com/conan/sigmoidal/public-conan"')

    if target_os == 'win':
        for msvc_platform in msvc_platforms:
            source_clear_cmd = "conan remove {name}/{version}@{channel} -s -f".format(name=name, version=version, channel=channel)
            os.system( source_clear_cmd )

            for arch in archs:
                for compiler_version in compiler_versions:
                    for build_type in build_types:
                        for link in shared:
                            if shared:
                                win_runtime = "MD" if build_type == "Release" else "MDd"
                            else:
                                win_runtime = "MT" if build_type == "Release" else "MTd"

                            cmd = 'conan create {channel} -k \
                                   -s arch={arch} \
                                   -s build_type={build_type} \
                                   -s compiler.version={compiler} \
                                   -s compiler.runtime={compiler_runtime} \
                                   -o icu:with_unit_tests=True \
                                   -o icu:msvc_platform={msvc_platform} \
                                   -o icu:shared={link} > {name}-{version}-{arch}-{build_type}-{link_str}-{compiler_runtime}-{msvc_platform}-{used_compiler}.log'.format(name=name,
                                                                                                                                                                         version=version,
                                                                                                                                                                         channel=channel,
                                                                                                                                                                         arch=arch,
                                                                                                                                                                         compiler=compiler_version,
                                                                                                                                                                         compiler_runtime=win_runtime,
                                                                                                                                                                         used_compiler="vs2017" if compiler_version == "15" else "vs2015",
                                                                                                                                                                         build_type=build_type,
                                                                                                                                                                         link=str(link),
                                                                                                                                                                         link_str='shared' if link else 'static',
                                                                                                                                                                         msvc_platform=msvc_platform)
                            print("[{os}] {cmdstr}".format(os=target_os, cmdstr=" ".join(cmd.split())))
                            os.system( cmd )

                            os.system('conan upload {name}/{version}@{channel} --all -r sigmoidal'.format(name=name, version=channel, channel=channel))

                            
    elif target_os == 'linux':
    
        compiler_versions = [ "5.4", "6.3" ]
    
        for arch in archs:
            for compiler_version in compiler_versions:
                                    
                compiler_major_version = compiler_version.split('.')[0]
            
                cc = "gcc-%s" % compiler_major_version
                cxx = "g++-%s" % compiler_major_version
                
                try:
                    output = subprocess.check_output("which %s" % cc, shell=True).decode('utf-8').strip()
                    cc = output
                except subprocess.CalledProcessError as e:
                    print("ERROR: CC Compiler \"%s\" is not installed!" % cc)
                    continue
                
                try:
                    output = subprocess.check_output("which %s" % cxx, shell=True).decode('utf-8').strip()
                    cxx = output
                except subprocess.CalledProcessError as e:
                    print("ERROR: CXX Compiler \"%s\" is not installed!" % cxx)
                    continue
                            
                os.environ['CC'] = cc
                os.environ['CXX'] = cxx
                        
                for build_type in build_types:
                    for link in shared:
                        cmd = 'conan create {channel} -k \
                               --profile {profile} \
                               -s arch={arch} \
                               -s build_type={build_type} \
                               -o icu:shared={link} 2>&1 | tee {name}-{version}-{arch}-{build_type}-{link_str}-{used_compiler}.log'.format(name=name,
                                                                                                                                           version=version,
                                                                                                                                           channel=channel, 
                                                                                                                                           profile='gcc%s' % compiler_major_version,
                                                                                                                                           arch=arch, 
                                                                                                                                           used_compiler="gcc" + compiler_version,
                                                                                                                                           build_type=build_type,
                                                                                                                                           link=str(link),
                                                                                                                                           link_str='shared' if link else 'static')
                        print("[{os}] {cmdstr}".format(os=target_os, cmdstr=" ".join(cmd.split())))
                        os.system( cmd )
                            
    elif target_os == 'macosx':
    
        compiler = "apple-clang"
        compiler_versions = [ "9.0" ]

        for arch in archs:
            for compiler_version in compiler_versions:
                for build_type in build_types:
                    for link in shared:
                        cmd = 'conan create {channel} -k \
                               -s arch={arch} \
                               -s build_type={build_type} \
                               -s compiler={compiler} \
                               -s compiler.version={compiler_v} \
                               -o icu:shared={link} 2>&1 | tee {name}-{version}-{arch}-{build_type}-{link_str}-{used_compiler}.log'.format(name=name,
                                                                                                                                           version=version,
                                                                                                                                           channel=channel, 
                                                                                                                                           arch=arch, 
                                                                                                                                           compiler=compiler,
                                                                                                                                           compiler_v=compiler_version,
                                                                                                                                           used_compiler=compiler + '-' + compiler_version,
                                                                                                                                           build_type=build_type,
                                                                                                                                           link=str(link),
                                                                                                                                           link_str='shared' if link else 'static')
                        print("[{os}] {cmdstr}".format(os=target_os, cmdstr=" ".join(cmd.split())))
                        os.system( cmd )
    else:
        usage()
        exit(1)
        
    os.system("conan search {name}/{version}@{channel} --table=file.html".format(name=name, version=version, channel=channel) )


if len(sys.argv) < 2:
    usage()
    exit(1)

target_os=sys.argv[1]

if target_os == 'win' or target_os == 'linux' or target_os == 'macosx':
    main(target_os)
else:
    usage()
    
