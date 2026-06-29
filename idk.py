import pygame
from pygame.locals import *
import random
import os
import sys
import json

def get_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(os.path.dirname(sys.executable), "_internal")
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, filename)

json_path = get_path("level1.json")

with open(json_path, "r", encoding="utf-8") as f:
    level1 = json.load(f)

pygame.init()

font = pygame.font.Font(None, 40)

class Game:
    def __init__(self):
        self.HEIGHT = 720
        self.WIDTH = 1280
        self.ACC = 2500
        self.FRIC = -12
        self.FPS = 165
        self.PROJ_LIMIT = 100
        self.GRAVITY = 2000
        self.CURRENT_GUN = "pistol"

        self.projectiles = pygame.sprite.Group()
        self.non_projectiles = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.floors_roofs = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()

        self.clock = pygame.time.Clock()

        self.vec = pygame.math.Vector2

        self.displaysurface = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
        pygame.display.set_caption("IDK")

class Button():
    def __init__(self, x, y, width, height, game, buttonText='Button', onclickFunction=None):
        self.game = game

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.onclickFunction = onclickFunction

        self.buttonRect = pygame.Rect(x, y, width, height)

        self.text = font.render(buttonText, True, (0, 0, 0))

    def process(self):
        mouse_pos = pygame.mouse.get_pos()

        color = (255, 255, 255)

        if self.buttonRect.collidepoint(mouse_pos):
            color = (150, 150, 150)

            if pygame.mouse.get_pressed()[0]:
                self.onclickFunction()

        pygame.draw.rect(self.game.displaysurface, color, self.buttonRect)

        text_rect = self.text.get_rect(center=self.buttonRect.center)

        self.game.displaysurface.blit(self.text, text_rect)

class Projectile(pygame.sprite.Sprite): #esto son los proyectiles en general
    def __init__(self, game, projectile_type, direction):
        self.game = game
        
        super().__init__()

        if projectile_type == "bullet": #las balas se usan para casi todo
            self.surf = pygame.Surface((2, 2))
            self.surf.fill((255, 0, 0))
            self.rect = self.surf.get_rect()

            self.pos = self.game.vec(self.game.player.pos) + self.game.vec(0, -40)
            self.vel = direction * 2000
            self.acc = self.game.vec(0, 0)

    def move(self):
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        for hit in hits:
            if self.vel.y > 0:
                self.kill()
            if self.vel.y < 0:
                self.kill()

        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos

class Player(pygame.sprite.Sprite): #obviamente el jugador
    def __init__(self, game):
        self.game = game
        super().__init__()
        self.surf = pygame.Surface((30, 40))
        self.surf.fill((128, 255, 40))
        self.rect = self.surf.get_rect()

        self.pos = self.game.vec((level1["spawn"]))
        self.vel = self.game.vec(0, 0)
        self.acc = self.game.vec(0, 0)

    def move(self):
        self.acc = self.game.vec(0, self.game.GRAVITY)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_a]:
            self.acc.x = - self.game.ACC
        if pressed_keys[K_d]:
            self.acc.x = self.game.ACC

        self.acc.x += self.vel.x * self.game.FRIC
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt

        if self.pos.x > self.game.WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = self.game.WIDTH
        

    def update(self):
        self.rect.midbottom = self.pos

        side_hits = pygame.sprite.spritecollide(self, self.game.walls, False)
        for hit in side_hits:
            if self.vel.x > 0:
                self.vel.x = 0
                self.pos.x = hit.rect.left - (self.rect.width / 2)
                self.rect.midbottom = self.pos
            if self.vel.x < 0:
                self.vel.x = 0
                self.pos.x = hit.rect.right + (self.rect.width / 2)
                self.rect.midbottom = self.pos

        top_bottom_hits = pygame.sprite.spritecollide(self, self.game.floors_roofs, False)
        for hit in top_bottom_hits:
            if self.vel.y > 0:
                self.pos.y = hit.rect.top + 1
                self.vel.y = 0
                self.rect.midbottom = self.pos
            if self.vel.y < 0:
                self.pos.y = hit.rect.bottom + self.rect.height
                self.vel.y = 0
                self.rect.midbottom = self.pos

    def jump(self):
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            self.vel.y = -1100
    
    def drop(self):                                
        self.vel.y = 1200 
    
    def shoot(self, gun):
        if gun == "pistol":
            player_pos = self.game.vec(self.game.player.rect.center)
            mouse_pos = self.game.vec(pygame.mouse.get_pos())

            base_direction = mouse_pos - player_pos
            base_direction = base_direction.normalize()
            
            direction = base_direction

            bull = Projectile(self.game, "bullet", direction)
            self.game.all_sprites.add(bull)
            self.game.projectiles.add(bull)

        if gun == "shotgun":
            player_pos = self.game.vec(self.game.player.rect.center)
            mouse_pos = self.game.vec(pygame.mouse.get_pos())
            
            base_direction = mouse_pos - player_pos
            base_direction = base_direction.normalize()
            
            for pellet in range(1, 13):
                spread = random.uniform(-15, 15)

                direction = base_direction.rotate(spread)

                bull = Projectile(self.game, "bullet", direction)
                self.game.all_sprites.add(bull)
                self.game.projectiles.add(bull)

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, pos_x, pos_y):
        super().__init__()
        self.surf = pygame.Surface((width, height))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect()
        self.rect.topleft = (pos_x, pos_y)

game = Game()

def quit_game():
    pygame.quit()
    sys.exit()

exit_button = Button(
    100,
    100,
    300,
    100,
    game,
    "EXIT",
    quit_game
)

game.player = Player(game)
game.all_sprites.add(game.player)

for plat in level1["platforms"]:
    x = plat[0]
    y = plat[1]
    w = plat[2]
    h = plat[3]

    new_plat = Platform(w, h, x, y)

    game.platforms.add(new_plat)
    game.all_sprites.add(new_plat)
    game.non_projectiles.add(new_plat)

    if w > h:
        game.floors_roofs.add(new_plat)
    else:
        game.walls.add(new_plat)

#utility functions (basically all the shit that for some reason doesn't work inside classes)
def switch(game, weapon):
        if weapon == "pistol":
            game.CURRENT_GUN = "pistol"
        if weapon == "shotgun":
            game.CURRENT_GUN = "shotgun"

#Main game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
                
            if event.key == pygame.K_w:
                game.player.jump()
            if event.key == pygame.K_s:
                game.player.drop()
            
            if event.key == pygame.K_2:
                switch(game, "pistol")
            if event.key == pygame.K_3:
                switch(game, "shotgun")

        if event.type == pygame.MOUSEBUTTONDOWN:
            game.player.shoot(game.CURRENT_GUN)

    game.displaysurface.fill((0,0,0))

    for entity in game.all_sprites:
        game.displaysurface.blit(entity.surf, entity.rect)
    for entity in game.projectiles:
        entity.move()
        game.displaysurface.blit(entity.surf, entity.rect)

    exit_button.process()

    pygame.display.update()

    game.dt = game.clock.tick(game.FPS) / 1000

    game.player.move()
    game.player.update()

