import shlex

DefaultEnvironment(tools=[])

EnsureSConsVersion(2, 5, 0)

env_vars = Variables()

# Setup the command-line variables
def variable_shlex_converter(val):
    print(val)
    # If the argument is something other than a string, propogate
    # it literally.
    if not isinstance(val, basestring):
        return val
    return shlex.split(val, posix=True)

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
env_vars.Add('CCFLAGS', converter=variable_shlex_converter)
env_vars.Add('CXXFLAGS', converter=variable_shlex_converter)
env_vars.Add('CPPPATH', converter=variable_shlex_converter)
env_vars.Add('LIBPATH', converter=variable_shlex_converter)
env_vars.Add('LINKFLAGS', converter=variable_shlex_converter)

env = Environment(
    variables=env_vars,
)

env.Tool('link_model')
env.Tool('auto_install_binaries')

sconsDir = env.Dir(env.subst('$BUILD_DIR/scons'))
env.SConsignFile(str(sconsDir.File('signatures')))
env.CacheDir(str(sconsDir.Dir('cache')))

env.SConscript(
    dirs=[
        'src'
    ],
    variant_dir=env.subst('$BUILD_DIR/$VARIANT_DIR'),
    exports=[
        'env'
    ],
    duplicate=False,
)

env.FinalizeInstallDependencies()
