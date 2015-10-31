EnsureSConsVersion( 2, 3, 0 )

env_vars = Variables()

env_vars.Add('BUILD_DIR',
    default='#build'
)

env_vars.Add('PREFIX',
    default='$BUILD_DIR/install'
)

env_vars.Add('RPATH',
    default='$$ORIGIN/../lib'
)

env_vars.Add('CC')
env_vars.Add('CXX')
env_vars.Add('CCFLAGS')
env_vars.Add('LINKFLAGS')

env = Environment(variables=env_vars)

env.AppendUnique(CXXFLAGS=['-std=c++11'])

env.SConscript('src/SConscript', variant_dir=env.subst('$BUILD_DIR'), exports={ 'env' : env })

env.Alias('install', ['install-libs', 'install-bins'])

