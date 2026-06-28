import pygame
from pygame.locals import *
import sys
import json
import random
with open('I:/IDK/level1.json', "r") as f:
    level1 = json.load(f)

pygame.init()
vec = pygame.math.Vector2

HEIGHT = 1080
WIDTH = 1920
ACC = 2500
FRIC = -12
FPS = 165
PROJ_LIMIT = 100
GRAVITY = 2000
CURRENT_GUN = "pistol"

FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IDK")

class Projectile(pygame.sprite.Sprite): #esto son los proyectiles en general
    def __init__(self, projectile_type, direction):
        super().__init__()
        if projectile_type == "bullet": #las balas se usan para casi todo
            self.surf = pygame.Surface((2, 2))
            self.surf.fill((255, 0, 0))
            self.rect = self.surf.get_rect()

            self.pos = vec(P1.pos + (0, -40))
            self.vel = direction * 2000
            self.acc = vec(0, 0)

    def move(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for hit in hits:
            if self.vel.y > 0:
                self.kill()
            if self.vel.y < 0:
                self.kill()

        self.pos += self.vel * dt
        self.rect.center = self.pos

class Player(pygame.sprite.Sprite): #obviamente el jugador
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((30, 40))
        self.surf.fill((128, 255, 40))
        self.rect = self.surf.get_rect()

        self.pos = vec((level1["spawn"]))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def move(self):
        self.acc = vec(0, GRAVITY)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_a]:
            self.acc.x = -ACC
        if pressed_keys[K_d]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc * dt
        self.pos += self.vel * dt

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        

    def update(self):
        self.rect.midbottom = self.pos

        side_hits = pygame.sprite.spritecollide(self, walls, False)
        for hit in side_hits:
            if self.vel.x > 0:
                self.vel.x = 0
                self.pos.x = hit.rect.left - (self.rect.width / 2)
                self.rect.midbottom = self.pos
            if self.vel.x < 0:
                self.vel.x = 0
                self.pos.x = hit.rect.right + (self.rect.width / 2)
                self.rect.midbottom = self.pos

        top_bottom_hits = pygame.sprite.spritecollide(self, floors_roofs, False)
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
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.vel.y = -1100
    
    def drop(self):                                
        self.vel.y = 1200 
    
    def shoot(self, gun):
        if gun == "pistol":
            player_pos = vec(P1.rect.center)
            mouse_pos = vec(pygame.mouse.get_pos())

            base_direction = mouse_pos - player_pos
            base_direction = base_direction.normalize()
            
            direction = base_direction

            bull = Projectile("bullet", direction)
            all_sprites.add(bull)
            projectiles.add(bull)

        if gun == "shotgun":
            player_pos = vec(P1.rect.center)
            mouse_pos = vec(pygame.mouse.get_pos())
            
            base_direction = mouse_pos - player_pos
            base_direction = base_direction.normalize()
            
            for pellet in range(1, 13):
                spread = random.uniform(-15, 15)

                direction = base_direction.rotate(spread)

                bull = Projectile("bullet", direction)
                all_sprites.add(bull)
                projectiles.add(bull)

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, pos_x, pos_y):
        super().__init__()
        self.surf = pygame.Surface((width, height))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect()
        self.rect.topleft = (pos_x, pos_y)

P1 = Player()

projectiles = pygame.sprite.Group()
non_projectiles = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

all_sprites.add(P1)
non_projectiles.add(P1)

floors_roofs = pygame.sprite.Group()
walls = pygame.sprite.Group()

for plat in level1["platforms"]:
    x = plat[0]
    y = plat[1]
    w = plat[2]
    h = plat[3]

    new_plat = Platform(w, h, x, y)

    platforms.add(new_plat)
    all_sprites.add(new_plat)
    non_projectiles.add(new_plat)

    if w > h:
        floors_roofs.add(new_plat)
    else:
        walls.add(new_plat)

#utility functions (basically all the shit that for some reason doesn't work inside classes)
def switch(weapon):
        global CURRENT_GUN

        if weapon == "pistol":
            CURRENT_GUN = "pistol"
        if weapon == "shotgun":
            CURRENT_GUN = "shotgun"

#Main game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                P1.jump()
            if event.key == pygame.K_s:
                P1.drop()
            
            if event.key == pygame.K_2:
                switch("pistol")
            if event.key == pygame.K_3:
                switch("shotgun")

        if event.type == pygame.MOUSEBUTTONDOWN:
            P1.shoot(CURRENT_GUN)

    displaysurface.fill((0,0,0))

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
    for entity in projectiles:
        entity.move()
        displaysurface.blit(entity.surf, entity.rect)
    
    pygame.display.update()
    dt = FramePerSec.tick(FPS) / 1000
    P1.move()
    P1.update()

