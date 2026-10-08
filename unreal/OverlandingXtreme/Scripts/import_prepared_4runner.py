"""Import the forward-X body and centered wheels produced by prepare_4runner.py."""
from pathlib import Path
import unreal as u

root = Path(u.Paths.project_dir()).resolve()
source = root.parents[1]/'.tools/assets/4runner/prepared'
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
for name in ('Body','FL','FR','RL','RR'):
    filename = source/('FourRunner_'+name+'.gltf')
    if not filename.exists():
        raise RuntimeError('Run prepare_4runner.py before importing')
    task = u.AssetImportTask()
    task.filename = str(filename)
    task.destination_path = '/Game/Licensed/Toyota4Runner/Prepared'
    task.automated = True
    task.replace_existing = True
    task.save = True
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
for path in assets.list_assets('/Game/Licensed/Toyota4Runner/Prepared',recursive=True):
    asset = u.load_asset(path)
    if isinstance(asset,u.StaticMesh):
        u.log('PREPARED_VEHICLE %s bounds=%s' % (path,asset.get_bounds()))
u.log('PREPARED_IMPORT_OK')
