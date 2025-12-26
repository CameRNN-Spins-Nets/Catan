import tkinter as tk
import math

class HexViewer3D:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Hexagonal Object Viewer")
        
        self.canvas = tk.Canvas(root, width=800, height=600, bg='black')
        self.canvas.pack()
        
        # Camera parameters
        self.cam_distance = 15
        self.cam_angle_x = 0.3
        self.cam_angle_y = 0.3
        
        # Mouse control
        self.last_x = 0
        self.last_y = 0
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        
        # Create hexagonal structure
        self.vertices = []
        self.faces = []
        self.create_hex_structure()
        
        self.render()
    
    def create_hex_structure(self):
        """Create a 3D structure made of hexagonal prisms"""
        # Create multiple hexagonal prisms arranged in a true honeycomb pattern
        # Honeycomb spacing: horizontal = 1.5 * radius, vertical = sqrt(3) * radius
        radius = 0.8
        density = 0.9
        h_spacing = density * radius
        v_spacing = math.sqrt(3) * density * radius
        
        positions = [
            # Center
            (0, 0, 0),
            # Ring 1 (6 hexagons around center)
            (2 * h_spacing, 0, 0),
            (h_spacing, v_spacing, 0),
            (-h_spacing, v_spacing, 0),
            (-2 * h_spacing, 0, 0),
            (-h_spacing, -v_spacing, 0),
            (h_spacing, -v_spacing, 0),
            # Ring 2 (partial - add a few more for visual interest)
            (4 * h_spacing, 0, 0),
            (3 * h_spacing, v_spacing, 0),
            (0, 2 * v_spacing, 0),
            (-3 * h_spacing, v_spacing, 0),
            (-4 * h_spacing, 0, 0),
            (0, -2 * v_spacing, 0),
        ]
        
        for px, py, pz in positions:
            self.add_hexagonal_prism(px, py, pz, radius, 2)
    
    def add_hexagonal_prism(self, cx, cy, cz, radius, height):
        """Add a hexagonal prism to the structure"""
        base_idx = len(self.vertices)
        
        # Create vertices for top and bottom hexagons
        rotation_offset = math.pi / 2  # 90 degrees counterclockwise rotation
        for layer in [0, 1]:
            z = cz + (layer - 0.5) * height
            for i in range(6):
                angle = i * math.pi / 3 + rotation_offset
                x = cx + radius * math.cos(angle)
                y = cy + radius * math.sin(angle)
                self.vertices.append([x, y, z])
        
        # Create faces
        # Top face
        self.faces.append([base_idx + i for i in range(6)])
        
        # Bottom face
        self.faces.append([base_idx + 6 + i for i in range(6)])
        
        # Side faces
        for i in range(6):
            next_i = (i + 1) % 6
            face = [
                base_idx + i,
                base_idx + next_i,
                base_idx + 6 + next_i,
                base_idx + 6 + i
            ]
            self.faces.append(face)
    
    def project_3d_to_2d(self, x, y, z):
        """Project 3D coordinates to 2D screen space"""
        # Rotate around Y axis
        x_rot = x * math.cos(self.cam_angle_y) - z * math.sin(self.cam_angle_y)
        z_rot = x * math.sin(self.cam_angle_y) + z * math.cos(self.cam_angle_y)
        
        # Rotate around X axis
        y_rot = y * math.cos(self.cam_angle_x) - z_rot * math.sin(self.cam_angle_x)
        z_final = y * math.sin(self.cam_angle_x) + z_rot * math.cos(self.cam_angle_x)
        
        # Apply perspective projection
        factor = self.cam_distance / (self.cam_distance + z_final)
        screen_x = 400 + x_rot * factor * 60
        screen_y = 300 - y_rot * factor * 60
        
        return screen_x, screen_y, z_final
    
    def render(self):
        """Render the 3D scene"""
        self.canvas.delete('all')
        
        # Project all vertices
        projected = []
        for v in self.vertices:
            x, y, z = self.project_3d_to_2d(v[0], v[1], v[2])
            projected.append((x, y, z))
        
        # Sort faces by average depth (painter's algorithm)
        face_depths = []
        for face in self.faces:
            avg_z = sum(projected[i][2] for i in face) / len(face)
            face_depths.append((avg_z, face))
        
        face_depths.sort(reverse=True)
        
        # Draw faces
        for depth, face in face_depths:
            points = []
            for i in face:
                points.extend([projected[i][0], projected[i][1]])
            
            # Color based on depth
            brightness = int(128 + 127 * (depth / 20))
            brightness = max(30, min(255, brightness))
            color = f'#{brightness//2:02x}{brightness//3:02x}{brightness:02x}'
            
            self.canvas.create_polygon(points, fill=color, outline='#00ffff', width=1)
    
    def on_mouse_down(self, event):
        """Record mouse position on click"""
        self.last_x = event.x
        self.last_y = event.y
    
    def on_mouse_drag(self, event):
        """Update camera angles based on mouse drag"""
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        self.cam_angle_y += dx * 0.01
        self.cam_angle_x -= dy * 0.01  # Inverted for intuitive vertical movement
        
        # Clamp X rotation to avoid gimbal lock
        self.cam_angle_x = max(-math.pi/2 + 0.1, min(math.pi/2 - 0.1, self.cam_angle_x))
        
        self.last_x = event.x
        self.last_y = event.y
        
        self.render()

if __name__ == '__main__':
    root = tk.Tk()
    app = HexViewer3D(root)
    root.mainloop()