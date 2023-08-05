"""
NOTES : 
    - CHANGER LA DETECTION VERS LE BAS QUAND LE BLOC EST TOUT SEUL
    - CHANGER LES NOMS DE CERTAINES FONCTIONS + AJOUTER DES COMMENTAIRES 
"""

from kandinsky import *
from ion import *
from time import sleep, monotonic
from random import randint


MAP_HEIGHT = 220
MAP_WIDTH = 320

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
bg_color = (248, 252, 248)
PROGRAM_SPEED = 0.1

""" 3 types of frames : 
    - active = actual bloc that we control
    - passive = blocs laies 
    - none = background
""" 

class grid_pattern():
    def __init__(self):
        # grid params
        self.n_frames_x = 16 
        self.n_frames_y = 11
        self.size_x = MAP_WIDTH // self.n_frames_x
        self.size_y = MAP_HEIGHT // self.n_frames_y
        
        self.tab = self.build_tab()
        # border
        self.border_x = self.n_frames_x - 1
        self.border_y = self.n_frames_y - 1
    def build_tab(self):
        virtual_tab = []

        for x in range(self.n_frames_x):
            virtual_tab.append([])

            for y in range(self.n_frames_y):
                # (type, color, (16x;11y) ) 
                virtual_tab[x].append({"type": "none", "color": bg_color, "position": (x*self.size_x, y*self.size_y)})
               
        return virtual_tab

    # check the state of the frame next to it
    def collision(self, figure):
    
        collision_informations = {"left" : False, "bottom" : False, "right" : False}
        # left
        if figure.active_sides[0]:
            if figure.x == 0 or self.tab[figure.x - 1][figure.y]["type"] == "passive" :
                collision_informations["left"] = True
        # bottom
        if figure.active_sides[1]:
            if figure.y == self.border_y or self.tab[figure.x][figure.y + 1]["type"] == "passive":
                collision_informations["bottom"] = True
        # right
        if figure.active_sides[2]:
            if figure.x == self.border_x or self.tab[figure.x + 1][figure.y]["type"] == "passive":
                collision_informations["right"] = True 
        
        return collision_informations
    
    def change_collision_sides(self, object_):
        for bloc in object_.list:
            bloc_under = False
            for bloc_ in object_.list:
                if bloc.y + 1 == bloc_.y and bloc.x == bloc_.x :
                    bloc_under = True

            if not bloc_under : bloc.active_sides[1] = True
        return object_

    def display_pbloc(self, blocs):
        for bloc in blocs.list:
            fill_rect(self.tab[bloc.x][bloc.y]["position"][0], self.tab[bloc.x][bloc.y]["position"][1], self.size_x, self.size_y, bloc.color)
    #We display the grid_pattern
    def display_pBlocs(self, pBlocs): 
        for blocs in pBlocs.objects:
            self.display_pbloc(blocs)       

    def display_aBlocs(self, object_):
        for figure in object_.list:
            fill_rect(self.tab[figure.x][figure.y]["position"][0], self.tab[figure.x][figure.y]["position"][1], self.size_x, self.size_y, figure.color)
       
    def display_bg(self, x, y):
        # modify parms of the fe
        self.tab[x][y]["type"] = "none"
        self.tab[x][y]["color"] = bg_color
        
        fill_rect(self.tab[x][y]["position"][0], self.tab[x][y]["position"][1], 20, 20, bg_color)

    
    def modify(self, direction, object_, state):
        if direction == "down" : object_.line += 1
        for figure in reversed(object_.list):
            self.display_bg(figure.x, figure.y)
            if direction == "left":
                self.tab[figure.x - 1][figure.y]["type"] = state
                self.tab[figure.x - 1][figure.y]["color"] = figure.color
                # modify
                figure.x -= 1
            elif direction == "down":
                self.tab[figure.x][figure.y + 1]["type"] = state
                self.tab[figure.x][figure.y + 1]["color"] = figure.color
                figure.y +=1
            elif direction == "right":
                self.tab[figure.x + 1][figure.y]["type"] = state
                self.tab[figure.x + 1][figure.y]["color"] = figure.color
                figure.x +=1
        
        return object_, self

    def passive_state(object_):
        for figure in object_:
           self.tab[figure.x][figure.y]["type"] = "passive"

# independants functions
def information_filter(grid, object_):
    all_informations = {"left" : False, "bottom" : False, "right" : False}
    for figure in object_.list:
        info_collisions = grid.collision(figure)
        if info_collisions["left"]: all_informations["left"] = True
        if info_collisions["bottom"]: all_informations["bottom"] = True
        if info_collisions["right"]: all_informations["right"] = True
    return all_informations

def command(grid, object_, pBlocs, auto_move):
    all_informations = information_filter(grid, object_)
    new_object_ = False
    if keydown(KEY_LEFT) and not all_informations["left"]:
        object_, grid = grid.modify("left", object_, "active")
 
    elif keydown(KEY_RIGHT) and not all_informations["right"]:
        object_, grid = grid.modify("right", object_, "active")
   
    elif (keydown(KEY_DOWN) or auto_move) and not all_informations["bottom"]:
        object_, grid = grid.modify("down", object_, "active")

    elif all_informations["bottom"]:
        object_.line += 1
        # add the object to the passive team
        grid.tab = pBlocs.add(object_, grid)
        # allow to generate a new object
        new_object_ = True
    
    return grid, object_, pBlocs, new_object_

class Figure():
    def __init__(self, x, y, color, collision_sides):

        # side that we need to check if there is a collision
        # [left, bottom, right]
        self.active_sides = collision_sides

        # pos in the grid
        self.x = x + 7
        self.y = y
                
        self.color = color    
 
class PassiveBlocs():
    def __init__(self, n_frames_y):
        # list all tab coo blocs, (x, y, color)
        self.objects = []
        self.lines = [0 for i in range(n_frames_y)]
    # [16, ..., 0]
    def sort_object(self, new_object):
        
        if len(self.objects) > 0:
            line_insert = 0
            if self.objects[-1].line > new_object.line : 
                self.objects.append(new_object)
            else :
                for object_ in self.objects :
                    if object_.line <= new_object.line :
                        line_insert = self.objects.index(object_)
                        self.objects.insert(line_insert, new_object)
                        break
        else :
            self.objects.append(new_object)

    def detect_full_line(self, grid, object_): 
        __full_line = []
        for bloc in object_.list :
            self.lines[bloc.y] += 1
            grid.tab[bloc.x][bloc.y]["type"] = "passive"
            
            if self.lines[bloc.y] == 16 : 
                __full_line.append(bloc.y)

        return sorted(__full_line), grid.tab

    def suppr_bloc(self, blocs, line, grid):
        for bloc in blocs.list:
            bloc_index = blocs.list.index(bloc)
            if bloc.y == line :
                grid.display_bg(bloc.x, bloc.y)
                blocs.list.pop(bloc_index)
                self.suppr_bloc(blocs, line, grid)
        return blocs
    
    def delete_blocs(self, __void_objects):
        i = 0
        for pos in __void_objects:
            self.objects.pop(pos+i)
            i -= 1
    
    def suppr_line(self, grid, __full_lines):
        __void_objects = []
        for line in __full_lines:
            for blocs in self.objects:
                blocs_index = self.objects.index(blocs)
                blocs = self.suppr_bloc(blocs, line, grid)
                
                if len(blocs.list) == 0 : 
                    __void_objects.append(blocs_index)
            self.lines[line] = 0

            __void_objects = sorted(__void_objects)
        if len(__void_objects) > 0 :
            self.delete_blocs(__void_objects)
            grid = self.move(__full_lines, grid)
        return grid.tab
              
    def move(self, __full_lines, grid):
        for line in __full_lines :
            print("HERE")
            for object_ in self.objects:
                #object_ = grid.change_collision_sides(object_)
                # if the objects is above the delete lines --> move it
                if object_.line < line:
                    all_informations = information_filter(grid, object_)
                    while not all_informations["bottom"]:
                        # move it in the tab
                        object_, grid = grid.modify("down", object_, "passive")
                        
                        all_informations  = information_filter(grid, object_)
        # we need to check if there is a new line full
        for object_ in self.objects : 
            __full_lines, grid.tab = self.detect_full_line(grid, object_)
            grid.tab = self.suppr_line(grid, __full_lines)

        return grid
   
    def add(self, object_, grid):
        
        self.sort_object(object_)
        __full_line, grid.tab = self.detect_full_line(grid, object_)        
        grid.tab = self.suppr_line(grid, __full_line)
        return grid.tab 

def def_line(list_):
    line = 0
    for figure in list_:
        if figure.y > line : line = figure.y
    return line

class FCube():
    def __init__(self):
        self.list = [Figure(0, 0, black, [True, False, False]), Figure(1, 0, black, [False, False, True]), Figure(0, 1, black, [True, True, False]), Figure(1, 1, black, [False, True, True])]
        self.line = def_line(self.list)

class Chrono():
    def __init__(self, frequence) -> None:
        self.frequence = frequence # = 1 second
        self.time_start = monotonic()
        self.time = 0

    def calculate_time(self):
        time_diff = monotonic() - self.time_start
        if time_diff >= self.frequence:
            self.time_start = monotonic()
            self.time += 1
            return True
        else : return False
    
    def adaptive_time(self, time):
        if time == "start":
            self.time_start = monotonic()
        if time == "end":
            time_exe = monotonic() - self.time_start
            time_sleep = self.frequence - time_exe
            if time_sleep > 0 : sleep(time_sleep)
            #else : print("time behind : ", time_exe - self.frequence) 
 
def main():
    grid = grid_pattern()
    timer_move = Chrono(1.2)
    timer_program = Chrono(PROGRAM_SPEED)
    pBlocs = PassiveBlocs(grid.n_frames_y)
    object_ = FCube()
 
    while True:
        timer_program.adaptive_time("start") 
        auto_move = timer_move.calculate_time()
        grid, object_, pBlocs, new_object_ = command(grid, object_, pBlocs, auto_move)
        if new_object_:
            object_ = FCube()
        
        grid.display_aBlocs(object_)
        grid.display_pBlocs(pBlocs)
        
        timer_program.adaptive_time("end")

main()
