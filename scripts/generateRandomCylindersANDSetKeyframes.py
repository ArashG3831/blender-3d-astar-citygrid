import random, math, bpy
from mathutils import Vector

# Get the list of objects with the specified name pattern
object_prefix = "Icosphere"
selected_objects = [obj for obj in bpy.context.scene.objects if obj.name.startswith(object_prefix)]

# Initialize a dictionary to store object coordinates
coordinates_dict = {}

# Iterate through the selected objects
for obj in selected_objects:
    # Get the index of the object
    index = int(obj.name.split(".")[-1])
    # Get the coordinates of the object and store them in the dictionary
    coordinates_dict[index] = [coord for coord in obj.location]

# Sort the dictionary by keys to maintain the order
coordinates_array = [coordinates_dict[key] for key in sorted(coordinates_dict.keys())]

# Print the coordinates array
print("Coordinates Array:")
for coordinates in coordinates_array:
    print(coordinates)


# Function to create a cylinder between two points without animation
def create_edge_between_nodes(start_point, end_point, radius=0.03, material_name="Edge"):
    # Calculate the direction vector from start to end
    direction = end_point - start_point
    # Calculate the midpoint between start and end
    midpoint = (start_point + end_point) / 2

    # Create the cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=direction.length,
        location=midpoint
    )

    # Retrieve the active object (the newly created cylinder)
    cylinder_object = bpy.context.active_object

    # Ensure the newly created object is selected
    bpy.context.view_layer.objects.active = cylinder_object
    cylinder_object.select_set(True)

    # Set the rotation of the cylinder to align with the direction vector
    cylinder_object.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

    # Check if the material already exists
    material = bpy.data.materials.get(material_name)

    if not material:
        # Create a new material if it doesn't exist
        material = bpy.data.materials.new(name=material_name)

    # Assign the material to the cylinder
    if cylinder_object.data.materials:
        # Use the existing material slot if available
        cylinder_object.data.materials[0] = material
    else:
        # Otherwise, add a new material slot
        cylinder_object.data.materials.append(material)


# Create cylinders between selected nodes without animation

# Function to generate random connections between nodes
def generate_specific_random_list(size):
    # Add additional random repetitions
    additional_elements = random.choices(range(size), k=random.randint(0, size))

    # Combine the lists
    result_list = additional_elements

    # Generate the rest of the pairs with the second element different from the first
    random_list = [(first, random.choice([x for x in range(size) if x != first])) for first in result_list]

    # Add connections between consecutive nodes
    consecutive_connections = [(i, i + 1) for i in range(size - 1)]

    # Combine the random list and consecutive connections
    node_indices_to_connect = list(set(random_list + consecutive_connections))

    return node_indices_to_connect


# Generate random connections
node_indices_to_connect = generate_specific_random_list(len(coordinates_array))
print("node_indices_to_connect:\n", node_indices_to_connect)

for start_index, end_index in node_indices_to_connect:
    start_point = Vector(coordinates_array[int(start_index)])
    end_point = Vector(coordinates_array[int(end_index)])
    create_edge_between_nodes(start_point, end_point, material_name="Edge", radius=0.03)


# Calculate Euclidean distance between two nodes
def euclidean_distance(coord1, coord2):
    return (sum((c1 - c2) ** 2 for c1, c2 in zip(coord1, coord2))) ** (1 / 3)


# Read node coordinates from the file
def read_node_coordinates(file_path):
    node_coordinates = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().strip('[]').split(', ')
            node_number = int(parts[0])
            coordinates = [float(coord) for coord in parts[1:]]
            node_coordinates[node_number] = coordinates
    return node_coordinates


# Read node coordinates
node_coordinates = read_node_coordinates('data/icosphere_coordinates.txt')

# Expand the list to include the weight of each edge (Euclidean distance)
expanded_node_indices_to_connect = []
for start_index, end_index in node_indices_to_connect:
    start_coord = node_coordinates[start_index]
    end_coord = node_coordinates[end_index]
    distance = euclidean_distance(start_coord, end_coord)
    distance_rounded = round(distance, 2)  # Round to two decimals
    expanded_node_indices_to_connect.append((start_index, end_index, distance_rounded))

# Print the expanded list
print("expanded_node_indices_to_connect:\n", expanded_node_indices_to_connect)


def edges_to_adjacency_list(edges):
    adjacency_list = {}
    for edge in edges:
        source, target, weight = edge
        if source not in adjacency_list:
            adjacency_list[source] = []
        adjacency_list[source].append((target, weight))
    return adjacency_list


adjacency_list = edges_to_adjacency_list(expanded_node_indices_to_connect)
print(adjacency_list)

# Write adjacency list to a text file with rounded weights
adjacency_list_file_path = "data/adjacency_list.txt"
with open(adjacency_list_file_path, 'w') as file:
    for node, connections in adjacency_list.items():
        rounded_connections = [(conn[0], round(conn[1], 2)) for conn in connections]
        file.write(f"{node}: {rounded_connections}\n")

frame_start = 200

# Set the animation frame
bpy.context.scene.frame_set(frame_start)

# Iterate through all objects in the scene
for obj in bpy.context.scene.objects:
    # Check if the object's name starts with "Cylinder"
    if obj.name.startswith("Cylinder"):
        z_value = original_z = obj.location.z + 25
        # Set Z-coordinate to 0 at frame_start
        obj.location.z = z_value
        # Insert keyframe at frame_start
        obj.keyframe_insert(data_path="location", index=2)  # Index 2 corresponds to the Z-coordinate

frame_end = 272

# Set the animation frame
bpy.context.scene.frame_set(frame_end)

# Iterate through all objects in the scene
for obj in bpy.context.scene.objects:
    # Check if the object's name starts with "Cylinder"
    if obj.name.startswith("Cylinder"):
        z_value = original_z = obj.location.z - 25
        # Set Z-coordinate to 0 at frame_start
        obj.location.z = z_value
        # Insert keyframe at frame_start
        obj.keyframe_insert(data_path="location", index=2)  # Index 2 corresponds to the Z-coordinate

