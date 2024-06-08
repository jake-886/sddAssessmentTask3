import pygame
from pygame.math import Vector2
from pygame import Color
import random
from pygame import constants

pygame.init()
screen = pygame.display.set_mode(Vector2(0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

displayInfo = pygame.display.Info()
screenWidth = displayInfo.current_w
screenHeight = displayInfo.current_h

platformCount = 100
platformColor = Color(255, 255, 0)
platformOffset = 100
platformSize = Vector2(screenWidth * 0.1, screenHeight * 0.01)
gravity = round(-screenHeight * 1.5)
terminalVelocity = screenHeight * 2
characterRadius = screenHeight * 0.05
characterImage = pygame.transform.scale(pygame.image.load("characterImage.png"), Vector2(characterRadius, characterRadius))

class character():
    def __init__(self):
        self.position = Vector2(screenWidth / 2, 0)
        self.velocity = Vector2(0, 0)

class menuButton():
    def __init__(self, buttonSize, buttonCenter, buttonColor, buttonId, buttonText, textColor):
        self.buttonId = buttonId
        self.size = buttonSize
        self.center = buttonCenter
        buttonRect = pygame.Rect(0, 0, buttonSize.x, buttonSize.y)
        buttonRect.center = buttonCenter
        
        font = pygame.font.SysFont("Arial", 25)
        text = font.render(buttonText, False, textColor)
        textRect = text.get_rect(center = buttonCenter)

        pygame.draw.rect(screen, buttonColor, buttonRect)
        screen.blit(text, textRect)

defaultVariables = {
    "gameState": "menu",
    "character": character(), 
    "pressedKeys": pygame.key.get_pressed(),
    "mouseClicked": False,
    "mousePosition": pygame.mouse.get_pos(),
    "deltaTime": 0,
    "score": 0,
    "zoneHeight": 200,
    "zoneVelocity": 0,
}

def generatePlatforms(currentHeight):
    platforms = []
    for i in range(0, platformCount):
        height = currentHeight + (i - platformCount / 2) * platformOffset
        random.seed(height)
        platforms.append(Vector2(random.randint(0, screenWidth), height))
    random.seed(currentHeight)

    return platforms

def gameHandler(dynamicVariables):
    screen.fill(Color(0, 100, 255))

    platforms = generatePlatforms(round(dynamicVariables["character"].position.y, -2))
    movementVector = 0

    dynamicVariables["score"] = round(-dynamicVariables["character"].position.y)
    
    if dynamicVariables["pressedKeys"][constants.K_a]:
        movementVector -= 1
    if dynamicVariables["pressedKeys"][constants.K_d]:
        movementVector += 1

    dynamicVariables["zoneVelocity"] = 0.1 * terminalVelocity - dynamicVariables["character"].velocity.y * 0.75 + (dynamicVariables["score"] * 0.001)

    dynamicVariables["zoneHeight"] -= dynamicVariables["zoneVelocity"] * dynamicVariables["deltaTime"]

    dynamicVariables["character"].velocity = Vector2(dynamicVariables["character"].velocity.x, max(-terminalVelocity, min(terminalVelocity, dynamicVariables["character"].velocity.y + gravity * dynamicVariables["deltaTime"])))
    dynamicVariables["character"].position += (Vector2(movementVector * (screenWidth * 0.5), 0) + dynamicVariables["character"].velocity) * dynamicVariables["deltaTime"]

    if dynamicVariables["character"].position.y + characterRadius / 2 > dynamicVariables["zoneHeight"]:
        dynamicVariables["gameState"] = "dead"

    if dynamicVariables["character"].position.x < 0:
        dynamicVariables["character"].position.x = screenWidth
    elif dynamicVariables["character"].position.x > screenWidth:
        dynamicVariables["character"].position.x = 0

    for platformPosition in platforms:
        if dynamicVariables["character"].velocity.y < 0:
            if dynamicVariables["character"].position.x < platformPosition.x + platformSize.x / 2 and dynamicVariables["character"].position.x > platformPosition.x - platformSize.x / 2:
                if abs(dynamicVariables["character"].position.y - platformPosition.y) - characterRadius / 2 < characterRadius / 2 and dynamicVariables["character"].position.y > platformPosition.y:
                  dynamicVariables["character"].velocity.y = terminalVelocity * 0.25

        relativePlatformHeight = dynamicVariables["character"].position.y - platformPosition.y
        platformRect = pygame.Rect(0, 0, platformSize.x, platformSize.y)
        platformRect.center = Vector2(platformPosition.x, screenHeight / 2 + relativePlatformHeight)
        pygame.draw.rect(screen, platformColor, platformRect)


    characterRect = pygame.Rect(0, 0, characterRadius, characterRadius)
    characterRect.center = Vector2(dynamicVariables["character"].position.x, screenHeight / 2)
    screen.blit(characterImage, characterRect)
    characterRect.center = Vector2(dynamicVariables["character"].position.x - screenWidth, screenHeight / 2)
    screen.blit(characterImage, characterRect)
    characterRect.center = Vector2(dynamicVariables["character"].position.x + screenWidth, screenHeight / 2)
    screen.blit(characterImage, characterRect)

    zoneDistance = abs(dynamicVariables["character"].position.y - dynamicVariables["zoneHeight"]) - characterRadius / 2
    zoneRect = pygame.Rect(0, -zoneDistance - screenHeight / 2, screenWidth, screenHeight)
    pygame.draw.rect(screen, Color(255, 0, 0), zoneRect)

    scoreFont = pygame.font.SysFont("Arial", 25)
    scoreText = scoreFont.render("SCORE: " + str(dynamicVariables["score"]), False, Color(0, 0, 0))
    scoreRect = pygame.Rect(0, 0, screenWidth * 0.1, screenHeight * 0.1)
    screen.blit(scoreText, scoreRect)

    return dynamicVariables

def deadHandler(dynamicVariables):
    screen.fill(Color(255, 0, 0))

    text1 = "You Died!"
    text2 = "Score: " + str(dynamicVariables["score"])
    titleFont = pygame.font.SysFont("Arial", round(screenWidth * 0.05))
    scoreFont = pygame.font.SysFont("Arial", round(screenWidth * 0.025))
    titleText = titleFont.render(text1, False, Color(0, 0, 0))
    scoreText = scoreFont.render(text2, False, Color(0, 0, 0))
    titleRect = pygame.Rect(0, 0, titleFont.size(text1)[0], titleFont.size(text1)[1])
    scoreRect = pygame.Rect(0, 0, scoreFont.size(text2)[0], scoreFont.size(text2)[1])
    titleRect.center = Vector2(screenWidth * 0.5, screenHeight * 0.25)
    scoreRect.center = Vector2(screenWidth * 0.5, screenHeight * 0.35)
    screen.blit(titleText, titleRect)
    screen.blit(scoreText, scoreRect)


    restartButton = menuButton(Vector2(screenWidth * 0.2, screenHeight * 0.1), Vector2(screenWidth / 2, screenHeight / 2), Color(255, 255, 255), "menu", "MENU", Color(0,0,0))

    if dynamicVariables["mouseClicked"] == True:
        distanceX = abs(dynamicVariables["mousePosition"][0] - restartButton.center.x)
        distanceY = abs(dynamicVariables["mousePosition"][1] - restartButton.center.y)

        if distanceX < restartButton.size.x / 2 and distanceY < restartButton.size.y / 2:
            dynamicVariables = dict(defaultVariables)
            dynamicVariables["character"] = character()
    return dynamicVariables

def menuHandler(dynamicVariables):
    screen.fill(Color(255, 0, 0))

    def play():
        dynamicVariables["gameState"] = "game"

    menuFunctions = {"play": play}

    text1 = "GAME NAME"
    titleFont = pygame.font.SysFont("Arial", round(screenWidth * 0.05))
    titleText = titleFont.render(text1, False, Color(0, 0, 0))
    titleRect = pygame.Rect(0, 0, titleFont.size(text1)[0], titleFont.size(text1)[1])
    titleRect.center = Vector2(screenWidth * 0.5, screenHeight * 0.25)
    screen.blit(titleText, titleRect)
    
    playButton = menuButton(Vector2(screenWidth * 0.2, screenHeight * 0.1), Vector2(screenWidth * 0.5, screenHeight * 0.5), Color(255, 255, 255), "play", "PLAY", Color(0,0,0))
    settingsButton = menuButton(Vector2(screenWidth * 0.2, screenHeight * 0.1), Vector2(screenWidth * 0.5, screenHeight * 0.625), Color(255, 255, 255), "settings", "SETTINGS", Color(0,0,0))
    helpButton = menuButton(Vector2(screenWidth * 0.2, screenHeight * 0.1), Vector2(screenWidth * 0.5, screenHeight * 0.75), Color(255, 255, 255), "help", "HELP", Color(0,0,0))

    menuButtons = [playButton]

    if dynamicVariables["mouseClicked"] == True:
        for button in menuButtons:
            distanceX = abs(dynamicVariables["mousePosition"][0] - button.center.x)
            distanceY = abs(dynamicVariables["mousePosition"][1] - button.center.y)

            if distanceX < button.size.x / 2 and distanceY < button.size.y / 2:
                menuFunctions[button.buttonId]()


    return dynamicVariables

def main():
    gameFunctions = {"menu": menuHandler, "game": gameHandler, "dead": deadHandler}
    dynamicVariables = dict(defaultVariables)
    running = True
    
    while running:
        dynamicVariables["deltaTime"] = clock.tick() / 1000
        dynamicVariables["mouseClicked"] = False
        dynamicVariables["mousePosition"] = pygame.mouse.get_pos()
        dynamicVariables["pressedKeys"] = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                dynamicVariables["mouseClicked"] = True
            elif event.type == pygame.QUIT:
                running = False
        
        dynamicVariables = gameFunctions[dynamicVariables["gameState"]](dynamicVariables)

        pygame.display.flip()

main()
pygame.quit()