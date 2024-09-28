# 9/27/2024 

import tkinter as tk    # tkinter for gui elements
import numpy as np      # array mgmt
import cnc_v1     # CNC class

class CNC_GUI:

    currentPos = np.array([float(0),float(0),float(0)]) # i don't remember what this is for
    pts = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]) #saved 4 point grid
    measurePts = [] # i should use this instead of pts since it's the same
    inc = 1 # movement increments (in mm)
    increments = [0.1, 1, 5, 10, 100] #movement map list
    curStr = '' # current string to write 
    currentState = "idle"

    btn_text = ""
    currPosStr = None
    ptsText = ""
    lbl_current_pos = None

    inputs = []
    labels = []
    buttons = []

    cnc = None

    port_name = ""

    def __init__ (self, port_name):
        self.port_name = port_name

    #
    # CNC related methods
    #
    def setPos (self, p): # sets position for p1-p4 buttons
        xyz_current = self.cnc.get_current_position()
        self.pts[p] = xyz_current
        self.ptsText[p].set(f"P{p+1}\n({self.pts[p][0]},{self.pts[p][1]},{self.pts[p][2]})")


    def moveToPoints(self, points):
        for y in range(len(points[0])):
            for x in range(len(points)):
                print(f"Moving to: X{points[x][y][0]} Y{points[x][y][1]}")
                z_current = 0;
                xyz = [points[x][y][0], points[x][y][1], z_current]
                self.updatePos_absolute(xyz)


    def updatePos_relative (self, xyz_offset):
        xyz_current = self.cnc.get_current_position()
        xyz_new = [x + y for x , y in zip(xyz_current, xyz_offset)]
        self.cnc.move_xyz_to(xyz_new)
        self.update_current_position()

    def updatePos_absolute (self, xyz):
        self.cnc.move_xyz_to(xyz)
        self.update_current_position()

    #
    # Chart related methods
    #
    def calculateMatrix (self):
        self.pts[4][0] = self.inputs[1][0].get("1.0","end-1c") # Y - split
        self.pts[4][1] = self.inputs[0][0].get("1.0","end-1c") # X - split
        measurePts = [[0.0,0.0,0.0]*(self.pts[4][0]+1)*(self.pts[4][1]+1)] #create array for all future points
        measurePts = np.reshape(np.array(measurePts),(self.pts[4][0]+1,self.pts[4][1]+1,3)) # convert to 3D numpy array (x split by y split by 3 coordinates)
        measurePts[0][0] = self.pts[0] #set corners 1-4
        measurePts[self.pts[4][0]][0] = self.pts[1]
        measurePts[0][self.pts[4][1]] = self.pts[2]
        measurePts[self.pts[4][0]][self.pts[4][1]] = self.pts[3]
        dist = np.subtract(measurePts[0][self.pts[4][1]], measurePts[0][0]) #3 number array for distance in cartesian 
        for x in range(self.pts[4][0]+1):
            measurePts[0][x] = np.add(measurePts[0][0], np.multiply(np.divide(dist,self.pts[4][0]),x)) # left side
        dist = np.subtract(measurePts[self.pts[4][0]][self.pts[4][1]], measurePts[self.pts[4][0]][0])
        for x in range(self.pts[4][0]+1):
            measurePts[self.pts[4][0]][x] = np.add(measurePts[self.pts[4][0]][0], np.multiply(np.divide(dist,self.pts[4][0]),x)) # right side
        for y in range(self.pts[4][0]+1): # fill in middle points
            dist = np.subtract(measurePts[self.pts[4][0]][y], measurePts[0][y])
            for x in range(self.pts[4][1]+1):
                measurePts[x][y] = np.add(measurePts[0][y], np.multiply(np.divide(dist,self.pts[4][1]),x))
        print(measurePts)
        self.moveToPoints(measurePts)

    #
    # GUI related methods
    #

    def updateInc (self): # updates increments for the increment button
        for x in range(len(self.increments)):
            if(self.inc == self.increments[x]):
                self.inc = self.increments[(x + 1) % len(self.increments)]
                break
        self.btn_text.set(f"Increment : {self.inc}")

    def placeGroup (self, group): # for when you have a list of tkinter objects to place (the list should be 2d, i.e., x = [[tk.Button(---), x, y]])
        for x in range(len(group)):
            group[x][0].place(x = group[x][1], y = group[x][2])

    def update_current_position (self):
        xyz = self.cnc.get_current_position()
        str = f"{xyz[0]:.3f}, {xyz[1]:.3f}, {xyz[2]:.3f}"
        self.currPosStr.set(str)

    def main (self):

        #
        # start CNC first because the GUI needs it
        #
        self.cnc = cnc_v1.Cnc(self.port_name)

        self.cnc.move_x_y_z_to("X", 0)
        self.cnc.move_x_y_z_to("X", 1)
        self.cnc.move_x_y_z_to("X", 0)

        #
        # GUI

        gui = tk.Tk() # initialize gui
        gui.title("CNC GUI Controller")
        gui.geometry("450x350")

        self.btn_text = tk.StringVar()
        self.currPosStr = tk.StringVar() #texts with variable strings!
        self.currPosStr.set("---, ---, ---")
        self.ptsText = [tk.StringVar(),tk.StringVar(),tk.StringVar(),tk.StringVar(), tk.StringVar()]

        for x in range(len(self.ptsText)):
            self.ptsText[x].set(f"P{x+1}")

        self.lbl_current_pos = tk.Label(gui, textvariable = self.currPosStr) #current position label
        self.lbl_current_pos.place(x = 300, y = 75)

        self.buttons = [
            [tk.Button(gui, text = "left" , command = lambda : self.updatePos_relative([-self.inc, 0, 0]), height = 2, width = 5) , 25, 75], #6 movement buttons
            [tk.Button(gui, text = "up"   , command = lambda : self.updatePos_relative([0, self.inc, 0]), height = 2, width = 5)   , 75, 25],
            [tk.Button(gui, text = "right", command = lambda : self.updatePos_relative([self.inc, 0, 0]), height = 2, width = 5), 125,75],
            [tk.Button(gui, text = "down" , command = lambda : self.updatePos_relative([0, -self.inc, 0]), height = 2, width = 5) , 75, 125],
            [tk.Button(gui, text = "z down" , command = lambda : self.updatePos_relative([0, 0, -self.inc]), height = 2, width = 5) , 200, 125],
            [tk.Button(gui, text = "z up" , command = lambda : self.updatePos_relative([0, 0, self.inc]), height = 2, width = 5) , 200, 25],
            [tk.Button(gui, textvariable = self.btn_text, command = lambda : self.updateInc(), height = 2, width = 12), 200, 75], #Increments button
            [tk.Button(gui, textvariable = self.ptsText[0], command = lambda : self.setPos(0), height = 2, width = 10), 25, 175], #p1 - p4 buttons
            [tk.Button(gui, textvariable = self.ptsText[1], command = lambda : self.setPos(1), height = 2, width = 10), 125, 175],
            [tk.Button(gui, textvariable = self.ptsText[2], command = lambda : self.setPos(2), height = 2, width = 10), 25, 225],
            [tk.Button(gui, textvariable = self.ptsText[3], command = lambda : self.setPos(3), height = 2, width = 10), 125, 225],
            [tk.Button(gui, text = "P1", command = lambda : self.updatePos_absolute(self.pts[0]), height = 1, width = 4), 25, 300], # move to p1-p4 buttons
            [tk.Button(gui, text = "P2", command = lambda : self.updatePos_absolute(self.pts[1]), height = 1, width = 4), 72, 300],
            [tk.Button(gui, text = "P3", command = lambda : self.updatePos_absolute(self.pts[2]), height = 1, width = 4), 119, 300],
            [tk.Button(gui, text = "P4", command = lambda : self.updatePos_absolute(self.pts[3]), height = 1, width = 4), 166, 300],
            [tk.Button(gui, text = "CALC", command = lambda : self.calculateMatrix()), 300, 200] #calculate matrix
        ]

        self.inputs = [
            [tk.Text(gui, height = 1, width = 10),300,25], #text entries (rows)
            [tk.Text(gui, height = 1, width = 10),300,50]  #cols
        ]

        self.labels = [
            [tk.Label(gui,text =  "Rows :"), 250, 25], #just plaintext :)
            [tk.Label(gui,text = "Cols :"), 250, 50],
            [tk.Label(gui,text = "Go to :"), 25, 275]   
        ]

        self.btn_text.set(f"Increment : {self.inc}") #update increment button

        self.placeGroup(self.buttons) #create buttons, inputs and labels
        self.placeGroup(self.inputs)
        self.placeGroup(self.labels)

        gui.mainloop()



i = CNC_GUI("COM3")
i.main()    
