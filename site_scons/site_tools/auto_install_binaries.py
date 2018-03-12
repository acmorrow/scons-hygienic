import datetime
import itertools

# TODO: implement sdk_headers
# TODO: Namedtuple for alias_map
# TODO: move keep_targetinfo to tag_install
# TODO: Add test tag automatically for unit tests, etc.
# TODO: Test tag still leaves things in the runtime component
# TODO: library dependency chaining for windows dynamic builds, static dev packages
# TODO: Separate debug info (different tool?)
# TODO: How should debug info work for tests?
# TODO: Handle chmod state
# TODO: tarfile generation
# TODO: Injectible component dependencies (jscore -> resmoke, etc.)
# TODO: Installing resmoke and configurations
# TODO: Distfiles and equivalent for the dist target
# TODO: package decomposition
# TODO: Install/package target help text

from collections import defaultdict

import SCons

def exists(env):
    return True

def generate(env):

    role_tags = set([
        'common',
        'debug',
        'dev',
        'meta',
        'runtime',
    ])

    role_dependencies = {
        'dev' : ['runtime', 'common'],
        'meta' : ['dev', 'runtime', 'common', 'debug'],
        'debug' : ['runtime'],
        'runtime' : ['common'],
    }

    predefined_component_tags = set([
        'all',
        'base',
        'default',
    ])

    env.Tool('install')

    suffix_map = {
        env.subst('$PROGSUFFIX') : ('bin', ['runtime',]),
        env.subst('$LIBSUFFIX') : ('lib', ['dev',]),
        '.dll' :   ('bin', ['runtime',]),
        '.dylib' : ('lib', ['runtime', 'dev',]),
        '.so' :    ('lib', ['runtime', 'dev',]),
    }

    alias_map = defaultdict(dict)

    def tag_install(env, target, source, **kwargs):
        prefixDir = env.Dir('$PREFIX')

        actions = []
        targetDir = prefixDir.Dir(target)
        actions = SCons.Script.Install(
            target=targetDir,
            source=source,
        )
        for s in map(env.Entry, env.Flatten(source)):
            setattr(s.attributes, "aib_install_actions", actions)

        tags = set(kwargs.get('INSTALL_TAGS', []))

        applied_role_tags = role_tags.intersection(tags)
        applied_component_tags = tags - applied_role_tags

        # The 'all' tag is implicitly attached as a component, and the
        # 'meta' tag is implicitly attached as a role.
        applied_role_tags.add("meta")
        applied_component_tags.add("all")

        for component_tag, role_tag in itertools.product(applied_component_tags, applied_role_tags):
            alias_name = 'install-' + component_tag
            alias_name = alias_name + ("" if role_tag == "runtime" else "-" + role_tag)
            prealias_name = 'pre' + alias_name
            alias = env.Alias(alias_name, actions)
            prealias = env.Alias(prealias_name, source)
            alias_map[component_tag][role_tag] = (alias_name, alias, prealias_name, prealias)

        return actions

    def finalize_install_dependencies(env):
        base_rolemap = alias_map.get('base', None)
        default_rolemap = alias_map.get('default', None)

        if default_rolemap and 'runtime' in default_rolemap:
            env.Alias('install', 'install-default')
            env.Default('install')

        for component, rolemap in alias_map.iteritems():
            for role, info in rolemap.iteritems():

                if base_rolemap and component != 'base' and role in base_rolemap:
                    env.Depends(info[1], base_rolemap[role][1])
                    env.Depends(info[3], base_rolemap[role][3])

                for dependency in role_dependencies.get(role, []):
                    dependency_info = rolemap.get(dependency, [])
                    if dependency_info:
                        env.Depends(info[1], dependency_info[1])
                        env.Depends(info[3], dependency_info[3])

        installedFiles = env.FindInstalledFiles()
        env.NoCache(installedFiles)

    env.AddMethod(finalize_install_dependencies, "FinalizeInstallDependencies")
    env.AddMethod(tag_install, 'Install')

    def auto_install_emitter(target, source, env):
        for t in target:
            tentry = env.Entry(t)
            # We want to make sure that the executor information stays
            # persisted for this node after it is built so that we can
            # access it in our install emitter below.
            tentry.attributes.keep_targetinfo = 1
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
        builder = env['BUILDERS'][builder]
        add_emitter(builder)

    def scan_for_transitive_install(node, env, path=()):
        results = []
        install_sources = node.sources
        for install_source in install_sources:
            is_executor = install_source.get_executor()
            is_targets = is_executor.get_all_targets()
            for is_target in is_targets:
                grandchildren = is_target.children()
                for grandchild in grandchildren:
                    actions = getattr(grandchild.attributes, "aib_install_actions", None)
                    if actions:
                        results.extend(actions)
        results = sorted(results, key=lambda t: str(t))
        return results

    from SCons.Tool import install
    base_install_builder = install.BaseInstallBuilder
    assert(base_install_builder.target_scanner == None)

    base_install_builder.target_scanner = SCons.Scanner.Scanner(
        function=scan_for_transitive_install,
        path_function=None,
    )
