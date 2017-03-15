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
        env['LIBLINKSUFFIX'] = "-static"
        env['LIBSUFFIX'] = env['LIBLINKSUFFIX'] + env['LIBSUFFIX']
    else:
        env['BUILDERS']['Library'] = env['BUILDERS']['SharedLibrary']
        env['_LIBRARY_API_CPPDEFINES'] = _dynamic_export_define_generator
