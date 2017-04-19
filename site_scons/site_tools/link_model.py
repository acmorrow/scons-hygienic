import SCons

def exists(env):
    return True

def generate(env):

    SCons.Script.AddOption('--link-model', dest='link-model', type='choice', choices=['static', 'dynamic'], default='dynamic')

    if SCons.Script.GetOption('link-model') == 'static':
        env['BUILDERS']['Library'] = env['BUILDERS']['StaticLibrary']
        env.AppendUnique(CPPDEFINES=['HYGENIC_DEMO_STATIC'])
    else:
        env['BUILDERS']['Library'] = env['BUILDERS']['SharedLibrary']

    if env['PLATFORM'] == 'posix':
        env.AppendUnique(
            RPATH=[
                env.Literal('\\$$ORIGIN/../lib')
            ],
            LINKFLAGS=[
                '-Wl,-z,origin'
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
        builder = env['BUILDERS']['Library']
        for lib in libs:
            newlib = SCons.Util.adjustixes(lib, builder.get_prefix(env), builder.get_suffix(env))
            newlibs.append(env.File(newlib))
        env['LIBS'] = newlibs
        return target, source

    def sharedlib_generation_emitter(target, source, env):
        targetbase = str(target[0].get_subst_proxy().filebase).upper()
        env.AppendUnique(CPPDEFINES=['HYGENIC_DEMO_API_' + targetbase])
        return target, source

    def add_emitter(builder, emitter):
        base_emitter = builder.emitter
        new_emitter = SCons.Builder.ListEmitter([base_emitter, emitter])
        builder.emitter = new_emitter

    for builder in ['Program', 'SharedLibrary', 'LoadableModule', 'StaticLibrary']:
        add_emitter(env['BUILDERS'][builder], libs_expansion_emitter)

    for builder in ['SharedLibrary', 'LoadableModule']:
        add_emitter(env['BUILDERS'][builder], sharedlib_generation_emitter)
