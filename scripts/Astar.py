import bpy
import random
from mathutils import Vector
import math


class Graph:

    def __init__(self, adjacency_list, node_coordinates):
        self.adjacency_list = adjacency_list
        self.node_coordinates = node_coordinates

    def get_neighbors(self, v):
        return self.adjacency_list[v]

    def euclidean_distance(self, node1, node2):
        coord1 = self.node_coordinates[node1]
        coord2 = self.node_coordinates[node2]
        distance = math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2 + (coord1[2] - coord2[2]) ** 2)
        return distance

    def h(self, n, goal_node):
        coord_n = self.node_coordinates[n]
        coord_goal = self.node_coordinates[goal_node]
        distance = math.sqrt(
            (coord_n[0] - coord_goal[0]) ** 2 + (coord_n[1] - coord_goal[1]) ** 2 + (coord_n[2] - coord_goal[2]) ** 2)
        return distance

    def a_star_algorithm(self, start_node, stop_node):
        open_list = set([start_node])
        closed_list = set([])
        g = {}
        g[start_node] = 0
        parents = {}
        parents[start_node] = start_node

        while len(open_list) > 0:
            n = None
            for v in open_list:
                if n == None or g[v] + self.h(v, stop_node) < g[n] + self.h(n, stop_node):
                    n = v;

            if n == None:
                print('Path does not exist!')
                return None

            if n == stop_node:
                reconst_path = []
                while parents[n] != n:
                    reconst_path.append(n)
                    n = parents[n]

                reconst_path.append(start_node)
                reconst_path.reverse()
                print('Path found: {}'.format(reconst_path))
                return reconst_path

            for (m, weight) in self.get_neighbors(n):
                if m not in open_list and m not in closed_list:
                    open_list.add(m)
                    parents[m] = n
                    g[m] = g[n] + weight

                else:
                    if g[m] > g[n] + weight:
                        g[m] = g[n] + weight
                        parents[m] = n

                        if m in closed_list:
                            closed_list.remove(m)
                            open_list.add(m)

            open_list.remove(n)
            closed_list.add(n)

        print('Path does not exist!')
        return None


def read_coordinates_from_file(file_path):
    coordinates_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip().strip('[').strip(']')
            node_info = line.split(', ')
            node_number = int(node_info[0])
            coordinates = [float(coord) for coord in node_info[1:]]
            coordinates_dict[node_number] = coordinates
    return coordinates_dict


def read_adjacency_list_from_file(file_path):
    adjacency_list = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split(':')
            node = int(parts[0])
            connections = eval(parts[1])
            for neighbor, weight in connections:
                if node not in adjacency_list:
                    adjacency_list[node] = []
                adjacency_list[node].append((neighbor, weight))
                if neighbor not in adjacency_list:
                    adjacency_list[neighbor] = []
                adjacency_list[neighbor].append((node, weight))
    return adjacency_list


def create_edge_between_nodes(start_point, end_point, radius=0.01, material_name="Edge"):
    direction = end_point - start_point
    midpoint = (start_point + end_point) / 2
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=direction.length,
        location=midpoint
    )
    cylinder_object = bpy.context.active_object
    cylinder_object.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    material = bpy.data.materials.get(material_name)
    if not material:
        material = bpy.data.materials.new(name=material_name)
    if cylinder_object.data.materials:
        cylinder_object.data.materials[0] = material
    else:
        cylinder_object.data.materials.append(material)


def read_node_coordinates(file_path):
    node_coordinates = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().strip('[]').split(', ')
            node_number = int(parts[0])
            coordinates = [float(coord) for coord in parts[1:]]
            node_coordinates[node_number] = coordinates
    return node_coordinates


def create_icosphere(location, material_name="Point"):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=0.5, location=location)
    icosphere = bpy.context.object
    material = bpy.data.materials.get(material_name)
    if not material:
        material = bpy.data.materials.new(name=material_name)
    icosphere.data.materials.append(material)
    return icosphere


# Delete existing Icospheres with material "Point"
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and obj.data.materials and obj.data.materials[0].name == "Point":
        bpy.data.objects.remove(obj, do_unlink=True)

# Delete existing cylinders with material "Result"
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and obj.data.materials and obj.data.materials[0].name == "Result":
        bpy.data.objects.remove(obj, do_unlink=True)

# Read icosphere coordinates from file
ico_coordinates_file_path = "data/icosphere_coordinates.txt"
node_coordinates = read_coordinates_from_file(ico_coordinates_file_path)

# Read adjacency list from file
adjacency_list_file_path = "data/adjacency_list.txt"
adjacency_list = read_adjacency_list_from_file(adjacency_list_file_path)

# Initialize the graph
graph1 = Graph(adjacency_list, node_coordinates)

# Execute the A* algorithm
start_node = 13
end_node = 19
result_path = graph1.a_star_algorithm(start_node, end_node)

edges = [(result_path[i], result_path[i + 1]) for i in range(len(result_path) - 1)]

# Print the list of edges
print("Edges representing the path:")
print(edges)

coordinates_array = read_node_coordinates('data/icosphere_coordinates.txt')

# Create edges between nodes
for start_index, end_index in edges:
    start_point = Vector(coordinates_array[int(start_index)])
    end_point = Vector(coordinates_array[int(end_index)])
    create_edge_between_nodes(start_point, end_point, material_name="Result", radius=0.2)

# Create Icospheres at start and end nodes
start_coordinates = Vector(node_coordinates[start_node])
end_coordinates = Vector(node_coordinates[end_node])
create_icosphere(start_coordinates, material_name="Point")
create_icosphere(end_coordinates, material_name="Point")
