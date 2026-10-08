"""Generate a continuous, upward-facing road ribbon in Unreal centimeters."""
import math

def write_trail_obj(points, destination, half_width=650.0):
    if len(points) < 2:
        raise ValueError('At least two route samples are required')
    rows = []
    # Legacy OBJ import uses Z-up and flips the right-handed Y axis.
    for i, p in enumerate(points):
        before, after = points[max(0,i-1)], points[min(len(points)-1,i+1)]
        dx, dy = after['x_cm']-before['x_cm'], after['y_cm']-before['y_cm']
        length = math.hypot(dx, dy)
        if length == 0:
            raise ValueError('Route tangent must not be zero')
        nx, ny = -dy/length, dx/length
        for offset in (-half_width, half_width):
            x, y, z = p['x_cm']+nx*offset, p['y_cm']+ny*offset, p['z_cm']
            rows.append('v %.6f %.6f %.6f' % (x,-y,z))
    rows += ['vt %f %f' % (i/10,side) for i in range(len(points)) for side in (0,1)]
    for i in range(len(points)-1):
        a,b,c,d = 2*i+1,2*i+2,2*i+3,2*i+4
        rows += ['f %d/%d %d/%d %d/%d' % (a,a,b,b,c,c), 'f %d/%d %d/%d %d/%d' % (b,b,d,d,c,c)]
    destination.write_text('\n'.join(rows)+'\n')
    return 2*(len(points)-1)
