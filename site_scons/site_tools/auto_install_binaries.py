import SCons

def exists(env):
    True

def generate(env):

    def auto_install_emitter(target, source, env):

        suffix_map = {
            '' :       ('$PREFIX/bin', ['runtime',]),
            '.a' :     ('$PREFIX/lib', ['dev',]),
            '.dll' :   ('$PREFIX/bin', ['runtime',]),
            '.dylib' : ('$PREFIX/lib', ['runtime, dev',]),
            '.exe' :   ('$PREFIX/bin', ['runtime',]),
            '.lib' :   ('$PREFIX/lib', ['dev',]),
            '.so' :    ('$PREFIX/lib', ['runtime, dev',]),
        }

        for t in target:
            tsuf = t.get_suffix()
            auto_install_location = suffix_map.get(tsuf)
            if auto_install_location:
                install = env.Install(auto_install_location[0], t)
                for install_tag in auto_install_location[1]:
                    env.Alias('install-' + install_tag, install)
        return (target, source)

    def add_emitter(builder):
        base_emitter = builder.emitter
        new_emitter = SCons.Builder.ListEmitter([base_emitter])
        new_emitter.append(auto_install_emitter)
        builder.emitter = new_emitter

    target_builders = ['Program', 'SharedLibrary', 'LoadableModule', 'Library']
    for builder in target_builders:
        add_emitter(env['BUILDERS'][builder])
