"""Create the playable 4Runner canyon variant after import and C++ build."""
import os
import unreal as u

assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
for part in ('Body','FL','FR','RL','RR'):
    path = '/Game/Licensed/Toyota4Runner/Prepared/FourRunner_%s/StaticMeshes/FourRunner_%s' % (part,part)
    if not isinstance(u.load_asset(path),u.StaticMesh):
        raise RuntimeError('Missing prepared 4Runner part: '+part)
mode = u.load_class(None,'/Script/OverlandingXtreme.OverlandingGameMode')
if not mode:
    raise RuntimeError('Build the OverlandingXtremeEditor target first')
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
folder = '/Game/LocalOnly/Maps/' if os.environ.get('OVERLANDING_USE_SCANS') == '1' else '/Game/Overlanding/Maps/'
destination = folder+'RedRockRun4Runner'
if assets.does_asset_exist(destination):
    opened = levels.load_level(destination)
else:
    opened = levels.new_level_from_template(destination,folder+'RedRockRun')
if not opened:
    raise RuntimeError('Missing canyon map')
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith('FourRunnerPreview_'):
        actors.destroy_actor(actor)
world = u.EditorLevelLibrary.get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',mode)
if not levels.save_current_level():
    raise RuntimeError('Cannot save 4Runner map')
u.log('FOURRUNNER_SETUP_OK')
