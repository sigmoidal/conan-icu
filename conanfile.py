from conans import ConanFile, tools, VisualStudioBuildEnvironment, AutoToolsBuildEnvironment
import os
import glob
import shutil

#
# Refer to http://userguide.icu-project.org/icudata for the data_packaging option
#
# Note that the MSVC builds with msvc_platform=visual_studio cannot do static ICU builds
# The default platform for building MSVC binaries is MSYS (msvc_platform=msys)
#
# If you're building with Cygwin, the environment variable CYGWIN_ROOT must be present or specified via the command line
#
# If you're building with MSYS, the environment variable MSYS_ROOT must be present or specified via the command line
#
# examples:
#
# To update the conanfile.py without rebuilding:
#
#    conan export icu/59.1@bincrafters/testing -k && conan package icu/59.1@bincrafters/testing addc9b54f567a693944ffcc56568c29b0d0926c8
#
# for creating a tgz:
#
#    conan upload --skip_upload icu/59.1@bincrafters/testing -p addc9b54f567a693944ffcc56568c29b0d0926c8
#
# Create an ICU package using a Cygwin/MSVC static release built
#   
#    conan create bincrafters/testing -o icu:msvc_platform=cygwin -o icu:shared=False -e CYGWIN_ROOT=D:\PortableApps\CygwinPortable\App\Cygwin
#
# Create an ICU package using a Cygwin/MSYS static debug built
#   
#    conan create bincrafters/testing -o icu:msvc_platform=cygwin -s icu:build_type=Debug -o icu:shared=False
#
# Create an ICU package using a Cygwin/MSYS static debug built
#   
#    conan create bincrafters/testing -e MSYS_ROOT=D:\dev\msys64
#

class IcuConan(ConanFile):
    name = "icu"
    version = "59.1"
    license="http://www.unicode.org/copyright.html#License"
    description = "ICU is a mature, widely used set of C/C++ and Java libraries providing Unicode and Globalization support for software applications."
    url = "https://github.com/bincrafters/conan-icu"
    settings = "os", "arch", "compiler", "build_type"
    source_url = "http://download.icu-project.org/files/icu4c/{0}/icu4c-{1}-src".format(version,version.replace('.', '_'))
    data_url = "http://download.icu-project.org/files/icu4c/{0}/icu4c-{1}-data".format(version,version.replace('.', '_'))

    options = {"shared": [True, False],
               "msvc_platform": ["msys", "visual_studio", "cygwin"],
               "data_packaging": ["shared", "static", "files", "archive"],
               "with_unit_tests": [True, False],
               "silent": [True, False]}

    default_options = "shared=False", \
                      "msvc_platform=msys", \
                      "data_packaging=archive", \
                      "with_unit_tests=False", \
                      "silent=True"
    
    # Dictionary storing strings useful for setting up the configuration and make command lines
    cfg = { 'enable_debug': '', 
            'platform': '', 
            'host': '', 
            'arch_bits': '',
            'output_dir': '', 
            'enable_static': '', 
            'data_packaging': '', 
            'general_opts': '' }
    
    def source(self):
        archive_type = "zip"
        if self.settings.os != 'Windows' or self.options.msvc_platform != 'visual_studio':
            archive_type = "tgz"

        self.output.info("Fetching sources: {0}.{1}".format(self.source_url, archive_type))
        
        tools.get("{0}.{1}".format(self.source_url, archive_type))
        
        src_folder = os.getcwd()
  
        # update the outdated config.guess and config.sub
        config_updates = [ 'config.guess', 'config.sub' ]
        for cfg_update in config_updates:
            dst_config = os.path.join(src_folder, self.name, 'source', cfg_update)
            if os.path.isfile(dst_config):
                os.remove(dst_config)
            self.output.info('Updating %s' % dst_config)
            tools.download('http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f={0};hb=HEAD'.format(cfg_update), dst_config);
        
        #
        # ICU v59.1 has incomplete data in the tgz file released, 
        # need to download and merge them separately.
        # http://bugs.icu-project.org/trac/ticket/13139
        #
        if archive_type == "tgz":
            data_web_file = "{0}.zip".format(self.data_url)
            self.output.info('Fetching data: %s' % data_web_file)
            tools.get(data_web_file)
            
            icu_datadir = os.path.join(src_folder, self.name, 'source', 'data')
            downloaded_icu_datadir = os.path.join(src_folder,'data')
            
            shutil.rmtree(icu_datadir)
            os.rename(downloaded_icu_datadir, icu_datadir)
              
        
        if self.settings.os == 'Windows':
            # Prevent multiple CL.EXE writes to the same .PDB file (use /FS)        
            runConfigureICU_file = os.path.join(self.name,'source','runConfigureICU')
            tools.replace_in_file(runConfigureICU_file, '        DEBUG_CFLAGS=\'-Zi -MDd\'\n', '        DEBUG_CFLAGS=\'-Zi -MDd -FS\'\n', strict=True)
            tools.replace_in_file(runConfigureICU_file, '        DEBUG_CXXFLAGS=\'-Zi -MDd\'\n', '        DEBUG_CXXFLAGS=\'-Zi -MDd -FS\'\n', strict=True)
        else:
            # This allows building ICU with multiple gcc compilers (overrides fixed compiler name)
            runConfigureICU_file = os.path.join(self.name,'source','runConfigureICU')
            tools.replace_in_file(runConfigureICU_file, '        CC=gcc; export CC\n', '', strict=True)
            tools.replace_in_file(runConfigureICU_file, '        CXX=g++; export CXX\n', '', strict=True)  

        #tools.replace_in_file(os.path.join(src_path,'data','makedata.mak'),
        #                      r'GODATA "$(ICU_LIB_TARGET)" "$(TESTDATAOUT)\testdata.dat"',
        #                      r'GODATA "$(ICU_LIB_TARGET)"')
        
    def build(self):    
        root_path = self.conanfile_directory
        src_path = os.path.join(root_path, self.name, 'source')

        # This handles the weird case of using ICU sources for Windows on a Unix environment, and vice-versa
        # this is primarily aimed at builds using Cygwin/MSVC which require unix line endings
        #if self.settings.os == 'Windows' and self.options.msvc_platform == 'visual_studio':
        #    if b'\r\n' not in open(os.path.join(src_path, "runConfigureICU"), 'rb').read():
        #        self.output.error("\n\nBuild failed. The line endings of your sources are inconsistent with the build configuration you requested. {0} / {1} \
        #                           \nPlease consider clearing your cache sources (i.e. remove the --keep-sources command line option\n\n".format(self.settings.os, self.options.msvc_platform))
        #        return
        #else:
        #    if b'\r\n' not in open(os.path.join(src_path, "runConfigureICU"), 'rb').read():
        #        self.output.error("\n\nBuild failed. The line endings of your sources are inconsistent with the build configuration you requested. {0} / {1} \
        #                           \nPlease consider clearing your cache sources (i.e. remove the --keep-sources command line option\n\n".format(self.settings.os, self.options.msvc_platform))
        #        return

        self.cfg['build_dir'] = os.path.join(root_path, self.name, 'build')
        self.cfg['output_dir'] = os.path.join(root_path, 'output')

        self.cfg['silent'] = '--silent' if self.options.silent else 'VERBOSE=1'
        self.cfg['enable_debug'] = '--enable-debug --disable-release' if self.settings.build_type == 'Debug' else ''
        self.cfg['arch_bits'] = '64' if self.settings.arch == 'x86_64' else '32'
        self.cfg['enable_static'] = '--enable-static --disable-shared' if not self.options.shared else '--enable-shared --disable-static'
        self.cfg['data_packaging'] = '--with-data-packaging={0}'.format(self.options.data_packaging) 
        self.cfg['general_opts'] = '--disable-layout --disable-layoutex'
                
        if not self.options.shared:
            self.cpp_info.defines.append("U_STATIC_IMPLEMENTATION")
            
        if self.settings.os == 'Windows':
            
            self.cfg['vcvars_command'] = tools.vcvars_command(self.settings)
                
            if self.options.msvc_platform == 'cygwin':
                self.build_cygwin()
            elif self.options.msvc_platform == 'msys':
                self.build_msys()
            else:
                sln_file = os.path.join(src_path,"allinone","allinone.sln")
                targets = ["i18n","common","pkgdata"]
                #if self.options.with_io:
                #    targets.append('io')
                build_command = tools.build_sln_command(self.settings, sln_file, targets=targets, upgrade_project=False)
                build_command = build_command.replace('"x86"','"Win32"')
                command = "{0} && {1}".format(self.cfg['vcvars_command'], build_command)
                self.run(command)
                cfg = 'x64' if self.settings.arch == 'x86_64' else 'x86'
                cfg += "\\"+str(self.settings.build_type)
                data_dir = src_path+"\\data"
                bin_dir = data_dir+"\\..\\..\\bin"
                if self.settings.arch == 'x86_64':
                    bin_dir += '64'
                makedata = '{vccmd} && cd {datadir} && nmake /a /f makedata.mak ICUMAKE="{datadir}" CFG={cfg}'.format(vccmd=self.cfg['vcvars_command'],
                                                                                                                      datadir=data_dir,
                                                                                                                      cfg=cfg)
                self.output.info(makedata)
                self.run(makedata)
        else:
            env_build = AutoToolsBuildEnvironment(self)
            with tools.environment_append(env_build.vars):
                if self.settings.os == 'Linux':
                    if self.settings.compiler == 'gcc':
                        self.cfg['platform'] = 'Linux/gcc'
                    else:
                        self.cfg['platform'] = 'Linux'
                elif self.settings.os == 'Macos':
                    self.cfg['platform'] = 'MacOSX'

                os.mkdir(self.cfg['build_dir'])


                
                config_cmd = self.build_config_cmd()

                #with tools.environment_append(env_build.vars):                                                                                                     
                self.run("cd {builddir} && bash {config_cmd}".format(builddir=self.cfg['build_dir'],
                                                                     config_cmd=config_cmd))
                    
                self.run("cd {builddir} && make {silent} -j {cpus_var}".format(builddir=self.cfg['build_dir'],
                                                                               cpus_var=tools.cpu_count(), 
                                                                               silent=self.cfg['silent']))
                   
                if self.options.with_unit_tests:
                    self.run("cd {builddir} && make {silent} check".format(builddir=self.cfg['build_dir'],
                                                                           silent=self.cfg['silent']))
                    
                self.run("cd {builddir} && make {silent} install".format(builddir=self.cfg['build_dir'],
                                                                         silent=self.cfg['silent']))

                if self.settings.os == 'Macos':
                    with tools.chdir('output/lib'):
                        for dylib in glob.glob('*icu*.{0}.dylib'.format(self.version)):
                            self.run('install_name_tool -id {0} {1}'.format(
                                os.path.basename(dylib), dylib))

    def package(self):
        if self.settings.os == 'Windows':
            bin_dir_dst, lib_dir_dst = ('bin64', 'lib64') if self.settings.arch == 'x86_64' else ('bin' , 'lib')
            if self.options.msvc_platform == 'cygwin' or self.options.msvc_platform == 'msys' or self.options.msvc_platform == 'any':
                bin_dir, include_dir, lib_dir, share_dir = (os.path.join('output', path) for path in ('bin', 'include', 'lib', 'share'))
                
                # we copy everything for a full ICU package
                self.copy("*", dst=bin_dir_dst, src=bin_dir, keep_path=True, symlinks=True)
                self.copy(pattern='*.dll', dst=bin_dir_dst, src=lib_dir, keep_path=False)
                
                self.copy("*", dst="include", src=include_dir, keep_path=True, symlinks=True)
                self.copy("*", dst=lib_dir_dst, src=lib_dir, keep_path=True, symlinks=True)
                self.copy("*", dst="share", src=share_dir, keep_path=True, symlinks=True)
            else:
                include_dir, bin_dir, lib_dir = (os.path.join(self.name, path) for path in ('include', bin_dir, lib_dir))
                self.output.info('include_dir = {0}'.format(include_dir))
                self.output.info('bin_dir = {0}'.format(bin_dir))
                self.output.info('lib_dir = {0}'.format(lib_dir))
                self.copy(pattern='*.h', dst='include', src=include_dir, keep_path=True)
                self.copy(pattern='*.lib', dst='lib', src=lib_dir, keep_path=False)
                self.copy(pattern='*.exp', dst='lib', src=lib_dir, keep_path=False)
                self.copy(pattern='*.dll', dst='lib', src=bin_dir, keep_path=False)
        else:
            #libs = ['i18n', 'uc', 'data']
            #if self.options.with_io:
            #    libs.append('io')
            #for lib in libs:
            #    self.copy(pattern="*icu{0}*.dylib".format(lib), dst="lib", src=lib_dir, keep_path=False, symlinks=True)
            #    self.copy(pattern="*icu{0}.so*".format(lib), dst="lib", src=lib_dir, keep_path=False, symlinks=True)

            bin_dir, include_dir, lib_dir, share_dir = (os.path.join('output', path) for path in ('bin', 'include', 'lib', 'share'))

            # we copy everything for a full ICU package
            self.copy("*", dst="bin", src=bin_dir, keep_path=True, symlinks=True)
            self.copy("*", dst="include", src=include_dir, keep_path=True, symlinks=True)
            self.copy("*", dst="lib", src=lib_dir, keep_path=True, symlinks=True)
            self.copy("*", dst="share", src=share_dir, keep_path=True, symlinks=True)

    def package_id(self):
        # Whether we built with Cygwin or MSYS shouldn't affect the package id
        if self.options.msvc_platform == "cygwin" or self.options.msvc_platform == "msys" or self.options.msvc_platform == "visual_studio":
            self.info.options.msvc_platform = "any"

        # ICU unit testing shouldn't affect the package's ID
        self.info.options.with_unit_tests = "any"

        # Verbosity doesn't affect package's ID
        self.info.options.silent = "any"
            
    def package_info(self):
        bin_dir, lib_dir = ('bin64', 'lib64') if self.settings.arch == 'x86_64' and self.settings.os == 'Windows' else ('bin' , 'lib')
        
        self.cpp_info.libdirs = [ lib_dir ]
        
        self.cpp_info.libs = []
        vtag = self.version.split('.')[0]
        keep = False
        for lib in tools.collect_libs(self, lib_dir):
            if not vtag in lib:
                if lib != 'icudata':
                    self.cpp_info.libs.append(lib)
                else:
                    keep = True

        # if icudata is not last, it fails to build on some platforms (Windows)
        # (have to double-check this)
        if keep:
            self.cpp_info.libs.append('icudata')

        self.env_info.PATH.append(os.path.join(self.package_folder, bin_dir))

        if not self.options.shared:
            self.cpp_info.defines.append("U_STATIC_IMPLEMENTATION")
            if self.settings.os == 'Linux':
                self.cpp_info.libs.append('dl')
                
            if self.settings.os == 'Windows':
                self.cpp_info.libs.append('advapi32')
                
        if self.settings.compiler == "gcc":
            self.cpp_info.cppflags = ["-std=c++11"]


            
    def build_config_cmd(self):   
        config_cmd = "../source/runConfigureICU {enable_debug} {platform} {host} {lib_arch_bits} {outdir} {enable_static} {data_packaging} {general}".format(enable_debug=self.cfg['enable_debug'], 
                                                                                                                                                             platform=self.cfg['platform'], 
                                                                                                                                                             host=self.cfg['host'], 
                                                                                                                                                             lib_arch_bits='--with-library-bits=%s' % self.cfg['arch_bits'],
                                                                                                                                                             outdir='--prefix=%s' % self.cfg['output_dir'], 
                                                                                                                                                             enable_static=self.cfg['enable_static'], 
                                                                                                                                                             data_packaging=self.cfg['data_packaging'], 
                                                                                                                                                             general=self.cfg['general_opts'])
                                                                                                                                                                                      
        return config_cmd

        
    # Detect MSYS2 build environment
    def detect_msys(self):
        # Check if MSYS_ROOT is provided in the environment
        if 'MSYS_ROOT' in os.environ:
            if os.path.isdir(os.path.join(os.environ["MSYS_ROOT"], 'usr', 'bin')):
                return True
            else:
                self.output.error(r'MSYS_ROOT: "{0}" does not seem to be a valid MSYS2 installation.'.format(os.environ["MSYS_ROOT"]))
                self.output.error(r'To build ICU with MSYS/MSVC you need a MSYS2 installation (see http://www.msys2.org/).')
                self.output.error(r'Setup the environment variable MSYS_ROOT to the installation path.')
        else:
            # check for a default MSYS2 installation
            msys_search_paths = [ r'C:\\msys64' ]
            
            for msys_path in msys_search_paths:
                # try to detect if MSYS2 is available at the default installation path
                if os.path.isdir(msys_path):
                    self.output.info(r'Detected MSYS2 in {0}'.format(msys_path))
                    os.environ["MSYS_ROOT"] = msys_path
                    return True
        
        return False
        
        
    # Detect Cygwin build environment
    def detect_cygwin(self):
        self.output.warn("DETECTING CYGWIN")
        # Check if CYGWIN_ROOT is provided in the environment
        if 'CYGWIN_ROOT' in os.environ:
            if os.path.isdir(os.path.join(os.environ["CYGWIN_ROOT"], "bin")):
                return True
            else:
                self.output.error(r'CYGWIN_ROOT: "{0}" does not seem to be a valid Cygwin installation.'.format(os.environ["CYGWIN_ROOT"]))
                self.output.error(r'To build ICU with Cygwin/MSVC you need a Cygwin installation (see http://cygwin.com/).')
                self.output.error(r'Setup the environment variable CYGWIN_ROOT to the installation path.')
        else:
            # check for a default Cygwin 32 and 64-bit installation
            cygwin_search_paths = [ r'C:\\Cygwin', r'C:\\Cygwin64' ]
            
            for cygwin_path in cygwin_search_paths:
                # try to detect if Cygwin is available at the default installation path
                if os.path.isdir(cygwin_path):
                    self.output.info(r'Detected Cygwin in {0}'.format(cygwin_path))
                    os.environ["CYGWIN_ROOT"] = cygwin_path
                    return True
                    
        return False
    

    def msys_patch(self):
        # There is a fragment in Makefile.in:22 of ICU that prevents from building with MSYS:
        #
        # ifneq (@platform_make_fragment_name@,mh-cygwin-msvc)
        # SUBDIRS += escapesrc
        # endif
        #
        # We patch the respective Makefile.in, to disable building it for MSYS
        #
        escapesrc_patch = os.path.join(self.conanfile_directory, self.name,'source','tools','Makefile.in')
        tools.replace_in_file(escapesrc_patch, 'SUBDIRS += escapesrc', '\tifneq (@platform_make_fragment_name@,mh-msys-msvc)\n\t\tSUBDIRS += escapesrc\n\tendif')
        
    def build_msys(self):
        self.cfg['platform'] = 'MSYS/MSVC'

        if 'MSYS_ROOT' not in os.environ:
            self.output.warn('MSYS_ROOT not in your environment')
        else:
            self.output.info("Using MSYS from: " + os.environ["MSYS_ROOT"]) 
        
        msys_root_path = os.environ["MSYS_ROOT"].replace('\\', '/')
        
        os.environ["PATH"] = r"C:\\Windows\\system32" + ";" + r"C:\\Windows" + ";" + r"C:\\Windows\\system32\Wbem" + ";" + os.path.join(msys_root_path,'usr','bin')
        self.output.info("PATH: " + os.environ["PATH"])
        
        os.mkdir(self.cfg['build_dir'])
        
        self.cfg['build_dir'] = self.cfg['build_dir'].replace('\\', '/')
        self.cfg['output_dir'] = self.cfg['output_dir'].replace('\\', '/')

        self.cfg['host'] = '--host=i686-pc-mingw{0}'.format(self.cfg['arch_bits'])
        
        # If you enable the stuff below => builds may start to stall when building x86/static/Debug
        #env_build = AutoToolsBuildEnvironment(self)
        #if self.settings.build_type == 'Debug':
        #    env_build.cxx_flags.append("-FS")
        
        config_cmd = self.build_config_cmd()

        # as of 59.1 this is necessary for building with MSYS
        self.msys_patch()
        
        #with tools.environment_append(env_build.vars):                    
        self.run("{vccmd} && bash -c ^'cd {builddir} ^&^& {config_cmd}^'".format(vccmd=self.cfg['vcvars_command'], 
                                                                                                builddir=self.cfg['build_dir'], 
                                                                                                config_cmd=config_cmd))



        # Builds may get stuck when using multiple CPUs in Debug mode
        #cpus = tools.cpu_count() if self.settings.build_type == 'Release' else '1'
        
        self.run("{vccmd} && bash -c ^'cd {builddir} ^&^& make {silent} -j {cpus_var}".format(vccmd=self.cfg['vcvars_command'], 
                                                                                              builddir=self.cfg['build_dir'], 
                                                                                              silent=self.cfg['silent'], 
                                                                                              cpus_var=tools.cpu_count()))
        if self.options.with_unit_tests:
            self.run("{vccmd} && bash -c ^'cd {builddir} ^&^& make {silent} check".format(vccmd=self.cfg['vcvars_command'], 
                                                                                          builddir=self.cfg['build_dir'], 
                                                                                          silent=self.cfg['silent']))

        self.run("{vccmd} && bash -c ^'cd {builddir} ^&^& make {silent} install'".format(vccmd=self.cfg['vcvars_command'], 
                                                                                         builddir=self.cfg['build_dir'], 
                                                                                         silent=self.cfg['silent']))

        
    def build_cygwin(self):
        self.cfg['platform'] = 'Cygwin/MSVC'

        if self.detect_cygwin():
            cygwin_root_path = os.environ["CYGWIN_ROOT"].replace('\\', '/')
            
            os.environ["PATH"] = r"C:\\Windows\\system32" + ";" + \
                                 r"C:\\Windows" + ";" + \
                                 r"C:\\Windows\\system32\Wbem" + ";" +  \
                                 cygwin_root_path + "/bin" + ";" + \
                                 cygwin_root_path + "/usr/bin" + ";" + \
                                 cygwin_root_path + "/usr/sbin"

            os.mkdir(self.cfg['build_dir'])
            self.cfg['output_dir'] = self.cfg['output_dir'].replace('\\', '/')
                            
            self.output.info("Starting configuration.")

            config_cmd = self.build_config_cmd()                  
            self.run("{vccmd} && cd {builddir} && bash {config_cmd}".format(vccmd=self.cfg['vcvars_command'], 
                                                                            builddir=self.cfg['build_dir'], 
                                                                            config_cmd=config_cmd))
                                                                                 
            self.output.info("Starting built.")

            self.run("{vccmd} && cd {builddir} && make {silent} -j {cpus_var}".format(vccmd=self.cfg['vcvars_command'], 
                                                                                      builddir=self.cfg['build_dir'], 
                                                                                      silent=self.cfg['silent'],
                                                                                      cpus_var=tools.cpu_count()))
            if self.options.with_unit_tests:
                self.run("{vccmd} && cd {builddir} && make {silent} check".format(vccmd=self.cfg['vcvars_command'], 
                                                                                  builddir=self.cfg['build_dir'], 
                                                                                  silent=self.cfg['silent']))
                                                                                        
            self.run("{vccmd} && cd {builddir} && make {silent} install".format(vccmd=self.cfg['vcvars_command'], 
                                                                                builddir=self.cfg['build_dir'], 
                                                                                silent=self.cfg['silent']))
            
            