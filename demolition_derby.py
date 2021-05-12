# Name: Demolition Derby
# Author: G.G.Otto
# Version: 1.2
# Date: 4/14/21

import pygame, random, math
from pygame.locals import *
import gamesetup as gs
from os.path import isfile

class Car(gs.Sprite):
    '''represents a car object'''

    def __init__(self, game, onsurface, color, eventUse=False):
        '''Car(Game, tuple, bool) -> Car
        constructs the car'''
        surface = game.change_color("car_0.png", (195, 195, 195, 255), color)
        self.afters = {}
        gs.Sprite.__init__(self, game, surface, onsurface)
        self.tilt(-90)
        self.flipLevel = 0
        self.flipFactor = 1
        self.turnSpeed = 12
        self.color = color
        self.turn = 0
        self.maxSpeed = 15
        self.minSpeed = 3
        self.speed = self.minSpeed
        self.maxTurn = 23
        self.increment = 0.1
        self.brakeBool = True
        self.eventUse = eventUse
        self.slamSpeed = 0.1
        self.afterDistances = {}
        self.last = None
        self.canMove = True
        self.turnDir = None
        self.changeSpeed = None
        self.clock = gs.Clock(game=game)
        self.clock.set_time(1)
        self.clock.start()
        self.tire = pygame.transform.rotozoom(self.game.change_color("tire.png", (255, 255, 255), color), 0, 0.4)
        self.turning = None

    def get_tire(self):
        '''Car.get_tire() -> pygame.Surface
        returns the tire surface'''
        return self.tire

    def set_move(self, boolean):
        '''Car.set_move(bool) -> None
        sets if the car can move or not'''
        self.canMove = boolean

    def can_move(self):
        '''Car.can_move() -> bool
        returns if car can move'''
        return self.canMove

    def get_color(self):
        '''Car.get_color() -> tuple
        returns the color of the car'''
        return self.color

    def get_speed(self):
        '''Car.get_speed() -> int
        returns the speed of the car'''
        return self.speed

    def get_max(self):
        '''Car.get_max() -> int
        returns the max speed of the car'''
        return max(self.maxSpeed, abs(self.minSpeed))

    def set_brake(self, boolean):
        '''Car.set_brake(bool) -> None
        sets the brake boolean of car'''
        self.brakeBool = boolean

    def set_speed(self, speed):
        '''Car.set_speed(int) -> None
        sets the speed of the car'''
        self.speed = speed

    def animate(self, images, wait, num=0):
        '''Car.animate(list, int) -> None
        animates the images of the car'''
        if num == 0:
            for i in range(4):
                r, theta = random.randint(15, 30), random.randrange(360)
                pos = self.xcor() + r*math.cos(math.radians(theta)), self.ycor() - r*math.sin(math.radians(theta))
                self.game.add_debris(pos, 25, 10, self.tire, self)
                
        heading = self.heading()
        self.surface(self.game.change_color(images[num], (195, 195, 195), self.color, 150))
        self.tilt(-90)
        self.heading(heading)
        num += 1
        
        if num >= len(images): return
        self.game.after(wait, lambda: self.animate(images, wait, num))

    def kill(self):
        '''Car.kill() -> None
        kills the car'''
        self.animate([f"car_wreck_{i+1}.png" for i in range(6)], 100)
        self.set_move(False)

    def set_color(self, color):
        '''Car.get_color(tuple) -> None
        sets the color of the car'''
        self.surface(self.game.change_color("car_raw.png", (195, 195, 195, 255), color))

    def accelerate(self, event=None):
        '''Car.accelerate(event) -> None
        causes the car to go faster'''
        if self.speed < self.maxSpeed and self.canMove:
            self.faster(self.increment)
            self.clock.reset()
            self.clock.start()
            
    def brake(self, event=None):
        '''Car.brake() -> None
        causes the car to brake'''
        if self.brakeBool and self.speed > self.minSpeed and self.canMove:
            reversing = self.speed < 0
            self.faster(-self.increment)

            if self.speed < 0.03:
                self.speed = 0

            if not reversing and self.speed == 0:
                self.brakeBool = False

    def can_turn(self, left):
        '''Car.can_turn(bool) -> bool
        returns if car is turning'''
        keys = pygame.key.get_pressed()
        if left: return (self.eventUse and keys[K_LEFT]) or (not self.eventUse and self.turnDir == "left")
        return (self.eventUse and keys[K_RIGHT]) or (not self.eventUse and self.turnDir == "right")              

    def can_change_speed(self, brake):
        '''Car.can_change_speed(bool) -> bool
        returns if the car can change speed'''
        keys = pygame.key.get_pressed()
        if brake: return (self.eventUse and (keys[K_DOWN])) or \
            (not self.eventUse and self.changeSpeed == "down")
        return (self.eventUse and keys[K_UP]) or (not self.eventUse and self.changeSpeed == "up")

    def set_change_speed(self, changeSpeed):
        '''Car.set_change_speed(changeSpeed) -> None
        sets the change speed of the car'''
        self.changeSpeed = changeSpeed

    def set_turn_dir(self, turnDir):
        '''Car.set_turn_dir(str) -> None
        setter for turn dir'''
        self.turnDir = turnDir

    def update(self):
        '''Car.update() -> None
        updates the car'''
        if self.canMove:
            self.forward(self.speed)

            # the direction the car is travelling
            factor = 0
            if self.speed < 0:
                factor = -1
            elif self.speed > 0:
                factor = 1

            if self.speed != 0 and self.can_turn(True):
                if self.turning == None: self.turning = random.randrange(360)
                else: self.pos(self.in_dir(self.turning, 1, False))
                if self.last not in self.afters:
                    self.last = self.after(5*abs(self.speed)/self.maxSpeed, lambda: self.heading(
                        self.heading()+factor*self.turnSpeed*abs(self.speed)/self.maxSpeed))
            if self.speed != 0 and self.can_turn(False):
                if self.turning == None: self.turning = random.randrange(360)
                else: self.pos(self.in_dir(self.turning, 1, False))
                if self.last not in self.afters:
                    self.last = self.after(5*abs(self.speed)/self.maxSpeed, lambda: self.heading(
                        self.heading()-factor*self.turnSpeed*abs(self.speed)/self.maxSpeed))
            if not self.can_turn(True) and not self.can_turn(False):
                self.turning = None

            # slam on brakes
            if self.can_change_speed(True):
                self.speed -= factor*self.slamSpeed
                if self.speed < self.minSpeed:
                    self.speed = self.minSpeed
            elif self.can_change_speed(False):
                self.accelerate()

            # check for hitting walls and cars
            self.hit_wall()

        # check afters
        for after in self.afters.copy():
            if self.afters[after][0] < 0:
                command = self.afters[after][1]
                self.afters.pop(after)
                command()
        for after in self.afterDistances.copy():
            distance = math.sqrt((self.xcor()-self.afterDistances[after][1][0])**2 + \
                (self.ycor()-self.afterDistances[after][1][1])**2)
            if distance > self.afterDistances[after][0]:
                command = self.afterDistances[after][2]
                self.afterDistances.pop(after)
                command()

        gs.Sprite.update(self)
                        
    def forward(self, pixels):
        '''Car.forward(pixels) -> None
        moves the car forward pixels'''
        for after in self.afters.copy():
            self.afters[after][0] -= abs(pixels)
        gs.Sprite.forward(self, pixels)

    def faster(self, change=1):
        '''Car.faster(int) -> None
        makes the car move faster'''
        self.speed += change

    def hit_wall(self):
        '''Car.hit_wall() -> bool
        returns if the wall is hit'''
        # get points
        heading = math.radians(self.heading())
        inFront = self.in_front(60)
        points = []
        for i in (-1,1):
            points.append((inFront[0] + 20*math.cos(heading+i*math.pi/2), inFront[1] - 20*math.sin(heading+i*math.pi/2)))

        # test points
        for point in points:
            radius = math.sqrt((2000-point[0])**2 + (2000-point[1])**2)
            if radius > 1915-self.speed:
                return True

        return False

    def hit_other(self, other):
        '''Car.hit_other(Car) -> bool
        returns if car has hit other'''
        # get points
        heading = math.radians(self.heading())
        inFront = self.in_front(60)
        points = []
        for i in (-1,1):
            points.append((inFront[0] + 20*math.cos(heading+i*math.pi/2), inFront[1] - 20*math.sin(heading+i*math.pi/2)))

        # test points
        for point in points:
            if is_in_rect(point, other.pos(), (45, 110), other.heading()):
                return True

        return False

    def after(self, pixels, command):
        '''Car.after(int, <function or method>) -> ID
        performs command after number of pixels'''
        ID = random.random()
        self.afters[ID] = [pixels, command]
        return ID

    def after_cancel(self, ID):
        '''Car.after_cancel(ID) -> None
        cancels after connected to ID'''
        if ID in self.afters:
            self.afters.pop(ID)

    def after_distance(self, distance, point, command):
        '''Car.after_distance(int, tuple, <function or method>) -> ID
        performs command after distance from points'''
        ID = random.random()
        self.afterDistances[ID] = [distance, point, command]
        return ID

    def after_distance_cancel(self, ID):
        '''Car.after_distance_cancel(ID) -> None
        cancels an after distance connected to ID'''
        if ID in self.afterDistances:
            self.afterDistances.pop(ID)     

class Worm(list):
    '''represents a chain of cars'''

    def __init__(self, game, color, useEvent=False, numCars=1):
        '''Worm(Game, tuple, bool, int) -> Worm
        constructs the chain of cars'''
        list.__init__(self)
        self.color = color
        self.game = game
        self.distance = 130
        self.stopped = {}
        self.dead = []
        self.xp = 0
        self.kills = 0

        x,y = 1000, 2000
        for i in range(numCars):
            event = useEvent and i == 0
            new = Car(self.game, self.game.get_field(), color, event)
            new.heading(90)
            new.pos((x,y))
            y += self.distance
            self.append(new)

    def head(self):
        '''Worm.head() -> x,y
        returns the head of the car'''
        if len(self.dead) == 0:
            return self[0].pos()
        return self.dead[0].pos()

    def get_kills(self):
        '''Worm.get_kills() -> int
        returns the number of kills the worm did'''
        return self.kills

    def get_xp(self):
        '''Worm.get_xp() -> int
        returns the number of xp'''
        return self.xp

    def is_dead(self):
        '''Worm.is_dead() -> bool
        returns if the worm is dead'''
        return not self[0].can_move()

    def add_xp(self, num):
        '''Worm.add_xp(int) -> None
        adds xp to the worm'''
        if num < 0 and abs(num) > self.xp:
            indic = -self.xp
            self.xp = 0
        else:
            self.xp += num
            indic = num
            if self.xp >= 100:
                self.xp -= 100
                self.add_car()

        if self == self.game.get_player(True):
            self.game.show_indicator(indic)

    def add_car(self):
        '''Worm.add_car() -> None
        adds a car to the chain'''
        new = Car(self.game, self.game.get_field(), self.color, False)
        new.heading(self[-1].heading())
        new.pos(self[-1].in_front(-20))
        self.stopped[new] = 20
        self.append(new)

    def add_kill(self):
        '''Worm.add_kill() -> None
        adds a kill to the worm's track record'''
        self.kills += 1

    def kill(self):
        '''Worm.kill() -> None
        kills the worm'''
        if len(self.dead) == len(self): return
        if len(self.dead) == 0: self.game.add_dead(self)
        self[len(self.dead)].kill()
        self.dead.append(self[len(self.dead)])
        if len(self.dead) < len(self): 
            self[len(self.dead)].set_speed(self[len(self.dead)-1].get_speed())
            self.game.after(200, self.kill)
            
    def update(self):
        '''Worm.update() -> None
        updates the worm'''
        for car in self: car.update()
        if len(self) == len(self.dead): return

        last = self[0]
        for i in range(len(self)):
            if i == 0: continue

            if last in self.dead:
                infront = 115
            elif self[i] in self.stopped:
                infront = self.stopped[self[i]]
                if infront >= self.distance:
                    self.stopped.pop(self[i])
                else:
                    self.stopped[self[i]] += self[0].get_speed()
            else:
                infront = self.distance

            if self[i] not in self.dead: 
                x, y = last.in_front(infront*(-3/7))
                self[i].heading(self[i].towards((x,y)))
                radians = math.radians(self[i].heading())
                self[i].pos((x - (infront*4/7)*math.cos(radians), y + (infront*4/7)*math.sin(radians)))
                
            last = self[i]

        # check if dead
        if self[0] not in self.dead and self[0].hit_wall():
            self.kill()
        for worm in self.game.get_cars():
            for car in worm:
                if car != self[0] and not worm.is_dead() and self[0].hit_other(car):
                    self.kill()
                    if worm != self:
                        worm.add_kill()

class BotWorm(Worm):
    '''represents a bot worm
    inherits from worm'''

    def __init__(self, *attri):
        '''BotCar(*tuple) -> BotCar
        constructs a bot car'''
        Worm.__init__(self, *attri)
        self.lastActions = None
        self.lastCollected = gs.Clock(game=self.game)
        self.lastCollected.start()

    def collect_debris(self):
        '''BotWorm.collect_debris() -> bool
        collects debris'''
        if self.lastCollected.get_time() < 0.5: return
        else:
            self.lastCollected.reset()
            self.lastCollected.start()
            
        # create collections of points
        collections = []
        for debris in self.game.get_debris():
            distance = self[0].distance(debris[0])
            if distance < 700:
                added = False
                for collection in collections:
                    if gs.distance(collection[1][0], debris[0]) < 50:
                        collection.append(debris)
                        collection[0] += debris[1]
                        added = True
                        break

                if not added: collections.append([debris[1], debris])

        # go for best
        best = None
        for collection in collections:
            if best == None or collection[0] > best[0]:
                best = collection
                
        # go to point
        if len(best) > 0:
            choice = best[1:][-1]
            headingDif = self[0].heading() - self[0].towards(choice[0])
            if headingDif > 10: self[0].set_turn_dir("right")
            elif headingDif < -10: self[0].set_turn_dir("left")
            else: self[0].set_turn_dir(None)

            speed = best[0]/7
            if speed > self[0].get_speed(): self[0].set_change_speed("up")
            else: self[0].set_change_speed("down")
        else:
            self.set_turn_dir(None)
                
    def check_wall(self):
        '''BotWorm.check_wall() -> bool
        checks for walls'''                    
        d1, d2 = gs.distance(self[0].in_dir(-45, 300), (2000, 2000)), \
            gs.distance(self[0].in_dir(45, 300), (2000, 2000))
        r = 1900

        if d1 >= r:
            self[0].set_turn_dir("left")
            self.lastActions = "left"
        elif d2 >= r:
            self[0].set_turn_dir("right")
            self.lastActions = "right"
        elif isinstance(self.lastActions, str):
            self.lastActions = 0
            return False
        else:
            return False

        if self[0].get_speed() > 5: self[0].set_change_speed("up")
        return True

    def move_away_from_wall(self):
        '''BotWorm.move_away_from_wall() -> bool
        returns if action is done or not'''
        if isinstance(self.lastActions, int):
            if self.lastActions == 15:
                self.lastActions = None
                return False
            else:
                self[0].set_change_speed("up")
                self.lastActions += 1
            return True
        
    def check_cars(self):
        '''BotWorm.check_cars() -> bool
        checks for other cars'''
        # get cars around
        carsAround = []
        closest = None
        for worm in self.game.get_cars():
            for car in worm:
                if not worm.is_dead() and car != self[0] and self[0].distance(car.pos()) < 400:
                    headingDif = self[0].towards(car.pos()) - self[0].heading()
                    if -120 < headingDif < 120:
                        if closest == None or abs(headingDif) < closest[0]: closest = abs(headingDif), car
                        carsAround.append(car)
        
        if closest == None:
            return False
        else:
            self[0].set_change_speed("up")
            headingDif = self[0].towards(carsAround[0].pos()) - self[0].heading()
            if headingDif > 0:
                self[0].set_turn_dir("right")
            elif headingDif < 0:
                self[0].set_turn_dir("left")
            return True

    def update(self):
        '''BotCar.update() -> None
        updates the bot car'''
        if not self.is_dead():
            hittingWall = self.check_wall()
            if not hittingWall:
                hittingCars = self.check_cars()
                if not hittingCars:
                    moveAway = self.move_away_from_wall()
                    if not moveAway:
                        self.collect_debris()

        Worm.update(self)   

class Dashboard(pygame.Surface):
    '''represents the dashboard'''

    def __init__(self, game, rect, maxSpeed):
        '''Dashboard(Game, tuple, int) -> Dashboard
        constructs the dashboard for the game'''
        pygame.Surface.__init__(self, rect[2:4], SRCALPHA)
        self.game = game
        self.rect = rect
        self.maxSpeed = maxSpeed
        self.speedometer = 0
        self.xpFull = 100

    def update(self):
        '''Dashboard.update() -> None
        updates the dashboard'''
        self.fill(0)
        
        # draw speedometer
        self.speedometer = abs(self.game.get_player().get_speed())
        radius = 110
        x,y = self.rect[2]/2, self.rect[3]-40
        pygame.draw.circle(self, (0, 0, 0, 130), (x,y), radius)
        degrees = 180
        while degrees >= 0:
            radians = math.radians(degrees)
            pygame.draw.line(self, "red", (x+radius*math.cos(radians), y-radius*math.sin(radians)),
                (x+(radius-15)*math.cos(radians), y-(radius-15)*math.sin(radians)), 3)
            degrees -= 15
        needle = 180-180*self.speedometer/self.maxSpeed
        base = 6
        pygame.draw.circle(self, "green", (x,y), base)
        pygame.draw.polygon(self, "green", ((x+base*math.cos(math.radians(needle-90)), y-base*math.sin(math.radians(needle-90))),
            (x+(radius-10)*math.cos(math.radians(needle)), y-(radius-10)*math.sin(math.radians(needle))),
            (x+base*math.cos(math.radians(needle+90)), y-base*math.sin(math.radians(needle+90)))))

        # draw map
        surface = pygame.Surface((110, 110), SRCALPHA)
        pygame.draw.circle(surface, (200, 200, 200, 170), (55, 55), 50*1950/2000)
        pygame.draw.circle(surface, (230, 0, 0, 170), (55, 55), 50*1950/2000+4, 5)

        # draw cars on map
        for worm in self.game.get_cars():
            x,y = worm.head()
            size = 2
            if worm == self.game.get_player(True): size = 3
            if not worm.is_dead():
                pygame.draw.circle(surface, worm[0].get_color(), (x/(2000/55), y/(2000/55)), size)
                polygon = []
                for car in worm:
                    if car.can_move():
                        polygon.append((round(car.xcor()/(2000/55)), round(car.ycor()/(2000/55))))
                if len(polygon) > 1:
                    pygame.draw.lines(surface, worm[0].get_color(), False, polygon, 2)
                
        self.game.blit(surface, (510, 105), True, True, self)

        # draw xp meter
        rect = (21, 135, 150*self.game.get_player(True).get_xp()/self.xpFull, 25)
        pygame.draw.rect(self, (23,180,90,170), rect)
        pygame.draw.rect(self, "white", (21,135,150,25), 3)
        
        self.game.blit(self, self.rect)

class EndScreen(gs.Sprite):
    '''represents the end game screen'''

    def __init__(self, game):
        '''EndScreen(game) -> EndScreen
        constructs the end screen sprite'''
        surface = pygame.Surface((350, 170), SRCALPHA)
        surface.fill((0,0,0,180))
        gs.Sprite.__init__(self, game, surface)
        self.pos((300, -320))
        self.set_image_turning(False)
        self.heading(270)
        self.headerFont = pygame.font.SysFont("Arial", 23, True)
        self.bodyFont = pygame.font.SysFont("Arial", 15, True)
        self.game = game
        self.isActivate = False
        self.restart = gs.Button(self.game, pygame.image.load("restart.png"), pos=(300, 155), command=self.game.__init__)
        self.high = self.get_high()

    def activated(self):
        '''EndScreen.activated() -> None
        returns if screen is activated'''
        return self.isActivate

    def end(self, score, rank, kills, time, win):
        '''EndScreen.win(int, int, int, float, bool) -> None
        ends the game with a win'''
        if self.isActivate: return
        if win: rank = 1
        if win:
            top = "You have won!"
            wait = 4000
        else:
            top = "You are out."
            wait = 15000

        # save high
        newHigh = ""
        if score > self.high:
            self.save_high(int(score))
            newHigh = " (New!)"
            
        header = self.headerFont.render(top, True, "white")
        body1 = self.bodyFont.render(f"Rank: {int(rank)}   Time: {round(time*10)/10}", True, "white")
        body2 = self.bodyFont.render(f"Score: {int(score)}   Kills: {int(kills)}", True, "white")
        body3 = self.bodyFont.render(f"High Score: {int(self.high)}{newHigh}", True, "white")

        # add everything on screen
        self.game.blit(header, (175, 25), True, True, self.surface())
        self.game.blit(body1, (175, 58), True, True, self.surface())
        self.game.blit(body2, (175, 76), True, True, self.surface())
        self.game.blit(body3, (175, 94), True, True, self.surface())

        # show end screen
        self.pos((300, 100))
        self.isActivate = True
        self.game.after(wait, self.game.stop)

    def update(self):
        '''EndScreen.update() -> None
        updates the end screen'''
        gs.Sprite.update(self)
        if self.isActivate: self.restart.update()

    def get_high(self):
        '''EndScreen.get_high() -> int
        returns the player's high score'''
        if not isfile("high.txt"):
            return 0
        file = open("high.txt")
        text = file.read()
        file.close()
        return int(text.split()[0])

    def save_high(self, high):
        '''EndScreen.save_high(int) -> None
        saves the high score'''
        self.high = high
        file = open("high.txt", "w")
        file.write(str(high))
        file.close()
            
class Game(gs.Game):
    '''represents the main game object'''

    def __init__(self):
        '''Game() -> Game
        constructs the game'''
        gs.Game.__init__(self)

        # display settings
        pygame.display.set_icon(pygame.transform.rotozoom(pygame.image.load("icon.png"), -20, 1))
        pygame.display.set_caption("Demolition Derby")
        self.screen = pygame.display.set_mode((600,600))
        load = pygame.font.SysFont("Arial", 50, True)
        self.blit(load.render("Loading Game...", True, "red"), (300, 300), True, True)
        pygame.display.update()

        # create arena
        self.fieldSize = 0, 0, 600, 500
        self.arenaSize = 4000
        self.field = pygame.Surface((self.arenaSize, self.arenaSize))
        self.spots = [(self.get_random_coords(), random.randint(5,12)) for i in range(300)]
        
        # car colors
        numCars = 12
        colors = [(237, 28, 36), (255, 127, 39), (242, 231, 0), (34, 177, 76),
            (63, 72, 204), (163, 73, 164), (0, 0, 0), (226, 16, 153), (230, 230, 230),
            (0, 0, 90), (0, 90, 0), (120, 0, 0), (0, 232, 232)]
        carColors = []
        for i in range(numCars):
            color = random.choices(colors)
            colors.remove(color[0])
            carColors.append(color[0])
        
        # player car
        self.player = Worm(self, carColors[0], True)
        self.player[0].pos(self.polar_coords(500, 90))
        self.follow = self.player
        
        # opponent cars
        self.cars = []
        self.opponents = [BotWorm(self, carColors[i+1], False) for i in range(numCars-1)]
        heading = 90
        for opponent in self.opponents:
            heading += 360/(numCars)
            opponent[0].pos(self.polar_coords(500, heading))
            opponent[0].heading(heading)
            self.cars.append(opponent)
        self.cars.append(self.player)
            
        # other attributes
        self.GRASS = (50, 216, 100)
        self.ROAD = (100, 100, 100)
        self.SPOT = (110, 110, 110)
        self.dashboard = Dashboard(self, (0, 430, 600, 200), self.player[0].get_max())
        self.battery = pygame.transform.rotozoom(pygame.image.load("battery.png").convert_alpha(), 0, 0.35)
        self.cone = pygame.transform.rotozoom(pygame.image.load("cone.png").convert_alpha(), 0, 0.5)
        self.gascan = pygame.transform.rotozoom(pygame.image.load("gascan.png").convert_alpha(), 0, 0.6)
        self.debris = []
        self.dead = []
        self.win = False
        self.end = EndScreen(self)
        self.clock = gs.Clock(game=self)
        self.indicator = ""
        self.indicFont = pygame.font.SysFont("Arial", 22, True)
        self.scoreFont = pygame.font.SysFont("Arial", 15, True)
        self.sizeFactor = 1
        self.score = 0
        self.stopped = False
        self.paused = False

        # start screen
        self.startScreen = pygame.image.load("start_screen.png")
        self.play = gs.Button(self, pygame.image.load("play.png"), command=self.start, pos=(300, 445))
        self.started = False

        # add debris
        for i in range(150):
            size = random.randint(3,5)/4
            self.debris.append((self.get_random_coords(), 8*size, 0,
                pygame.transform.rotozoom(self.gascan, 0, size)))
        for i in range(70):
            size = random.randint(4,6)/5
            self.debris.append((self.get_random_coords(), 15*size, 0,
                pygame.transform.rotozoom(self.battery, 0, size)))
        for i in range(30):
            size = random.randint(4,6)/5
            self.debris.append((self.get_random_coords(), -35*size, 5,
                pygame.transform.rotozoom(self.cone, 0, size)))

        # paused screen
        pausedFont = pygame.font.SysFont("Arial", 70, True)
        self.pausedScreen = pygame.Surface(self.screen.get_size(), SRCALPHA).convert_alpha()
        self.pausedScreen.fill((0,0,0,150))
        self.blit(pausedFont.render("Game Paused", True, "white"), (300, 300), True, True, self.pausedScreen)

        self.replenishEvent = pygame.event.custom_type()
        pygame.time.set_timer(self.replenishEvent, 10000)

    def following(self, worm=None):
        '''Game.following(Worm) -> None/Worm
        if worm not given, returns following. otherwise, sets following'''
        if worm == None: return self.follow
        self.follow = worm

    def get_field(self):
        '''Game.get_field() -> Surface
        returns the surface for the arena'''
        return self.field

    def get_player(self, wholeChain=False):
        '''Game.get_player(bool) -> Car
        returns the player'''
        if wholeChain: return self.player
        return self.player[0]

    def get_opponents(self):
        '''Game.get_opponents() -> list
        returns a list of opponent cars'''
        return self.opponents

    def get_cars(self):
        '''Game.get_cars() -> list
        returns all cars'''
        return self.cars

    def get_debris(self):
        '''Game.get_debris() -> list
        returns a list of debris'''
        return self.debris

    def add_dead(self, worm):
        '''Game.add_dead(Worm) -> None
        adds worm to dead worms'''
        self.dead.append(worm)

    def start(self):
        '''Game.start() -> None
        starts the game'''
        self.started = True
        self.clock.start()

    def change_color(self, image, old=None, new=None, transparent=255):
        '''Game.change_color(tuple, tuple) -> pygame.Surface
        returns a surface with old and new colors switched'''
        if isinstance(image, pygame.Surface):
            surface = image
        else:
            surface = pygame.image.load(image).convert_alpha()

        rect = surface.get_rect()
        for x in range(rect[2]):
            for y in range(rect[3]):
                pixel = surface.get_at((x,y))
                if new != None and pixel == old:
                    color = list(new[:3])+[transparent]
                    surface.set_at((x,y), color)
                elif pixel[:3] == (127, 127, 127):
                    surface.set_at((x,y), 0)
                else:
                    color = list(surface.get_at((x,y)))[:3]+[transparent]                
                    surface.set_at((x,y), color)

        return surface

    def polar_coords(self, r, theta):
        '''Game.polar_coords(int, int) -> (int, int)
        returns the rectangle coordinates for r and theta'''
        return self.arenaSize/2+r*math.cos(math.radians(theta)), self.arenaSize/2-r*math.sin(math.radians(theta))

    def add_debris(self, *attri):
        '''Game.add_desbris(tuple, int, int, pygame.Surface) -> None
        adds a bit of debris to the game'''
        self.debris.append(attri)

    def show_indicator(self, num):
        '''Game.show_indicator(int) -> None
        shows number on indicator'''
        if self.end.activated(): return
        self.indicator = ("+"+str(round(num))).replace("+-", "-")
        self.score += num

    def replenish(self, num):
        '''Game.replenish(int) -> None
        replenishes the items in the arena to num'''
        if len(self.debris) >= num: return
        for i in range(num-len(self.debris)):
            randomize = random.random()
            if randomize > 2/5:
                size = random.randint(3,5)/4
                self.debris.append((self.get_random_coords(), 8*size, 0,
                    pygame.transform.rotozoom(self.gascan, 0, size)))
            elif randomize > 3/25:
                size = random.randint(4,6)/5
                self.debris.append((self.get_random_coords(), 15*size, 0,
                    pygame.transform.rotozoom(self.battery, 0, size)))
            else:
                size = random.randint(4,6)/5
                self.debris.append((self.get_random_coords(), -35*size, 5,
                        pygame.transform.rotozoom(self.cone, 0, size)))

    def stop(self):
        '''Game.stop() -> None
        stops movement on the board'''
        self.stopped = True

    def event(self, event):
        '''Game.update(event) -> None
        checks event'''
        if event.type == self.replenishEvent:
            self.replenish(250)
        elif event.type == KEYDOWN:
            if event.key == K_SPACE and not self.stopped and self.started and not self.end.activated():
                if self.paused:
                    self.play_all_clocks()
                else:
                    self.pause_all_clocks()
                    self.blit(self.pausedScreen, (0,0))
                    pygame.display.update()
                self.paused = not self.paused

    def update(self):
        '''Game.update() -> None
        updates a single frame of the same'''
        if self.stopped or self.paused: return
        
        self.screen.fill((210, 0, 0))
        
        # prepare field
        if self.started:
            self.field.fill((210, 0, 0))
            pygame.draw.circle(self.field, self.ROAD, (self.arenaSize/2, self.arenaSize/2), self.arenaSize/2-50)
            for spot in self.spots:
                pygame.draw.circle(self.field, self.SPOT, spot[0], spot[1])

            # update dead worms
            for car in self.dead:
                car.update()

            # add gascans
            for debris in self.debris[:]:
                self.blit(debris[3], debris[0], True, True, self.field)
                for worm in self.cars:
                    if worm.is_dead():
                        continue
                    if not (len(debris) > 4 and debris[-1] in worm) and \
                       is_in_rect(debris[0], worm[0].pos(), (60+debris[2], 110+debris[2]), worm[0].heading()):
                        if debris in self.debris:
                            self.debris.remove(debris)
                            worm.add_xp(debris[1])
                
            # update cars
            for car in self.cars:
                if car not in self.dead:
                    car.update()

            pygame.draw.circle(self.field, (230, 0, 0), (self.arenaSize/2, self.arenaSize/2), self.arenaSize/2-50, 50)

            # add everything on
            rect, carp = self.fieldSize, self.follow.head()
            blitRect = (rect[2]/2-self.sizeFactor*carp[0], rect[3]/2-self.sizeFactor*carp[1], rect[2], rect[3])
            if self.sizeFactor == 1: self.blit(self.field, blitRect)
            else: self.blit(pygame.transform.rotozoom(self.field, 0, self.sizeFactor), blitRect)
        else:
            self.screen.blit(self.startScreen, (0,-20))
            self.play.update()

        # win or lose the game
        end = None
        if len(self.cars) - len(self.dead) == 1 and not self.player.is_dead(): end = True
        elif len(self.cars) - len(self.dead) != 0 and self.player.is_dead(): end = False
        if end != None: self.end.end(self.score, len(self.cars) - len(self.dead) + 1,
            self.player.get_kills(), self.clock.get_time(), end)

        # get rank
        if end: rank = 1
        elif end == False: rank = len(self.cars) - len(self.dead) + 1
        else: rank = len(self.cars) - len(self.dead)
        
        self.dashboard.update()
        self.blit(self.indicFont.render(self.indicator, True, (255, 255, 255)), (96, 548), True, True)
        self.blit(self.scoreFont.render("Score: "+str(round(self.score)), True, (255, 255, 255)), (96, 577), True, True)
        if not self.end.activated(): self.blit(self.scoreFont.render("#"+str(rank), True, (255, 255, 255)), (6,5))
        self.end.update()
        pygame.display.update()

    def get_random_coords(self):
        '''Game.get_random_coords() -> (x,y)
        returns random coordinates'''
        coords = random.randrange(4000), random.randrange(4000)
        while gs.distance(coords, (2000, 2000)) > 1500:
            coords = random.randrange(4000), random.randrange(4000)
        return coords

def is_in_rect(point, center, size, angle):
    '''is_in_rect(tuple, tuple, tuple, angle) -> bool
    returns if point is in rect with center, size, and angle'''
    pos = complex(point[0]-center[0], point[1]-center[1])*pow(math.e, math.radians(angle)*complex(0,1))
    return -size[1]/2 < pos.real < size[1]/2 and -size[0]/2 < pos.imag < size[0]/2
    
pygame.init()
Game().mainloop()
