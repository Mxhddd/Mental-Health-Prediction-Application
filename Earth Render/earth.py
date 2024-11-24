import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image
import time

# Dictionary of country names with approximate coordinates (just for the demo)
countries = {
    "USA": {"coords": [1, 0, 5], "info": "Capital: Washington D.C."},
    "Canada": {"coords": [2, 1, 5], "info": "Capital: Ottawa"},
    "India": {"coords": [-1, 3, 5], "info": "Capital: New Delhi"},
    "Brazil": {"coords": [0, -3, 5], "info": "Capital: Brasília"},
}

cities = {
    "Washington D.C.": {"coords": [1, 0, 5], "info": "Population: 700,000"},
    "New Delhi": {"coords": [-1, 3, 5], "info": "Population: 20 million"},
    "Ottawa": {"coords": [2, 1, 5], "info": "Population: 1 million"},
    "Brasília": {"coords": [0, -3, 5], "info": "Population: 3 million"},
}

def load_texture_from_file(filename):
    try:
        image = Image.open(filename).convert("RGB")
        img_data = np.array(list(image.getdata()), np.uint8)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        return texture_id
    except Exception as e:
        print(f"Error loading texture: {e}")
        return None

def draw_earth(radius, texture_id):
    if texture_id is not None:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        quad = gluNewQuadric()
        gluQuadricTexture(quad, GL_TRUE)
        gluSphere(quad, radius, 100, 100)
        gluDeleteQuadric(quad)
        glDisable(GL_TEXTURE_2D)
    else:
        print("No texture to draw.")

def draw_text(text, x, y):
    # This function will draw the text on the screen at position (x, y)
    font = pygame.font.SysFont('Arial', 24)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen = pygame.display.get_surface()
    screen.blit(text_surface, text_rect)

def init_display():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("3D Earth Globe")
    glEnable(GL_DEPTH_TEST)
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -12)

def get_mouse_ray(mouse_x, mouse_y, display_width, display_height):
    # Convert the mouse position to normalized device coordinates (NDC)
    x = (2.0 * mouse_x) / display_width - 1.0
    y = 1.0 - (2.0 * mouse_y) / display_height
    z = 1.0

    # Create the ray direction (in world coordinates)
    ray_ndc = np.array([x, y, z])

    # Convert from NDC to camera space (by applying the inverse of the projection matrix)
    projection_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
    modelview_matrix = glGetDoublev(GL_MODELVIEW_MATRIX)

    # Compute inverse of the combined matrix
    combined_matrix = np.matmul(projection_matrix, modelview_matrix)
    inverse_matrix = np.linalg.inv(combined_matrix)

    # Transform the ray direction using the inverse matrix
    ray_world = np.dot(inverse_matrix[:3, :3], ray_ndc)  # Transform the direction only

    return ray_world

def handle_mouse_click(mouse_x, mouse_y, display_width, display_height):
    ray_direction = get_mouse_ray(mouse_x, mouse_y, display_width, display_height)
    print(f"Ray direction: {ray_direction}")
    return ray_direction

def check_country_click(ray_direction):
    # Check if the ray intersects with any of the countries
    for country, data in countries.items():
        # For simplicity, assume that the country click is based on approximate coordinates
        country_coords = data["coords"]
        if np.linalg.norm(ray_direction - np.array(country_coords)) < 1:  # Simple distance check
            return country, data["info"]
    return None, None

def check_city_click(ray_direction):
    # Check if the ray intersects with any of the cities
    for city, data in cities.items():
        city_coords = data["coords"]
        if np.linalg.norm(ray_direction - np.array(city_coords)) < 1:  # Simple distance check
            return city, data["info"]
    return None, None

def main():
    init_display()
    earth_texture_path = "C:\\Users\\GamaZone\\Desktop\\Coding\\Earth Render\\land_ocean_ice_8192.png"  # Updated path
    earth_texture_id = load_texture_from_file(earth_texture_path)

    rotation_angle_x = 23.5
    rotation_angle_y = 0
    zoom = -12  # Zoom level, negative means the camera is far from the globe
    last_mouse_x = 0
    last_mouse_y = 0
    dragging = False

    country = None  # Initialize the country variable
    city = None  # Initialize the city variable
    country_info = None  # To store country info for display
    city_info = None  # To store city info for display

    clock = pygame.time.Clock()  # Add clock to control the frame rate

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_x, last_mouse_y = event.pos
                    # Handle the mouse click event here
                    ray_direction = handle_mouse_click(last_mouse_x, last_mouse_y, 800, 600)
                    print(f"Mouse clicked at: {last_mouse_x, last_mouse_y}")

                    # Check if a country or city is clicked
                    country, country_info = check_country_click(ray_direction)
                    if country:
                        print(f"Country clicked: {country}, Info: {country_info}")

                    city, city_info = check_city_click(ray_direction)
                    if city:
                        print(f"City clicked: {city}, Info: {city_info}")

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            if event.type == MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    delta_x = mouse_x - last_mouse_x
                    delta_y = mouse_y - last_mouse_y

                    sensitivity = 0.1  # Adjust this value to control rotation speed
                    rotation_angle_y += delta_x * sensitivity
                    rotation_angle_x -= delta_y * sensitivity

                    rotation_angle_x = max(-90, min(90, rotation_angle_x))

                    last_mouse_x, last_mouse_y = mouse_x, mouse_y

            if event.type == MOUSEWHEEL:
                zoom += event.y * 0.5  # Zoom in/out
                glTranslatef(0.0, 0.0, zoom)

            if event.type == VIDEORESIZE:
                display = (event.w, event.h)
                pygame.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
                glViewport(0, 0, display[0], display[1])
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
                glMatrixMode(GL_MODELVIEW)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        glRotatef(rotation_angle_x, 1, 0, 0)
        glRotatef(rotation_angle_y, 0, 1, 0)
        draw_earth(5, earth_texture_id)
        draw_text("Use Mouse to Click on a Country or City", 400, 50)

        # Show pop-up info for country or city (just for example)
        if country:
            draw_text(f"{country}: {country_info}", 400, 100)
        if city:
            draw_text(f"{city}: {city_info}", 400, 150)

        glPopMatrix()
        pygame.display.flip()
        clock.tick(60)  # Set frame rate limit

if __name__ == "__main__":
    main()
