import argparse
import simpy
import numpy as np
import random
#from zombie import *

import Tkinter
import time
import math

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--strategy', type=int, default=0)
    parser.add_argument('--num_replication', type=int, default=30)
    config = parser.parse_args()

#Global variable
NUMBER_OF_CITIES = 6
UNIVERS_COLOR = "white"
TRANSPARENCY_LEVEL = 1
SCREEN_SAVER_CLOSING_EVENTS = ['<Any-KeyPress>', '<Any-Button>']
DAY = 0

num_zombie_threshold = 147
num_soldiers = 176
power_zombie = 15
power_human = 15
power_wounded = 0
power_soldier = 500
adjacent_cities = {0:[0,1,2,3,4,5],1:[0,1,2,5],2:[0,1,2,3],3:[0,2,3,4],4:[0,3,4,5],5:[0,1,4,5]}
army_strategy = config.strategy #0: move/regular, 1: move/zombie, 2: static/proportional, 3: static/even
initial_soldiers = {0:[176,0,0,0,0,0],1:[176,0,0,0,0,0],2:[115, 13, 12, 12, 14, 10],3:[31,29,29,29,29,29]}

POPULATION = [9668,1030,1009,1001,1193,843]
HUMAN = [9668,1030,1009,1001,1193,843]
WOUNDED = [0,0,0,0,0,0]
ZOMBIE = [0,0,0,0,0,0]
DEAD = [0,0,0,0,0,0]
SOLDIER = [0,0,0,0,0,0]

STATISTIC_SUVIVOR = [0,0,0,0,0,0]
STATISTIC_WOUNDED = [0,0,0,0,0,0]
STATISTIC_DEAD = [0,0,0,0,0,0]
ZOMBIE_DEFEATED = 0
HUMAN_DEFEATED = 0

animation = False
num_replications = config.num_replication

#
#
#Entity
class Zombie:
    def __init__(self, sim):
        self.HP = 1000
        self.power = abs(np.random.normal(power_zombie,5))
        self.sim = sim
        self.human = None
        self.wounded = None
        self.soldier = None

    def fight(self):
        if self.human != None:
            self.HP -= self.human.power
            self.human = None
        if self.wounded != None:
            self.HP -= self.wounded.power
            self.wounded = None
        if self.soldier != None:
            self.HP -= self.soldier.power
            self.soldier = None

    def move(self):
        # move to adjacent cities
        self.city = random.choice(adjacent_cities[self.city])

    def update(self):
        self.fight()
        self.move()

class Human:
    def __init__(self, sim):
        self.HP = 100
        self.sim = sim
        self.power = abs(np.random.normal(power_human,5))
        self.fightable = False # Extract Fighter
        self.zombie = None
        self.infected = False

    def fight(self):
        if self.zombie != None:
            self.HP -= self.zombie.power
            self.zombie = None
            if np.random.uniform(0,1) < 0.3:
                self.infected = True

    def move(self):
        # move to adjacent cities
        if np.random.uniform(0,1)<0.2:
            zombie_proportion = {}
            for i in adjacent_cities[self.city]:
                num_zombies = self.sim.num_zombies[i] #len([z for z in self.sim.zombies if z.city == i])
                num_humans = self.sim.num_humans[i] #len([h for h in self.sim.humans if h.city == i])
                num_woundeds = self.sim.num_woundeds[i] #len([w for w in self.sim.woundeds if w.city == i])
                num_soldiers = self.sim.num_soldiers[i] #len([s for s in self.sim.soldiers if s.city == i])
                zombie_proportion[i]=(float(num_zombies)/(num_humans+num_woundeds+num_soldiers+1))
            min_prop = min(zombie_proportion.values())
            city = random.choice([key for key in zombie_proportion.keys() if zombie_proportion[key]==min_prop])
            self.city = city #random.choice(adjacent_cities[self.city]

    def update(self):
        self.fight()
        self.move()

class Wounded:
    def __init__(self, sim):
        self.HP = 50
        self.fightable = False
        self.sim = sim
        self.power = power_wounded#abs(np.random.normal(power_wounded,5))
        self.zombie = None
        self.infected = False

    def fight(self):
        if self.zombie != None:
            self.HP -= self.zombie.power
            self.zombie = None
            if np.random.uniform(0,1) < 0.05:
                self.infected = True

    def move(self):
        self.city = self.city # cannot move

    def update(self):
        self.fight()
        self.move()

class Soldier:
    def __init__(self, sim):
        self.HP = 5000
        self.sim = sim
        self.power = abs(np.random.normal(power_soldier,5))
        self.zombie = None
        self.infected = False

    def fight(self):
        if self.zombie != None:
            self.HP -= self.zombie.power
            self.zombie = None
            if np.random.uniform(0,1) < 0.1:
                self.infected = True

    def move(self):
        if army_strategy == 0:
            self.city = (self.city + 1) % 6
        elif army_strategy == 1:
            zombie_proportion = {}
            for i in adjacent_cities[self.city]:
                num_zombies = self.sim.num_zombies[i] #len([z for z in self.sim.zombies if z.city == i])
                num_humans = self.sim.num_humans[i] #len([h for h in self.sim.humans if h.city == i])
                num_woundeds = self.sim.num_woundeds[i] #len([w for w in self.sim.woundeds if w.city == i])
                num_soldiers = self.sim.num_soldiers[i] #len([s for s in self.sim.soldiers if s.city == i])
                zombie_proportion[i]=(float(num_zombies)/(num_humans+num_woundeds+num_soldiers+1))
            max_prop = max(zombie_proportion.values())
            city = random.choice([key for key in zombie_proportion.keys() if zombie_proportion[key]==max_prop])
            self.city = city #random.choice(adjacent_cities[self.city]
        elif army_strategy == 2:
            self.city = self.city
        elif army_strategy == 3:
            self.city = self.city

    def update(self):
        self.move()
        self.fight()
#
#
##Main
class Simulation():
    def __init__(self, env):
        self.env = env
        self.env.process(self.run())

        self.activated = False
        self.soldier_next_city = 1

        num_zombie = [1,0,0,0,0,0] # Seoul, Goyang, Yongin Sungnam Bucheon Suwon Bucheon
        num_humans = [9668, 1030, 1009, 1001, 1193, 843]
        num_woundeds = [0,0,0,0,0,0]
        num_soldiers = [0,0,0,0,0,0] #[31,29,29,29,29,29]
        #print 'simulation started'
        self.zombies = []
        self.humans = []
        self.woundeds = []
        self.soldiers = []

        for i in range(6):
            for _ in range(num_zombie[i]):
                zombie = Zombie(self)
                zombie.city = i
                self.zombies.append(zombie)
            for _ in range(num_humans[i]):
                human = Human(self)
                human.city = i
                self.humans.append(human)
            for _ in range(num_woundeds[i]):
                wounded = Wounded(self)
                wounded.city = i
                self.woundeds.append(wounded)
            for _ in range(num_soldiers[i]):
                soldier = Soldier(self)
                soldier.city = i
                self.soldiers.append(soldier)

        global DEAD
        DEAD = [0,0,0,0,0,0]

    def activate_army(self):
        num_soldiers = initial_soldiers[army_strategy]
        for i in range(6):
            for _ in range(num_soldiers[i]):
                soldier = Soldier(self)
                soldier.city = i
                self.soldiers.append(soldier)

    def update(self):
        for zombie in self.zombies:
            zombie.update()
        for human in self.humans:
            human.update()
            if human.infected:
                zombie = Zombie(self)
                zombie.city = human.city
                self.humans.remove(human)
                self.zombies.append(zombie)
            elif human.HP <= 50:
                wounded = Wounded(self)
                wounded.city = human.city
                self.humans.remove(human)
                self.woundeds.append(wounded)
        for wounded in self.woundeds:
            wounded.update()
            if wounded.infected:
                zombie = Zombie(self)
                zombie.city = wounded.city
                self.woundeds.remove(wounded)
                self.zombies.append(zombie)



        #print 'before calculate : ', len(self.soldiers)
        infection = 0;
        for soldier in self.soldiers:
            soldier.update()
            if soldier.infected == True:
                infection = infection + 1;
                zombie = Zombie(self)
                zombie.city = soldier.city
                self.soldiers.remove(soldier)
                self.zombies.append(zombie)
            elif soldier.HP <= 50:
                wounded = Wounded(self)
                wounded.city = soldier.city
                self.soldiers.remove(soldier)
                self.woundeds.append(wounded)
        #print 'after calculate : ', len(self.soldiers)
        #print 'infection : ', infection
        #for i in range(6):
        #    print 'soldiers in %d:'%i,len([s for s in self.soldiers if (s.city == i and s.infected==True)])
        #    print 'soldiers in %d:'%i,len([s for s in self.soldiers if (s.city == i and s.infected==False)])

        for i in range(6):
            num_dead_zombies = len([zombie for zombie in self.zombies if zombie.city == i and zombie.HP <= 0])
            num_dead_humans = len([human for human in self.humans if human.city == i and human.HP <= 0])
            num_dead_woundeds = len([wounded for wounded in self.woundeds if wounded.city == i and wounded.HP <= 0])
            num_dead_soldiers = len([soldier for soldier in self.soldiers if soldier.city == i and soldier.HP <= 0])
            total_deads = num_dead_zombies + num_dead_humans + num_dead_woundeds + num_dead_soldiers
            DEAD[i] += total_deads
        self.zombies = [zombie for zombie in self.zombies if zombie.HP > 0]
        self.humans = [human for human in self.humans if human.HP > 0]
        self.woundeds = [wounded for wounded in self.woundeds if wounded.HP > 0]
        self.soldiers = [soldier for soldier in self.soldiers if soldier.HP > 0]
        #print 'total soldiers 1 : ', len(self.soldiers)-num_dead_soldiers
        #for i in range(6):
        #    print 'soldiers in %d:'%i,len([s for s in self.soldiers if (s.city == i and s.infected==False)])
        self.soldier_next_city = (self.soldier_next_city+1) % 6
        #print 'city:', self.soldier_next_city
        #print 'total soldiers:',len(self.soldiers)

    def run(self):
        while(True):
            global DAY
            DAY = self.env.now
            #print DAY, 'day'
            zombies = {}
            humans = {}
            woundeds = {}
            soldiers = {}

            global soldier_city
            soldier_city = 1;

            self.num_zombies = {}
            self.num_humans = {}
            self.num_woundeds = {}
            self.num_soldiers = {}
            for i in range(6):
                zombies[i] = [zombie for zombie in self.zombies if zombie.city == i]
                humans[i] = [human for human in self.humans if human.city == i]
                woundeds[i] = [wounded for wounded in self.woundeds if wounded.city == i]
                soldiers[i] = [soldier for soldier in self.soldiers if soldier.city == i]

                self.num_zombies[i] = len(zombies[i])
                self.num_humans[i] = len(humans[i])
                self.num_woundeds[i] = len(woundeds[i])
                self.num_soldiers[i] = len(soldiers[i])
                #print 'soldiers in ', i, ': ', len(soldiers[i])

            for i in range(6):
                for j in range(min(len(zombies[i]), len(humans[i]))):
                    humans[i][j].zombie = zombies[i][j]
                    zombies[i][j].human = humans[i][j]
                for j in range(min(len(zombies[i]), len(woundeds[i]))):
                    woundeds[i][j].zombie = zombies[i][j]
                    zombies[i][j].human = woundeds[i][j]
                for j in range(min(len(zombies[i]), len(soldiers[i]))):
                    soldiers[i][j].zombie = zombies[i][j]
                    zombies[i][j].human = soldiers[i][j]

            global HUMAN
            global WOUNDED
            global ZOMBIE
            global SOLDIER
            HUMAN = self.num_humans.values()
            WOUNDED = self.num_woundeds.values()
            ZOMBIE = self.num_zombies.values()
            SOLDIER = self.num_soldiers.values()
            #print 'Survivor:',[HUMAN[i] for i in range(6)]
            #print 'Wounded:', WOUNDED
            #print 'Deads:', DEAD

            if animation==True:
                root.update()
                root.update_idletasks()
                screen.update_screen()

            self.update()
            if self.activated == False and len(self.zombies) >= num_zombie_threshold:
                self.activate_army()
                self.activated = True
                #print 'army activated'
            if len(self.zombies) == 0:
                print 'zombies have been defeated at ', self.env.now
                global ZOMBIE_DEFEATED
                ZOMBIE_DEFEATED += 1
                break
            elif len(self.humans) == 0:
                print 'humans have been defeated at ', self.env.now
                global HUMAN_DEFEATED
                HUMAN_DEFEATED += 1
                break
            yield self.env.timeout(1)

# Canvas class
class Sky(Tkinter.Canvas):
 def __init__(self, *args, **kwargs):
  Tkinter.Canvas.__init__(self, *args, **kwargs)

  self.cities=[]
  self.create_cities()

  # Function For Creating City
 def create_cities(self):
  for i in range(NUMBER_OF_CITIES):
   self.cities.append(City(self, i))
  return
 #Function for information
 def write_information(self):
     parent = self
     #DAY
     parent.create_text(30 , 20 , font="Purisa", text= 'DAY : ')
     parent.create_text(60 , 20 , font="Purisa", text= DAY)
     #Infection Rate
     infection_rate = (100.0* sum(ZOMBIE))/sum(POPULATION)
     infection_rate = round(infection_rate,2)
     parent.create_text(60 , 50 , font="Purisa", text= 'Infection Rate : ')
     parent.create_text(140 , 50 , font="Purisa", text= infection_rate)
     parent.create_text(170 , 50 , font="Purisa", text= '%')

     #Legend
     parent.create_text(40 , 100 , font="Purisa", text= 'Human')
     parent.create_line(80, 100, 120, 100, fill="#FAF402", width=8)
     parent.create_text(40 , 130 , font="Purisa", text= 'Wounded')
     parent.create_line(80, 130, 120, 130, fill="#00AC36", width=8)
     parent.create_text(40 , 160 , font="Purisa", text= 'Zombie')
     parent.create_line(80, 160, 120, 160, fill="#7A0871", width=8)
     parent.create_text(40 , 190 , font="Purisa", text= 'Dead')
     parent.create_line(80, 190, 120, 190, fill="#E00022", width=8)
     parent.create_text(40 , 220 , font="Purisa", text= 'Soldier')
     parent.create_line(80, 220, 120, 220, fill="#9CF0C9", width=8)

 # Function For Updating City Shape
 def update_screen(self):
     self.delete("all")
     self.write_information()
     for i in self.cities:
         i.draw_city()
         i.write_dead_num()
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
  parent = self.parent

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
  POPULATION[index] = HUMAN[index]+WOUNDED[index]+ZOMBIE[index]+DEAD[index]+SOLDIER[index]
  allP=POPULATION[index]
  if(allP == 0): return (0,0,0,0,0)
  epsilon = 0.01
  hp = math.floor(360.0 * HUMAN[index]/(allP+epsilon))
  wp = math.floor(360.0 * WOUNDED[index]/(allP+epsilon))
  zp = math.floor(360.0 * ZOMBIE[index]/(allP+epsilon))
  dp = math.floor(360.0 * DEAD[index]/(allP+epsilon))
  sp = math.floor(360.0 * SOLDIER[index]/(allP+epsilon))
  return (hp,wp,zp,dp,sp)

#Draw City
 def draw_city(self):
  parent = self.parent

  #Cacluate postiion
  position = self.calculate_position()
  #Calculate percentage
  (hp,wp,zp,dp,sp) = self.caculate_proportion()
  #draw arc
  if(hp==360): hp = 359.999
  parent.create_arc(position, fill="#FAF402", outline="#FAF402", start=0, extent = hp)
  parent.create_arc(position, fill="#00AC36", outline="#00AC36", start=hp, extent = wp)
  parent.create_arc(position, fill="#7A0871", outline="#7A0871", start=hp+wp, extent = zp)
  parent.create_arc(position, fill="#E00022", outline="#E00022", start=hp+wp+zp, extent = dp)
  parent.create_arc(position, fill="#9CF0C9", outline="#9CF0C9", start=hp+wp+zp+dp, extent = sp)
  return
#Write Letter
 def write_dead_num(self):
     index = self.index
     parent = self.parent
     (x1,y1,x2,y2) = self.calculate_position()
     POPULATION[index]
     parent.create_text(x2 , y1 , font="Purisa", text=DEAD[index])
     parent.create_text(x1 , y2 , font="Purisa", text=DEAD[index])


if animation==True:
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

#print 'slkdfjldsjflskdjfdsdfj'
for i in range(num_replications):
    env = simpy.Environment()
    simulation = Simulation(env)
    env.run(until=1000)
    STATISTIC_SUVIVOR = [HUMAN[j]+STATISTIC_SUVIVOR[j] for j in range(6)]
    STATISTIC_WOUNDED = [WOUNDED[j]+STATISTIC_WOUNDED[j] for j in range(6)]
    STATISTIC_DEAD = [DEAD[j]+STATISTIC_DEAD[j] for j in range(6)]
    print 'Replication ', i
    print 'STATISTIC_SURVIOVR:',STATISTIC_SUVIVOR
    print 'STATISTIC_WOUNDED:', STATISTIC_WOUNDED
    print 'STATISTIC_DEAD:',STATISTIC_DEAD
    print 'ZOMBIE_DEFEATED:', ZOMBIE_DEFEATED
    print 'HUMAN_DEFEATED:', HUMAN_DEFEATED
