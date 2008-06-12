import pygame
from pygame.locals import *
import rawinputreader

class MousePointer(pygame.sprite.Sprite):
    """This is our snake that will move around the screen"""
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self) 
        try:
            self.image = pygame.image.load('mouse_pointer.png').convert_alpha()
        except pygame.error, message:
            self.image = pygame.Surface((10, 10), SRCALPHA).convert_alpha()
            self.image.fill((0xff, 0, 0, 0xff))
        self.rect = self.image.get_rect()
        self.rect.move_ip(x, y)

pygame.init()

display_flags = 0*DOUBLEBUF | 1*FULLSCREEN | HWSURFACE
width, height = pygame.display.list_modes()[0] 

screen = pygame.display.set_mode((width, height), display_flags)
pygame.mouse.set_visible(False)

id2mice = {}

mouse_sprites = pygame.sprite.RenderUpdates()

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((32,32,64))

screen.blit(background, (0, 0))
pygame.display.update()

clock = pygame.time.Clock()

rir = rawinputreader.rawinputreader()

run = True
while run:

    events = pygame.event.get()

    for event in events:
        if (event.type == QUIT or 
            (event.type == KEYDOWN and event.key in [K_ESCAPE, K_q])):
            run = False

    rir_events = rir.pollEvents()
    for rir_event in rir_events:
        (id, 
         usflags, ulbuttons, usbuttonflags, usbuttondata, ulrawbuttons, 
         x, y, extra) = rir_event
        button_event = rawinputreader.eventTupleToButton(rir_event)
        if not id in id2mice:
            mouse = MousePointer(width/2, height/2)
            id2mice[id] = mouse
            mouse_sprites.add(mouse)
        else:
            mouse = id2mice[id]
        button_action, button = button_event
        if button_action != (rawinputreader.NO_BUTTON):
            print button_event
        mouse.rect.move_ip(x, y)
        mouse.rect.clamp_ip(screen.get_rect())

    mouse_sprites.clear(screen, background)
    mouse_sprites.update() # Calls update on all sprites
    dirty = mouse_sprites.draw(screen)
    pygame.display.update(dirty)

    clock.tick(40)

rir.stop() # Must currently be called before ending program :-(

