import tkinter as tk
import math
from PIL import Image, ImageTk, ImageDraw
import random

img_path = './static/images/'

images = ['forest.jpg', 'bricks.jpg', 'field.jpg', 'quarry.jpg', 'sheep.jpg']

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
        
        # Load images
        try:
            self.images = [Image.open(img_path + img_label).convert('RGBA') for img_label in images]
            print("Images loaded successfully")
        except Exception as e:
            print(f"Error loading images: {e}")
            # Create placeholder images if files don't exist
            self.images = [Image.new('RGBA', (100, 100), color=color) for color in ['red', 'yellow', 'blue', 'green', 'black', 'white']]
        
        # Create hexagonal structure
        self.vertices = []
        self.faces = []
        self.face_textures = []  # Track which texture each face should use
        self.create_hex_structure()
        
        self.render()
    
    def create_hex_structure(self):
        """Create a 3D structure made of hexagonal prisms"""
        # Create multiple hexagonal prisms arranged in a true honeycomb pattern
        # Honeycomb spacing: horizontal = 1.5 * radius, vertical = sqrt(3) * radius
        radius = 0.8
        density = 0.9
        x_spacing = density * radius
        y_spacing = math.sqrt(3) * density * radius
        
        positions = [
            # Center
            (0, 0, 0),
            # Ring 1 (6 hexagons around center)
            (2 * x_spacing, 0, 0),
            (x_spacing, y_spacing, 0),
            (-x_spacing, y_spacing, 0),
            (-2 * x_spacing, 0, 0),
            (-x_spacing, -y_spacing, 0),
            (x_spacing, -y_spacing, 0),
            # Ring 2 (partial - add a few more for visual interest)
            (4 * x_spacing, 0, 0),
            (3 * x_spacing, y_spacing, 0),
            (3 * x_spacing, -y_spacing, 0),
            (0, 2 * y_spacing, 0),
            (2 * x_spacing, 2 * y_spacing, 0),
            (2 * x_spacing, -2 * y_spacing, 0),
            (-3 * x_spacing, y_spacing, 0),
            (-3 * x_spacing, -y_spacing, 0),
            (-4 * x_spacing, 0, 0),
            (0, -2 * y_spacing, 0),
            (-2 * x_spacing, -2 * y_spacing, 0),
            (-2 * x_spacing, 2 * y_spacing, 0)
        ]
        
        for idx, (px, py, pz) in enumerate(positions):
            texture = random.choice([i for i, _ in enumerate(self.images)]) + 1
            self.add_hexagonal_prism(px, py, pz, radius, 2, texture)
    
    def add_hexagonal_prism(self, cx, cy, cz, radius, height, texture):
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
        # Top face (this is the visible surface of the honeycomb)
        self.faces.append([base_idx + i for i in range(6)])
        self.face_textures.append(texture)
        
        # Bottom face
        self.faces.append([base_idx + 6 + i for i in range(6)])
        self.face_textures.append(0)  # No texture for bottom
        
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
            self.face_textures.append(0)  # No texture for sides
    
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
    
    def create_textured_hexagon(self, face_coords, img):
        """Create a properly textured and clipped hexagon image"""
        # Get bounding box
        xs = [c[0] for c in face_coords]
        ys = [c[1] for c in face_coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = int(max_x - min_x) + 1
        height = int(max_y - min_y) + 1
        
        if width < 5 or height < 5:
            return None, None, None
        
        # Create a new image for this hexagon
        size = max(width, height)
        hex_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Resize source image to fit
        resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Create hexagon mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Translate coordinates to local space
        offset_x = (size - width) / 2
        offset_y = (size - height) / 2
        local_coords = [(x - min_x + offset_x, y - min_y + offset_y) for x, y in face_coords]
        
        # Draw filled hexagon on mask
        mask_draw.polygon(local_coords, fill=255)
        
        # Apply mask to resized image
        hex_img.paste(resized_img, (0, 0), mask)
        
        # Calculate position to center the image
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        return hex_img, center_x, center_y
    
    def render(self):
        """Render the 3D scene"""
        self.canvas.delete('all')
        # Clear old image references
        self.canvas.image_refs = []
        
        # Project all vertices
        projected = []
        for v in self.vertices:
            x, y, z = self.project_3d_to_2d(v[0], v[1], v[2])
            projected.append((x, y, z))
        
        # Sort faces by average depth (painter's algorithm)
        face_depths = []
        for idx, face in enumerate(self.faces):
            avg_z = sum(projected[i][2] for i in face) / len(face)
            face_depths.append((avg_z, face, self.face_textures[idx]))
        
        face_depths.sort(reverse=True)
        
        # Draw faces
        for depth, face, texture in face_depths:
            points = []
            face_coords = []
            for i in face:
                x, y = projected[i][0], projected[i][1]
                points.extend([x, y])
                face_coords.append((x, y))
            
            # Draw textured face or colored face
            if texture > 0:
                # Use the appropriate image
                img = self.images[texture-1]
                
                # Create textured hexagon
                hex_img, center_x, center_y = self.create_textured_hexagon(face_coords, img)
                
                if hex_img:
                    # Convert to PhotoImage and draw
                    photo = ImageTk.PhotoImage(hex_img)
                    self.canvas.create_image(center_x, center_y, image=photo)
                    
                    # Keep reference to prevent garbage collection
                    self.canvas.image_refs.append(photo)
                    
                    # Draw outline on top
                    self.canvas.create_polygon(points, fill='', outline='#00ffff', width=1)
                else:
                    # Too small to texture, just draw outline
                    self.canvas.create_polygon(points, fill='gray', outline='#00ffff', width=1)
            else:
                # Color based on depth for non-textured faces
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