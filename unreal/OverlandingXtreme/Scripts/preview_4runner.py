"""Assemble imported vehicle parts beside the canyon start for art review.

This is a static display; it does not replace the working Chaos vehicle.
Interchange bakes the glTF node transforms into these mesh vertices.
"""
import json
import math
from pathlib import Path
import unreal as u

root = Path(u.Paths.project_dir()).resolve()
points = json.loads((root.parent / 'Migration/RedRockRun.json').read_text())['trail_samples']
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
parts = []
for path in assets.list_assets('/Game/Licensed/Toyota4Runner', recursive=True):
    asset = u.load_asset(path)
    if isinstance(asset, u.StaticMesh):
        parts.append(asset)
if len(parts) != 17:
    raise RuntimeError('Expected all 17 vehicle parts; run import_4runner.py first')
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
if not levels.load_level('/Game/Overlanding/Maps/RedRockRun'):
    raise RuntimeError('Cannot open canyon map')
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
for actor in actors.get_all_level_actors():
    if actor.get_actor_label().startswith('FourRunnerPreview_'):
        actors.destroy_actor(actor)
p, q = points[:2]
heading = math.atan2(q['y_cm']-p['y_cm'], q['x_cm']-p['x_cm'])
# SUV nose is local -Y; rotate it to point along the trail's +X heading.
rotation = u.Rotator(yaw=math.degrees(heading)+90)
position = u.Vector(p['x_cm']-math.sin(heading)*650,
                    p['y_cm']+math.cos(heading)*650, p['z_cm']+10)
for part in parts:
    actor = actors.spawn_actor_from_class(u.StaticMeshActor, position, rotation)
    actor.set_actor_label('FourRunnerPreview_'+part.get_name())
    actor.static_mesh_component.set_static_mesh(part)
    actor.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
if not levels.save_current_level():
    raise RuntimeError('Cannot save assembled preview')
u.log('FOURRUNNER_PREVIEW_OK parts=%d' % len(parts))
