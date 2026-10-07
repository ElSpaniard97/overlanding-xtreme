"""Rebuild the deterministic canyon blockout from the browser route export."""
import unreal as u
import json, math, random
from pathlib import Path
ROOT = Path(u.Paths.project_dir()).resolve()
route = json.loads((ROOT.parent / 'Migration/RedRockRun.json').read_text())
rng = random.Random(97)
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
map_path = '/Game/Overlanding/Maps/RedRockRun'
if assets.does_asset_exist(map_path):
    if not levels.load_level(map_path):
        raise RuntimeError('Cannot load generated canyon map')
    for old in actors.get_all_level_actors():
        if not isinstance(old, u.WorldSettings):
            actors.destroy_actor(old)
elif not levels.new_level(map_path):
    raise RuntimeError('Cannot create canyon map')
cube = u.load_asset('/Game/Overlanding/Meshes/SM_CollisionCube')
if not cube:
    cube = assets.duplicate_asset('/Engine/BasicShapes/Cube','/Game/Overlanding/Meshes/SM_CollisionCube')
    u.EditorStaticMeshLibrary.add_simple_collisions(cube,u.ScriptingCollisionShapeType.BOX)
    assets.save_loaded_asset(cube)
sphere = u.load_asset('/Engine/BasicShapes/Sphere')

def material(name, rgb, roughness=0.9):
    path = '/Game/Overlanding/Materials/' + name
    m = u.load_asset(path)
    if not m:
        m = u.AssetToolsHelpers.get_asset_tools().create_asset(name, '/Game/Overlanding/Materials', u.Material, u.MaterialFactoryNew())
        c = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionConstant3Vector)
        c.set_editor_property('constant', u.LinearColor(*rgb, 1))
        u.MaterialEditingLibrary.connect_material_property(c, '', u.MaterialProperty.MP_BASE_COLOR)
        r = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionConstant)
        r.set_editor_property('r', roughness)
        u.MaterialEditingLibrary.connect_material_property(r, '', u.MaterialProperty.MP_ROUGHNESS)
        u.MaterialEditingLibrary.recompile_material(m)
    assets.save_loaded_asset(m)
    return m
sand = material('M_TrailSand', (0.34, 0.18, 0.085))
rock = material('M_Sandstone', (0.29, 0.105, 0.047))
strata = material('M_Strata', (0.46, 0.235, 0.12))
water = material('M_River', (0.035, 0.16, 0.19), 0.22)

def mesh(name, pos, scale, mat, shape=cube, rotation=None):
    a = actors.spawn_actor_from_class(u.StaticMeshActor, u.Vector(*pos), rotation or u.Rotator())
    a.set_actor_label(name)
    c = a.static_mesh_component
    c.set_mobility(u.ComponentMobility.STATIC)
    c.set_static_mesh(shape)
    c.set_collision_profile_name("BlockAll")
    c.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS)
    a.set_actor_enable_collision(True)
    c.set_material(0, mat)
    a.set_actor_scale3d(u.Vector(*scale))
    return a

points = route['trail_samples']
# Overlapping tangent slabs provide collision along the complete exported route.
for i, (p, q) in enumerate(zip(points, points[1:])):
    dx, dy, dz = (q[k] - p[k] for k in ('x_cm', 'y_cm', 'z_cm'))
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    yaw = math.degrees(math.atan2(dy, dx))
    pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
    mesh('Trail_%03d' % i, ((p['x_cm']+q['x_cm'])/2, (p['y_cm']+q['y_cm'])/2, (p['z_cm']+q['z_cm'])/2-65), ((length+90)/100, 13, 1.3), sand, rotation=u.Rotator(pitch, yaw, 0))
    mesh('CanyonFloor_%03d' % i, ((p['x_cm']+q['x_cm'])/2, (p['y_cm']+q['y_cm'])/2, (p['z_cm']+q['z_cm'])/2-700), ((length+120)/100, 180, 12), rock, rotation=u.Rotator(pitch, yaw, 0))
    if i % 3 == 0:
        for side in (-1, 1):
            h = rng.uniform(900, 2600)
            x = p['x_cm'] + rng.uniform(-400,400)
            y = p['y_cm'] + side*rng.uniform(2200, 4200)
            mesh('CanyonWall_%03d_%d' % (i,side), (x,y,p['z_cm']-700+h/2), (rng.uniform(15,28),rng.uniform(16,27),h/100), rock, shape=sphere, rotation=u.Rotator(0,rng.uniform(-12,12),0))
            mesh('RockShelf_%03d_%d' % (i,side), (x,y,p['z_cm']-700+h*.7), (30,29,2.5), strata)
    if i % 2 == 0:
        side = rng.choice((-1,1))
        mesh('TrailRock_%03d' % i, (p['x_cm'],p['y_cm']+side*rng.uniform(720,1100),p['z_cm']+rng.uniform(0,45)), (rng.uniform(1,3),rng.uniform(1,2),rng.uniform(.5,1.4)), rock, sphere)
mesh('RiverBelowCanyon', (75000,18000,-1700), (1650,160,2), water)
start = points[0]
mesh('StartingPlateau', (start['x_cm'],start['y_cm'],start['z_cm']-120), (120,120,2), sand)
mesh('StartRearBarrier', (-5500,0,700), (4,120,12), rock)
q = points[1]
yaw = math.degrees(math.atan2(q['y_cm']-start['y_cm'],q['x_cm']-start['x_cm']))
actors.spawn_actor_from_class(u.PlayerStart,u.Vector(start['x_cm'],start['y_cm'],start['z_cm']+180),u.Rotator(0,yaw,0))
world = u.EditorLevelLibrary.get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Game/Variant_Offroad/Blueprints/BP_OffroadGameMode.BP_OffroadGameMode_C'))
sun = actors.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,8000),u.Rotator(-12,-35,0))
sun.set_actor_label('GoldenHourSun')
sun.light_component.set_editor_property('atmosphere_sun_light',True)
sun.light_component.set_editor_property('intensity',4.5)
sun.light_component.set_editor_property('light_color',u.Color(255,195,135,255))
actors.spawn_actor_from_class(u.SkyAtmosphere,u.Vector())
sky = actors.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,5000))
sky.light_component.set_editor_property('real_time_capture',True)
sky.light_component.set_editor_property('intensity',0.8)
actors.spawn_actor_from_class(u.ExponentialHeightFog,u.Vector(0,0,-1000))
for obj in route['objectives']:
    p=obj['location_cm']
    marker=actors.spawn_actor_from_class(u.TextRenderActor,u.Vector(p['x'],p['y']+900,p['z']+400),u.Rotator(0,180,0))
    marker.set_actor_label('Objective_'+str(obj['id']))
    marker.text_render.set_text(obj['label'])
    marker.text_render.set_world_size(70)
if not levels.save_current_level():
    raise RuntimeError('Cannot save generated canyon map')
u.log('OVERLANDING_LEVEL_BUILT actors=%d route_segments=%d' % (len(actors.get_all_level_actors()),len(points)-1))
