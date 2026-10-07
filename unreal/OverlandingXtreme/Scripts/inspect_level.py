import unreal as u
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/Overlanding/Maps/RedRockRun')
a=u.get_editor_subsystem(u.EditorActorSubsystem)
for actor in a.get_all_level_actors():
    if isinstance(actor,u.StaticMeshActor) and actor.get_actor_location().x < 1:
        c=actor.static_mesh_component
        u.log('GROUND location=%s scale=%s collision=%s profile=%s mesh=%s boxes=%s' % (actor.get_actor_location(),actor.get_actor_scale3d(),c.get_collision_enabled(),c.get_collision_profile_name(),c.static_mesh,u.EditorStaticMeshLibrary.get_simple_collision_count(c.static_mesh)))
    if isinstance(actor,u.PlayerStart):
        u.log('START location=%s' % actor.get_actor_location())
