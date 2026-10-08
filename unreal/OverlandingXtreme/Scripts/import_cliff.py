"""Import the locally acquired Fab cliff into a licensed asset folder."""
from pathlib import Path
import unreal as u
root = Path(u.Paths.project_dir()).resolve()
source = root.parents[1] / '.tools/assets/cliff/vjrmfb1ab_tier_1.gltf'
if not source.exists():
    raise RuntimeError('Extract the acquired UE high-quality cliff archive into .tools/assets/cliff')
task = u.AssetImportTask()
task.filename = str(source)
task.destination_path = '/Game/Licensed/QuixelCliff'
task.automated = True
task.replace_existing = True
task.save = True
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
meshes = []
for path in assets.list_assets('/Game/Licensed/QuixelCliff', recursive=True):
    asset = u.load_asset(path)
    if isinstance(asset,u.StaticMesh):
        meshes.append(asset)
        u.EditorStaticMeshLibrary.add_simple_collisions(asset,u.ScriptingCollisionShapeType.NDOP26)
        assets.save_loaded_asset(asset)
        u.log('CLIFF_MESH path=%s bounds=%s' % (path,asset.get_bounds()))
if not meshes:
    raise RuntimeError('Cliff import produced no static mesh')
u.log('CLIFF_IMPORT_OK meshes=%d' % len(meshes))
