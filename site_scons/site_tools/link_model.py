import SCons

class _dynamic_export_define_generator(object):
    def __init__(self, arg):
        self.arg = arg

    def __call__(self, target, source, env, for_signature):
        return "HYGENIC_DEMO_API_LIB" + self.arg

class _static_export_define_generator(object):
    def __init__(self, arg):
        self.arg = arg

    def __call__(self, target, source, env, for_signature):
        return "HYGENIC_DEMO_STATIC_LIB" + self.arg

def exists(env):
    return True

def generate(env):

    SCons.Script.AddOption('--link-model', dest='link-model', type='choice', choices=['static', 'dynamic'], default='dynamic')

    if SCons.Script.GetOption('link-model') == 'static':
        env['BUILDERS']['Library'] = env['BUILDERS']['StaticLibrary']
        env['_LIBRARY_API_CPPDEFINES'] = _static_export_define_generator
    else:
        env['BUILDERS']['Library'] = env['BUILDERS']['SharedLibrary']
        env['_LIBRARY_API_CPPDEFINES'] = _dynamic_export_define_generator

    def lib_emitter(target, source, env):
        libs = env.get('LIBS', [])
        newlibs = []
        builder = env['BUILDERS']['Library']
        for lib in libs:
            newlib = SCons.Util.adjustixes(lib, builder.get_prefix(env), builder.get_suffix(env))
            newlibs.append(env.File(newlib))
        env['LIBS'] = newlibs
        return target, source

    def add_emitter(builder):
        base_emitter = builder.emitter
        new_emitter = SCons.Builder.ListEmitter([base_emitter, lib_emitter])
        builder.emitter = new_emitter

    target_builders = ['Program', 'SharedLibrary', 'LoadableModule', 'StaticLibrary']
    for builder in target_builders:
        add_emitter(env['BUILDERS'][builder])
