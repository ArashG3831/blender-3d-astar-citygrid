import bpy
import random

def create_icosphere(location, scale, material):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=scale, location=location)
    icosphere = bpy.context.object
    icosphere.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return icosphere

def animate_icosphere(icosphere, frame_start, frame_end, z_value):
    # Set the animation frame for setting Z value
    bpy.context.scene.frame_set(frame_start)
    # Set Z-coordinate to the desired value at frame_start
    icosphere.location.z = z_value
    # Insert keyframe at frame_start
    icosphere.keyframe_insert(data_path="location", index=2)  # Index 2 corresponds to the Z-coordinate

    # Set the animation frame for setting random Z value
    bpy.context.scene.frame_set(frame_end)
    # Set random Z-coordinate at frame_end within the range
    random_z = round(random.uniform(*z_range), 2)
    icosphere.location.z = random_z
    # Insert keyframe at frame_end
    icosphere.keyframe_insert(data_path="location", index=2)  # Index 2 corresponds to the Z-coordinate

# Clear existing objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Create material if not exists
material_name = "BrightLight"
material = bpy.data.materials.get(material_name)
if material is None:
    material = bpy.data.materials.new(name=material_name)
    material.diffuse_color = (1, 1, 1)  # White color

# Parameters
num_icospheres = 20  # Number of Icospheres to generate
scale = 0.072  # Scale of Icospheres

# Generate Icospheres and animate
z_range = (0.5, 3)  # Range for random Z-coordinate
frame_start = 48  # Start frame for setting Z to 0
frame_end = 144  # End frame for setting random Z

# Generate Icospheres and animate
for _ in range(num_icospheres):
    location = (
        random.uniform(-num_icospheres / 2, num_icospheres / 2),
        random.uniform(-num_icospheres / 2, num_icospheres / 2),
        round(random.uniform(0, 2), 2)
    )
    icosphere = create_icosphere(location, scale, material)
    animate_icosphere(icosphere, frame_start, frame_end, 0)

# Get the list of objects with the specified name pattern
object_prefix = "Icosphere"
selected_objects = [obj for obj in bpy.context.scene.objects if obj.name.startswith(object_prefix)]
# Rename the remaining Icosphere to "Icosphere.000"
for obj in bpy.context.scene.objects:
    if obj.name == "Icosphere":
        obj.name = "Icosphere.000"

# Initialize a 3D array to store rounded XYZ coordinates
coordinates_array = []

# Iterate through the selected objects
for obj in selected_objects:
    # Round the XYZ coordinates to two decimal places
    rounded_coordinates = [round(coord, 2) for coord in obj.location]

    # Extract the icosphere number as an integer
    object_number = int(obj.name.split(".")[-1])  # Extracting the object number as int

    # Append the rounded coordinates to the array along with the object number
    coordinates_array.append([object_number] + rounded_coordinates)

# Define the file path
file_path = bpy.path.abspath("//data/icosphere_coordinates.txt")

# Write coordinates to the text file
with open(file_path, 'w') as file:
    for coordinates in coordinates_array:
        file.write(str(coordinates) + '\n')

print("Coordinates written to:", file_path)

