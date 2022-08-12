import pygame
from warnings import warn
import heapq

pygame.init()

screen = pygame.display.set_mode((1366, 768))

rows, cols = (30, 64)
rect_width = 20
rect_height = 20
box_arrays = []
start_box_pos = (80, 60)
end_box_pos = (1150, 60)
blockers_box_pos = (460, 60)
start_algo_btn_pos = (750, 60)

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


start_node_position = ()
end_node_position = ()


# Colors Defined
white = pygame.Color(255, 255, 255)
off_white = pygame.Color(189, 188, 187)
black = pygame.Color(0, 0, 0)
orange_col = pygame.Color(250, 161, 27)
orange_dark_col = pygame.Color(201, 99, 4)
grey_col = pygame.Color(41,41,41)
hinged_sky_blue_col = pygame.Color(255, 140, 26)
start_green_col = pygame.Color(4, 222, 77)
start_green_dark_col = pygame.Color(0, 102, 34)
start_algo_light_col = pygame.Color(5, 143, 242)
start_algo_dark_col = pygame.Color(5, 93, 176)


# Fonts Defined
font_large = pygame.font.Font('Roboto-Bold.ttf', 28)
font_small = pygame.font.Font('Roboto-Regular.ttf', 20)

class Node():
    def __init__(self, parent = None, position = None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

        # blank block
        self.node_type = 69
        self.x_index = -1
        self.y_index = -1

        self.x_position = -1
        self.y_position = -1

    def set_index(self, index):
        x_ind, y_ind = index
        self.x_index = x_ind
        self.y_index = y_ind

    def set_position(self, x_pos, y_pos):
        self.x_position = x_pos
        self.y_position = y_pos

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

def draw_text():
    textual_surface = font_large.render("A* Pathfinding Algorithm Visualizer", True, hinged_sky_blue_col)
    screen.blit(textual_surface, (screen.get_width() / 2 - textual_surface.get_width() / 2, 10))

def draw_rects():
    global box_arrays
    l_x = 12
    l_y = 130
    outer_shell_rect = (9, 127, 1349, 635)
    pygame.draw.rect(screen, orange_col, outer_shell_rect, width = 3, border_radius=2)
    for i in range(rows):
        for j in range(cols):
            box_arrays.append((l_x, l_y))
            pygame.draw.rect(screen, white, (l_x, l_y, rect_width, rect_height))
            box_node_array[i][j].set_position(l_x, l_y)
            box_node_array[i][j].set_index(convert_pos_to_array_index((l_x, l_y)))
            l_x += 21
        l_x = 12
        l_y += 21

    # for i in range(rows):
    #     for j in range(cols):
    #         print(f'({box_node_array[i][j].x_index}, {box_node_array[i][j].y_index})', end = '\t')
    #     print()


def mouse_event_handler(cur_pos, color = black):
    for box_pos_x, box_pos_y in box_arrays:
        if (cur_pos[0] >= box_pos_x and cur_pos[0] <= (box_pos_x + rect_width)) and (cur_pos[1] >= box_pos_y and cur_pos[1] <= (box_pos_y + rect_height)):
            pygame.draw.rect(screen, color, (box_pos_x, box_pos_y, rect_width, rect_height))
            if blockers_btn_state:
                cur_index_value = convert_pos_to_array_index(cur_pos)
                box_node_array[cur_index_value[0]][cur_index_value[1]].node_type = 0

def start_algo_btn(color):
    global start_algo_btn_pos
    start_algo_btn_w = 160
    start_algo_btn_h = 35  
    start_algo_btn_text = font_small.render("Run Algorithm", True, black)

    pygame.draw.rect(screen, color, (start_algo_btn_pos[0], start_algo_btn_pos[1], start_algo_btn_w, start_algo_btn_h), width = 0, border_radius = 8)    
    screen.blit(start_algo_btn_text, (start_algo_btn_pos[0] + start_algo_btn_w / 2 - start_algo_btn_text.get_width() / 2, start_algo_btn_pos[1] + start_algo_btn_h / 2 - start_algo_btn_text.get_height() / 2))

def blockers_box(color):
    global blockers_box_pos
    blockers_box_w = 120
    blockers_box_h = 35  
    blockers_box_text = font_small.render("Blockers", True, black)

    pygame.draw.rect(screen, color, (blockers_box_pos[0], blockers_box_pos[1], blockers_box_w, blockers_box_h), width = 0, border_radius = 8)    
    screen.blit(blockers_box_text, (blockers_box_pos[0] + blockers_box_w / 2 - blockers_box_text.get_width() / 2, blockers_box_pos[1] + blockers_box_h / 2 - blockers_box_text.get_height() / 2))

def end_box_node(color):
    global end_box_node
    end_node_w = 120
    end_node_h = 35  
    end_node_text = font_small.render("End", True, white)

    pygame.draw.rect(screen, color, (end_box_pos[0], end_box_pos[1], end_node_w, end_node_h), width = 0, border_radius = 8)    
    screen.blit(end_node_text, (end_box_pos[0] + end_node_w / 2 - end_node_text.get_width() / 2, end_box_pos[1] + end_node_h / 2 - end_node_text.get_height() / 2))

def start_box_node(color):
    global start_box_pos
    start_node_w = 120
    start_node_h = 35    
    start_node_text = font_small.render("Start", True, white)

    pygame.draw.rect(screen, color, (start_box_pos[0], start_box_pos[1], start_node_w, start_node_h), width = 0, border_radius = 8)
    screen.blit(start_node_text, (start_box_pos[0] + start_node_w / 2 - start_node_text.get_width() / 2, start_box_pos[1] + start_node_h / 2 - start_node_text.get_height() / 2))

def contained(click_pos, box_pos, box_dim):
    return (click_pos[0] > box_pos[0] and click_pos[0] < box_pos[0] + box_dim[0] and click_pos[1] > box_pos[1] and click_pos[1] < box_pos[1] + box_dim[1])
        
def flip_btn_state():
    global start_btn_state
    global end_btn_state
    global blockers_btn_state

    start_btn_state = ~start_btn_state
    end_btn_state = ~end_btn_state
    blockers_btn_state = ~blockers_btn_state

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
        
    elif contained(click_pos, end_box_pos, (120, 35)) and not end_btn_clicked:
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

        # for node in animation_list:
        #     pygame.draw.rect(screen, pygame.Color(0, 255, 0), (node[1] * 21 + 12, node[0] * 21 + 130, 20, 20))

        # for node in path:
        #     pygame.draw.rect(screen, pygame.Color(255, 0, 0), (node[1] * 21 + 12, node[0] * 21 + 130, 20, 20))


        


def draw_basic_UIs():
    screen.fill(grey_col)
    draw_text()
    draw_rects()
    start_box_node(start_green_dark_col)
    end_box_node(orange_dark_col)
    blockers_box(off_white)
    start_algo_btn(start_algo_dark_col)

def draw_green_node(clicked_pos):
    global start_btn_state
    global start_node_position

    mouse_event_handler(clicked_pos, start_green_col)
    start_btn_state = False
    start_box_node(start_green_dark_col)
    start_node_position = clicked_pos

def draw_orange_node(clicked_pos):
    global end_btn_state
    global end_node_position

    mouse_event_handler(clicked_pos, orange_col)
    end_btn_state = False
    end_box_node(orange_dark_col)
    end_node_position = clicked_pos

def convert_pos_to_array_index(pos):
    x_val = 0
    y_val = 0
    x, y = pos
    x -= 12
    y -= 130
    while x >= 0:
        x -= 21
        x_val += 1
    while y >= 0:
        y -= 21
        y_val += 1

    return (y_val - 1, x_val - 1) 

def run_a_star_algorithm(allow_diagonal_movement = False):
    start_index = convert_pos_to_array_index(start_node_position)
    end_index = convert_pos_to_array_index(end_node_position)
    box_node_array[start_index[0]][start_index[1]].node_type = 1
    box_node_array[end_index[0]][end_index[1]].node_type = -1


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

    # Adding a stop condition
    outer_iterations = 0
    # max_iterations = (len(maze[0]) * len(maze) // 2)
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
        animation_list.append({"pos": current_node.position, "color": start_algo_light_col})
        # Found the goal
        if current_node == end_node:
            print(len(animation_list))
            print(outer_iterations)
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
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)
            animation_list.append({"pos": child.position, "color": pygame.Color(0,255,0)})

    warn("Couldn't get a path to destination")
    return None


draw_basic_UIs()

animation_index = 0
path_index = 0
time_gap = 5

path_time_gap = 5

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
    
    # if node_list_complete:
    #     if time_gap < 0:
    #         time_gap = 5
    #         pygame.draw.rect(screen, animation_list[animation_index]["color"], (animation_list[animation_index]["pos"][1] * 21 + 12, animation_list[animation_index]["pos"][0] * 21 + 130, 20, 20))
    #         if animation_index + 1 == len(animation_list):
    #             node_list_complete = False
    #             path_list_complete = True
    #         else:
    #             animation_index += 1
    #     else:
    #         time_gap -= 1

    if node_list_complete:
        pygame.draw.rect(screen, animation_list[animation_index]["color"], (animation_list[animation_index]["pos"][1] * 21 + 12, animation_list[animation_index]["pos"][0] * 21 + 130, 20, 20))
        if animation_index + 1 == len(animation_list):
            node_list_complete = False
            path_list_complete = True
        else:
            animation_index += 1

    if path_list_complete:
        if path_time_gap < 0:
            path_time_gap = 5
            pygame.draw.rect(screen, pygame.Color(255, 0, 0), (path[path_index][1] * 21 + 12, path[path_index][0] * 21 + 130, 20, 20))
            if path_index + 1 == len(path):
                path_list_complete = False
            else:
                path_index += 1
        else:
            path_time_gap -= 1

    
    if mouse_motion and blockers_btn_state:
        mouse_event_handler(pygame.mouse.get_pos())
            
    pygame.display.update()