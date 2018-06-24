import pygame
from RoseRoyale.Gun import Pistol, RPG, SMG, Shotgun
from RoseRoyale.Terrain import Terrain
from RoseRoyale.EndScreen import Win
import RoseRoyale.ClientConnection


class Player:
    
    def __init__(self, name, posX, posY, weapon, window, terrain):        
        self.win = window
        self.name = name
        self.terrain = terrain
        self.terrainList = terrain.terrain
        self.pTextureR = pygame.image.load('chess_piece_right.png').convert_alpha()
        self.pTextureL = pygame.image.load('chess_piece_left.png').convert_alpha()
        self.hitbox = pygame.Rect(posX, posY, 45, 104)
        self.posX = posX
        self.posY = posY
        self.serverPosX = 0
        self.serverPosY = 0
        self.isLocal = True
        self.weaponName = weapon
        self.living = True
        self.onGround = False
        self.setWeapon(weapon)
    
    def _checkTerrain(self):
        for t in self.terrainList:
            if self.hitbox.colliderect(t):
                return True
            
        return False
    
    def move(self, dx, dy, terrain, direction):
        self.onGround = False
        
        # Process movement and collisions in x-axis
        if dx > 0:
            while dx > 0:
                self.hitbox.x = self.hitbox.x + 1
                dx = dx - 1
                if self._checkTerrain():
                    self.hitbox.x = self.hitbox.x - 1
                    break
        elif dx < 0:
            while dx < 0:
                self.hitbox.x = self.hitbox.x - 1
                dx = dx + 1
                if self._checkTerrain():
                    self.hitbox.x = self.hitbox.x + 1
                    break
                
        # Process movement and collisions in y-axis
        if dy > 0:
            while dy > 0:
                self.hitbox.y = self.hitbox.y + 1
                dy = dy - 1
                if self._checkTerrain():
                    self.hitbox.y = self.hitbox.y - 1
                    self.onGround = True
                    break
        elif dy < 0:
            while dy < 0:
                self.hitbox.y = self.hitbox.y - 1
                dy = dy + 1
                if self._checkTerrain():
                    self.hitbox.y = self.hitbox.y + 1
                    break
                
        self.posX = self.hitbox.x
        self.posY = self.hitbox.y
        if direction:
            self.win.blit(self.pTextureR, (self.posX, self.posY))  # Draw player
        else:
            self.win.blit(self.pTextureL, (self.posX, self.posY))
            
        self.weapon.draw(self.posX, self.posY, direction)
        
        totalMovement = self.posX + self.posY
        totalMovementServer = self.serverPosX + self.serverPosY
        if abs(totalMovement - totalMovementServer) > 4 and RoseRoyale.ClientConnection.theClientConnection != None:
            RoseRoyale.ClientConnection.theClientConnection.sendPlayerPos(self.posX, self.posY, direction, self.weaponName)  # Send new player position to the server
            self.serverPosX = self.posX
            self.serverPosY = self.posY
        
    def getPosX(self):
        return self.posX
    
    def getPosY(self):
        return self.posY
    
    def setWeapon(self, weapon):
        if (weapon == 'shotgun'):
            self.weapon = Shotgun(126, 770, self.win, self.terrain, False, self.name)
        if (weapon == 'pistol'):
            self.weapon = Pistol(126, 770, self.win, self.terrain, self.name)
        if (weapon == 'rpg'):
            self.weapon = RPG(126, 770, self.win, self.terrain, False, self.name)
        if (weapon == 'smg'):
            self.weapon = SMG(126, 770, self.win, self.terrain, False, self.name)
            
        self.weaponName = weapon
            
    def getWeapon(self):
        return self.weapon
    
    def pickup(self, terrain):
        for weapon in terrain.weapons:
            if self.hitbox.colliderect(weapon.hitbox):
                self.weapon = weapon
                self.weapon.owner = self.name
                self.weaponName = weapon.name
                weapon.onGround = False
    
    def lived(self):
        Win.draw(self.win)
