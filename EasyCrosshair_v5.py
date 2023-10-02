# IMPORTS
import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor
from turtle import *
import win32gui, win32con, win32api
import threading
import ctypes


# hide exe window at start
exe_window = win32gui.GetForegroundWindow()
if win32gui.GetWindowText(exe_window)[-3:] == "exe":
    win32gui.ShowWindow(exe_window, win32con.SW_HIDE)

# change taskbar icon
myappid = 'Easy.Crosshair.V.5'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


# MAIN PROGRAM
class App(tk.Frame):
    canvas_size = 604
    n=12
    psize = canvas_size//n - 3
    
    fgd= "#AAA"
    bgd = "#1a1a1a"
    rgb = "#F00"
    colour = "#00FF00"
    selected = {}
    def __init__(self, parent):
        super().__init__(parent)
        self.p = parent

        
    # standard menu setup
        parent.title("EasyCrosshair")
        parent.geometry('700x605+000+50')
        try:
            parent.iconbitmap(r"assets/icon.ico")
        except tk.TclError:
            pass
        parent.config(bg=self.bgd)
        parent.resizable(False,False)
        parent.wm_attributes("-topmost", True)


    # canvas
        # set up canvas for turtle
        self.canvas = tk.Canvas(parent, width=self.canvas_size, height=self.canvas_size, highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=10)
        self.screen = TurtleScreen(self.canvas)
        self.screen.bgcolor("#1a1a1a")
        self.canvas.bind('<Button-1>',self.create)
        self.canvas.bind('<B1-Motion>',self.create)
        self.canvas.bind('<Button-3>',self.delete)
        self.canvas.bind('<B3-Motion>',self.delete)
        
        
    # buttons
        # frame 1
        frame1 = tk.Frame(parent, bg=self.bgd)
        frame1.grid(row = 7, column = 1, pady = 5)
        
        # size button
        szborder = tk.Frame(frame1, highlightbackground=self.rgb, highlightcolor=self.rgb, highlightthickness = 2, bd=0)
        szborder.grid(row = 0, column = 0, padx = 2)
        sizes = [i for i in range(6,51,2)]
        self.svar = tk.IntVar()
        self.size_entry = tk.Spinbox(szborder, bg="#1a1a1a", fg=self.fgd, width=3, font=("Moderne Sans","17"), values=sizes, readonlybackground="#1a1a1a", textvariable=self.svar)
        self.size_entry.delete(0,"end")
        self.size_entry.insert(0,"12")
        self.size_entry.config({"state":"readonly"})
        self.size_entry.grid()
        
        # apply the size
        asborder = tk.Frame(frame1, highlightbackground=self.rgb, highlightthickness = 2, bd=0)
        asborder.grid(row = 0, column = 1, padx = 2)
        self.size_btn = tk.Button(asborder, text="+", font=("Moderne Sans","8"), bd=5, fg=self.fgd, bg=self.bgd, activebackground="#444", relief="flat", command=self.update_size)
        self.size_btn.grid()

        
        # frame 2
        frame2 = tk.Frame(parent, bg=self.bgd)
        frame2.grid(row = 9, column = 1, padx = 5)
        
        # colour change button
        ccborder = tk.Frame(frame2, highlightbackground=self.fgd, highlightthickness = 2, bd=0)
        ccborder.grid(row = 0, column = 0, pady = 5)
        self.colour_btn = tk.Button(ccborder, width=2, bd=5, bg=self.colour, relief="ridge", command=self.change_colour)
        self.colour_btn.grid()

        # clear button
        clborder = tk.Frame(frame2, highlightbackground=self.rgb, highlightthickness = 2, bd=0)
        clborder.grid(row = 1, column = 0, pady = 2)
        tk.Button(clborder, text="Clear", font=("Moderne Sans","11"), width=5, bd=5, fg=self.fgd, bg=self.bgd, activebackground="#444", relief="flat", command=self.clear).grid()
        
        # apply button
        apborder = tk.Frame(frame2, highlightbackground=self.rgb, highlightthickness = 2, bd=0)
        apborder.grid(row = 2, column = 0, pady = 2)
        tk.Button(apborder, text="Apply", font=("Moderne Sans","11"), width=5, bd=5, fg=self.fgd, bg=self.bgd, activebackground="#444", relief="flat", command=self.apply).grid()

    # ninja turtles (because i am using the turtle library)
        # introducing 'leonardo' the turtle (for base UI creation)
        self.leo = RawTurtle(self.screen)
        self.leo.speed(speed=0)
        self.leo.color("#000")
        self.leo.ht()
        self.leo.up()
        # introducing 'donatello' the turtle (for crosshair editor drawing)
        self.don = RawTurtle(self.screen)
        self.don.speed(speed=0)
        self.don.color(self.colour)
        self.don.ht()

        
    # start
        self.start()


# methods for the buttons in UI
    # change colour
    def change_colour(self):
        colour = askcolor(title="Colour Chooser")
        self.colour = colour[1]
        if self.colour == "#000000":
            self.colour = "#000001"
        self.don.color(self.colour)
        self.colour_btn.config(bg=colour[1])
        for i in self.selected.items():
            self.don.setpos(i[1])
            self.don.dot(self.psize)


    # change the editor size
    def update_size(self):
        self.n=self.svar.get()
        self.psize = self.canvas_size//self.n - 3
        self.start()

            
    # clear the canvas
    def clear(self):
        self.don.clear()
        self.reset_grid()
        self.selected={}


    # apply the drawn crosshair to the screen
    def apply(self):
        crosshair.apply(self.grid, self.colour)


# canvas stuff
    # find closest node to mouse pos on click
    def closest_node(self, pos):
        list_nodes = []
        for i in self.nodes.items():
            list_nodes.append(i[1])
        distance_metric = lambda x: (x[0] - pos[0])**2 + (x[1] - pos[1])**2
        node = min(list_nodes, key=distance_metric)
        return node

    # create dot at closest node to mouse pos on click
    def create(self, event):
        # find closest node to cursor
        xy = (event.x - self.canvas_size/2, -event.y + self.canvas_size/2)
        x,y = self.closest_node(xy)
        self.don.up()
        self.don.setpos(x,y)
        self.don.dot(self.psize)

        node = list(self.nodes.keys())[list(self.nodes.values()).index( (x, y) )]
        self.grid[node//self.n][node%self.n] = 1

        self.selected[node] = (x, y)

    # delete dot at closest node to mouse pos on click
    def delete(self, event):
        # find closest node to cursor
        xy = (event.x - self.canvas_size/2, -event.y + self.canvas_size/2)
        x,y = self.closest_node(xy)
        self.don.up()
        self.don.setpos(x,y)
        self.don.color("#1a1a1a")
        self.don.dot(self.psize)
        self.don.color(self.colour)

        node = list(self.nodes.keys())[list(self.nodes.values()).index( (x, y) )]
        self.grid[node//self.n][node%self.n] = 0

        try:
            self.selected.pop(node)
        except KeyError:
            pass
        self.don.color(self.colour)
        

    # creates grid to draw in
    def create_nodes(self):     
        def create_square(size, posx, posy, index):
            self.leo.setpos(posx, posy)
            self.leo.down()
            
            # draw a square
            for _ in range(2):
                self.leo.forward(size)
                self.leo.left(90)
            self.leo.up()
            
            # get center of node
            for _ in range(2):
                self.leo.forward(size//2)
                self.leo.left(90)
            self.nodes[index] = (int(self.leo.pos()[0]), int(self.leo.pos()[1]))
            #self.leo.write(str(index), font=("Courier", 8, "bold"), align="center")

            # reset to original pos
            self.leo.setpos(posx, posy)

        self.nodes = {}
        index = 0
        size = self.canvas_size//self.n
        offset=self.canvas_size//2

        # leo setup
        self.leo.width(1)
        self.leo.pencolor("#999")
        self.leo.fillcolor("#1a1a1a")

        # loop for grid creation
        for y in range(self.n):
            posy = (offset-size*y)-size
            for x in range(self.n):
                posx = (-offset+size*x)
                create_square(size, posx, posy, index)
                index+=1

        center = size * (self.n//2)
        self.leo.up()
        self.leo.color("#FFF")
        self.leo.width(1)

        # cross to help find center
        self.leo.left(90) # make turtle face up for loop
        for i in [(-offset, offset-center), (-offset+center, offset)]:
            self.leo.right(90)
            self.leo.setpos(i)
            self.leo.down()
            self.leo.forward(self.n*size)
            self.leo.up()
        #self.leo.left(90)

        self.leo.pencolor("#999")
        self.leo.setpos(-offset, offset)
        self.leo.down()
        self.leo.forward(self.n*size)
        self.leo.up()

        self.leo.left(90)
                
            
    # creates the graph
    def start(self):
        self.leo.clear()
        self.clear()
        self.screen.tracer(0)
        self.create_nodes()
        self.screen.update()
        self.reset_grid()


    # resets grid to blank
    def reset_grid(self):
        self.grid = []
        for i in range(self.n):
            self.grid.append([0]*self.n)



# CROSSHAIR
class Crosshair(tk.Frame):
    def __init__(self, parent, dim):
        super().__init__(parent)
        self.p = parent
        
        x = dim[0]//2 - 50
        y = dim[1]//2 - 50

        # setup window
        parent.resizable(False, False)
        parent.geometry(f"100x100+{x}+{y}")
        parent.overrideredirect(True)
        parent.config(bg="#123")
        parent.wm_attributes("-disabled", True)

        # canvas to draw crosshair on
        canvas = tk.Canvas(parent, bg="#000", width=100, height=100, highlightthickness=0)
        canvas.pack(anchor = 'c')
        self.screen = TurtleScreen(canvas)
        self.screen.bgcolor("#000")
        
        hwnd = win32gui.FindWindow(None, parent.title())
        self.set_clickthrough(hwnd)

    # ninja turtles (because i am using the turtle library)
        # introducing 'raphael' the turtle (for crosshair creation)
        self.rap = RawTurtle(self.screen)
        self.rap.speed(speed=0)
        self.rap.color("#F00")
        self.rap.ht()
        self.rap.up()

    # draws the created crosshair
    def apply(self, grid, colour):
        offset = (100 - len(grid)) // 2
        self.rap.clear()
        self.rap.color(colour)
        self.screen.tracer(0)
        for c1, y in enumerate(grid):
            for c2, x in enumerate(y):
                if bool(x):
                    self.rap.setpos(c2-50+offset, -c1+50-offset)
                    self.rap.dot(2)
        self.screen.update()
            
    # loop to always keep the crosshair on top of all other windows
    def top(self):
        self.p.attributes("-topmost", True)
        self.p.after(10, self.top)

    # make the window clickthroughable
    def set_clickthrough(self, hwnd):
        try:
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            styles = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, 0x00000001)
        except Exception:
            pass

            

# START
if __name__ == "__main__":
    # window set up
    main = tk.Tk()
    sub = tk.Toplevel()

    dim = (main.winfo_screenwidth(), main.winfo_screenheight())
    app = App(main)
    crosshair = Crosshair(sub, dim)

    # thread for always on top loop
    thread_1 = threading.Thread(target=crosshair.top)
    thread_1.start()
    tk.mainloop()
