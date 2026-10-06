import pygame
from random import randint
import os
import sys

pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error:
    sound_enabled = False

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

save_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Schlange")
os.makedirs(save_dir, exist_ok=True)
save_file = os.path.join(save_dir, "besto.txt")

def saveIt(besto):
    with open(save_file, "w") as arquivo:
        arquivo.write(str(besto))

def loadIt():
    try:
        with open(save_file, "r") as arquivo:
            return int(arquivo.read())
    except (FileNotFoundError, ValueError):
        return 0

class mona:
    w = 640
    h = 480

class Schlange:
    w = 25
    h = 25
    x = (mona.w / 2) - (w / 2)
    y = (mona.h / 2) - (h / 2)
    rapideza = 5
    way = -1
    tamain = 1

class Apfel:
    r = 20
    x = randint(r, mona.w - r)
    y = randint(r, mona.h - r)

def circleCollision(Schl: object, cX: float, cY: float, r: float) -> bool:
    pX = max(Schl.left, min(cX, Schl.right))
    pY = max(Schl.top, min(cY, Schl.bottom))
    dX = cX - pX
    dY = cY - pY
    return dX**2 + dY**2 <= r**2

def bigBoy(body: list, paused: bool) -> None:
    if not paused:
        for position in body[:-1]:
            pygame.draw.rect(monalisa, (255, 212, 59), (position[0], position[1], Schlange.w, Schlange.h))
    else:
        for position in body[:-1]:
            pygame.draw.rect(monalisa, (205, 162, 9), (position[0], position[1], Schlange.w, Schlange.h))

def reset():
    global pintos, timingBrochacho, gameState, paused, hi
    Schlange.x = (mona.w / 2) - (Schlange.w / 2)
    Schlange.y = (mona.h / 2) - (Schlange.h / 2)
    Schlange.tamain = 1
    Schlange.way = -1
    body.clear()
    pintos = 0
    hi = False
    timingBrochacho = 0
    paused = False
    Apfel.x = randint(Apfel.r, mona.w - Apfel.r)
    Apfel.y = randint(Apfel.r, mona.h - Apfel.r)
    gameState = 0

pintos = 0
besto = loadIt()
body = []
hi = False
lastWay = 18

Tahoma = pygame.font.SysFont("Tahoma", 24)
escTesc = Tahoma.render("esc para fechar o jogo", True, (255, 255, 255))
gameOver = Tahoma.render("ESTÁ MORTO!", True, (255, 255, 255))
beaten_hiScore = Tahoma.render("NOVO RECORDE!!", True, (255, 255, 255))

gameState = 0
paused = False
timingBrochacho = 0

monalisa = pygame.display.set_mode((mona.w, mona.h))
pygame.display.set_caption("Schlange")
pygame.display.set_icon(pygame.transform.smoothscale(pygame.image.load(resource_path("icon/icon.png")), (32, 32)))

reloju = pygame.time.Clock()

if sound_enabled:
    ate = pygame.mixer.Sound(resource_path("sfx/hungrySchlange.wav"))
    dmg = pygame.mixer.Sound(resource_path("sfx/slicedSchlange.wav"))
    death = pygame.mixer.Sound(resource_path("sfx/SchlangeIsDead.wav"))

while True:
    reloju.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.WINDOWMINIMIZED:
            paused = True

        if event.type == pygame.KEYDOWN:

            if gameState == 0:

                if not paused:

                    if event.key == pygame.K_ESCAPE:
                        paused = True

                    elif event.key in [pygame.K_w, pygame.K_UP]:
                        if Schlange.way != 4:
                            Schlange.way = 21

                    elif event.key in [pygame.K_a, pygame.K_LEFT]:
                        if Schlange.way != 18:
                            Schlange.way = 12

                    elif event.key in [pygame.K_s, pygame.K_DOWN]:
                        if Schlange.way != 21:
                            Schlange.way = 4

                    elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                        if Schlange.way != 12:
                            Schlange.way = 18

                else:

                    if event.key == pygame.K_ESCAPE:
                        if pintos > besto:
                            besto = pintos
                            saveIt(besto)
                        pygame.quit()
                        sys.exit()

                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                        Schlange.way = lastWay
                        paused = False

            elif gameState == 0.5:

                if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                    if sound_enabled:
                        death.play()
                    gameState = 1

                if event.key == pygame.K_ESCAPE:
                    if pintos > besto:
                        besto = pintos
                        saveIt(besto)
                    pygame.quit()
                    sys.exit()

            elif gameState == 1:

                if event.key in [pygame.K_r, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER]:
                    reset()

                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    match gameState:

        case 0:

            if not paused:

                monalisa.fill((0, 190, 0))
                pointuacao = Tahoma.render(f"Pontuação: {pintos}", True, (255, 255, 255), (0, 0, 0))

                match Schlange.way:

                    case 21:
                        Schlange.y -= Schlange.rapideza

                    case 12:
                        Schlange.x -= Schlange.rapideza

                    case 4:
                        Schlange.y += Schlange.rapideza

                    case 18:
                        Schlange.x += Schlange.rapideza

                if Schlange.x >= mona.w:
                    Schlange.x = 0
                elif Schlange.x < 0:
                    Schlange.x = mona.w

                if Schlange.y >= mona.h:
                    Schlange.y = 0
                elif Schlange.y < 0:
                    Schlange.y = mona.h

                body.append([Schlange.x, Schlange.y])

                if len(body) > Schlange.tamain * 6:
                    del body[0]

                if Schlange.way != -1:
                    bigBoy(body, False)

                dieSchlange = pygame.draw.rect(monalisa, (48, 105, 152), (Schlange.x, Schlange.y, Schlange.w, Schlange.h))
                pygame.draw.circle(monalisa, (255, 0, 0), (Apfel.x, Apfel.y), Apfel.r)

                if circleCollision(dieSchlange, Apfel.x, Apfel.y, Apfel.r):

                    Apfel.x = randint(Apfel.r, mona.w - Apfel.r)
                    Apfel.y = randint(Apfel.r, mona.h - Apfel.r)

                    while circleCollision(dieSchlange, Apfel.x, Apfel.y, Apfel.r):
                        Apfel.x = randint(Apfel.r, mona.w - Apfel.r)
                        Apfel.y = randint(Apfel.r, mona.h - Apfel.r)

                    if sound_enabled:
                        ate.play()
                    Schlange.tamain += 1
                    pintos += 1

                if body.count([Schlange.x, Schlange.y]) > 1 and Schlange.way != -1:
                    Schlange.way = -1
                    gameState = 0.5

                monalisa.blit(pointuacao, (20, mona.h - 462))
                pygame.display.flip()

            else:

                monalisa.fill((0, 140, 0))
                pointuacao = Tahoma.render(f"Pontuação: {pintos}", True, (175, 175, 175), (0, 0, 0))
                pauseT = Tahoma.render("pause", True, (255, 255, 255))
                pauseTPos = pauseT.get_rect(center=(mona.w / 2, mona.h / 2))

                if Schlange.way == 21:
                    lastWay = 21
                elif Schlange.way == 12:
                    lastWay = 12
                elif Schlange.way == 4:
                    lastWay = 4
                elif Schlange.way == 18:
                    lastWay = 18

                Schlange.way = -1

                bigBoy(body, True)
                pygame.draw.rect(monalisa, (48, 105, 152), (Schlange.x, Schlange.y, Schlange.w, Schlange.h))
                pygame.draw.circle(monalisa, (175, 0, 0), (Apfel.x, Apfel.y), Apfel.r)

                monalisa.blit(pointuacao, (20, mona.h - 462))
                monalisa.blit(pauseT, pauseTPos)
                monalisa.blit(escTesc, (1, mona.h - 30))

                pygame.display.flip()

        case 0.5:

            monalisa.fill((0, 190, 0))
            timingBrochacho += 1

            if timingBrochacho == 30:

                timingBrochacho = 0

                if len(body) > 1:

                    for _ in range(min(6, len(body))):
                        del body[0]

                    if sound_enabled:
                        dmg.play()

                else:

                    if sound_enabled:
                        death.play()
                    gameState = 1

            bigBoy(body, False)
            pygame.draw.rect(monalisa, (48, 105, 152), (Schlange.x, Schlange.y, Schlange.w, Schlange.h))
            pygame.draw.circle(monalisa, (255, 0, 0), (Apfel.x, Apfel.y), Apfel.r)

            pygame.display.flip()


        case 1:

            monalisa.fill((0, 0, 0))

            if pintos > besto and not hi:
                besto = pintos
                saveIt(besto)
                hi = True

            pointuacao = Tahoma.render(f"Pontuação: {pintos}", True, (255, 255, 255))
            hiScore = Tahoma.render(f"Recorde: {besto}", True, (255, 255, 255))

            pointuacaoPos = pointuacao.get_rect(center=(mona.w / 2, mona.h / 2))
            gameOverPos = gameOver.get_rect(midbottom=(pointuacaoPos.centerx, pointuacaoPos.top - 10))
            recordePos = hiScore.get_rect(midtop=(pointuacaoPos.centerx, pointuacaoPos.bottom + 10))
            beaten_hiScorePos = beaten_hiScore.get_rect(midtop=(pointuacaoPos.centerx, pointuacaoPos.bottom + 10))

            monalisa.blit(gameOver, gameOverPos)
            monalisa.blit(pointuacao, pointuacaoPos)
            monalisa.blit(escTesc, (1, mona.h - 30))

            if hi:
                monalisa.blit(beaten_hiScore, beaten_hiScorePos)
            else:
                monalisa.blit(hiScore, recordePos)

            pygame.display.flip()