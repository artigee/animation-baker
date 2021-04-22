import bpy
import bmesh
import numpy
import math
import mathutils

TEXTURE_SIZE = 128
TEXTURE_NAME = "animation"
keyframes = numpy.arange(1, 43)

pixelData = [1.0] * TEXTURE_SIZE * TEXTURE_SIZE

def main():
    setup_model_UV()
    prepare_image()
    keyframe_cycle()
    fill_image()
    
    print("DONE!")

def setup_model_UV():
    global frame_width
    bpy.ops.object.mode_set(mode='EDIT')
    
    me = bpy.context.edit_object.data
    bm = bmesh.from_edit_mesh(me)
    
    if len(me.uv_layers) < 2:
        me.uv_layers.new(name = 'UVMapAnimation')
    
    uv_layer = bm.loops.layers.uv.get('UVMapAnimation')
    uv_verts = {}

    for face in bm.faces:
        for loop in face.loops:
            if loop.vert not in uv_verts:
                uv_verts[loop.vert] = [loop[uv_layer]]
            else:
                uv_verts[loop.vert].append(loop[uv_layer])

    vert_count = len(uv_verts)
    frame_width = math.ceil(vert_count / TEXTURE_SIZE)
    
    for vert in uv_verts:
        for uv_loop in uv_verts[vert]:
            xs = math.floor(vert.index / TEXTURE_SIZE)
            ys = vert.index % TEXTURE_SIZE

            uv_loop.uv = mathutils.Vector((xs / TEXTURE_SIZE, ys / TEXTURE_SIZE))

    bmesh.update_edit_mesh(me, False, False)
    bpy.ops.object.mode_set(mode = 'OBJECT')


def prepare_image():
    global pixelData
    
    im = bpy.data.images.get(TEXTURE_NAME)
    if im is not None and im.size[0] != TEXTURE_SIZE:
        bpy.data.images.remove(im)
    
    im = bpy.data.images.get(TEXTURE_NAME)
    if im is None:
        bpy.data.images.new(TEXTURE_NAME, TEXTURE_SIZE, TEXTURE_SIZE, alpha=True)
    
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            pixelData[y * TEXTURE_SIZE + x] = [0.0, 0.0, 0.0, 168./255.]


def fill_image():
    global pixelData
    image = bpy.data.images[TEXTURE_NAME]
    pixelData = [chan for px in pixelData for chan in px]
    image.pixels = pixelData


def keyframe_cycle():
    wm = bpy.context.window_manager
    wm.progress_begin(0, len(keyframes))
    
    src_obj = bpy.context.active_object
    progress = 0
    
    vertices = src_obj.data.vertices
    verts = [src_obj.matrix_world @ vert.co for vert in vertices] 
    default_verts = [vert.to_tuple() for vert in verts]
    
    for kf in keyframes:
        bpy.context.scene.frame_set(kf)

        new_obj = src_obj.copy()
        new_obj.data = src_obj.data.copy()
        new_obj.animation_data_clear()
        bpy.context.collection.objects.link(new_obj)

        src_obj.select_set(False)
        new_obj.select_set(True)

        bpy.context.view_layer.objects.active = new_obj
        
        printPositions(new_obj, kf, default_verts)
        
        bpy.ops.object.delete()
        
        src_obj.select_set(True)
        bpy.context.view_layer.objects.active = src_obj
        
        progress += 1
        wm.progress_update(progress)
    wm.progress_end()

def get_scale(value):
    value = abs(value)
    return math.floor(value / 2)

def get_color(v_from, v_to):
        
    dv = numpy.subtract(v_from, v_to)
    w = max(get_scale(dv[0]), get_scale(dv[1]), get_scale(dv[2]))
    if w > 3:
        raise Exception(f" the scale is out of range")
        
    if w != 0:
        dv = numpy.multiply(dv, (2*w))
        
    int_dv = numpy.floor(dv)
    fract_dv = numpy.subtract(dv, int_dv)
    
    int_dv = numpy.add(int_dv, 2)
    alpha = int(int_dv[0]) << 6 | int(int_dv[1]) << 4 | int(int_dv[2]) << 2 | w
    
    return [fract_dv[0], fract_dv[1], fract_dv[2], alpha/255.]
    

def printPositions(obj, frame, default_verts):
    global pixelData
    global frame_width
    
    bpy.ops.object.modifier_apply(modifier = "Armature")
    
    vertices = obj.data.vertices
    verts = [obj.matrix_world @ vert.co for vert in vertices] 
    plain_verts = [vert.to_tuple() for vert in verts]
    
    nvert = 0
    for vert in plain_verts:
        color = get_color(default_verts[nvert], vert)
        
        xs = (frame - 1) * frame_width + math.floor(nvert / TEXTURE_SIZE)
        ys = (nvert % TEXTURE_SIZE)
        
        pixelData[ys * TEXTURE_SIZE + xs] = [color[0], color[1], color[2], color[3]]
        
        nvert = nvert + 1

if bpy.context.object.type == "MESH":
    if bpy.context.object.modifiers:
        main()
    else:
        print("select model with armature")

