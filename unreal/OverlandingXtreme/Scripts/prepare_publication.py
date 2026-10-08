"""Preserve scanned local maps and make the shared maps self-contained.

Run in the full editor. Prepared CC-BY 4Runner content is publishable with
ASSET_NOTICES.md; acquired Quixel source content stays in the local project.
"""
import unreal as u

assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
rock = u.load_asset('/Game/Overlanding/Meshes/SM_LayeredSandstone')
material = u.load_asset('/Game/Overlanding/Materials/M_Sandstone_Detailed')
if not rock or not material:
    raise RuntimeError('Missing original procedural sandstone fallback')

for name in ('RedRockRun','RedRockRun4Runner'):
    source = '/Game/Overlanding/Maps/'+name
    local = '/Game/LocalOnly/Maps/'+name
    if not assets.does_asset_exist(local):
        if not levels.new_level_from_template(local,source):
            raise RuntimeError('Cannot preserve scanned local map: '+name)
        if not levels.save_current_level():
            raise RuntimeError('Cannot save scanned local map: '+name)
    if not levels.load_level(source):
        raise RuntimeError('Cannot open shared map: '+name)
    replaced = 0
    for actor in actors.get_all_level_actors():
        if actor.get_actor_label().startswith('FourRunnerPreview_'):
            actors.destroy_actor(actor)
            continue
        if not isinstance(actor,u.StaticMeshActor):
            continue
        component = actor.static_mesh_component
        old = component.static_mesh
        if old and old.get_path_name().startswith('/Game/Licensed/QuixelCliff/'):
            scale = actor.get_actor_scale3d()
            position = actor.get_actor_location()
            # Preserve width, depth and bottom elevation. Procedural sandstone
            # is approximately a centered 100 cm mesh; the scan is bottom-pivoted.
            position.z += (1484/2-81)*scale.z
            actor.set_actor_location(position,False,False)
            actor.set_actor_scale3d(u.Vector(scale.x*2570/100,scale.y*1357/100,scale.z*1484/100))
            component.set_static_mesh(rock)
            component.set_editor_property('override_materials',[material])
            replaced += 1
    if not levels.save_current_level():
        raise RuntimeError('Cannot save shared fallback map: '+name)
    u.log('PUBLIC_MAP_OK name=%s replaced_cliffs=%d' % (name,replaced))

registry = u.AssetRegistryHelpers.get_asset_registry()
options = u.AssetRegistryDependencyOptions(include_soft_package_references=True,
    include_hard_package_references=True,include_searchable_names=False,
    include_soft_management_references=False,include_hard_management_references=False)
visited = set()
pending = ['/Game/Overlanding/Maps/RedRockRun','/Game/Overlanding/Maps/RedRockRun4Runner']
while pending:
    package = pending.pop()
    if package in visited: continue
    visited.add(package)
    if package.startswith('/Game/Licensed/QuixelCliff') or package.startswith('/Game/LocalOnly'):
        raise RuntimeError('Shared map still references local-only content: '+package)
    if package.startswith('/Game/'):
        pending.extend(str(path) for path in registry.get_dependencies(package,options))
u.log('PUBLICATION_DEPENDENCIES_OK packages=%d' % len(visited))
