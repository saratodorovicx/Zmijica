import math
import random
import pygame
import sys

width = 700
height = 400
columns = 14
rows = 8
colorBerry = (255, 0, 0)
colorCube = (0, 255, 0)
sizeCube = 50


class Cube():
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color 
       
    def draw(self, screen):
        pygame.draw.rect( screen, self.color, (self.x, self.y, self.size, self.size))
   

class Snake():
   
    keyMap = {
        pygame.K_UP: (0, -50),
        pygame.K_DOWN: (0, 50),
        pygame.K_LEFT: (-50, 0),
        pygame.K_RIGHT: (50, 0)
    }
    def __init__(self):
        self.body = [ Cube(100, 100, colorCube), Cube(150, 100, colorCube), Cube(200, 100, colorCube) ]
        self.xPlus = 0
        self.yPlus = 0
    def changeDirection(self, key):
        if key in self.keyMap:
            xNew, yNew = self.keyMap[key]
            if (xNew, yNew) == (-self.xPlus, -self.yPlus):
                return
        else: return
        self.xPlus, self.yPlus = xNew, yNew

    def addHead(self):
        xNew = self.body[0].x + self.xPlus
        yNew = self.body[0].y + self.yPlus
        self.body.insert(0, Cube(xNew, yNew, colorCube))

    def move(self):
        self.addHead()
        self.body.pop()

    def draw(self, screen):
        for i in range (len(self.body)):
            self.body[i].draw(screen)
    def ate(self, berry):
        return (self.body[0].x == berry.x and self.body[0].y == berry.y)

    def hitSelf(self):
        for i in range (len(self.body())):
            if (self.body[0].x < 0  or self.body[0].x + sizeCube > width
                or self.body[0].y < 0 or self.body[0].y + sizeCube > height):
                return true
        return false
    

    def hitWall(self):
        for i in range (len(self.body())):
            if (self.body[0].x == self.body[i].x and self.body[0].y == self.body[i].y):
                return true
        return false

    def grow(self):
        self.addHead()
        

    

def randomBerries():
    x = random.randint(0, columns - 1) * 50
    y = random.randint(0, rows - 1) * 50
    #while()
     #   for i in range len(snake.body)
      #      if(snake.)
    
    return Cube(x, y, colorBerry)
   

screen = pygame.display.set_mode((width, height))
screen.fill((255, 255, 255))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()


snake = Snake()

berry = randomBerries()

while True:
   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
           
        if event.type == pygame.KEYDOWN:
            snake.changeDirection(event.key)
    screen.fill((255, 255, 255))
    berry.draw(screen)
    snake.draw(screen)
    snake.move()
    if snake.ate(berry):
        snake.grow()
        berry = randomBerries()
   
    pygame.display.update()
    clock.tick(5)
