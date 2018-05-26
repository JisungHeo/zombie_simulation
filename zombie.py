#!/usr/bin/python

# ---------------- READ ME ---------------------------------------------
# This Script is Created Only For Practise And Educational Purpose Only
# This is an Example Of Tkinter Canvas Graphics
# This Script Is Created For http://bitforestinfo.blogspot.in
# This Script is Written By
#
#
##################################################
######## Please Don't Remove Author Name #########
############### Thanks ###########################
##################################################
#
#
__author__='''

######################################################
                Strawberry & Octopus group
######################################################
    Kim Jisoo
    Heo Jisung
######################################################
'''
print __author__
# ============ CONFIGURATIONS =====================
NUMBER_OF_CITIES = 6
POPULATION = [9668,1030,1009,1001,1193,843]
HUMAN = [9668,1030,1009,1001,1193,843]
WOUNDED = [0,0,0,0,0,0]
ZOMBIE = [0,0,0,0,0,0] 
DEAD = [0,0,0,0,0,0]
SOLDIER = [0,0,0,0,0,0]

UNIVERS_COLOR = "black"
TRANSPARENCY_LEVEL = 1
SCREEN_SAVER_CLOSING_EVENTS = ['<Any-KeyPress>', '<Any-Button>']


# =====================================================

# import module
import Tkinter
import time
import random
import math

# Canvas class
class Sky(Tkinter.Canvas):
 def __init__(self, *args, **kwargs):
  Tkinter.Canvas.__init__(self, *args, **kwargs)
  self.canvas = Tkinter.Canvas
  self.cities=[]
  self.create_cities()

  # Function For Creating Stars
 def create_cities(self):
  for i in range(NUMBER_OF_CITIES):
   self.cities.append(City(self, i))
  return

  # Function For Updating Stars Coordinates
 def update_screen(self):
  for i in self.cities:
    i.draw_city()
  return
#
#City Class Object
class City:
 def __init__(self, parent, index):
  self.parent = parent # screen
  self.index = index # city number
  self.position_setting()
  self.draw_city()

 # Setup City Position
 def position_setting(self):
  index = self.index
  width = 1280
  height = 720
  if(index == 0):#Seoul
    self.x1 = width*0.5
    self.y1 = height*0.55
  elif(index == 1):#Goyang
    self.x1 = width*0.5
    self.y1 = height*0.15
  elif(index == 2):#YongIn
    self.x1 = width*0.8
    self.y1 = height*0.35
  elif(index == 3):#Sungnam
    self.x1 = width*0.25
    self.y1 = height*0.8
  elif(index == 4):#Suwon
    self.x1 = width*0.75
    self.y1 = height*0.8
  else:#Buchun
    self.x1 = width*0.2
    self.y1 = height*0.35
  return

#Calculate position of City
 def calculate_position(self):
  index = self.index
  x1 = self.index
  y1 = self.index
  
  #Cacluate postiion
  radius = math.sqrt(POPULATION[index])*4
  x1 = self.x1 - radius/2
  y1 = self.y1 - radius/2
  x2,y2=x1+radius, y1+radius
  position = (x1,y1,x2,y2)
  return position

#Calculate proprtion of human, wounded, zombie, dead in City
 def caculate_proportion(self):
  index = self.index
  POPULATION[index] = HUMAN[index]+WOUNDED[index]+ZOMBIE[index]+DEAD[index]
  allP=POPULATION[index]
  hp = 360.0 * HUMAN[index]/allP
  wp = 360.0 * WOUNDED[index]/allP
  zp = 360.0 * ZOMBIE[index]/allP
  dp = 360.0 * DEAD[index]/allP
  sp = 360.0 * SOLDIER[index]/allP
  return (hp,wp,zp,dp,sp)
  
#Draw City
 def draw_city(self):
  parent = self.parent
  
  #Cacluate postiion
  position = self.calculate_position()
  #Calculate percentage
  (hp,wp,zp,dp,sp) = self.caculate_proportion()
  if(hp==360): hp = 359.999
  parent.create_arc(position, fill="#FAF402", outline="#FAF402", start=0, extent = hp)
  parent.create_arc(position, fill="#00AC36", outline="#00AC36", start=hp, extent = wp)
  parent.create_arc(position, fill="#7A0871", outline="#7A0871", start=hp+wp, extent = zp)
  parent.create_arc(position, fill="#E00022", outline="#E00022", start=hp+wp+zp, extent = dp)
  parent.create_arc(position, fill="#9CF0C9", outline="#9CF0C9", start=hp+wp+zp+dp, extent = sp)
  #lbl = Label(parent.canvas, text=hp)
  #lbl.pack()
  return

# main function
def main():
 # create window object
 root=Tkinter.Tk()
 # create canvas
 screen = Sky(root,bg=UNIVERS_COLOR)
 screen.pack(expand="yes",fill="both")

 # Tkinter Window Configurations
 root.wait_visibility(screen)
 root.wm_attributes('-fullscreen', True)
 root.overrideredirect(1)
 
 # Windows Destroy Function
 def out(event):
  root.destroy()
  return

 # Event Bindings
 for seq in SCREEN_SAVER_CLOSING_EVENTS:
  root.bind_all(seq, out)

 while True:
  root.update()
  root.update_idletasks()
  screen.update_screen()

# main trigger function
if __name__ == '__main__':
 main()
