# -*- mode: python -*-

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

a = Entrypoint('distellipsoid',
             'gui_scripts',
             'EllipsoidGUI',
             pathex=['C:\\Users\\JCC\\Documents\\custom_python_libs\\distellipsoid'],
             binaries=None,
             datas=None,
             hiddenimports=['FileDialog'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
             
#options = [ ('v', None, 'OPTION')]
options=[]             
             
exe = EXE(pyz,
          a.scripts,
          options,
          exclude_binaries=True,
          name='distellipsoid_gui',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='distellipsoid_gui')
