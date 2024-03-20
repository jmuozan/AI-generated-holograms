import bpy
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import STL file
bpy.ops.import_mesh.stl(filepath='/Users/jorgemuyo/Desktop/Challenge/ZOOCAD.stl')  

imported_objects = bpy.context.selected_objects
if imported_objects:
    obj = imported_objects[0]
    obj.name = "ImportedSTL"

    # Define the target bounding box dimensions
    target_dimensions = Vector((10.0, 10.0, 10.0))

    # Calculate the current bounding box dimensions
    obj_dimensions = obj.dimensions
    scale_factors = Vector((target_dimensions.x / obj_dimensions.x if obj_dimensions.x else 1,
                            target_dimensions.y / obj_dimensions.y if obj_dimensions.y else 1,
                            target_dimensions.z / obj_dimensions.z if obj_dimensions.z else 1))

    uniform_scale_factor = min(scale_factors)
    obj.scale *= Vector((uniform_scale_factor, uniform_scale_factor, uniform_scale_factor))

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bbox_center = sum((Vector(b) for b in obj.bound_box), Vector()) / 8
    obj.location = -bbox_center

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)  # Move object to world origin

    # Lights
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 10))
    top_light = bpy.context.object
    top_light.data.energy = 2000

    bpy.ops.object.light_add(type='POINT', location=(0, -10, 5))
    back_light = bpy.context.object
    back_light.data.energy = 1000  
    back_light.rotation_euler = (0.785398, 0, 0)  

    # Animation
    bpy.context.scene.frame_start = 1
    start_frame = 1
    bpy.context.scene.frame_end = 250
    end_frame = 250

    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)
    obj.rotation_euler = (0, 0, 3.14159 * 2)  # Radians
    obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)

    fcurves = obj.animation_data.action.fcurves
    for fcurve in fcurves:
        for keyframe_point in fcurve.keyframe_points:
            keyframe_point.interpolation = 'BEZIER'

    # Material
    material = bpy.data.materials.new(name="ProceduralMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear() 

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    texture_node = nodes.new(type='ShaderNodeTexNoise')
    colorramp_node = nodes.new(type='ShaderNodeValToRGB')

    colorramp_node.color_ramp.elements[0].color = (1, 0, 0, 1)  # Red
    colorramp_node.color_ramp.elements[1].color = (0, 0, 1, 1)  # Blue

    material.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    material.node_tree.links.new(texture_node.outputs['Fac'], colorramp_node.inputs['Fac'])
    material.node_tree.links.new(colorramp_node.outputs['Color'], bsdf_node.inputs['Base Color'])

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

    texture_node.inputs['Scale'].default_value = 5.0
    texture_node.inputs['Scale'].keyframe_insert(data_path="default_value", frame=start_frame)

    texture_node.inputs['Scale'].default_value = 25.0
    texture_node.inputs['Scale'].keyframe_insert(data_path="default_value", frame=end_frame)

    # Camera
    bpy.ops.object.camera_add(location=(10, -10, 10))
    camera = bpy.context.object
    camera.data.lens = 35
    camera.location = (10, -10, 10)
    camera.rotation_euler = (0.785398, 0, 0.785398)
    bpy.context.scene.camera = camera
    
    # Transparent background
    bpy.context.scene.render.film_transparent = True

    # Rendering
    bpy.context.scene.render.filepath = '/Users/jorgemuyo/Desktop/Challenge/rendered_blender_video.mp4' 
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    bpy.context.scene.render.resolution_x = 2500
    bpy.context.scene.render.resolution_y = 2500
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.fps = 24

    bpy.ops.render.render(animation=True)
