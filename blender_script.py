import bpy
from mathutils import Vector


# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import STL file
bpy.ops.import_mesh.stl(filepath=r'/Users/jorgemuyo/Desktop/Challenge/ZOOCAD.stl')

# Assuming the imported STL file becomes the active object, we rename it for consistency
imported_objects = bpy.context.selected_objects
for obj in imported_objects:
    obj.name = "ImportedSTL"
cube = bpy.context.view_layer.objects.active
cube.name = "Cube"

# Scale the selected STL from its geometry center with a factor of 100
cube.scale = (20, 20, 20)
# Apply the scale to make the transformation permanent
bpy.ops.object.transform_apply(location=False, scale=True, rotation=False)

# Adjust object position based on the bounding box to align its geometric center with the world origin
local_bbox_center = 0.125 * sum((Vector(b) for b in cube.bound_box), Vector())
world_bbox_center = cube.matrix_world @ local_bbox_center
cube.location -= world_bbox_center

# Assign material to imported object
material = bpy.data.materials.new(name="AbstractMaterial")
cube.data.materials.append(material)

material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

shader = nodes.new(type='ShaderNodeBsdfPrincipled')
shader.location = 300, 0

noise_tex = nodes.new(type='ShaderNodeTexNoise')
noise_tex.location = -400, 0
noise_tex.inputs['Scale'].default_value = 5.0  
noise_tex.inputs['Detail'].default_value = 2.0  

color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.location = -200, 0
color_ramp.color_ramp.elements[0].color = (0, 0, 1, 1)  
color_ramp.color_ramp.elements[1].color = (1, 0, 0, 1)  

links.new(noise_tex.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], shader.inputs['Base Color'])
links.new(shader.outputs['BSDF'], nodes.new('ShaderNodeOutputMaterial').inputs['Surface'])

noise_tex.inputs['Scale'].keyframe_insert('default_value', frame=1)
noise_tex.inputs['Scale'].default_value = 25.0
noise_tex.inputs['Scale'].keyframe_insert('default_value', frame=250)

noise_tex.inputs['Detail'].keyframe_insert('default_value', frame=1)
noise_tex.inputs['Detail'].default_value = 16.0
noise_tex.inputs['Detail'].keyframe_insert('default_value', frame=250)

color_ramp.color_ramp.elements[0].keyframe_insert("position", frame=1)
color_ramp.color_ramp.elements[0].position = 0.8
color_ramp.color_ramp.elements[0].keyframe_insert("position", frame=250)

# Add rotation animation to the imported object
cube.rotation_euler = (0, 0, 0)
cube.keyframe_insert(data_path="rotation_euler", frame=1)
cube.rotation_euler = (0, 0, 3.14159 * 2)
cube.keyframe_insert(data_path="rotation_euler", frame=250)

# Camera setup with adjusted location
bpy.ops.object.camera_add(location=(50, -50, 25), rotation=(1.1, 0, 0.785))
camera = bpy.context.object
camera.name = "Camera"
# Uncomment and adjust the line below if you need to change the camera's focal length
# camera.data.lens = 50
bpy.context.scene.camera = camera

# Lighting setup
bpy.ops.object.light_add(type='AREA', location=(4, -4, 5))
key_light = bpy.context.object
key_light.data.energy = 1000
key_light.data.size = 3
key_light.name = "KeyLight"

bpy.ops.object.light_add(type='AREA', location=(-4, 4, 5))
fill_light = bpy.context.object
fill_light.data.energy = 500
fill_light.data.size = 3
fill_light.name = "FillLight"

bpy.ops.object.light_add(type='AREA', location=(0, -6, 5))
back_light = bpy.context.object
back_light.data.energy = 700
back_light.data.size = 3
back_light.name = "BackLight"

# Render settings and render
bpy.context.scene.render.filepath = "/Users/jorgemuyo/Desktop/Challenge/rendered_blender_video.avi"
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'AVI'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.fps = 24

bpy.ops.render.render(animation=True)
