"""Split the acquired glTF into a forward-X body and four centered wheels.

Uses only Python's standard library. Run outside Unreal before setup_4runner.py.
The generated glTFs retain the source materials and creator/license metadata.
"""
import copy
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / '.tools/assets/4runner'
OUT = SOURCE / 'prepared'
IDENTITY = [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]

def multiply(a, b):
    return [sum(a[k*4+r]*b[c*4+k] for k in range(4))
            for c in range(4) for r in range(4)]

def prepare():
    doc = json.loads((SOURCE/'scene.gltf').read_text())
    data = (SOURCE/doc['buffers'][0]['uri']).read_bytes()
    transforms = {}
    def walk(index, parent):
        node = doc['nodes'][index]
        matrix = multiply(parent, node.get('matrix', IDENTITY))
        if 'mesh' in node:
            transforms[node['mesh']] = matrix
        for child in node.get('children', []):
            walk(child, matrix)
    for index in doc['scenes'][doc.get('scene',0)]['nodes']:
        walk(index, IDENTITY)
    def read(index):
        accessor = doc['accessors'][index]
        view = doc['bufferViews'][accessor['bufferView']]
        fmt = {5126:'f',5125:'I',5123:'H',5121:'B'}[accessor['componentType']]
        size = {'SCALAR':1,'VEC2':2,'VEC3':3}[accessor['type']]
        stride = view.get('byteStride',struct.calcsize(fmt)*size)
        start = view.get('byteOffset',0)+accessor.get('byteOffset',0)
        return [struct.unpack_from('<'+fmt*size,data,start+i*stride)
                for i in range(accessor['count'])]
    def position(v, m):
        # glTF is Y-up. Export local glTF X=source Z, Z=-source X;
        # Unreal imports this as forward X, right Y, up Z (centimeters).
        p = [sum(m[k*4+r]*v[k] for k in range(3))+m[12+r] for r in range(3)]
        return (p[2],p[1],-p[0])
    groups = {key:[] for key in ('Body','FL','FR','RL','RR')}
    wheel_positions = {key:[] for key in ('FL','FR','RL','RR')}
    def corner(p):
        return ('F' if p[0]>0.2 else 'R')+('R' if p[2]>0 else 'L')
    for mesh_index, mesh in enumerate(doc['meshes']):
        matrix = transforms[mesh_index]
        for primitive in mesh['primitives']:
            attrs = primitive['attributes']
            positions = [position(v,matrix) for v in read(attrs['POSITION'])]
            normals = []
            for n in read(attrs['NORMAL']):
                # Source transforms are diagonal scale plus translation.
                v = (n[2]/matrix[10],n[1]/matrix[5],-n[0]/matrix[0])
                length = math.sqrt(sum(x*x for x in v)) or 1
                normals.append(tuple(x/length for x in v))
            uv = read(attrs['TEXCOORD_0'])
            indices = [v[0] for v in read(primitive['indices'])]
            buckets = {key:[] for key in groups}
            for offset in range(0,len(indices),3):
                triangle = indices[offset:offset+3]
                corners = {corner(positions[i]) for i in triangle}
                # Object_15 is the fixed axle/undercarriage, spanning wheel
                # centers. It must stay on the chassis rather than rotate.
                fixed_axle = mesh_index>=9 and any(abs(positions[i][2])<.65 for i in triangle)
                key = 'Body' if mesh_index<9 or mesh_index==15 or fixed_axle or len(corners)!=1 else corners.pop()
                buckets[key].extend(triangle)
                if mesh_index in (9,10,11,12) and key!='Body':
                    wheel_positions[key].extend(positions[i] for i in triangle)
            for key, selected in buckets.items():
                if selected:
                    groups[key].append((positions,normals,uv,selected,primitive['material']))
    centers = {}
    for key, points in wheel_positions.items():
        if not points:
            raise RuntimeError('Missing tire geometry: '+key)
        centers[key] = tuple((min(p[i] for p in points)+max(p[i] for p in points))/2
                             for i in range(3))
    OUT.mkdir(parents=True,exist_ok=True)
    report = {'wheel_centers_cm':{},'triangles':{}}
    for key, primitives in groups.items():
        output = {'asset':copy.deepcopy(doc['asset']), 'materials':copy.deepcopy(doc['materials']),
                  'buffers':[], 'bufferViews':[], 'accessors':[], 'meshes':[],
                  'nodes':[{'name':'FourRunner_'+key,'mesh':0}],
                  'scenes':[{'nodes':[0]}], 'scene':0}
        binary = bytearray()
        def append(values, kind, fmt, component):
            while len(binary)%4: binary.append(0)
            start = len(binary)
            for value in values:
                binary.extend(struct.pack('<'+fmt*len(value),*value))
            view = len(output['bufferViews'])
            output['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':len(binary)-start})
            accessor = {'bufferView':view,'componentType':component,'count':len(values),'type':kind}
            if kind=='VEC3':
                accessor['min']=[min(v[i] for v in values) for i in range(3)]
                accessor['max']=[max(v[i] for v in values) for i in range(3)]
            output['accessors'].append(accessor)
            return len(output['accessors'])-1
        exported = []
        center = centers.get(key,(0,0,0))
        triangles = 0
        for positions,normals,uv,selected,material in primitives:
            used = sorted(set(selected))
            remap = {old:new for new,old in enumerate(used)}
            vertices = [tuple(positions[i][axis]-center[axis] for axis in range(3)) for i in used]
            exported.append({'attributes':{'POSITION':append(vertices,'VEC3','f',5126),
                                          'NORMAL':append([normals[i] for i in used],'VEC3','f',5126),
                                          'TEXCOORD_0':append([uv[i] for i in used],'VEC2','f',5126)},
                             'indices':append([(remap[i],) for i in selected],'SCALAR','I',5125),
                             'material':material})
            triangles += len(selected)//3
        name = 'FourRunner_'+key
        output['meshes']=[{'name':name,'primitives':exported}]
        output['buffers']=[{'uri':name+'.bin','byteLength':len(binary)}]
        (OUT/(name+'.bin')).write_bytes(binary)
        (OUT/(name+'.gltf')).write_text(json.dumps(output))
        report['triangles'][key]=triangles
        if key!='Body':
            report['wheel_centers_cm'][key]=[center[0]*100,center[2]*100,center[1]*100]
    (OUT/'setup.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    prepare()
