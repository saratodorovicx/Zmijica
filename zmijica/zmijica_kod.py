import pygame
import random
import sys
import time

pygame.init()
pygame.mixer.init()

#----------------------------------------------------------------

columns = 20
rows = 14

sizeCube = 20
space = 2
widthBerry = 8
heightBerry = 6

sideSpace = 15
upperSpace = 55
downSpace = 15

pencilWidth = 5

lineY = 45

black = (0, 0, 0)
gray = (100, 100, 100)
green = (154, 197, 2)

interval = sizeCube + space

widthSubframe = columns * interval - space
heightSubframe = rows * interval - space

frameW = widthSubframe + 2 * (space + pencilWidth)
frameH = heightSubframe + 2 * (space + pencilWidth)

width = sideSpace * 2 + frameW
height = upperSpace + downSpace + frameH

center = width // 2

gridX = sideSpace + pencilWidth + space
gridY = upperSpace + pencilWidth + space

startX = gridX + (columns // 2) * interval
startY = gridY + (rows // 2) * interval

font1Size = 40
font2Size = 60
font3Size = 20

font1 = pygame.font.Font("pixelFont.otf", font1Size)
font2 = pygame.font.Font("pixelFont.otf", font2Size)
font3 = pygame.font.Font("pixelFont.otf", font3Size)

gameOverCount = 20
easyFCount = 12
midFCount = 8
hardFCount = 5

gameOverSound = pygame.mixer.Sound("gameOver.wav")
eatSound = pygame.mixer.Sound("eat.wav")
clickSound = pygame.mixer.Sound("click.mp3")


#----------------------------------------------------------------


class Cube():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def draw(self, screen, color):
        pygame.draw.rect(screen, color, (self.x, self.y, sizeCube, sizeCube))


class Berry():

    def __init__(self, x, y):
        self.x = x
        self.y = y
    def draw(self, screen):
        pygame.draw.rect(screen, black,(self.x + (sizeCube - widthBerry)//2, self.y, widthBerry, heightBerry))
        pygame.draw.rect(screen, black,(self.x + (sizeCube - widthBerry)//2, self.y + (sizeCube - heightBerry), widthBerry, heightBerry))
        pygame.draw.rect(screen, black,(self.x, self.y + (sizeCube - widthBerry)//2, heightBerry, widthBerry))
        pygame.draw.rect(screen, black,(self.x + (sizeCube - heightBerry), self.y + (sizeCube - widthBerry)//2, heightBerry, widthBerry))

class HighScoreFile():

    framesMap = {
        easyFCount: 0,
        midFCount: 1,
        hardFCount: 2
    }
   
    file = "highscore.txt"

    def load(self, frameCount):
        try:
            with open(self.file, "r") as file:
                lines = file.readlines()
                index = self.framesMap[frameCount]
                return int(lines[index].strip())
        except:
            return 0
       
    def save(self, frameCount, score):
        current_scores = [0, 0, 0]
        try:
            with open(self.file, "r") as file:
                lines = file.readlines()
                for i in range(min(len(lines), 3)):
                    current_scores[i] = int(lines[i].strip())
        except:
            pass
       
        index = self.framesMap[frameCount]
        current_scores[index] = score

        with open(self.file, "w") as file:
            for s in current_scores:
                file.write(f"{s}\n")


class Snake():

    keyMap = {
        pygame.K_UP: (0, -interval),
        pygame.K_DOWN: (0, interval),
        pygame.K_LEFT: (-interval, 0),
        pygame.K_RIGHT: (interval, 0),
        pygame.K_w: (0, -interval),
        pygame.K_s: (0, interval),
        pygame.K_a: (-interval, 0),
        pygame.K_d: (interval, 0)
    }
   
    def __init__(self):
        self.body = [ Cube(startX, startY), Cube(startX - interval, startY), Cube(startX - 2 * interval, startY) ]
        self.directions = [self.keyMap[pygame.K_RIGHT]]
        self.started = False
        self.exists = True
        self.color = black
       
    def changeDirection(self, key):
        if not self.started and key == self.keyMap[pygame.K_RIGHT]:
            return False
       
        self.started = True
       
        x, y = self.keyMap[key]
        if len(self.directions) < 3:
            if (x, y) == (-self.directions[-1][0], -self.directions[-1][1]):
                return
            else:
                self.directions.append((x, y))
        return True

    def addHead(self):
        if len(self.directions) > 1: index = 1
        else: index = 0
        xNew = self.body[0].x + self.directions[index][0]
        yNew = self.body[0].y + self.directions[index][1]
        self.body.insert(0, Cube(xNew, yNew))

    def move(self, grow = False):
        self.addHead()
        if not grow:
            self.body.pop()
        if len(self.directions) > 1:
            self.directions.pop(0)
        

    def draw(self, screen):
        for i in range (len(self.body)):
            self.body[i].draw(screen, self.color)
        
           
    def ate(self, berry):
        return self.body[0].x == berry.x and self.body[0].y == berry.y

   

    def hitWall(self):        
        head = self.body[0]
        if head.x < gridX:
            return True
        if head.y < gridY:
            return True
        if head.x > gridX + (columns - 1) * interval:
            return True
        if head.y > gridY + (rows - 1) * interval:
            return True
        return False

    def win(self):
        return len(self.body) == rows*columns

    def hitSelf(self):
        for i in range (2, len(self.body)):
            if self.body[0].x == self.body[i].x and self.body[0].y == self.body[i].y:
                return True
        return False

    def lost(self):
        self.addHead()
        if self.hitWall() or self.hitSelf():
            self.body.pop(0)
            return True
        else:
            self.body.pop(0)
            return False
       

class Game:

    HOME = -1
    PLAYING = 0
    PAUSED = 1
    GAME_OVER = 2
    WIN = 3


    def __init__(self):

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.highScoreFile = HighScoreFile()
        self.highScore = 0
        self.reset()

    def reset(self):

        self.snake = Snake()
        self.berry = self.randomBerry()
        self.score = 0
        self.moving = False
        self.state = self.HOME
        self.pauseRect = pygame.Rect(sideSpace, 10, 35, 28)
        self.frameCount = easyFCount
        self.frameCounter = 0
        self.gameOverCounter = 0
        self.gameOverCounter2 = 0
        self.soundCheck = True
        self.replayRect = pygame.Rect(0, 0, 0, 0)

    def randomBerry(self):
        occupied = True
        while occupied:
            x = gridX + random.randint(0, columns - 1) * interval
            y = gridY + random.randint(0, rows - 1) * interval
            occupied = False
            for cube in self.snake.body:
                if cube.x == x and cube.y == y:
                    occupied = True
                    break
        return Berry(x, y)

    def drawFrame(self):
        self.screen.fill(green)
        pygame.draw.rect(self.screen, black, (sideSpace, upperSpace, frameW, frameH), pencilWidth)
        pygame.draw.line(self.screen, black, (sideSpace, lineY), (sideSpace + frameW, lineY), pencilWidth)
        scoreText = font1.render(f"{self.score}", True, black)
        self.screen.blit(scoreText, (sideSpace + 2 * 15 + 12, -2))
        if self.state == self.PAUSED:
            pygame.draw.polygon(self.screen, black, ((sideSpace + 5, 10), (sideSpace + 5, 38), (sideSpace + 34, 24)), 6)
        else:
            pygame.draw.rect(self.screen, black, (sideSpace, 10, 15, 28), 5)
            pygame.draw.rect(self.screen, black, (sideSpace + 20, 10, 15, 28), 5)
       
        if(self.frameCount == easyFCount): difficultyText = font1.render("easy", True, black)
        elif(self.frameCount == midFCount): difficultyText = font1.render("medium", True, black)
        else: difficultyText = font1.render(f"hard", True, black)
       
        difficultyRect = difficultyText.get_rect()
        difficultyRect.right = width - sideSpace
        difficultyRect.top = -2
        self.screen.blit(difficultyText, difficultyRect)

    def drawHome(self):
        self.screen.fill(green)
        pygame.draw.rect(self.screen, black, (sideSpace, downSpace, frameW, frameH + upperSpace - downSpace), pencilWidth)
       
        titleText = font2.render("SNAKE GAME", True, black)
        titleRect = titleText.get_rect()
        titleRect.center = (center, downSpace + 60)
        self.screen.blit(titleText, titleRect)
       
        easyText = font1.render("(e) easy", True, black)
        midText = font1.render("(m) medium", True, black)
        hardText = font1.render("(h) hard", True, black)
       
        self.easyRect = easyText.get_rect()
        self.easyRect.center = (center, downSpace + 160)
       
        self.midRect = midText.get_rect()
        self.midRect.center = (center, downSpace + 220)
       
        self.hardRect = hardText.get_rect()
        self.hardRect.center = (center, downSpace + 280)
       
        self.screen.blit(easyText, self.easyRect)
        self.screen.blit(midText, self.midRect)
        self.screen.blit(hardText, self.hardRect)

    def drawGameOver(self):
        self.drawFrame()
       
        gameOverText = font2.render("GAME OVER", True, black)
        self.gameOverRect = gameOverText.get_rect()
        self.gameOverRect.center = (center, 115)
        self.screen.blit(gameOverText, self.gameOverRect)

        bestScoreText = font3.render(f"High score: {self.highScore}", True, black)
        self.bestScoreRect = bestScoreText.get_rect()
        self.bestScoreRect.center = (center, 185)
        self.screen.blit(bestScoreText, self.bestScoreRect)

        if(self.score > self.highScore):
            newHighText = font3.render(f"NEW HIGH SCORE!", True, black)
            self.newHighRect = newHighText.get_rect()
            self.newHighRect.center = (center, 220)
            self.screen.blit(newHighText, self.newHighRect)
           
        replayText = font1.render("(r) replay", True, black)
        self.replayRect = replayText.get_rect()
        self.replayRect.center = (center, 270)
        self.screen.blit(replayText, self.replayRect)

    def drawWin(self):
        self.screen.fill(green)
        pygame.draw.rect(self.screen, black, (sideSpace, downSpace, frameW, frameH + upperSpace - downSpace), pencilWidth)

        win1Text = font2.render("you won!", True, black)
        self.win1Rect = win1Text.get_rect()
        self.win1Rect.center = (center, 115)

        self.screen.blit(win1Text, self.win1Rect)
       
        replayText = font1.render("(r) replay", True, black)
        self.replayRect = replayText.get_rect()
        self.replayRect.center = (center, 270)
        self.screen.blit(replayText, self.replayRect)
       
       
    def handleEvents(self):
        for event in pygame.event.get():
           
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
               
            if event.type == pygame.KEYDOWN:
                
                if self.state != self.HOME:
                    if event.key == pygame.K_r:
                        self.reset()
                        clickSound.play()
                    elif event.key == pygame.K_p and self.state != self.GAME_OVER:
                        if self.state == self.PAUSED:
                            self.state = self.PLAYING
                        elif self.moving:
                            self.state = self.PAUSED
                        clickSound.play()
               
                    elif event.key in self.snake.keyMap and self.state == self.PLAYING:
                        if self.snake.changeDirection(event.key):
                            self.moving = True
                        
                else:
                    if event.key == pygame.K_e:
                        self.frameCount = easyFCount
                        clickSound.play()
                    elif event.key == pygame.K_m:
                        self.frameCount = midFCount
                        clickSound.play()
                    elif event.key == pygame.K_h:
                        self.frameCount = hardFCount
                        clickSound.play()
                    else: continue
                    self.highScore = self.highScoreFile.load(self.frameCount)
                    self.state = self.PLAYING
                
                   
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                if self.state == self.HOME:
                    if self.easyRect.collidepoint(event.pos):
                        self.frameCount = easyFCount
                        clickSound.play()
                    elif self.midRect.collidepoint(event.pos):
                        self.frameCount = midFCount
                        clickSound.play()
                    elif self.hardRect.collidepoint(event.pos):
                        self.frameCount = hardFCount
                        clickSound.play()
                    else: continue
                    self.highScore = self.highScoreFile.load(self.frameCount)
                    self.state = self.PLAYING
                   
                elif self.pauseRect.collidepoint(event.pos) and self.state != self.GAME_OVER:
                    if self.state == self.PAUSED:
                        self.state = self.PLAYING
                    elif self.state == self.PLAYING and self.moving:
                        self.state = self.PAUSED
                    clickSound.play()

                elif (self.state == self.GAME_OVER or self.state == self.WIN) and self.replayRect.collidepoint(event.pos):
                    self.reset()
                    clickSound.play()

               

    def update(self):
        if self.state != self.PLAYING:
            return
        self.frameCounter += 1
        if self.moving and self.frameCounter % self.frameCount == 0:
           
            if self.snake.ate(self.berry):
                self.score += 5
                if not self.snake.lost():
                    self.snake.move(grow = True)
                    eatSound.play()
                self.berry = self.randomBerry()
            else:
                if not self.snake.lost():
                    self.snake.move()
                else:
                    if self.score > self.highScore:
                        self.highScoreFile.save(self.frameCount, self.score)
                    self.state = self.GAME_OVER
                    self.moving = False
        if(self.snake.win()):
            self.state = self.WIN

    def draw(self):
        if self.state == self.HOME:
            self.drawHome()
        elif self.state == self.PLAYING:
            self.drawFrame()
            self.berry.draw(self.screen)
            self.snake.draw(self.screen)
        elif self.state == self.PAUSED:
            self.drawFrame()
            self.berry.draw(self.screen)
            self.snake.draw(self.screen)
            pausedText = font2.render("paused (p)", True, black)
            pausedRect = pausedText.get_rect()
            pausedRect.center = (center, height // 2 - font2Size)
            self.screen.blit(pausedText, pausedRect)
        elif self.state == self.GAME_OVER:
            if self.soundCheck:
                gameOverSound.play()
                self.soundCheck = False
            self.gameOverCounter += 1
            if self.gameOverCounter2 == 7:
                self.drawGameOver()
            elif self.gameOverCounter % gameOverCount == 0:
                self.gameOverCounter2 += 1
                self.drawFrame()
                self.berry.draw(self.screen)
                if self.snake.exists:
                    self.snake.draw(self.screen)
                    self.snake.exists = False
                else:
                    self.snake.exists = True
           
        elif self.state == self.WIN:
            self.drawWin()
        pygame.display.update()

    def run(self):
        while True:
            self.handleEvents()
            self.update()
            self.draw()
            self.clock.tick(60)



game = Game()

game.run()

