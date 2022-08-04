import pygame

pygame.init()

screen = pygame.display.set_mode((1366, 768))

rows, cols = (30, 64)
rect_width = 20
rect_height = 20
box_arrays = []
start_box_pos = (80, 60)
end_box_pos = (1150, 60)
blockers_box_pos = (600, 60)

running = True
mouse_motion = False
start_btn_state = True
end_btn_state = False
blockers_btn_state = False

# Colors Defined
white = pygame.Color(255, 255, 255)
off_white = pygame.Color(189, 188, 187)
black = pygame.Color(0, 0, 0)
orange_col = pygame.Color(255,163,26)
orange_dark_col = pygame.Color(173, 107, 9)
grey_col = pygame.Color(41,41,41)
hinged_sky_blue_col = pygame.Color(255, 140, 26)
start_green_col = pygame.Color(0, 153, 51)
start_green_dark_col = pygame.Color(0, 102, 34)

# Fonts Defined
font_large = pygame.font.Font('Roboto-Bold.ttf', 28)
font_small = pygame.font.Font('Roboto-Regular.ttf', 20)

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
            l_x += 21
        l_x = 12
        l_y += 21

def mouse_event_handler(cur_pos):
    for box_pos_x, box_pos_y in box_arrays:
        if (cur_pos[0] >= box_pos_x and cur_pos[0] <= (box_pos_x + rect_width)) and (cur_pos[1] >= box_pos_y and cur_pos[1] <= (box_pos_y + rect_height)):
            pygame.draw.rect(screen, black, (box_pos_x, box_pos_y, rect_width, rect_height))

def blockers_box():
    global blockers_box_pos
    blockers_box_w = 120
    blockers_box_h = 35  
    blockers_box_text = font_small.render("Blockers", True, black)

    if blockers_btn_state:
        btn_state_color = white
    else:
        btn_state_color = off_white

    pygame.draw.rect(screen, btn_state_color, (blockers_box_pos[0], blockers_box_pos[1], blockers_box_w, blockers_box_h), width = 0, border_radius = 8)    
    screen.blit(blockers_box_text, (blockers_box_pos[0] + blockers_box_w / 2 - blockers_box_text.get_width() / 2, blockers_box_pos[1] + blockers_box_h / 2 - blockers_box_text.get_height() / 2))

def end_box_node():
    global end_box_node
    end_node_w = 120
    end_node_h = 35  
    end_node_text = font_small.render("End", True, white)

    if end_btn_state:
        btn_state_color = orange_col
    else:
        btn_state_color = orange_dark_col

    pygame.draw.rect(screen, btn_state_color, (end_box_pos[0], end_box_pos[1], end_node_w, end_node_h), width = 0, border_radius = 8)    
    screen.blit(end_node_text, (end_box_pos[0] + end_node_w / 2 - end_node_text.get_width() / 2, end_box_pos[1] + end_node_h / 2 - end_node_text.get_height() / 2))


def start_box_node():
    global start_box_pos
    start_node_w = 120
    start_node_h = 35    
    start_node_text = font_small.render("Start", True, white)

    if start_btn_state:
        btn_state_color = start_green_col
    else:
        btn_state_color = start_green_dark_col

    pygame.draw.rect(screen, btn_state_color, (start_box_pos[0], start_box_pos[1], start_node_w, start_node_h), width = 0, border_radius = 8)
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
    if contained(click_pos, start_box_pos, (120, 35)):
        print('Start Button')
        start_btn_state = ~start_btn_state
        end_btn_state = ~end_btn_state
        blockers_btn_state = ~blockers_btn_state
        
    elif contained(click_pos, end_box_pos, (120, 35)):
        print('End Button')
        

def draw_basic_UIs():
    screen.fill(grey_col)
    draw_text()
    draw_rects()
    start_box_node()
    end_box_node()
    blockers_box()


draw_basic_UIs()
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if blockers_btn_state:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_motion = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_motion = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            btn_classifier(pygame.mouse.get_pos())
    
    if mouse_motion:
        mouse_event_handler(pygame.mouse.get_pos())
            
    pygame.display.update()