import simpy
import numpy as np
import random

num_zombie_threshold = 147
num_soldiers = 176

class Zombie:
    def __init__(self):
        self.HP = 1000

    def fight(self):
        self.HP -= abs(np.random.normal(15,5))

    def move(self):
        # move to adjacent cities
        if self.city == 0: # Seoul
            self.city = random.choice([0,1,2,3,4,5])
        elif self.city == 1: # Goyang
            self.city = random.choice([0,1,2,5])
        elif self.city == 2: # YongIn
            self.city = random.choice([0,1,2,3])
        elif self.city == 3: # Sungnam
            self.city = random.choice([0,2,3,4])
        elif self.city == 4: # Suwon
            self.city = random.choice([0,3,4,5])
        elif self.city == 5: # Bucheon
            self.city = random.choice([0,1,4,5])

    def update(self):
        self.fight()
        self.move()

class Human:
    def __init__(self):
        self.HP = 100
        self.fightable = False # Extract Fighter

    def fight(self):
        if self.fightable:
            self.HP -= abs(np.random.normal(15,5))

    def move(self):
        # move to adjacent cities
        if self.city == 0: # Seoul
            self.city = random.choice([0,1,2,3,4,5])
        elif self.city == 1: # Goyang
            self.city = random.choice([0,1,2,5])
        elif self.city == 2: # YongIn
            self.city = random.choice([0,1,2,3])
        elif self.city == 3: # Sungnam
            self.city = random.choice([0,2,3,4])
        elif self.city == 4: # Suwon
            self.city = random.choice([0,3,4,5])
        elif self.city == 5: # Bucheon
            self.city = random.choice([0,1,4,5])

    def update(self):
        self.fight()
        self.move()

class Wounded:
    def __init__(self):
        self.HP = 50
        self.fightable = False

    def fight(self):
        if self.fightable:
            self.HP -= abs(np.random.normal(15,5))

    def move(self):
        self.city = self.city # cannot move

    def update(self):
        self.fight()
        self.move()

class Soldier:
    def __init__(self):
        self.HP = 500

    def fight(self):
        self.HP -= 10

    def move(self):
        self.city = np.random.randint(1,7)

    def update(self):
        self.fight()
        self.move()


class Simulation():
    def __init__(self, env):
        env.process(self.run())

        num_zombie = [1,0,0,0,0,0] # Seoul, Goyang, Yongin Sungnam Bucheon Suwon Bucheon
        num_humans = [9668, 1030, 1009, 1001, 1193, 843]
        num_woundeds = [0,0,0,0,0,0]
        num_soldiers = [0,0,0,0,0,0]
        print 'simulation started'
        self.zombies = []
        self.humans = []
        self.woundeds = []
        self.soldiers = []

        for i in range(6):
            for _ in range(num_zombie[i]):
                zombie = Zombie()
                zombie.city = i
                self.zombies.append(zombie)
            for _ in range(num_humans[i]):
                human = Human()
                human.city = i
                self.humans.append(human)
            for _ in range(num_woundeds[i]):
                wounded = Wounded()
                wounded.city = i
                self.woundeds.append(wounded)
            for _ in range(num_soldiers[i]):
                soldier = Soldier()
                soldier.city = i
                self.soldiers.append(soldier)

    def update(self):
        for zombie in self.zombies:
            zombie.update()
        for human in self.humans:
            human.update()
            if human.HP <= 50:
                wounded = Wounded()
                wounded.city = human.city
                self.humans.remove(human)
                self.wounded.append(wounded)
        for wounded in self.woundeds:
            wounded.update()
        for soldier in self.soldiers:
            soldier.update()
            if soldier.HP <= 50:
                wounded = Wounded()
                wounded.city = soldier.city
                self.soldiers.remove(soldier)
                self.wounded.append(wounded)
        self.zombies = [zombie for zombie in self.zombies if zombie.HP > 0]
        self.humans = [human for human in self.humans if human.HP > 0]
        self.woundeds = [wounded for wounded in self.woundeds if wounded.HP > 0]
        self.soldiers = [soldier for soldier in self.soldiers if soldier.HP > 0]


    def run(self):
        while(True):
            print env.now, 'day'
            self.update()

            zombies = {}
            humans = {}
            woundeds = {}
            soldiers = {}
            for i in range(6):
                zombies[i] = [zombie for zombie in self.zombies if zombie.city == i]
                humans[i] = [human for human in self.humans if human.city == i]
                woundeds[i] = [wounded for wounded in self.woundeds if wounded.city == i]
                soldiers[i] = [soldier for soldier in self.soldiers if soldier.city == i]
                print 'zombies in ', i, ': ', len(zombies[i])

            for i in range(6):
                if len(zombies[i]) > 0:
                    fighters = random.sample(humans[i], int(len(humans[i])*0.1))
                    non_fighters = list(set(humans[i]) - set(fighters))
                    for fighter in fighters:
                        fighter.fightable = True
                        if np.random.uniform(0,1)<0.3:
                            self.humans.remove(fighter)
                            zombie = Zombie()
                            zombie.city = i
                            self.zombies.append(zombie)
                    for non_fighter in non_fighters:
                        non_fighter.fightable = False
                        if np.random.uniform(0,1)<0.05:
                            self.humans.remove(non_fighter)
                            zombie = Zombie()
                            zombie.city = i
                            self.zombies.append(zombie)



            yield env.timeout(1)



env = simpy.Environment()
simulation = Simulation(env)
env.run(until=100)
