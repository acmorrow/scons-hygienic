import itertools

import SCons

def exists(env):
    True

def generate(env):

    suffix_map = {
        env.subst('$PROGSUFFIX') : ('bin', ['runtime',]),
        env.subst('$LIBSUFFIX') : ('lib', ['dev',]),
        '.dll' :   ('bin', ['runtime',]),
        '.dylib' : ('lib', ['runtime', 'dev',]),
        '.so' :    ('lib', ['runtime', 'dev',]),
    }

    def tag_install(env, target, source, **kwargs):

        prefixDir = env.Dir('$PREFIX')

        actions = SCons.Script.Install(
            target=prefixDir.Dir(target),
            source=source,
        )

        tags = kwargs.get('INSTALL_TAGS', [])

        for tag in tags:
            env.Alias('install-' + tag, actions)
            env.Alias('preinstall-' + tag, source)
            if tag == "default":
                env.Alias('install', actions)
                env.Alias('preinstall', source)
                env.Default('install')

        env.Alias('install-all', actions)
        env.Alias('preinstall-all', source)

    def finalize_install_dependencies(env):

        installedFiles = env.FindInstalledFiles()
        env.NoCache(installedFiles)

        def source_is_runtime(t):
            assert(len(t.sources) == 1)
            return 'runtime' in getattr(env.File(t.sources[0]).attributes, 'INSTALL_TAGS', [])
        installedFiles = filter(source_is_runtime, installedFiles)

        prefixPairs = itertools.permutations(installedFiles, 2)
        transitive_cache=dict()

        def do_exists_transitive_dependency(f, t):
            cached = transitive_cache.get((f, t))
            if cached is not None:
                return cached
            f_children = f.children()
            if t in f_children:
                transitive_cache[(f, t)] = True
                transitive_cache[(t, f)] = False
                return True
            for child in f_children:
                if do_exists_transitive_dependency(child, t):
                    transitive_cache[(f, t)] = True
                    transitive_cache[(t, f)] = False
                    return True
            transitive_cache[(f, t)] = False
            return False

        def exists_transitive_dependency(fromsource, tosource):
            assert(len(fromsource) == 1)
            assert(len(tosource) == 1)
            fromsource = env.Flatten([fromsource])[0]
            tosource = env.Flatten([tosource])[0]
            return do_exists_transitive_dependency(fromsource, tosource)

        for pair in prefixPairs:
            if exists_transitive_dependency(pair[0].sources, pair[1].sources):
                env.Depends(pair[0], pair[1])

    env.AddMethod(finalize_install_dependencies, "FinalizeInstallDependencies")
    env.AddMethod(tag_install, 'Install')

    def auto_install_emitter(target, source, env):

        for t in target:
            tentry = env.Entry(t)
            tsuf = tentry.get_suffix()
            auto_install_location = suffix_map.get(tsuf)
            if auto_install_location:
                tentry_install_tags = env.get('INSTALL_TAGS', [])
                tentry_install_tags.extend(auto_install_location[1])
                setattr(tentry.attributes, 'INSTALL_TAGS', tentry_install_tags)
                env.Install(auto_install_location[0], tentry, INSTALL_TAGS=tentry_install_tags)
        return (target, source)

    def add_emitter(builder):
        base_emitter = builder.emitter
        new_emitter = SCons.Builder.ListEmitter([base_emitter, auto_install_emitter])
        builder.emitter = new_emitter

    target_builders = ['Program', 'SharedLibrary', 'LoadableModule', 'StaticLibrary']
    for builder in target_builders:
        add_emitter(env['BUILDERS'][builder])
