import pygame
from pygame.locals import *
import math

class RotatableSprite(pygame.sprite.Sprite):
  empty_canvas = None # Can't be initialized until pygame.init() has run

  def __init__(self, texture, position = (0, 0), 
               angle = 0, scale = 1.0, 
               texture_rect = None, 
               width_factor = 1.0, 
               height_factor = 1.0, 
               center_of_rotation = None, 
               smooth_noncentered_zoom = False):
    pygame.sprite.Sprite.__init__(self)
    self.smooth_noncentered_zoom = smooth_noncentered_zoom
    self.x, self.y = position
    self.angle = angle
    self.width_factor = width_factor
    self.height_factor = height_factor
    self.scale = scale

    self.setTexture(texture, texture_rect, center_of_rotation)
    if self.center_of_rotation == None:
        self.center_of_rotation = self.texture_rect.center
    # Set class variables
    if RotatableSprite.empty_canvas == None:
      empty_canvas = pygame.Surface((1, 1), SRCALPHA).convert_alpha()
      empty_canvas.fill((0, 0, 0, 0))
    self._update_draw_state()

  def setTexture(self, texture, texture_rect = None, center_of_rotation = None):
    if not (self.smooth_noncentered_zoom and center_of_rotation != None):
      self.texture = texture
      if texture_rect == None:
        texture_rect = texture.get_rect()
      self.texture_rect = texture_rect
      if center_of_rotation == None:
        center_of_rotation = self.texture_rect.center
      self.center_of_rotation = center_of_rotation
    else:
      if texture_rect == None:
        texture_rect = texture.get_rect()
      if center_of_rotation == None:
        center_of_rotation = texture_rect.center
      orig_w, orig_h = texture.get_size()
      dx, dy = (orig_w - 2*center_of_rotation[0], 
                orig_h - 2*center_of_rotation[1])
      new_w, new_h = orig_w + abs(dx), orig_h + abs(dy)

      centered_texture = pygame.Surface((new_w, new_h), 
                                        SRCALPHA).convert_alpha()
      centered_texture.fill((0, 0, 0, 0))
      centered_texture.blit(texture, (dx, dy), texture_rect)
      self.texture = centered_texture
      self.texture_rect = centered_texture.get_rect()
      self.center_of_rotation = self.texture_rect.center


  def update(self):
    self._update_draw_state()

  def _update_draw_state(self):
    # Be smarter, don't redraw stuff that has not changed
    # Also keep the squeezed image
    squeeze_size = (int(round(self.texture_rect.width * 
                               self.width_factor)),
                     int(round(self.texture_rect.height * 
                               self.height_factor)))
    sz_before_rot = (int(round(self.texture_rect.width * 
                               self.width_factor *
                               self.scale)),
                     int(round(self.texture_rect.height * 
                               self.height_factor *
                               self.scale)))

    if any(d == 0 for d in sz_before_rot):
      # Don't show anything
      canvas = empty_canvas
    else:
      # --- Start from the original texture ---
      if self.texture_rect != self.texture.get_rect:
        canvas = self.texture.subsurface(self.texture_rect)
      else:
        canvas = self.texture

      is_right_angle = self.angle % 90 == 0

      # --- Rotate ---
      if is_right_angle:
        if sz_before_rot != self.texture_rect.size:
          canvas = pygame.transform.smoothscale(canvas, sz_before_rot)
        # Make right angle images "clean"
        canvas = pygame.transform.rotate(canvas, -self.angle)
      else:
        if self.width_factor != 1.0 or self.height_factor != 1.0:
          canvas = pygame.transform.smoothscale(canvas, squeeze_size)
        canvas = pygame.transform.rotozoom(canvas, -self.angle, self.scale)

    self.image = canvas
    px, py = self.texture_rect.center
    ox, oy = self.center_of_rotation
    dx, dy = px-ox, py-oy
    sdx, sdy = self.scale*self.width_factor*dx, self.scale*self.height_factor*dy
    radians = self.angle * math.pi / 180.0
    s, c = math.sin(radians), math.cos(radians)
    x_add, y_add = c*sdx - s*sdy, c*sdy + s*sdx
    self.rect = self.image.get_rect(center = (self.x + x_add, self.y + y_add))

  def screen_2_texture_pos(self, pos):
      sx, sy = pos
      # diff to middle
      mdx, mdy = sx - self.rect.centerx, sy - self.rect.centery
      # rotate back
      radians = -self.angle * math.pi / 180.0
      s, c = math.sin(radians), math.cos(radians)
      x, y = c*mdx - s*mdy, c*mdy + s*mdx
      unrot_w, unrot_h = (int(round(self.texture_rect.width * 
                                    self.width_factor *
                                    self.scale)),
                          int(round(self.texture_rect.height * 
                                    self.height_factor *
                                    self.scale)))
      sx, sy = x/unrot_w, y/unrot_h
      return sx + 0.5, sy + 0.5

  def get_texture_at(self, pos):
    """
    Gets the pixel value at pos in texture. The coordiates are (0, 0) in the 
    top left corner and (1, 1) in the bottom right corner. 
    """
    nx, ny = pos
    tex_pos = (int(self.texture_rect.left + nx * self.texture_rect.width), 
               int(self.texture_rect.top + ny * self.texture_rect.height))
    return self.texture.get_at(tex_pos)

  def covers(self, pos):
    ipos = tip_sprite.screen_2_texture_pos(pos)
    return (ipos[0] >= 0.0 and ipos[0] <= 1.0 and
            ipos[1] >= 0.0 and ipos[1] <= 1.0 and
            tip_sprite.get_texture_at(ipos)[3] != 0)
    

if __name__ == "__main__":
    def draw_sprites():
        sprite_group.clear(screen, background)
        sprite_group.update() # Calls update on all sprites
        dirty = sprite_group.draw(screen)
        pygame.display.update(dirty)

    pygame.init()
    from pygame.colordict import THECOLORS

    width, height = 320, 240

    screen = pygame.display.set_mode((width, height), 0*FULLSCREEN)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(THECOLORS['white'])
    for x in xrange(0, width, 10):
        for y in xrange(0, height, 10):
            background.set_at((x, y), THECOLORS["gray"])

    screen.blit(background, (0, 0))
    pygame.display.update()

    mouse_texture = pygame.image.load('mouse_pointer.png').convert_alpha()
    mouse_texture_nopad = \
        pygame.image.load('mouse_pointer_unpadded.png').convert_alpha()
    # A rotating sprite, one rotation in four seconds
    rotating_sprite = RotatableSprite(mouse_texture, (20, 20))
    # A sprite that use a texture without a single pixel transparent border
    noborder_sprite = RotatableSprite(mouse_texture_nopad, (20, 60))
    # A sprite that only use the left part of the texture
    half_rect = mouse_texture.get_rect(width = mouse_texture.get_width()/2)
    half_sprite = \
        RotatableSprite(mouse_texture, (60, 20), 
                        texture_rect = half_rect, 
                        angle = 180)
    # A sprite of half width
    squeezed_sprite = RotatableSprite(mouse_texture, (100, 20), 
                                      width_factor = 0.5)
    # A sprite with double height
    high_sprite = RotatableSprite(mouse_texture, (160, 30), height_factor = 2)
    # A side, double sized sprite
    big_sprite = RotatableSprite(mouse_texture, (220, 60), 
                                 width_factor = 2.0, scale = 2.0)
    # A sprite rotating about it's tip
    tip_sprite = RotatableSprite(mouse_texture, (90, 90), 
                                  scale = 2.0,
                                  center_of_rotation = (1, 1))
    # A sprite rotating about it's tip smooth rot
    smooth_tip_sprite = RotatableSprite(mouse_texture, (150, 90), 
                                        scale = 2.0,
                                        center_of_rotation = (1, 1), 
                                        smooth_noncentered_zoom = True)
    # A sprite rotating about it's tip smooth rot
    smooth_tip_sprite2 = RotatableSprite(mouse_texture, (150, 150), 
                                        scale = 2.0,
                                        smooth_noncentered_zoom = True)

    four_sec_rot_sprites = [rotating_sprite, half_sprite, squeezed_sprite,
                            noborder_sprite, high_sprite, big_sprite, 
                            tip_sprite, smooth_tip_sprite, smooth_tip_sprite2]
    sprite_group = pygame.sprite.OrderedUpdates(four_sec_rot_sprites)

    clock = pygame.time.Clock()

    run = True
    MS_PER_SEC = 1000.0
    while run:
        secs = clock.tick(40) / MS_PER_SEC
        events = pygame.event.get()
        for event in events:
            if (event.type == QUIT or 
                (event.type == KEYDOWN and event.key in [K_ESCAPE, K_q])):
                run = False
        for s in four_sec_rot_sprites:
            s.angle += 0.25 * 360 * secs
        #pos_in_big = tip_sprite.screen_2_texture_pos(*(pygame.mouse.get_pos()))
        #if (pos_in_big[0] >= 0.0 and pos_in_big[0] <= 1.0 and
            #pos_in_big[1] >= 0.0 and pos_in_big[1] <= 1.0 and
            #tip_sprite.get_texture_at(pos_in_big)[3] != 0):
        if tip_sprite.covers(pygame.mouse.get_pos()):
          pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        else:
          pygame.mouse.set_cursor(*pygame.cursors.diamond)
        draw_sprites()


