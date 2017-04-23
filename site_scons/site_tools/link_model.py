import SCons

def exists(env):
    return True

def generate(env):

    SCons.Script.AddOption('--link-model', dest='link-model', type='choice', choices=['static', 'dynamic'], default='dynamic')

    link_model = SCons.Script.GetOption('link-model')

    # In all windows builds, and static non-windows builds, we want to
    # put .a or .lib on the end of libraries. In dynamic mode on
    # non-windows, we want to use SHLIBSUFFIX.
    env['LINK_MODEL_LIBSUFFIX'] = '$LIBSUFFIX'

    if link_model == 'static':
        env['BUILDERS']['Library'] = env['BUILDERS']['StaticLibrary']
        env.AppendUnique(CPPDEFINES=['HYGENIC_DEMO_STATIC'])

        # In static mode on Windows, prefix static libraries with
        # 'lib' to differentiate them from a DLL import library.
        if env['PLATFORM'] == 'win32':
            env['LIBPREFIX'] = 'lib'
    else:
        env['BUILDERS']['Library'] = env['BUILDERS']['SharedLibrary']

        # In dynamic mode on non-Windows, we want the shared librray suffix.
        if not env['PLATFORM'] == 'win32':
            env['LINK_MODEL_LIBSUFFIX'] = '$SHLIBSUFFIX'

    if env['PLATFORM'] == 'posix':
        env.AppendUnique(
            RPATH=[
                env.Literal('\\$$ORIGIN/../lib')
            ],
            LINKFLAGS=[
                '-Wl,-z,origin',
                '-Wl,--enable-new-dtags',
            ],
            SHLINKFLAGS=[
                # -h works for both the sun linker and the gnu linker.
                "-Wl,-h,${TARGET.file}",
            ]
        )
    elif env['PLATFORM'] == 'darwin':
        env.AppendUnique(
            LINKFLAGS=[
                '-Wl,-rpath,@loader_path/../lib'
            ],
            SHLINKFLAGS=[
                "-Wl,-install_name,@loader_path/../lib/${TARGET.file}",
            ],
        )

    if not 'MSVC_VERSION' in env:
        env.AppendUnique(
            SHCXXFLAGS=[
                '-fvisibility=hidden',
                '-fvisibility-inlines-hidden',
            ],
        )

    def libs_expansion_emitter(target, source, env):
        libs = env.get('LIBS', [])
        newlibs = []
        for lib in libs:
            newlib = SCons.Util.adjustixes(lib, env.subst('$LIBPREFIX'), env.subst('$LINK_MODEL_LIBSUFFIX'))
            newlibs.append(env.File(newlib))
        env['LIBS'] = newlibs
        return target, source

    def add_emitter(builder, emitter):
        base_emitter = builder.emitter
        new_emitter = SCons.Builder.ListEmitter([base_emitter, emitter])
        builder.emitter = new_emitter

    for builder in ['Program', 'SharedLibrary', 'LoadableModule', 'StaticLibrary']:
        add_emitter(env['BUILDERS'][builder], libs_expansion_emitter)
