EnsureSConsVersion( 2, 3, 0 )

env_vars = Variables()

env_vars.Add('BUILD_DIR',
    default='#build'
)

env_vars.Add('VARIANT_DIR',
    default='variant'
)

env_vars.Add('PREFIX',
    default='$BUILD_DIR/install'
)

env_vars.Add('CC')
env_vars.Add('CXX')
env_vars.Add('CCFLAGS')
env_vars.Add('CXXFLAGS')
env_vars.Add('CPPPATH')
env_vars.Add('LIBPATH')

env = Environment(
    variables=env_vars,
)

env.Tool('auto_install_binaries')

sconsDir = env.Dir(env.subst('$BUILD_DIR/scons'))
env.SConsignFile(str(sconsDir.File('signatures')))
env.CacheDir(str(sconsDir.Dir('cache')))

env.SConscript(
    dirs=[
        'src'
    ],
    variant_dir=env.subst('$BUILD_DIR/$VARIANT_DIR'),
    exports={
        'env' : env
    }
)

env.Alias('install', ['install-dev', 'install-runtime'])
env.Default('install')

env.NoCache(FindInstalledFiles())
