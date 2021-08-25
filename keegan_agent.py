# -*- coding: utf-8 -*-
from sdl2 import *
import ctypes
import OpenGL.GL as gl

import imgui
from imgui.integrations.sdl2 import SDL2Renderer

import psutil

import pygame

import json

##### DEPENDENCIES
# winget install python3
# pip install imgui[full]
# pip install pysdl2
# pip install pysdl2-dll
# pip install psutil
# pip install pywin32
# pip install pygame


### [ ]     Application Metrics
### [ ]     Windows
###     [x]     Name
###     [x]     Pid
###     [x]     Path
###     [x]     Icon
###     [x]     CPU
###     [x]     RAM
### [ ]     Linux
###     [ ]     Name
###     [ ]     Pid
###     [ ]     Path
###     [ ]     Icon
###     [ ]     CPU
###     [ ]     RAM
### [ ]     Both
###     [ ]     Icon texture dictionary
###     [ ]     Threading

### [ ]     PC Metrics
###     [ ]     Name
###     [ ]     CPU
###     [ ]     GPU
###     [ ]     RAM
###     [ ]     UPTIME

### Application/System
###     [ ] Network
###     [ ] Disk Usage

### Receive Commands
### File I/O
###


### Output all data as json.


### TO DO: 23/08/21
### FINISH APPLICATION METRICS
### COLLECT SYSTEM METRICS
### IMPLEMENT THREADING
### OUTPUT AS JSON





###############
## LIST HANDLERS
###############


list_current_processes = []
list_current_processes_show = []
system_metrics = None

###############
## APPLICATION CLASS
###############


class application:
    def __init__(self, name, cpu, ram):
        self.name = name
        self.cpu = cpu
        self.ram = ram
    def to_dict(self):
        return {"name": self.name, "cpu": self.cpu, "ram": self.ram}

###############
## SYSTEM CLASS
###############
class system:
    def __init__(self, name, cpu, ram):
        self.name = name
        self.cpu = cpu
        self.ram = ram



import socket

###############
## GET HOSTNAME
###############

def get_hostname():
    return socket.gethostname()

import threading
import time

###############
## APPLICATION METRICS THREAD
###############


def thread_application_metrics():
    global list_current_processes
    global list_current_processes_show
    while(True):
        list_current_processes.clear()
        get_list_of_processes(list_current_processes)
        list_current_processes.sort(key=lambda x: x.cpu, reverse=True)
        list_current_processes_show.clear()
        list_current_processes_show = list_current_processes.copy()
        time.sleep(5)

###############
## SYSTEM METRICS THREAD
###############


def thread_system_metrics():
    global system_metrics
    while(True):
        system_metrics = system(get_hostname(),psutil.cpu_percent(), psutil.virtual_memory().percent)
        time.sleep(5)


###############
## GET LIST OF PROCESSES
###############

def get_list_of_processes(list_processes):
    process_iter = psutil.process_iter()
    cpu_count = psutil.cpu_count()
    for proc in process_iter:
        try:
            exe_path = proc.exe()
            process_name = proc.name()
            if ".exe" in process_name:
                list_processes.append(application(process_name, round(proc.cpu_percent()/cpu_count,2), round(proc.memory_percent(),2)))

            
        #print(process_name , ' ::: ', processID)
        except psutil.Error:
            pass







from datetime import datetime

###############
## PRODUCT JSON FROM LIST
###############


def get_json():
    now = datetime.now()
    app_metrics = []
    for i in range(5):
        app_metrics.append(list_current_processes_show[i].to_dict())
    x = {
        "machine_name": socket.gethostname(),
        "collection_time": now.strftime("%m/%d/%Y, %H:%M:%S"),
        "app_metrics": app_metrics,
        "system_metrics": [{"cpu":system_metrics.cpu}, {"ram":system_metrics.ram}]
    }
    return json.dumps(x)


# json start time for collection
# machine
# time
# app metrics
# system metrics



###############
## MAIN FUNCTION
###############

def main():
    window, gl_context = impl_pysdl2_init()
    
    imgui.create_context()
    impl = SDL2Renderer(window)
    
    io = imgui.get_io()
    
    font1 = io.fonts.add_font_from_file_ttf("C:\\Windows\\Fonts\\consola.ttf", 26)
    impl.refresh_font_texture()
    
    

    running = True
    event = SDL_Event()

    processList = None

    #texture.append(loadImage_mod(pygame.image.load("blank.png")))

    exeFilter = ""
    
    debug_output = ""
    
    hostname = get_hostname()
    
    json_output = ""
    
    
    ###############
    ## START THREADS
    ###############
    
    application_thread = threading.Thread(target = thread_application_metrics).start()
    system_thread = threading.Thread(target = thread_system_metrics).start()
    
    #time.sleep(1)
    
    #threading.Thread(target = thread_system_metrics).start()
    #system_thread.start()
    

    while running:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break
            impl.process_event(event)
        impl.process_inputs()

        #if not application_thread.is_alive():
        #    application_thread.start()
        #    
        #if not system_thread.is_alive():
        #    system_thread.start()

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        #imgui.show_test_window()
        imgui.push_font(font1)
        imgui.begin("Custom window", True)

        #imgui.image(texture[0], 32, 32)
        #global global_test
        
        
        ###############
        ## PRESS BUTTON TO START THREAD
        ###############
        
        
        #if imgui.button("ThreadTest"):
        #    # START THREAD
        #    x = threading.Thread(target = thread_application_metrics, args=(debug_output,))
        #    x.start()
        
        
        
        imgui.text(hostname)
        
        count = 0

        #style = imgui.get_style()
        #imgui.columns(4)
        #for color in range(0, imgui.COLOR_COUNT):
        #    imgui.text("Color: {}".format(color))
        #    imgui.color_button("color#{}".format(color), *style.colors[color])
        #    imgui.next_column()
        #text_val = 'Please, type the coefficient here.'

        imgui.text("Filter: ")
        imgui.same_line()

        
        changed, exeFilter = imgui.input_text("",exeFilter, 256)

        columns = ["one", "two", "three"]
        
        #imgui.text(str(dictionary_textures))
        
        #for texture in dictionary_textures:
        #    imgui.text(texture.)
        
        ###############
        ## AFTER THREAD IS STARTED, PRESS GET JSON TO POPULATE JSON STRING
        ###############
        
        if imgui.button("Get Json"):
            json_output = get_json()
            print(json_output)

        imgui.text_wrapped(json_output)
        if system_metrics is not None:
            imgui.text("System Name: ")
            imgui.same_line()
            imgui.text(system_metrics.name)
            imgui.text("CPU: ")
            imgui.same_line()
            imgui.text(str(system_metrics.cpu))
            imgui.text("RAM: ")
            imgui.same_line()
            imgui.text(str(system_metrics.ram))

        imgui.separator()
        imgui.begin_child("processRegion1", 0, 40, border=False)
        imgui.columns(3)
        imgui.set_column_width(0,100)
        imgui.set_column_width(1,100)
        imgui.set_column_width(2,100)
        #imgui.text("Image")
        #imgui.next_column()
        #imgui.text("Pid")
        #imgui.next_column()
        imgui.text("Name")
        imgui.next_column()
        #imgui.text("Path")
        #imgui.next_column()
        imgui.text("CPU")
        imgui.next_column()
        imgui.text("RAM")
        imgui.next_column()
        imgui.end_child()
        imgui.begin_child("processRegion2", 0, 0, border=True)
        imgui.columns(3)
        imgui.set_column_width(0,100)
        imgui.set_column_width(1,100)
        imgui.set_column_width(2,100)
        for s in list_current_processes_show:
            if(list_current_processes_show[count].name != "None"):
                if(exeFilter.lower() in list_current_processes_show[count].name.lower()):
                    #imgui.image(list_current_processes[count].texture,32,32)
                    #imgui.next_column()
                    #imgui.text(str(list_current_processes_show[count].pid))
                    #imgui.next_column()
                    imgui.text(list_current_processes_show[count].name)
                    imgui.next_column()
                    #imgui.text(list_current_processes_show[count].path)
                    #imgui.next_column()
                    imgui.text(str(list_current_processes_show[count].cpu))
                    imgui.next_column()
                    imgui.text(str(list_current_processes_show[count].ram))
                    imgui.next_column()
            count+=1 
        count = 0   
        imgui.end_child()


        imgui.end()
        imgui.pop_font()

        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        SDL_GL_SwapWindow(window)

    impl.shutdown()
    SDL_GL_DeleteContext(gl_context)
    SDL_DestroyWindow(window)
    SDL_Quit()




###############
## SDL INITIALISE
###############


def impl_pysdl2_init():
    width, height = 1680, 1050
    window_name = "minimal ImGui/SDL2 example"

    if SDL_Init(SDL_INIT_EVERYTHING) < 0:
        print("Error: SDL could not initialize! SDL Error: " + SDL_GetError().decode("utf-8"))
        exit(1)

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24)
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8)
    SDL_GL_SetAttribute(SDL_GL_ACCELERATED_VISUAL, 1)
    SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS, 1)
    SDL_GL_SetAttribute(SDL_GL_MULTISAMPLESAMPLES, 16)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 4)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

    SDL_SetHint(SDL_HINT_MAC_CTRL_CLICK_EMULATE_RIGHT_CLICK, b"1")
    SDL_SetHint(SDL_HINT_VIDEO_HIGHDPI_DISABLED, b"1")

    window = SDL_CreateWindow(window_name.encode('utf-8'),
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              width, height,
                              SDL_WINDOW_OPENGL|SDL_WINDOW_RESIZABLE)

    if window is None:
        print("Error: Window could not be created! SDL Error: " + SDL_GetError().decode("utf-8"))
        exit(1)

    gl_context = SDL_GL_CreateContext(window)
    if gl_context is None:
        print("Error: Cannot create OpenGL Context! SDL Error: " + SDL_GetError().decode("utf-8"))
        exit(1)

    SDL_GL_MakeCurrent(window, gl_context)
    if SDL_GL_SetSwapInterval(1) < 0:
        print("Warning: Unable to set VSync! SDL Error: " + SDL_GetError().decode("utf-8"))
        exit(1)

    return window, gl_context



###############
## START MAIN
###############

if __name__ == "__main__":
    main()