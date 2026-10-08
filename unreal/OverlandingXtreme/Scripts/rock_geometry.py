"""Deterministic layered sandstone mesh; no external asset dependencies."""
import math
import random

def write_rock_obj(destination):
    rng = random.Random(421)
    sides, rings = 18, 9
    rows = []
    profile = [0.78, 1.0, 0.96, 0.88, 0.95, 0.78, 0.69, 0.55, 0.28]
    for j in range(rings):
        for i in range(sides):
            angle = i*2*math.pi/sides
            radius = profile[j]*(1+rng.uniform(-0.13,0.13))*50
            x = math.cos(angle)*radius + 6*math.sin(j*.7)
            y = math.sin(angle)*radius
            z = -50+j*100/(rings-1)+rng.uniform(-2,2)
            rows.append('v %.5f %.5f %.5f' % (x,-y,z))
    # Flip winding alongside OBJ's Y conversion, keeping outward normals.
    for j in range(rings-1):
        for i in range(sides):
            a=j*sides+i+1; b=j*sides+(i+1)%sides+1
            c=a+sides; d=b+sides
            rows.extend(['f %d %d %d' % (a,c,b),'f %d %d %d' % (b,c,d)])
    rows.append('f '+' '.join(str(i+1) for i in range(sides)))
    rows.append('f '+' '.join(str((rings-1)*sides+i+1) for i in reversed(range(sides))))
    write_obj_with_uv(destination, rows)

def write_shrub_obj(destination):
    """Clustered evergreen foliage silhouette, centered at ground level."""
    rng = random.Random(88)
    rows, faces, count = [], [], 0
    for cluster in range(14):
        angle = cluster*2.399
        reach = rng.uniform(10,38)
        cx,cy,cz = math.cos(angle)*reach,math.sin(angle)*reach,rng.uniform(18,55)
        radius = rng.uniform(14,25)
        base = count
        for ring in range(7):
            latitude = -math.pi/2+ring*math.pi/6
            for side in range(10):
                a = side*math.pi/5
                x = cx+radius*math.cos(latitude)*math.cos(a)
                y = cy+radius*math.cos(latitude)*math.sin(a)
                z = cz+radius*.85*math.sin(latitude)
                rows.append('v %.4f %.4f %.4f' % (x,-y,z))
                count += 1
        for ring in range(6):
            for side in range(10):
                a=base+ring*10+side+1; b=base+ring*10+(side+1)%10+1
                c=a+10; d=b+10
                faces.extend(['f %d %d %d' % (a,c,b),'f %d %d %d' % (b,c,d)])
    write_obj_with_uv(destination, rows+faces)


def write_obj_with_uv(destination, rows):
    vertices = [row for row in rows if row.startswith('v ')]
    uv = ['vt %.6f %.6f' % (float(row.split()[1])/100, float(row.split()[3])/100) for row in vertices]
    faces = ['f '+' '.join(index+'/'+index for index in row.split()[1:]) for row in rows if row.startswith('f ')]
    destination.write_text('\n'.join(vertices+uv+faces)+'\n')
