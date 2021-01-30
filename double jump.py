WINDOW_TITLE = "mario (double) jump"
 
import pygame
from pygame.locals import Rect, Color
from pygame.sprite import Sprite
from pygame import *
 
class Mario(Sprite):
    def __init__(self):
        """
        hold key = move
        tap = jumping"""
        Sprite.__init__(self)
        self.image = Surface([40,80])
        self.image.fill(Color("gray80"))
        self.rect = self.image.get_rect()        
        self.screen = pygame.display.get_surface()
 
        # start mario centered on bot 
        self.rect.midbottom = self.screen.get_rect().midbottom
 
        self.velx, self.vely = 0., 0.
        self.can_doublejump = True
        self.can_jump = True
 
 
    def update(self):
        # gravity 
        self.vely += 4
 
        # units update velocity, even if you don't have gravity
        self.rect.left += self.velx
        self.rect.top += self.vely
 
        # Mario touched ground
        if self.rect.bottom > self.screen.get_rect().bottom:
            self.rect.bottom = self.screen.get_rect().bottom
            self.vely = 0
            self.can_doublejump = True
            self.can_jump = True
 
    
    def draw(self):        
        self.screen.blit(self.image, self.rect)       
 
    def jump(self):
        """jump if able considering cooldown and state"""
        if self.can_jump:
            self.can_jump = False
            self.vely -= 50
            print ("jump")
        elif self.can_doublejump:
            self.can_doublejump = False
            self.vely -= 50
            print ("double")
 
 
class Game(object):
    """game Main entry point. handles intialization of game and graphics, as well as game loop"""    
    done = False
    
    def __init__(self, width=800, height=600):
        """Initialize PyGame window. boilerplate stuff.
        
        variables:
            width, height = screen width, height
            screen = main video surface, to draw on
            
            fps_max     = framerate limit to the max fps
            limit_fps   = boolean toggles capping FPS, to share cpu, or let it run free.
            color_bg    = backround color, accepts many formats. see: pygame.Color() for details
        """
        pygame.init()
 
        # save w, h, and screen
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode(( self.width, self.height ))
        pygame.display.set_caption( WINDOW_TITLE )        
 
        # fps clock, limits max fps
        self.clock = pygame.time.Clock()
        self.fps_max = 40        
 
        self.mario = Mario()
 
    def main_loop(self):
        """Game() main loop goes like this:
        
            1. player input
            2. move stuff
            3. draw stuff
        """
        while not self.done:
            self.handle_events()                                
            self.update()
            self.draw()
            
            # cap FPS if: limit_fps == True
            self.clock.tick( self.fps_max )
    
    def draw(self):
        """draw screen"""
        self.screen.fill(Color("gray20"))
        self.mario.draw()
        pygame.display.flip()
        
    def update(self):
        """physics. collisions."""
        self.mario.update()
 
    def handle_events(self):
        """handle events: keyboard, mouse, etc."""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT: self.done = True
 
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.done = True
                elif event.key == K_SPACE:
                    self.mario.jump()
 
 
 
 
 
 
 
 
                    
if __name__ == "__main__":         
    print ("""Keys:ESC = quit""")
    
    game = Game()
    game.main_loop()