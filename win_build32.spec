# -*- mode: python -*-

# PyInstaller specification for building ellipsoidGUI and CIFellipsoid
# as self-contained distributables (within one directory)
# To run, use:
#     pyinstaller win_build.spec
#

block_cipher = None

def Entrypoint(dist,
               group,
               name,
               pathex=None,
               binaries=None,
               datas=None,
               hiddenimports=None,
               hookspath=[],
               runtime_hooks=[],
               excludes=None,
               scripts=None,
               win_no_prefer_redirects=False,
               win_private_assemblies=False,
               cipher=block_cipher,             
                ):

    import pkg_resources

    # get toplevel packages of distribution from metadata
    def get_toplevel(dist):
        distribution = pkg_resources.get_distribution(dist)
        if distribution.has_metadata('top_level.txt'):
            return list(distribution.get_metadata('top_level.txt').split())
        else:
            return []

    packages = hiddenimports or []
    #for distribution in hiddenimports:
    #    packages += distribution
    #    packages += get_toplevel(distribution)

    scripts = scripts or []
    pathex = pathex or []
    # get the entry point
    ep = pkg_resources.get_entry_info(dist, group, name)
    # insert path of the egg at the verify front of the search path
    pathex = [ep.dist.location] + pathex
    # script name must not be a valid module name to avoid name clashes on import
    script_path = os.path.join(workpath, name + '-script.py')
    print "creating script for entry point", dist, group, name
    with open(script_path, 'w') as fh:
        fh.write("import {0}\n".format(ep.module_name))
        for package in packages:
            fh.write("import {0}\n".format(package))        
        fh.write("{0}.{1}()\n".format(ep.module_name, '.'.join(ep.attrs)))


    return Analysis([script_path] + scripts, pathex, binaries, datas, hiddenimports, hookspath, runtime_hooks, excludes, win_no_prefer_redirects, win_private_assemblies, cipher)

# Additional files (e.g. data files) to copy directly into the output directory
ADDEDFILES = [
            ('README.rst', '.'),
            ('README.pdf', '.'),
            ('pieface_docs\\images\\PIEFACE.ico', '.\\pieface_docs\\images\\'),
            ('pieface_docs\\PIEFACE_manual.pdf', '.\\pieface_docs\\'),
            ('license.txt','.'),
            ('pieface\\data\\pieface.ico', '.\\pieface\\data\\'),
            ('pieface\\tests\\test_data\\fayalite_COD1000064.cif', '.\\pieface\\tests\\test_data\\'),
            ('pieface\\tests\\test_data\\MnSnO3_COD1004021.cif', '.\\pieface\\tests\\test_data\\')
             ]

# By default, some required MKL DLLs are missing (seems to be related to Enthought, matplotlib and numpy...)


MISSINGDLLS = [
                ('lib32\\mk2_avx2.dll', '.'),
                ('lib32\\mk2_p4.dll', '.')
               ]
       

GUI = Entrypoint('pieface',
             'gui_scripts',
             'EllipsoidGUI',
             pathex=['C:\\Users\\JCC\\Documents\\custom_python_libs\\pieface'],
             binaries=MISSINGDLLS,
             datas=ADDEDFILES,
             hiddenimports=['FileDialog','Queue'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
             
CMD = Entrypoint('pieface',
               'console_scripts',
               'CIFellipsoid',
               pathex=['C:\\Users\\JCC\\Documents\\custom_python_libs\\pieface'],
               binaries=MISSINGDLLS,
               datas=None,
               hiddenimports=[],
               hookspath=[],
               runtime_hooks=[],
               excludes=[],
               win_no_prefer_redirects=False,
               win_private_assemblies=False,
               cipher=block_cipher)
             
MERGE( (GUI, 'EllipsoidGUI', 'EllipsoidGUI'), (CMD, 'CIFellipsoid', 'CIFellipsoid') )
             
             
GUIpyz = PYZ(GUI.pure, GUI.zipped_data,
             cipher=block_cipher)
CMDpyz = PYZ(CMD.pure, CMD.zipped_data,
             cipher=block_cipher)
             
 
GUIexe = EXE(GUIpyz,
          GUI.scripts,
          exclude_binaries=True,
          name='EllipsoidGUI',
          debug=False,
          strip=False,
          upx=False,
          console=True,
          icon='pieface\\data\\pieface.ico',
          version='win_GUI_info.txt')
CMDexe = EXE(CMDpyz,
          CMD.scripts,
          exclude_binaries=True,
          name='CIFellipsoid',
          debug=False,
          strip=False,
          upx=False,
          console=True,
          icon='pieface\\data\\pieface.ico',
          version='win_CMD_info.txt')                
          
GUIcoll = COLLECT(GUIexe,
               GUI.binaries,
               GUI.zipfiles,
               GUI.datas,
               strip=False,
               upx=False,
               name='PIEFACE_win32')
CMDcoll = COLLECT(CMDexe,
               CMD.binaries,
               CMD.zipfiles,
               CMD.datas,
               strip=False,
               upx=False,
               name='CIFellipsoid32')
