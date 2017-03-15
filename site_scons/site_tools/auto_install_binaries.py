import itertools

import SCons

def exists(env):
    True

def generate(env):

    base_install = env.Install

    def tag_install(env, target, source, **kwargs):

        tmpPrefixDir = env.Dir('$TMP_PREFIX')
        prefixDir = env.Dir('$PREFIX')

        tmp_actions = base_install(
            target=tmpPrefixDir.Dir(target),
            source=source,
        )

        actions = tmp_actions
        if (tmpPrefixDir != prefixDir):
            actions = base_install(
                target=prefixDir.Dir(target),
                source=tmp_actions,
            )

        tags = kwargs.get('INSTALL_TAGS')
        for tag in tags:
            env.Alias('preinstall-' + tag, tmp_actions)
            env.Alias('install-' + tag, actions)
            if tag == "default":
                env.Alias('preinstall', tmp_actions)
                env.Alias('install', actions)
        env.Alias('preinstall-all', tmp_actions)
        env.Alias('install-all', actions)


    def finalize_install_dependencies(env):

        installedFiles = env.FindInstalledFiles()
        env.NoCache(installedFiles)

        tmpPrefix = env.Dir('$TMP_PREFIX')
        prefix = env.Dir('$PREFIX')

        if prefix == tmpPrefix:
            env.Default('install')
            return

        prefixFiles = [f for f in installedFiles if f.abspath.startswith(prefix.abspath)]
        prefixPairs = itertools.permutations(prefixFiles, 2)

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
            fromsource = env.Flatten([fromsource])
            tosource = env.Flatten([tosource])
            # TODO: Need to verify only one source
            return do_exists_transitive_dependency(fromsource[0], tosource[0])

        for pair in prefixPairs:
            if exists_transitive_dependency(pair[0].sources, pair[1].sources):
                env.Depends(pair[0], pair[1])

        env.Default('preinstall')

    env.AddMethod(finalize_install_dependencies, "FinalizeInstallDependencies")
    env.AddMethod(tag_install, 'Install')

    def auto_install_emitter(target, source, env):

        suffix_map = {
            '' :       ('bin', ['runtime',]),
            '.a' :     ('lib', ['dev',]),
            '.dll' :   ('bin', ['runtime',]),
            '.dylib' : ('lib', ['runtime', 'dev',]),
            '.exe' :   ('bin', ['runtime',]),
            '.lib' :   ('lib', ['dev',]),
            '.so' :    ('lib', ['runtime', 'dev',]),
        }

        for t in target:
            tsuf = env.Entry(t).get_suffix()
            auto_install_location = suffix_map.get(tsuf)
            if auto_install_location:
                target_install_tags = env.get('INSTALL_TAGS', [])
                target_install_tags.extend(auto_install_location[1])
                env.Install(auto_install_location[0], t, INSTALL_TAGS=target_install_tags)
        return (target, source)

    def add_emitter(builder):
        base_emitter = builder.emitter
        new_emitter = SCons.Builder.ListEmitter([base_emitter, auto_install_emitter])
        builder.emitter = new_emitter

    target_builders = ['Program', 'SharedLibrary', 'LoadableModule', 'StaticLibrary']
    for builder in target_builders:
        add_emitter(env['BUILDERS'][builder])
