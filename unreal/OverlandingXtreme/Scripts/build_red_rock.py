"""Rebuild the deterministic canyon blockout from the browser route export."""
import unreal as u
import json, math, random, os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from trail_geometry import write_trail_obj
from rock_geometry import write_rock_obj, write_shrub_obj
ROOT = Path(u.Paths.project_dir()).resolve()
route = json.loads((ROOT.parent / 'Migration/RedRockRun.json').read_text())
rng = random.Random(97)
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
cube = u.load_asset('/Game/Overlanding/Meshes/SM_CollisionCube')
if not cube:
    cube = assets.duplicate_asset('/Engine/BasicShapes/Cube','/Game/Overlanding/Meshes/SM_CollisionCube')
    u.EditorStaticMeshLibrary.add_simple_collisions(cube,u.ScriptingCollisionShapeType.BOX)
    assets.save_loaded_asset(cube)
sphere = u.load_asset('/Engine/BasicShapes/Sphere')

def material(name, rgb, roughness=0.9, variation=False):
    path = '/Game/Overlanding/Materials/' + name
    m = u.load_asset(path)
    if not m:
        m = u.AssetToolsHelpers.get_asset_tools().create_asset(name, '/Game/Overlanding/Materials', u.Material, u.MaterialFactoryNew())
        c = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionConstant3Vector)
        c.set_editor_property('constant', u.LinearColor(*rgb, 1))
        if variation:
            position = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionWorldPosition)
            scale = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionMultiply)
            scale.set_editor_property('const_b', 0.035)
            noise = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionNoise)
            noise.set_editor_property('quality', 1)
            noise.set_editor_property('levels', 2)
            noise.set_editor_property('output_min', 0.0)
            noise.set_editor_property('output_max', 1.0)
            tint = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionConstant3Vector)
            tint.set_editor_property('constant', u.LinearColor(*(v*.48 for v in rgb),1))
            blend = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionLinearInterpolate)
            for source, target, pin in [(position,scale,'A'),(scale,noise,'Position'),(c,blend,'A'),(tint,blend,'B'),(noise,blend,'Alpha')]:
                u.MaterialEditingLibrary.connect_material_expressions(source,'',target,pin)
            u.MaterialEditingLibrary.connect_material_property(blend, '', u.MaterialProperty.MP_BASE_COLOR)
        else:
            u.MaterialEditingLibrary.connect_material_property(c, '', u.MaterialProperty.MP_BASE_COLOR)
        r = u.MaterialEditingLibrary.create_material_expression(m, u.MaterialExpressionConstant)
        r.set_editor_property('r', roughness)
        u.MaterialEditingLibrary.connect_material_property(r, '', u.MaterialProperty.MP_ROUGHNESS)
        u.MaterialEditingLibrary.recompile_material(m)
    assets.save_loaded_asset(m)
    return m
sand = material('M_TrailSand_Detailed', (0.34, 0.18, 0.085), variation=True)
rock = material('M_Sandstone_Detailed', (0.29, 0.105, 0.047), variation=True)
strata = material('M_Strata', (0.46, 0.235, 0.12))
water = material('M_River', (0.035, 0.16, 0.19), 0.22)
amber = material('M_RouteAmber', (0.95, 0.55, 0.055))
dark = material('M_MarkerCharcoal', (0.035, 0.045, 0.04))
foliage = material('M_DesertFoliage', (0.065, 0.11, 0.027), variation=True)
canvas = material('M_CampCanvas', (0.26, 0.31, 0.17))

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
source = ROOT / 'Intermediate' / 'GeneratedTrail.obj'
source.parent.mkdir(parents=True, exist_ok=True)
triangle_count = write_trail_obj(points, source)
task = u.AssetImportTask()
task.filename = str(source)
task.destination_path = '/Game/Overlanding/Meshes'
task.destination_name = 'SM_ContinuousTrail'
task.automated = True
task.replace_existing = True
task.save = True
options = u.FbxImportUI()
options.import_mesh = True
options.import_as_skeletal = False
options.import_materials = False
options.import_textures = False
options.static_mesh_import_data.set_editor_property('auto_generate_collision', False)
task.options = options
task.factory = u.FbxFactory()
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
trail_mesh = u.load_asset('/Game/Overlanding/Meshes/SM_ContinuousTrail')
if not trail_mesh:
    raise RuntimeError('Continuous trail import failed; existing level has not been changed')
bounds = trail_mesh.get_bounds()
if bounds.box_extent.z > 3000 or bounds.box_extent.y < 3000:
    raise RuntimeError('Imported road axes do not match the route')
body = trail_mesh.get_editor_property('body_setup')
body.set_editor_property('collision_trace_flag', u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
assets.save_loaded_asset(trail_mesh)
# Layered irregular rock geometry replaces stretched spheres and box shelves.
rock_source = ROOT / 'Intermediate' / 'GeneratedSandstone.obj'
write_rock_obj(rock_source)
rock_task = u.AssetImportTask()
rock_task.filename = str(rock_source)
rock_task.destination_path = '/Game/Overlanding/Meshes'
rock_task.destination_name = 'SM_LayeredSandstone'
rock_task.automated = True
rock_task.replace_existing = True
rock_task.save = True
rock_task.options = options
rock_task.factory = u.FbxFactory()
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([rock_task])
rock_mesh = u.load_asset('/Game/Overlanding/Meshes/SM_LayeredSandstone')
if not rock_mesh:
    raise RuntimeError('Sandstone import failed before map rebuild')
u.EditorStaticMeshLibrary.add_simple_collisions(rock_mesh,u.ScriptingCollisionShapeType.NDOP26)
assets.save_loaded_asset(rock_mesh)
shrub_source = ROOT / 'Intermediate' / 'GeneratedShrub.obj'
write_shrub_obj(shrub_source)
shrub_task = u.AssetImportTask()
shrub_task.filename = str(shrub_source)
shrub_task.destination_path = '/Game/Overlanding/Meshes'
shrub_task.destination_name = 'SM_DesertShrub'
shrub_task.automated = True
shrub_task.replace_existing = True
shrub_task.save = True
shrub_task.options = options
shrub_task.factory = u.FbxFactory()
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([shrub_task])
shrub_mesh = u.load_asset('/Game/Overlanding/Meshes/SM_DesertShrub')
if not shrub_mesh:
    raise RuntimeError('Shrub import failed before map rebuild')
use_scans = os.environ.get('OVERLANDING_USE_SCANS') == '1'
scanned_cliff = u.load_asset('/Game/Licensed/QuixelCliff/vjrmfb1ab_tier_1/StaticMeshes/vjrmfb1ab_tier_1') if use_scans else None
scanned_material = u.load_asset('/Game/Licensed/QuixelCliff/vjrmfb1ab_tier_1/Materials/MI_vjrmfb1ab') if use_scans else None
map_path = '/Game/LocalOnly/Maps/RedRockRun' if use_scans else '/Game/Overlanding/Maps/RedRockRun'
if assets.does_asset_exist(map_path):
    if not levels.load_level(map_path):
        raise RuntimeError('Cannot load generated canyon map')
    for old in actors.get_all_level_actors():
        if not isinstance(old, u.WorldSettings):
            actors.destroy_actor(old)
elif not levels.new_level(map_path):
    raise RuntimeError('Cannot create canyon map')
mesh('ContinuousTrail', (0,0,0), (1,1,1), sand, trail_mesh)
points = route['trail_samples']
# Canyon floor supports excursions outside the continuous road ribbon.
for i, (p, q) in enumerate(zip(points, points[1:])):
    dx, dy, dz = (q[k] - p[k] for k in ('x_cm', 'y_cm', 'z_cm'))
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    yaw = math.degrees(math.atan2(dy, dx))
    pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
    mesh('CanyonFloor_%03d' % i, ((p['x_cm']+q['x_cm'])/2, (p['y_cm']+q['y_cm'])/2, (p['z_cm']+q['z_cm'])/2-700), ((length+120)/100, 180, 12), rock, rotation=u.Rotator(pitch=pitch, yaw=yaw, roll=0))
    if i % 3 == 0:
        for side in (-1, 1):
            h = rng.uniform(900, 2600)
            x = p['x_cm'] + rng.uniform(-400,400)
            y = p['y_cm'] + side*rng.uniform(2200, 4200)
            width,depth = rng.uniform(15,28),rng.uniform(16,27)
            rotation = u.Rotator(yaw=rng.uniform(-12,12))
            if scanned_cliff and scanned_material:
                # Scan bounds: 2570 x 1357 x 1484 cm; pivot sits 81 cm below its base.
                scale = (width*100/2570,depth*100/1357,h/1484)
                mesh('CanyonWall_%03d_%d' % (i,side),
                    (x,y,p['z_cm']-700+81*scale[2]),scale,scanned_material,
                    shape=scanned_cliff,rotation=rotation)
            else:
                mesh('CanyonWall_%03d_%d' % (i,side), (x,y,p['z_cm']-700+h/2),
                    (width,depth,h/100),rock,shape=rock_mesh,rotation=rotation)
    if i % 2 == 0:
        side = rng.choice((-1,1))
        mesh('TrailRock_%03d' % i, (p['x_cm'],p['y_cm']+side*rng.uniform(720,1100),p['z_cm']+rng.uniform(0,45)), (rng.uniform(1,3),rng.uniform(1,2),rng.uniform(.5,1.4)), rock, rock_mesh)
mesh('RiverBelowCanyon', (75000,18000,-1700), (1650,160,2), water)
start = points[0]
mesh('StartingPlateau', (start['x_cm'],start['y_cm'],start['z_cm']-120), (120,120,2), sand)
mesh('StartRearBarrier', (-5500,0,700), (4,120,12), rock)
q = points[1]
yaw = math.degrees(math.atan2(q['y_cm']-start['y_cm'],q['x_cm']-start['x_cm']))
actors.spawn_actor_from_class(u.PlayerStart,u.Vector(start['x_cm'],start['y_cm'],start['z_cm']+180),u.Rotator(yaw=yaw))
world = u.EditorLevelLibrary.get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Game/Variant_Offroad/Blueprints/BP_OffroadGameMode.BP_OffroadGameMode_C'))
sun = actors.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,8000),u.Rotator(pitch=-4, yaw=-35))
sun.set_actor_label('GoldenHourSun')
sun.light_component.set_editor_property('atmosphere_sun_light',True)
sun.light_component.set_editor_property('intensity',3.0)
sun.light_component.set_editor_property('light_color',u.Color(255,195,135,255))
actors.spawn_actor_from_class(u.SkyAtmosphere,u.Vector())
sky = actors.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,5000))
sky.light_component.set_editor_property('real_time_capture',True)
sky.light_component.set_editor_property('intensity',0.65)
fog = actors.spawn_actor_from_class(u.ExponentialHeightFog,u.Vector(0,0,-1000))
fog.get_component_by_class(u.ExponentialHeightFogComponent).set_editor_property('fog_density',0.012)
fog.get_component_by_class(u.ExponentialHeightFogComponent).set_editor_property('fog_height_falloff',0.12)
# Small clustered shrubs add roadside cover without obstructing driving.
for i in range(0,len(points),3):
    p = points[i]
    before,after = points[max(0,i-1)],points[min(len(points)-1,i+1)]
    dx,dy = after['x_cm']-before['x_cm'],after['y_cm']-before['y_cm']
    length = math.hypot(dx,dy)
    for side in (-1,1):
        offset = rng.uniform(950,1700)*side
        shrub = mesh('DesertShrub_%03d_%d' % (i,side),
            (p['x_cm']-dy/length*offset,p['y_cm']+dx/length*offset,p['z_cm']-95),
            (rng.uniform(1.3,2.8),rng.uniform(1.3,2.8),rng.uniform(1.4,2.6)),
            foliage,shrub_mesh,rotation=u.Rotator(yaw=rng.uniform(0,360)))
        shrub.set_actor_enable_collision(False)

def route_frame(index):
    p = points[index]
    before, after = points[max(0,index-1)], points[min(len(points)-1,index+1)]
    dx, dy = after['x_cm']-before['x_cm'], after['y_cm']-before['y_cm']
    length = math.hypot(dx,dy)
    return p, -dy/length, dx/length, math.degrees(math.atan2(dy,dx))

def route_text(name, text, index, side=1, offset=950, height=320, size=65):
    p, nx, ny, heading = route_frame(index)
    a = actors.spawn_actor_from_class(u.TextRenderActor,
        u.Vector(p['x_cm']+nx*offset*side,p['y_cm']+ny*offset*side,p['z_cm']+height),
        u.Rotator(yaw=heading+180))
    a.set_actor_label(name)
    a.text_render.set_text(text)
    a.text_render.set_world_size(size)
    a.text_render.set_text_render_color(u.Color(255,211,112,255))
    return a

# Reflector posts are outside the 13 m road and do not snag the vehicle.
for i in range(0,len(points),5):
    p, nx, ny, heading = route_frame(i)
    for side in (-1,1):
        pos = (p['x_cm']+nx*780*side,p['y_cm']+ny*780*side,p['z_cm']+55)
        post = mesh('RoutePost_%03d_%d' % (i,side),pos,(0.16,0.16,1.1),dark)
        post.set_actor_enable_collision(False)
        cap = mesh('RouteReflector_%03d_%d' % (i,side),
            (pos[0],pos[1],pos[2]+45),(0.24,0.24,0.2),amber)
        cap.set_actor_enable_collision(False)
    if i > 0 and i % 50 == 0:
        route_text('Distance_%03d' % i,'%0.2f km / 1.50 km' % (i*0.005),i)

# Warn ahead of bends; compare headings over the next 100 m.
last_warning = -30
for i in range(5,len(points)-20):
    heading = route_frame(i)[3]
    ahead = route_frame(i+20)[3]
    bend = (ahead-heading+180)%360-180
    if abs(bend) > 12 and i-last_warning >= 25:
        route_text('BendWarning_%03d' % i,
            'RIGHT TURN  >>' if bend > 0 else '<<  LEFT TURN',i,
            side=-1 if bend > 0 else 1,size=75)
        last_warning = i

route_text('StartControls','RED ROCK RUN\nW / S - DRIVE & BRAKE\nA / D - STEER\nESC - EXIT    F10 - RESTART\nFOLLOW THE AMBER MARKERS',0,
    side=-1,offset=1100,height=550,size=80)
finish = points[-1]
mesh('SummitParking', (finish['x_cm'],finish['y_cm'],finish['z_cm']-110), (95,95,2), sand)
route_text('FinishSign','SUMMIT LOOKOUT\nEND OF TRAIL - PARK HERE',len(points)-1,height=500,size=100)
# A small camp beside the finish provides a visible destination.
p,nx,ny,heading = route_frame(len(points)-1)
cx,cy,cz = p['x_cm']+nx*2300,p['y_cm']+ny*2300,p['z_cm']
mesh('CampDeck',(cx,cy,cz-5),(18,18,0.2),strata)
for side in (-1,1):
    mesh('TentRoof_%d' % side,(cx,cy+side*125,cz+145),(4.8,3.6,0.08),canvas,
        rotation=u.Rotator(roll=side*40))
for offset in (-450,450):
    mesh('CampBench_%d' % offset,(cx+offset,cy,cz+45),(0.9,2.8,0.16),dark)
route_text('CampLabel','LOOKOUT CAMP\nREST & ENJOY THE VIEW',len(points)-1,
    offset=2300,height=350,size=70)
for obj in route['objectives']:
    p=obj['location_cm']
    marker=actors.spawn_actor_from_class(u.TextRenderActor,u.Vector(p['x'],p['y']+900,p['z']+400),u.Rotator(yaw=180))
    marker.set_actor_label('Objective_'+str(obj['id']))
    marker.text_render.set_text(obj['label'])
    marker.text_render.set_world_size(70)
if not levels.save_current_level():
    raise RuntimeError('Cannot save generated canyon map')
u.log('OVERLANDING_LEVEL_BUILT actors=%d route_segments=%d' % (len(actors.get_all_level_actors()),len(points)-1))
