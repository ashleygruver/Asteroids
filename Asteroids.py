# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0.5
splashText = True

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

def wrap(pos):
    if pos[0] <= 0:
        pos[0] = pos[0] % WIDTH
    if pos[0] >= WIDTH:
        pos[0] = pos[0] % WIDTH
    if pos[1] <= 0:
        pos[1] = pos[1] % HEIGHT
    if pos[1] >= HEIGHT:
        pos[1] = pos[1] % HEIGHT
    return pos

def groupCrash(group, other):
    outcome = 0
    removeSet = set([])
    for i in group:
        if i.crash(other):
            outcome += 1
            removeSet.add(i)
            boomGroup.add(Sprite(i.getPos(), (0, 0), 0, 0, explosion_image, explosion_info, explosion_sound))
    rockGroup.difference_update(removeSet)
    return outcome

def processSpriteGroup(c, group):
    for i in set(group):
        i.draw(c)
        if i.update():
            group.remove(i)
    return group

def groupGroupCrash(group, otherGroup):
    crashNum = 0
    for i in set(group):
        crash = groupCrash(otherGroup, i)
        crashNum += crash
        if crash >= 1:
            missileGroup.remove(i)
    return crashNum
        

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
    
    def turn(self, change):
        self.angle_vel += change
    
    def thrusterOn(self):
        self.thrust = True
        ship_thrust_sound.play()
    
    def thrusterOff(self):
        self.thrust = False
        ship_thrust_sound.pause()
        ship_thrust_sound.rewind()
    
    def pewpew(self):
        global a_missile
        missileGroup.add(Sprite((angle_to_vector(self.angle)[0] * self.radius + self.pos[0], angle_to_vector(self.angle)[1] * self.radius + self.pos[1]), (self.vel[0] + angle_to_vector(self.angle)[0] * 10, self.vel[1] + angle_to_vector(self.angle)[1] * 10), 0, 0, missile_image, missile_info, missile_sound))

    def getPos(self):
        return self.pos
    
    def getRadius(self):
        return self.radius
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(ship_image, (self.image_center[0] * 3, self.image_center[1]), self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(ship_image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        if self.thrust:
            self.vel[0] += angle_to_vector(self.angle)[0] / 8
            self.vel[1] += angle_to_vector(self.angle)[1] / 8
        else:
            self.vel[0] *= .97
            self.vel[1] *= .97
        wrap(self.pos)
            
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
    def crash(self, other):
        if math.sqrt((self.pos[0] - other.getPos()[0]) ** 2 + (self.pos[1] -
                                                               other.getPos()[1]) ** 2) <= self.radius + other .getRadius():
#            if self.pos[1] + other.getPos()[1] <= self.radius + other.getPos()[1]:
             return True
        return False
    
    def getPos(self):
        return self.pos
    
    def getRadius(self):
        return self.radius
    
   
    def draw(self, canvas):
        if self.animated:
             canvas.draw_image(self.image, (self.image_center[0] + self.image_size[0] * self.age, self.image_center[1]), self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image,self.image_center, self.image_size, self.pos, self.image_size, self.angle)
    
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        wrap(self.pos)
        self.age += 1
        if self.age >= self.lifespan:
            return True
        else:
            return False
        
           
def draw(canvas):
    global time, lives, missileGroup, rockGroup, score, splashText
    
    # animiate background
    time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, [center[0] - wtime, center[1]], [size[0] - 2 * wtime, size[1]], 
                                [WIDTH / 2 + 1.25 * wtime, HEIGHT / 2], [WIDTH - 2.5 * wtime, HEIGHT])
    canvas.draw_image(debris_image, [size[0] - wtime, center[1]], [2 * wtime, size[1]], 
                                [1.25 * wtime, HEIGHT / 2], [2.5 * wtime, HEIGHT])

    # draw ship and sprites
    my_ship.draw(canvas)
    processSpriteGroup(canvas, rockGroup)
    processSpriteGroup(canvas, boomGroup)
    missileGroup = processSpriteGroup(canvas, missileGroup)
    
    # update ship and sprites
    my_ship.update()
    canvas.draw_text('Lives left: ' + str(lives), (0, 20), 20, 'white')
    canvas.draw_text('Score: ' + str(score), (0, 40), 20, 'white')
    if splashText:
        canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), (WIDTH / 2, HEIGHT / 2), splash_info.get_size())
    if groupCrash(rockGroup, my_ship) >= 1:
        lives -= 1
    for i in range(groupGroupCrash(missileGroup, rockGroup)):
        score += 100
    if lives <= 0:
        splashText = True
        timer.stop()
        rockGroup = set([])
        my_ship.thrusterOff()
        my_ship.angle_vel = 0
        

def keyDown(key):
    if not splashText:
        keys = {simplegui.KEY_MAP['left']: my_ship.turn, simplegui.KEY_MAP['right']: my_ship.turn, simplegui.KEY_MAP['up']: my_ship.thrusterOn, simplegui.KEY_MAP['space']: my_ship.pewpew}
        values = {simplegui.KEY_MAP['left']: -.2, simplegui.KEY_MAP['right']: .2}
        if key in keys.keys():
            if key in values.keys():
                keys[key](values[key])
            else:
                keys[key]()
def keyUp(key):
     if not splashText:
        keys = {simplegui.KEY_MAP['left']: my_ship.turn, simplegui.KEY_MAP['right']: my_ship.turn, simplegui.KEY_MAP['up']: my_ship.thrusterOff}
        values = {simplegui.KEY_MAP['left']: .2, simplegui.KEY_MAP['right']: -.2}
        if key in keys.keys():
            if key in values.keys():
                keys[key](values[key])
            else:
                keys[key]()
def click(pos):
    global splashText, lives, score
    if splashText:
        lives = 3
        score = 0
        soundtrack.rewind()
        soundtrack.play()
        timer.start()
        splashText = False
            
# timer handler that spawns a rock    
def rock_spawner():
    if len(rockGroup) < 12:
        pos = (random.randrange(WIDTH), random.randrange(HEIGHT))
        if math.sqrt((my_ship.getPos()[0] - pos[0]) ** 2 + (my_ship.getPos()[1] - pos[1]) ** 2) > 50 + my_ship.getRadius() * 2:
            rockGroup.add(Sprite(pos, (random.choice([1 + score * .0001, -1 + score * .0001]), random.choice([1, -1])), random.randrange(5), .1, asteroid_image, asteroid_info))
    
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rockGroup = set([])
missileGroup = set([])
boomGroup = set([])

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keyDown)
frame.set_keyup_handler(keyUp)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
frame.start()
soundtrack.set_volume(1)
soundtrack.play()