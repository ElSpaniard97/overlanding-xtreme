"""Import the user-downloaded CC-BY Toyota 4Runner glTF."""
from pathlib import Path
import unreal as u
root = Path(u.Paths.project_dir()).resolve()
source = root.parents[1] / '.tools/assets/4runner/scene.gltf'
if not source.exists():
    raise RuntimeError('Extract the acquired vehicle into .tools/assets/4runner')
task = u.AssetImportTask()
task.filename = str(source)
task.destination_path = '/Game/Licensed/Toyota4Runner'
task.automated = True
task.replace_existing = True
task.save = True
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
meshes = []
for path in assets.list_assets('/Game/Licensed/Toyota4Runner', recursive=True):
    asset = u.load_asset(path)
    if isinstance(asset,u.StaticMesh):
        meshes.append(asset)
        u.EditorStaticMeshLibrary.add_simple_collisions(asset,u.ScriptingCollisionShapeType.NDOP26)
        assets.save_loaded_asset(asset)
        u.log('VEHICLE_MESH path=%s bounds=%s' % (path,asset.get_bounds()))
if not meshes:
    raise RuntimeError('Vehicle import produced no static mesh')
u.log('VEHICLE_IMPORT_OK meshes=%d' % len(meshes))
