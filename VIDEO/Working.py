import bpy
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import STL file
bpy.ops.import_mesh.stl(filepath='/Users/jorgemuyo/Desktop/Challenge/ZOOCAD.stl')

# Assuming the imported STL file becomes the active object, we rename it for consistency
imported_objects = bpy.context.selected_objects
if imported_objects:
    obj = imported_objects[0]
    obj.name = "ImportedSTL"

    # Define the target bounding box dimensions for a 10x10x10 volume
    target_dimensions = Vector((10.0, 10.0, 10.0))

    # Calculate the current bounding box dimensions of the object
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

    # Add top light pointing down
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 10))
    top_light = bpy.context.object
    top_light.data.energy = 1000  # Adjust light intensity as needed

    # Add backlight pointing towards the object
    bpy.ops.object.light_add(type='POINT', location=(0, -10, 5))
    back_light = bpy.context.object
    back_light.data.energy = 500  # Adjust light intensity as needed
    back_light.rotation_euler = (0.785398, 0, 0)  # Pointing towards the object, adjust angle as needed

    # Ensure the object for animation is correctly selected and active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Set the frame where the animation starts
    bpy.context.scene.frame_start = 1
    start_frame = 1
    # Set the frame where the animation ends
    bpy.context.scene.frame_end = 250
    end_frame = 250

    # Insert the first keyframe (rotation = 0 degrees around Z-axis)
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)

    # Insert the second keyframe (rotation = 360 degrees around Z-axis)
    obj.rotation_euler = (0, 0, 3.14159 * 2)  # 2*pi radians = 360 degrees
    obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)

    # Change F-curve interpolation to BEZIER
    fcurves = obj.animation_data.action.fcurves
    for fcurve in fcurves:
        for keyframe_point in fcurve.keyframe_points:
            keyframe_point.interpolation = 'BEZIER'
else:
    print("ImportedSTL object not found")

# Adding a camera to the scene
bpy.ops.object.camera_add(location=(10, -10, 10))
camera = bpy.context.object
camera.data.lens = 35

# Point the camera towards the object's center
camera.location = (10, -10, 10)
camera.rotation_euler = (0.785398, 0, 0.785398)

# Set the camera as the active camera
bpy.context.scene.camera = camera

# Rendering setup
bpy.context.scene.render.filepath = "/Users/jorgemuyo/Desktop/Challenge/rendered_blender_video.mp4"
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
bpy.context.scene.render.resolution_x = 500
bpy.context.scene.render.resolution_y = 500
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.fps = 24

bpy.ops.render.render(animation=True)