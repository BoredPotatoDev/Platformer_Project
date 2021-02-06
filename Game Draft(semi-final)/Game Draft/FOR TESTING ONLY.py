import pygame
from pygame.locals import *
from pygame import mixer
import time
import pickle
from os import path
import random

mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

width = 1300
height = 650

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Group 11')

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
WHITE = (255,255,255)
BLUE = (0,0,225)
GREEN = (0, 255, 0)

#define game variables
tile_size = 26
game_over = 0
main_menu = True
level = 0
max_level = 7
chip = 0
total_chip = 0
quote = 0

#font
font = pygame.font.SysFont('Bauhaus 93', 70)
font2 = pygame.font.SysFont('Bauhaus 93', 30)
font_chip = pygame.font.SysFont('Bauhaus 93', 25)

#Load images
bgimg_test = pygame.image.load("img/bg/bg_img2.jpg")
bgimg_anger = pygame.image.load("img/bg/bg_anger.jpg")
bgimg_bargaining = pygame.image.load("img/bg/bg_bargaining.jpg")
bgimg_depression = pygame.image.load("img/bg/bg_depression.jpg")
bgimg_acceptance = pygame.image.load('img/bg/bg_acceptance.jpg')

restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
bg_main = pygame.image.load('img/bg/bg_main.jpg')
chip_img = pygame.image.load('img/chip.png')
vhs_dead = pygame.image.load('img/vhs.png')
merge = pygame.image.load("img/continue.png")
end = pygame.image.load("img/end.png")

#--------------------load sounds (NOT BG, SOUND EFFECTS ONLY--------------------
chip_fx = pygame.mixer.Sound('img/sound/chipsound.wav')
chip_fx.set_volume(0.5)

jump_fx = pygame.mixer.Sound('img/sound/jump.wav')
jump_fx.set_volume(0.5)

death_fx = pygame.mixer.Sound('img/sound/death.wav')
death_fx.set_volume(0.3)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#function to reset level
def reset_level(level):
    player.reset (50, height - 50 )
    player.update(game_over)
    glitch_group.empty()
    lava_group.empty()
    spikes_group.empty()
    exit_group.empty()
    platform_group.empty()

    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

#---------------------------------GRID LINES---------------------------------------------------------
def draw_grid():
    for line in range(0, 50):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, height))

#------------------Fade Transtion-------------------
def fadefirst(width, height):
    fade = pygame.Surface((width, height))
    fade.fill((0,0,0))
    for alpha in range(0, 150):
        fade.set_alpha(alpha)
        screen.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(2)


def fadeout(width, height):
    fade = pygame.Surface((width, height))
    fade.fill((0,0,0))
    for alpha in range(-500, 150):
        fade.set_alpha(alpha)
        screen.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(5)




class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        screen.blit(self.image, self.rect)

        return action

#-----------------------PLAYER------------------------------Z
class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
            #set cooldown varible
            cooldown = 550 #milliseconds
            dx = 0
            dy = 0
            walk_cooldown = 3
            col_thresh = 20

            if game_over == 0:
                #get keypresses
                key = pygame.key.get_pressed()
                if key[pygame.K_w] and self.jumped == False and self.in_air == False:
                    jump_fx.play()
                    self.vel_y = -12
                    self.jumped = True
                if key[pygame.K_w] == False:
                    self.jumped = False
                if key[pygame.K_a]:
                    dx -= 4
                    self.counter += 1
                    self.direction = -1
                if key[pygame.K_d]:
                    dx += 4
                    self.counter += 1
                    self.direction = 1
                if key[pygame.K_a] == False and key[pygame.K_d] == False:
                    self.counter = 0
                    self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]


                #record current time
                time_now = pygame.time.get_ticks()
                #shoot
                if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
                    if self.direction == 1:
                        direction = 1
                        bullet = Bullets(self.rect.x, self.rect.centery, direction)
                        bullet_group.add(bullet)
                        self.last_shot = time_now
                    if self.direction == -1:
                        direction = -1
                        bullet = Bullets(self.rect.x, self.rect.centery, direction)
                        bullet_group.add(bullet)
                        self.last_shot = time_now


                #handle animation
                if self.counter > walk_cooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images_right):
                        self.index = 0
                    if self.direction == 1:
                        self.image = self.images_right[self.index]
                    if self.direction == -1:
                        self.image = self.images_left[self.index]

                #add gravity
                self.vel_y += 1
                if self.vel_y > 20:
                    self.vel_y = 20
                dy += self.vel_y

                #check for collision
                self.in_air = True
                for tile in world.tile_list:
                    #check for collision in x direction
                    if tile[1].colliderect(self.rect.x + dx - 5, self.rect.y, self.width , self.height):
                        dx = 0
                    #check for collision in y direction
                    if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width - 10, self.height):
                        #check if below the ground i.e. jumping
                        if self.vel_y < 0:
                            dy = tile[1].bottom - self.rect.top
                            self.vel_y = 0
                        #check if above the ground i.e. falling
                        elif self.vel_y >= 0:
                            dy = tile[1].top - self.rect.bottom
                            self.vel_y = 0
                            self.in_air = False

                #check for collision with enemies
                if pygame.sprite.spritecollide(self, glitch_group, False):
                    game_over = 0

                #check for collision with lava
                if pygame.sprite.spritecollide(self, lava_group, False):
                    game_over = 0

                #check for spike collision
                if pygame.sprite.spritecollide(self, spikes_group, False):
                    game_over = 0

                #check for collision with exit
                if pygame.sprite.spritecollide(self, exit_group, False):
                    game_over = 1

                #check for collision with platforms
                for platform in platform_group:
                    #collision in the x direction
                    if platform.rect.colliderect(self.rect.x + dx - 5, self.rect.y, self.width, self.height):
                        dx = 0
                    #collision in the y direction
                    if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                        #check if below platform
                        if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                            self.vel_y = 0
                            dy = platform.rect.bottom - self.rect.top
                        #check if above platform
                        elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                            self.rect.bottom = platform.rect.top - 1
                            self.in_air = False
                            dy = 0
                            self.vel_y = 0
                        #move sideways with the platform
                        if platform.move_x != 0:
                            self.rect.x += platform.move_direction

                #Update coordiantes
                self.rect.x += dx
                self.rect.y += dy

            elif game_over == -1:
                self.image = self.img_dead
                draw_text('GAME OVER!', font, GRAY, (width // 2) - 200, height // 2)
                draw_text('Chips is your memory! Be careful...', font_chip, RED, (width // 2 - 200) , (height //2) + 65)

            #draw player onto the screen
            screen.blit(self.image, self.rect)

            return game_over

    def reset(self, x, y):
            self.images_right = []
            self.images_left = []
            self.index = 0
            self.counter = 0
            for num in range(1,7):
                img = pygame.image.load(f'img/MOVING{num}.png')
                img_right = pygame.transform.scale(img, (25, 45))
                img_left = pygame.transform.flip(img_right, True, False)
                self.images_right.append(img_right)
                self.images_left.append(img_left)
            dead = self.dead_image = pygame.image.load('img/DEAD3.png')
            self.img_dead = pygame.transform.scale(dead, (40, 50))
            self.image = self.images_right[self.index]
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.vel_y = 0
            self.jump = False
            self.direction = 0
            self.in_air = True
            self.in_air = True
            self.last_shot = pygame.time.get_ticks()

#---------BULLETS------
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, direction ):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.direction = direction
        self.vel = 13*direction

    def update(self):
        self.rect.x += self.vel
        if self.rect.x > 1200:
            self.kill()

        #check for collision with blocks
        for tile in world.tile_list:
            #check for collision in x direction
            if tile[1].colliderect(self.rect):
                self.kill()


        #check for collision with enemies
        if pygame.sprite.spritecollide(self, glitch_group, True):
            self.kill()



#-----------------WORLD--------------------------
class World():
    def __init__(self, data):
        self.tile_list = []



        #Copy paste this for bg per level
        #if level == 0:
        #    pygame.mixer.music.load('img/sound/level0.mp3')
        #    pygame.mixer.music.play(1)

        #load images for blocks
        #stage 0 tile number = 1 and 2
        tutorial1_block = pygame.image.load('img/blocks/tutorial1.jpg')
        tutorial2_block = pygame.image.load('img/blocks/tutorial2.jpg')
        #stage 1 denial number = 11 and 12
        denial1_block = pygame.image.load('img/blocks/denial1.jpg')
        denial2_block = pygame.image.load('img/blocks/denial2.jpg')
        #stage 2 anger number = 21 and 22
        anger1_block = pygame.image.load('img/blocks/anger1.jpg')
        anger2_block = pygame.image.load('img/blocks/anger2.jpg')
        #stage 3 bargaining number = 31 and 32
        bargaining1_block = pygame.image.load('img/blocks/bargaining1.jpg')
        bargaining2_block = pygame.image.load('img/blocks/bargaining2.jpg')
        #stage 4 depression number = 41 and 42
        depression1_block = pygame.image.load('img/blocks/depression1.jpg')
        depression2_block = pygame.image.load('img/blocks/depression2.jpg')
        #stage 5 depression number = 51 and 52
        acceptance1_block = pygame.image.load('img/blocks/acceptance1.jpg')
        acceptance2_block = pygame.image.load('img/blocks/acceptance2.jpg')

        #----------Variable Placement------------------
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                #--------------------------------------- Tiles ---------------------------
                #----- FOR INTRO INTRO -----
                if tile == 1:
                    img = pygame.transform.scale(tutorial1_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(tutorial2_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #----- FOR DENIAL LEVEL  -----
                if tile == 11:
                    img = pygame.transform.scale(denial1_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 12:
                    img = pygame.transform.scale(denial2_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #----- FOR ANGER LEVEL  -----
                if tile == 21:
                    img = pygame.transform.scale(anger1_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 22:
                    img = pygame.transform.scale(anger2_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #----- FOR BARGAINING LEVEL  -----
                if tile == 31:
                    img = pygame.transform.scale(bargaining1_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 32:
                    img = pygame.transform.scale(bargaining2_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #----- FOR DEPRESSION LEVEL  -----
                if tile == 41:
                    img = pygame.transform.scale(depression1_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 42:
                    img = pygame.transform.scale(depression2_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                #----- FOR ACCEPTANCE LEVEL  -----
                if tile == 51:
                    img = pygame.transform.scale(acceptance1_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 52:
                    img = pygame.transform.scale(acceptance2_block, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                #----- FOR LEVEL VARIABLES  -----
                if tile == 3:
                    glitch = Enemy(col_count * tile_size, row_count * tile_size - 15)
                    glitch_group.add(glitch)
                if tile == 5:
                    chip = Chip(col_count * tile_size + (tile_size // 2),row_count * tile_size )
                    chip_group.add(chip)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    spikes = Spikes(col_count * tile_size, row_count * tile_size)
                    spikes_group.add(spikes)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - 10)
                    exit_group.add(exit)
                #----- FOR MOVING TILES  -----
                #----- UP AND DOWN MOVEMENT  -----
                if tile == 9:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                #----- LEFT AND RIGHT MOVEMENT -----
                if tile == 10:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (0, 0, 0), tile[1], 2)

#--------------- VARIABLES --------------------

class Enemy(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('img/enemy/MOVING1.png')
            self.image = pygame.transform.scale(img, (21, 42))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_direction = 1
            self.move_counter = 0

        def update(self):
            self.rect.x += self.move_direction
            self.move_counter += random.randrange(10, 25)
            if self.move_counter > 500:
                self.image  = pygame.transform.flip(self.image, True, False)
                self.move_direction *= -1
                self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('img/lava.png')
            self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_direction = 1
            self.move_counter = 0

class Spikes(pygame.sprite.Sprite):
        def __init__(self, x, y):

            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('img/spikes.png')
            self.image = pygame.transform.scale(img, (tile_size, tile_size))

            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_direction = 1
            self.move_counter = 0

class Chip(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('img/chip.png')
            self.image = pygame.transform.scale(img, (tile_size + 10, tile_size + 10))
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)

class Exit(pygame.sprite.Sprite):
        def __init__(self, x, y):

            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('img/exit.png')
            self.image = pygame.transform.scale(img, (tile_size, tile_size + 10))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_direction = 1
            self.move_counter = 0

class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y, move_x, move_y):
            pygame.sprite.Sprite.__init__(self)
            img = pygame.image.load('img/blocks/white.jpg')
            self.image = pygame.transform.scale(img, (tile_size + 20, tile_size // 2))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.move_direction = 1
            self.move_counter = 0
            self.move_x = move_x
            self.move_y = move_y

        def update(self):
            self.rect.x += self.move_direction * self.move_x
            self.rect.y += self.move_direction * self.move_y
            self.move_counter += 1
            if self.move_counter > 50:
                self.move_direction *= -1
                self.move_counter *= -1

# ---------------------------- MAP TILES ----------------------
world_data = [
[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 5, 0, 0, 1, 0, 0, 0, 10, 0, 0, 0, 0, 0, 1, 6, 6, 6, 6, 6, 1, 0, 1, 0, 0, 1, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 10, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 7, 7, 7, 7, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 7, 7, 7, 7, 7, 1, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 2],
[2, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 1, 6, 6, 6, 6, 6, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 2],
[2, 0, 0, 0, 7, 7, 7, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 7, 7, 7, 7, 1, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 7, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 10, 0, 2],
[2, 7, 7, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 2],
[2, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 9, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 2],
[2, 0, 0, 0, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1, 1, 7, 1, 1, 0, 0, 3, 0, 0, 0, 1, 0, 5, 0, 3, 0, 0, 0, 1, 6, 6, 6, 1, 6, 6, 6, 1, 1, 1, 1, 5, 2],
[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
]

player = Player(50, height -50 )

#create sprite group
bullet_group = pygame.sprite.Group()
glitch_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
chip_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

#Chip symbol
chip_num = Chip(tile_size, tile_size)
chip_group.add(chip_num)

#---------------------- CHANGE THE TILES, THEN RUN THE CODE. DONT FORGET TO CHANGE THE LEVEL BEFORE RUNNING THE CODE
#---------------------- WB MEANS SAVING IT INTO THE PICKLE FILE, RB MEANS CALLING IT. BE CAREFUL!
pickle_out = open("level0_data","wb")
pickle.dump(world_data,pickle_out)
pickle_out.close()

pickle_in = open('level0_data', 'rb')
world_data = pickle.load(pickle_in)


# --------------------- IF ALL THE LEVEL IS FINISHED, DISABLE THE PICKLES THEN MAKE THIS CODE ACTIVE
#if path.exists(f'level{level}_data'):
#   pickle_in = open(f'level{level}_data', 'rb')
#   world_data = pickle.load(pickle_in)

world = World(world_data)

#create buttons
restart_button = Button(width // 2 - 140, height // 2 + 100, restart_img)
start_button = Button(width // 2 - 530, height // 2 , start_img)
exit_button = Button(width // 2 + 60, height // 2 -10, exit_img)
#Ending
merge_button = Button(width // 2 - 530, height // 2 , merge)
skip_button = Button(width // 2 + 60, height // 2 -10, end)

run = True
while run:



        clock.tick(fps)
        #------------------ BACKGROUND FOR EACH LEVEL
        # INTRO
        if level == 0:
            image = pygame.transform.scale(bgimg_test, (width, height ))
            screen.blit(image, (0, 0))
            draw_text('Tutorial', font2, GRAY, (width // 2) - 220, height // 2)


        # DENIAL
        if level == 1:
            background_colour = (255,255,255)
            screen.fill(background_colour)
            draw_text('DENIAL', font2, BLACK, (width // 2) - 220, height // 2)
        # ANGER
        if level == 2:
            image = pygame.transform.scale(bgimg_anger, (width, height ))
            screen.blit(image, (0, 0))
            draw_text('ANGER', font2, RED, (width // 2) - 220, height // 2)
        # BARGAINING
        if level == 3:
            image = pygame.transform.scale(bgimg_bargaining, (width, height ))
            screen.blit(image, (0, 0))
            draw_text('BARGAINING', font2, BLACK, (width // 2) - 220, height // 2)
        # DEPRESSION
        if level == 4:
            image = pygame.transform.scale(bgimg_depression, (width, height ))
            screen.blit(image, (0, 0))
            draw_text('DEPRESSION', font2, BLUE, (width // 2) - 220, height // 2)
        # DEPRESSION
        if level == 5:
            image = pygame.transform.scale(bgimg_acceptance, (width, height ))
            screen.blit(image, (0, 0))
            draw_text('ACCEPTANCE', font2, WHITE, (width // 2) - 220, height // 2)
        # SEMI FINAL
        if level == 6:
            background_colour = (255,255,255)
            screen.fill(background_colour)
        # FINAL WITH OPTION
        if level == 7:
            background_colour = (0, 0, 0)
            screen.fill(background_colour)
            if merge_button.draw():
                font = pygame.font.SysFont(None, 60)
                img = font.render('Sample text', True, GRAY)
                screen.blit(img, (100, 100))

            if skip_button.draw():
                font = pygame.font.SysFont(None, 60)
                img = font.render('Sample text', True, GRAY)
                screen.blit(img, (100, 100))

        # MAIN MENU
        if main_menu == True:
            image = pygame.transform.scale(bg_main, (width, height))
            screen.blit(image, (0, 0))
            key = pygame.key.get_pressed()
            if exit_button.draw() or key[pygame.K_ESCAPE]:
                run = False
                fadefirst(width, height)
            if start_button.draw() or key[pygame.K_RETURN]:
                main_menu = False
                fadefirst(width, height)
        else:
            world.draw()
            #draw_grid()

            if game_over == 0:
                glitch_group.update()
                platform_group.update()
                #Collecting chip
                if pygame.sprite.spritecollide(player, chip_group, True):
                    image = pygame.transform.scale(vhs_dead, (width, height ))
                    screen.blit(image, (0, 0))
                    chip += 1
                    chip_fx.play()
                    total_chip = chip
                    #delattr(Player, "reset")
                #draw_text('X ' + str(total_chip), font_chip, WHITE, 45, 13)

            #update sprite groups
            bullet_group.update()

            glitch_group.draw(screen)
            lava_group.draw(screen)
            spikes_group.draw(screen)
            chip_group.draw(screen)
            exit_group.draw(screen)
            platform_group.draw(screen)
            bullet_group.draw(screen)

            game_over = player.update(game_over)

            #if player has died
            if game_over == -1:
                death_fx.play()
                key = pygame.key.get_pressed()
                if restart_button.draw() or key[pygame.K_RETURN]:
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    total_chip = total_chip - chip
                    chip = 0
                    fadefirst(width, height)


            #if player has completed the level
            if game_over == 1:
                fadefirst(width, height)
                quote += 1
                if quote == 1:
                    draw_text('are you healed or just distracted?', font2, GRAY, (width // 2) - 220, height // 2)
                    fadeout(width, height)
                if quote == 2:
                    draw_text('am i really low maintenance or am i just used to being neglected?', font2, GRAY, (width // 2) - 450, height // 2)
                    fadeout(width, height)
                if quote == 3:
                    draw_text('"Giving up is what kills people” – Hellsing', font2, GRAY, (width // 2) - 300, height // 2)
                    fadeout(width, height)
                if quote == 4:
                    draw_text('“How can you move forward when you keep regretting the past?” ', font2, GRAY, (width // 2) - 450, height // 2)
                    draw_text('– Fullmetal Alchemist', font2, GRAY, (width // 2) + 100, height // 2 + 30)
                    fadeout(width, height)
                if quote == 5:
                    draw_text('“No matter how deep the night, it always turns to day, eventually.”', font2, GRAY, (width // 2) - 450, height // 2)
                    draw_text('– One Piece', font2, GRAY, (width // 2) + 100, height // 2 + 30)
                    fadeout(width, height)
                level += 1
                if level <= max_level:
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    #total_chip = chip
                else:
                    draw_tetx('YOU WIN!', font, GRAY, (width // 2) - 140, height // 2)
                    if restart_button.draw():
                        level = 1
                        world_data = []
                        world = reset_level(level)
                        game_over = 0
                        chip = 0


        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            fadefirst(width, height)
            world_data = []
            world = reset_level(level)
            game_over = 0
            total_chip = total_chip - chip
            chip = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False



        pygame.display.update()

pygame.quit()



