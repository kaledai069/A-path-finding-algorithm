from turtle import title
import pygame
from warnings import warn
import heapq
from pygame import *
pygame.init()
fps = 360
fps_clock = pygame.time.Clock()

screen = pygame.display.set_mode((1366, 768))
pygame.display.set_caption("A* Path Finding Visualizer")
icon_image = pygame.image.load('idea.png')
pygame.display.set_icon(icon_image)

rows, cols = (57, 122)
rect_width = 10
rect_height = 10
box_arrays = []
start_box_pos = (60, 75)
end_box_pos = (220, 75)
blockers_box_pos = (380, 75)
start_algo_btn_pos = (540, 75)
reset_btn_pos = (1120, 75)

animation_list = []
path = []

node_list_complete = False
path_list_complete = False

running = True
mouse_motion = False
start_btn_state = False
end_btn_state = False
blockers_btn_state = False
start_algo_btn_state = False
start_btn_clicked = False
end_btn_clicked = False
blockers_btn_clicked = False
animation_completion = False

start_node_position = ()
end_node_position = ()

# Colors Defined
white = pygame.Color(255, 255, 255)
little_off_white = pygame.Color(255, 255, 255, 5)
off_white = pygame.Color(189, 188, 187)
black = pygame.Color(0, 0, 0)
orange_col = pygame.Color(250, 161, 27)
orange_dark_col = pygame.Color(201, 99, 4)
grey_col = pygame.Color('#3FA796')
hinged_sky_blue_col = pygame.Color(255, 140, 26)
start_green_col = pygame.Color(6, 204, 72)
start_green_dark_col = pygame.Color(0, 102, 34)
start_algo_light_col = pygame.Color(5, 143, 242)
start_algo_dark_col = pygame.Color(5, 93, 176)
block_rect_color = black
background_color = pygame.Color("#361d32")
title_color = pygame.Color('#f55951')
box_background_color = pygame.Color(190, 190, 190)
current_node_fill_color = pygame.Color("#FFD93D")
open_list_node_fill_color = pygame.Color("#21ABA5")

# Fonts Defined
font_large = pygame.font.Font('Roboto-Bold.ttf', 28)
font_small = pygame.font.Font('Roboto-Regular.ttf', 18)

class Node():
    def __init__(self, parent = None, position = None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

        # blank block
        # node_type defines 'blockers', 'free way', 'start node' , 'end node'
        self.node_type = 69

        self.xdist_position = -1
        self.ydist_position = -1

        self.in_open_list = False
        self.in_close_list = False

    def set_positional_index(self, index):
        x_pos, y_pos = index
        self.position = (x_pos, y_pos)

    def set_position(self, x_pos, y_pos):
        self.xdist_position = x_pos
        self.ydist_position = y_pos

    def __eq__(self, other):
        return self.position == other.position
    
    def __repr__(self):
      return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    # defining less than for purposes of heap queue
    def __lt__(self, other):
      return self.f < other.f
    
    # defining greater than for purposes of heap queue
    def __gt__(self, other):
      return self.f > other.f

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path

box_node_array = [[Node() for i in range(cols)] for j in range(rows)]

# Place the Visualizer billboard at the top of the display window
def draw_text():
    textual_surface = font_large.render("A* Pathfinding Algorithm Visualizer", True, title_color)
    screen.blit(textual_surface, (screen.get_width() / 2 - textual_surface.get_width() / 2, 10))

# Draw the grid base 
def draw_rects():
    global box_arrays
    l_x = 13
    l_y = 131
    outer_shell_rect = (9, 127, 1349, 634)
    pygame.draw.rect(screen, title_color, outer_shell_rect, width = 4, border_radius=2)
    for i in range(rows):
        for j in range(cols):
            box_arrays.append((l_x, l_y))
            pygame.draw.rect(screen, little_off_white, (l_x, l_y, rect_width, rect_height))
            box_node_array[i][j].set_position(l_x, l_y)
            box_node_array[i][j].set_positional_index(convert_pos_to_array_index((l_x, l_y)))
            l_x += 11
        l_x = 13
        l_y += 11


def mouse_event_handler(cur_pos, color = block_rect_color, other_node = False):
    for box_pos_x, box_pos_y in box_arrays:
        if (cur_pos[0] >= box_pos_x and cur_pos[0] <= (box_pos_x + rect_width)) and (cur_pos[1] >= box_pos_y and cur_pos[1] <= (box_pos_y + rect_height)):
            if not other_node:
                pygame.draw.rect(screen, color, (box_pos_x - 0.5, box_pos_y - 0.5, rect_width + 2, rect_height + 2))
            else:
                pygame.draw.rect(screen, color, (box_pos_x, box_pos_y, rect_width, rect_height))
            if blockers_btn_state:
                cur_index_value = convert_pos_to_array_index(cur_pos)
                box_node_array[cur_index_value[0]][cur_index_value[1]].node_type = 0

def reset_btn_logic():
    global reset_btn_pos
    reset_btn_w = 120
    reset_btn_h = 30
    reset_btn_text = font_small.render("Reset", True, white)

    pygame.draw.rect(screen, pygame.Color(235, 20, 20), (reset_btn_pos[0], reset_btn_pos[1], reset_btn_w, reset_btn_h), width = 0, border_radius = 8)
    screen.blit(reset_btn_text, (reset_btn_pos[0] + reset_btn_w / 2 - reset_btn_text.get_width() / 2, reset_btn_pos[1] + reset_btn_h / 2 - reset_btn_text.get_height() / 2))

def start_algo_btn(color):
    global start_algo_btn_pos
    start_algo_btn_w = 140
    start_algo_btn_h = 30
    start_algo_btn_text = font_small.render("Run Algorithm", True, white)

    pygame.draw.rect(screen, color, (start_algo_btn_pos[0], start_algo_btn_pos[1], start_algo_btn_w, start_algo_btn_h), width = 0, border_radius = 8)    
    screen.blit(start_algo_btn_text, (start_algo_btn_pos[0] + start_algo_btn_w / 2 - start_algo_btn_text.get_width() / 2, start_algo_btn_pos[1] + start_algo_btn_h / 2 - start_algo_btn_text.get_height() / 2))

def blockers_box(color):
    global blockers_box_pos
    blockers_box_w = 120
    blockers_box_h = 30
    blockers_box_text = font_small.render("Blockers", True, black)

    pygame.draw.rect(screen, color, (blockers_box_pos[0], blockers_box_pos[1], blockers_box_w, blockers_box_h), width = 0, border_radius = 8)    
    screen.blit(blockers_box_text, (blockers_box_pos[0] + blockers_box_w / 2 - blockers_box_text.get_width() / 2, blockers_box_pos[1] + blockers_box_h / 2 - blockers_box_text.get_height() / 2))

def end_box_node(color):
    global end_box_node
    end_node_w = 120
    end_node_h = 30 
    end_node_text = font_small.render("End", True, white)

    pygame.draw.rect(screen, color, (end_box_pos[0], end_box_pos[1], end_node_w, end_node_h), width = 0, border_radius = 8)    
    screen.blit(end_node_text, (end_box_pos[0] + end_node_w / 2 - end_node_text.get_width() / 2, end_box_pos[1] + end_node_h / 2 - end_node_text.get_height() / 2))

def start_box_node(color):
    global start_box_pos
    start_node_w = 120
    start_node_h = 30  
    start_node_text = font_small.render("Start", True, white)

    pygame.draw.rect(screen, color, (start_box_pos[0], start_box_pos[1], start_node_w, start_node_h), width = 0, border_radius = 8)
    screen.blit(start_node_text, (start_box_pos[0] + start_node_w / 2 - start_node_text.get_width() / 2, start_box_pos[1] + start_node_h / 2 - start_node_text.get_height() / 2))

def contained(click_pos, box_pos, box_dim):
    return (click_pos[0] > box_pos[0] and click_pos[0] < box_pos[0] + box_dim[0] and click_pos[1] > box_pos[1] and click_pos[1] < box_pos[1] + box_dim[1])
        

def btn_classifier(click_pos):
    global start_btn_state
    global end_btn_state
    global blockers_btn_state
    global start_btn_clicked 
    global end_btn_clicked
    global path
    global node_list_complete

    if contained(click_pos, start_box_pos, (120, 35)) and not start_btn_clicked:
        global start_btn_state

        start_btn_state = not start_btn_state
        start_btn_clicked = True
        if start_btn_state:
            start_box_node(start_green_col)
        else:
            start_box_node(start_green_dark_col)
        
    elif contained(click_pos, end_box_pos, (120, 35)) and not end_btn_clicked and start_btn_clicked:
        global end_btn_state

        end_btn_state = not end_btn_state
        end_btn_clicked = True
        if end_btn_state:
            end_box_node(orange_col)
        else:
            end_box_node(orange_dark_col)

    elif contained(click_pos, blockers_box_pos, (120, 35)) and start_btn_clicked and end_btn_clicked:
        global blockers_btn_clicked
        global blockers_btn_state
        global start_algo_btn_state

        blockers_btn_state = not blockers_btn_state
        if blockers_btn_state:
            blockers_box(white)
            blockers_btn_clicked = True
            start_algo_btn(start_algo_dark_col)
        else:
            blockers_box(off_white)
            if blockers_btn_clicked:
                start_algo_btn(start_algo_light_col)
                start_algo_btn_state = True
    
    elif contained(click_pos, start_algo_btn_pos, (160, 35)) and start_algo_btn_state:
        path = run_a_star_algorithm()
        node_list_complete = True

    elif contained(click_pos, reset_btn_pos, (120, 30)):
        reset_all_vals()
   
def reset_all_vals():
    global box_arrays 
    global animation_list
    global path
    global node_list_complete
    global path_list_complete
    global mouse_motion
    global start_btn_state 
    global end_btn_state
    global blockers_btn_state
    global start_algo_btn_state
    global start_btn_clicked
    global end_btn_clicked
    global blockers_btn_clicked
    global animation_completion
    global start_node_position
    global end_node_position
    global box_node_array
    global animation_index
    global path_index
    global path_time_gap 

    box_arrays = []
    animation_list = []
    path = []
    node_list_complete = False
    path_list_complete = False
    mouse_motion = False
    start_btn_state = False
    end_btn_state = False
    blockers_btn_state = False
    start_algo_btn_state = False
    start_btn_clicked = False
    end_btn_clicked = False
    blockers_btn_clicked = False
    animation_completion = False
    start_node_position = ()
    end_node_position = ()
    box_node_array = [[Node() for i in range(cols)] for j in range(rows)]
    animation_index = 0
    path_index = 0
    path_time_gap = 1
    draw_basic_UIs()


def draw_basic_UIs():
    screen.fill(background_color)
    pygame.draw.rect(screen, box_background_color, (13, 131, 1341, 626))
    draw_text()
    draw_rects()
    start_box_node(start_green_dark_col)
    end_box_node(orange_dark_col)
    blockers_box(off_white)
    start_algo_btn(start_algo_dark_col)
    reset_btn_logic()

def draw_green_node(clicked_pos):
    global start_btn_state
    global start_node_position

    mouse_event_handler(clicked_pos, start_green_col, True)
    start_btn_state = False
    start_box_node(start_green_dark_col)
    start_node_position = convert_pos_to_array_index(clicked_pos)
    box_node_array[start_node_position[0]][start_node_position[1]].node_type = 1

def draw_orange_node(clicked_pos):
    global end_btn_state
    global end_node_position

    mouse_event_handler(clicked_pos, orange_col, True)
    end_btn_state = False
    end_box_node(orange_dark_col)
    end_node_position = convert_pos_to_array_index(clicked_pos)
    box_node_array[start_node_position[0]][start_node_position[1]].node_type = -1

def convert_pos_to_array_index(pos):
    x_val = 0
    y_val = 0
    x, y = pos
    x -= 13
    y -= 131
    while x >= 0:
        x -= 11
        x_val += 1
    while y >= 0:
        y -= 11
        y_val += 1

    return (y_val - 1, x_val - 1) 

def calculate_val(pos):
    global cols
    return pos[0] + pos[1] * cols 

def run_a_star_algorithm(allow_diagonal_movement = False):
    global start_node_position
    global end_node_position

    start_index = start_node_position
    end_index = end_node_position

    global cols 
    global rows
    global animation_list

    maze = [[0 for i in range(cols)] for j in range(rows)]

    for i in range(rows):
        for j in range(cols):
            if box_node_array[i][j].node_type == 0:
                maze[i][j] = 1

    start_node = Node(None, start_index)
    start_node.g = start_node.h = start_node.f = 0

    end_node = Node(None, end_index)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []


    # Heapify the open_list and Add the start node
    heapq.heapify(open_list) 
    heapq.heappush(open_list, start_node)
    box_node_array[start_node.position[0]][start_node.position[1]].in_open_list = True

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = 50000

    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
    if allow_diagonal_movement:
        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

    current_node = Node()
    # Loop until you find the end
    while len(open_list) > 0:
        outer_iterations += 1

        if outer_iterations > max_iterations:
          # if we hit this point return the path such as it is
          # it will not contain the destination
          warn("giving up on pathfinding too many iterations")
          return return_path(current_node)       
        
        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)
        box_node_array[current_node.position[0]][current_node.position[1]].in_open_list = False
        box_node_array[current_node.position[0]][current_node.position[1]].in_close_list = True
        
        animation_list.append({"pos": current_node.position, "color": pygame.Color(255,0,0)})
        animation_list.append({"pos": current_node.position, "color": current_node_fill_color})

        # Found the goal
        if current_node == end_node:
            print("Animation objects number: ", len(animation_list))
            print("Iteration number: ", outer_iterations)
            return return_path(current_node)

        # Generate children
        children = []
        
        for new_position in adjacent_squares: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            if box_node_array[child.position[0]][child.position[1]].in_close_list:
                continue

            # Create the f, g, and h values

            # Euclidean Heuristic Distance Value
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)

            # Manhattan Heuristic Distance Value
            # child.h = 2 * (abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1]))

            child.f = child.g + child.h
                
            if box_node_array[child.position[0]][child.position[1]].in_open_list:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)
            box_node_array[child.position[0]][child.position[1]].in_open_list = True
            animation_list.append({"pos": child.position, "color": open_list_node_fill_color})
           
    warn("Couldn't get a path to destination")
    return None



draw_basic_UIs()

animation_index = 0
path_index = 0
time_gap = -1
path_time_gap = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if blockers_btn_state:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_motion = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_motion = False
        
        if start_btn_state:
            if event.type == pygame.MOUSEBUTTONDOWN:
                draw_green_node(pygame.mouse.get_pos())

        if end_btn_state:
            if event.type == pygame.MOUSEBUTTONDOWN:
                draw_orange_node(pygame.mouse.get_pos())
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            btn_classifier(pygame.mouse.get_pos())
    

    if node_list_complete:
        x_pos, y_pos = animation_list[animation_index]["pos"]

        pygame.draw.rect(screen, animation_list[animation_index]["color"], (animation_list[animation_index]["pos"][1] * 11 + 13, animation_list[animation_index]["pos"][0] * 11 + 131, 10, 10))
        if animation_index + 1 == len(animation_list):
            node_list_complete = False
            path_list_complete = True
            pygame.draw.rect(screen, pygame.Color(235,40,40), (start_node_position[1] * 11 + 13 - 0.5, start_node_position[0] * 11 + 131 - 0.5, rect_width + 2, rect_height + 2))
        else:
            animation_index += 1

    if path_list_complete:
        if path_time_gap < 0:
            path_time_gap = 1
            if path_index + 1 != len(path):
                pygame.draw.line(screen, pygame.Color(235, 40, 40), (path[path_index][1] * 11 + 13 + 5, path[path_index][0] * 11 + 131 + 5), (path[path_index + 1][1] * 11 + 13 + 5, path[path_index + 1][0] * 11 + 131 + 5), 3)

            if path_index + 1 == len(path):
                path_list_complete = False
                animation_completion = True
                pygame.draw.rect(screen, pygame.Color(235,40,40), (end_node_position[1] * 11 + 13 - 0.5, end_node_position[0] * 11 + 131 - 0.5, rect_width + 2, rect_height + 2))
                print("Path Calculated: ", len(path), " units")
            else:
                path_index += 1
        else:
            path_time_gap -= 1
    
    if mouse_motion and blockers_btn_state:
        mouse_event_handler(pygame.mouse.get_pos())
            
    pygame.display.update()
    fps_clock.tick(fps)