import pygame
from pygame.locals import *
import math
from recursos.Scripts.tiles_world import TileSet

# Lucas Souza Sllva - 32058179


clock = pygame.time.Clock()


def checkcolision(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

    # Formulazinha pra interpolação linear


def lerp(A, B, C):
    return (C * A) + ((1 - C) * B)


class TapeApp:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 600, 400
        self.display = self.weight, self.height = 300, 200
        self.scrollvalue = [0, 0]

    # noinspection PyAttributeOutsideInit
    def on_init(self):
        pygame.init()

        self._screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf = pygame.Surface((300, 200))
        self._nivel = Nivel()
        self._particula = Particulas()
        pygame.display.set_caption("Foco")

        # Cria o player
        self.player = Player(x=350, y=120)

        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if self.player.focused:
                if event.key == pygame.K_LEFT:
                    self.player.mold(self._nivel, "left", self._particula)
                if event.key == pygame.K_RIGHT:
                    self.player.mold(self._nivel, "right", self._particula)
                if event.key == pygame.K_UP:
                    self.player.mold(self._nivel, "up", self._particula)
                if event.key == pygame.K_DOWN:
                    self.player.mold(self._nivel, "down", self._particula)
            else:
                if event.key == pygame.K_x:
                    self.player.focus("chaos", self._particula)
                    self.player.stop()
                elif event.key == pygame.K_c:
                    self.player.focus("ordem", self._particula)
                    self.player.stop()
                elif event.key == pygame.K_LEFT:
                    self.player.goLeft()
                elif event.key == pygame.K_RIGHT:
                    self.player.goRight()
                elif event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_DOWN:
                    self.player.dive()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_x or event.key == pygame.K_c:
                self.player.unfocus()
            if event.key == pygame.K_LEFT and self.player.changeX < 0:
                self.player.stop()
            elif event.key == pygame.K_RIGHT and self.player.changeX > 0:
                self.player.stop()

    def on_loop(self):
        self.scrollvalue[0] += self.player.rect.x - self.scrollvalue[0] - 152
        self.scrollvalue[1] += self.player.rect.y - self.scrollvalue[1] - 98
        self.player.update(self._nivel.tile_retangulos)

    def on_render(self):
        self._display_surf.fill((105, 155, 125))
        self._nivel.blitnivel(self._display_surf, self.scrollvalue)
        self.player.draw(self._display_surf, self.scrollvalue)
        self._particula.update(self._display_surf, self.scrollvalue)

        # ARRUMAR ISSO GAMBIARRA
        if self._particula.ativovt:
            self._particula.renderizarvortice(self._display_surf, self.scrollvalue, self.player.materia,
                                              (self.player.rect.x + 6, self.player.rect.y + 8))
        # TODO: ARRUMAR ISSO GAMBIARRA

        displaysurf = pygame.transform.scale(self._display_surf, self.size)
        self._screen.blit(displaysurf, (0, 0))
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        self.on_init()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            clock.tick(60)
        self.on_cleanup()


class Nivel:
    # Carrega o arquvio .txt como um nivel
    def __init__(self):
        self.tile_set = TileSet(self)
        self.tile_retangulos = []
        self.tile_coords = []
        self.leveldata = None

        self.loadnivel('recursos/Niveis/Nivel 1.txt')

    def loadnivel(self, nomearquivo):
        infocollector = []
        with open(nomearquivo, 'r') as txt:
            for linha in txt.read().splitlines():
                infocollector.append(linha.split(';'))

        self.leveldata = infocollector

    # Renderiza o nivel e armazena os rects para testes de colisao
    def blitnivel(self, tela, telapan):
        tile_retangulos = []
        tile_coords = []
        tile_size = self.tile_set.tile_size

        y = 0
        for row in self.leveldata:
            x = 0
            for tile in row:
                if tile != '0':
                    tilepos = x * tile_size, y * tile_size, tile_size, tile_size
                    renderpos = x * tile_size - telapan[0], y * tile_size - telapan[1]
                    tileid = int(tile) - 1

                    if self.tile_set.tiles[tileid].colide:
                        tile_retangulos.append(pygame.Rect(tilepos))
                        tile_coords.append((x, y))

                    tela.blit(self.tile_set.tiles[tileid].image, renderpos)
                x += 1
            y += 1

        self.tile_retangulos = tile_retangulos
        self.tile_coords = tile_coords


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Carrega os frames
        self.stillanim = (pygame.image.load('recursos/Player/idle0.png'),
                          pygame.image.load('recursos/Player/idle1.png'),
                          pygame.image.load('recursos/Player/idle2.png'),
                          pygame.image.load('recursos/Player/idle3.png'))

        self.runninganim = (pygame.image.load('recursos/Player/run0.png'),
                            pygame.image.load('recursos/Player/run1.png'),
                            pygame.image.load('recursos/Player/run2.png'),
                            pygame.image.load('recursos/Player/run3.png'))

        # Adiciona transparencia
        for image in self.runninganim:
            image.set_colorkey((0, 255, 0))
        for image in self.stillanim:
            image.set_colorkey((0, 255, 0))

        self.image = self.stillanim[0]

        # Seta posição incial e imagem
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Seta velocidade e orientação
        self.changeX = 0
        self.changeY = 0
        self.direction = "right"

        # Booleanas e valores com relação a o personagem, como por exemplo correndo, qntd de materia e etc
        self.running = False
        self.midair = False
        self.focused = False
        self.focustype = None
        self.materia = 0
        self.runningFrame = 0
        self.runningTime = pygame.time.get_ticks()

    def update(self, tilesexistentes):
        # Update posição jogador
        self.rect.x += self.changeX

        # Busca colisão com o player
        lista_colisao = checkcolision(self.rect, tilesexistentes)

        # Se ocorre colisão remover o jogador do bloco
        for tile in lista_colisao:
            if self.changeX > 0:
                self.rect.right = tile.left
            elif self.changeX < 0:
                self.rect.left = tile.right

        # update posição vertical
        self.rect.y += self.changeY
        self.changeY += 0.2
        if self.changeY > 3:
            self.changeY = 3

        lista_colisao = checkcolision(self.rect, tilesexistentes)

        # Get tiles in collision layer that player is now touching
        for tile in lista_colisao:
            if self.changeY > 0:
                self.rect.bottom = tile.top
                self.midair = False
                self.changeY = 0
            if self.changeY < 0:
                self.rect.top = tile.bottom
                self.changeY = 0

        # Gerencia animação no ar
        if self.midair:
            if self.changeY > 0:
                if self.direction == "right":
                    self.image = self.runninganim[2]
                else:
                    self.image = pygame.transform.flip(self.runninganim[2], True, False)
            else:
                if self.direction == "right":
                    self.image = self.runninganim[1]
                else:
                    self.image = pygame.transform.flip(self.runninganim[1], True, False)

        # Gerencia animação no chão
        elif self.running:
            if self.direction == "right":
                self.image = self.runninganim[self.runningFrame]
            else:
                self.image = pygame.transform.flip(self.runninganim[self.runningFrame], True, False)
        else:
            if self.direction == "right":
                self.image = self.stillanim[self.runningFrame]
            else:
                self.image = pygame.transform.flip(self.stillanim[self.runningFrame], True, False)

        # Rotaciona os frames
        if (pygame.time.get_ticks() - self.runningTime > 70 and self.running) or \
                (pygame.time.get_ticks() - self.runningTime > 100 and not self.running):

            self.runningTime = pygame.time.get_ticks()
            if self.runningFrame == 3:
                self.runningFrame = 0
            else:
                self.runningFrame += 1

        # Salto

    def jump(self):
        if not self.midair:
            self.changeY = -3
            self.midair = True

        # Força queda

    def dive(self):
        if self.midair and self.changeY < 0:
            self.changeY = 0

        # Movimento direita

    def goRight(self):
        self.direction = "right"
        self.running = True
        self.changeX = 2

        # Movimento esquerda

    def goLeft(self):
        self.direction = "left"
        self.running = True
        self.changeX = -2

        # Parar

    def stop(self):
        self.running = False
        self.changeX = 0

        # Remove um bloco do grid

    # tile_retangulos.append(pygame.Rect(tilepos))
    def destroy(self, tiles, direction, particula):
        ponto = None
        if direction == "left":
            ponto = self.rect.x - 5, self.rect.y + 11
        elif direction == "right":
            ponto = self.rect.x + 22, self.rect.y + 11
        elif direction == "up":
            ponto = self.rect.x + 5, self.rect.y - 10
        elif direction == "down":
            ponto = self.rect.x + 5, self.rect.y + 25

        for index, tile in enumerate(tiles.tile_retangulos):
            if tile.collidepoint(ponto):
                coords = tiles.tile_coords[index]
                tiles.leveldata[coords[1]][coords[0]] = "0"

                centrobloco = coords[0] * 16 + 8, coords[1] * 16 + 8
                particula.criarburaconegro(centrobloco, 4, 16, False)
                self.materia += 1

        # Cria um bloco no grid

    def create(self, tiles, direction, particula):
        ponto = None
        if direction == "left":
            ponto = self.rect.x - 16, self.rect.y + 11
        elif direction == "right":
            ponto = self.rect.x + 26, self.rect.y + 11
        elif direction == "up":
            ponto = self.rect.x + 8, self.rect.y - 10
        elif direction == "down":
            ponto = self.rect.x + 8, self.rect.y + 25

        nocolide = True
        for tile in tiles.tile_retangulos:
            if tile.collidepoint(ponto):
                nocolide = False

        if nocolide:
            adjacentes = [(ponto[0] - 16, ponto[1]), (ponto[0] + 16, ponto[1]),
                          (ponto[0], ponto[1] + 16), (ponto[0], ponto[1] - 16)]

            flag = False
            for posição, coords in enumerate(adjacentes):
                for index, tile2 in enumerate(tiles.tile_retangulos):
                    if tile2.collidepoint(coords):
                        coords = tiles.tile_coords[index]
                        truecoords = None

                        if posição == 0:
                            truecoords = coords[1], coords[0] + 1
                        elif posição == 1:
                            truecoords = coords[1], coords[0] - 1
                        elif posição == 2:
                            truecoords = coords[1] - 1, coords[0]
                        elif posição == 3:
                            truecoords = coords[1] + 1, coords[0]

                        tiles.leveldata[truecoords[0]][truecoords[1]] = "72"
                        # TODO: 16 é o tamanho do grid, pegar direto do class Nivel dps pra n deixar hardcoded
                        centrobloco = truecoords[1] * 16 + 8, truecoords[0] * 16 + 8
                        particula.criarburaconegro(centrobloco, 5, 16, True)
                        self.materia -= 1
                        flag = True
                        break
                if flag:
                    break

        # Draw player

    def draw(self, screen, scroll):
        # ponto = self.rect.x - 15 - scroll[0], self.rect.y + 11 - scroll[1]
        # pygame.draw.circle(screen, (0, 0, 0), ponto, 5)

        # adjacentes = [(ponto[0] - 16, ponto[1]), (ponto[0] + 16, ponto[1]),
        #               (ponto[0], ponto[1] + 16), (ponto[0], ponto[1] - 16)]

        # for coord in adjacentes:
        #     pygame.draw.circle(screen, (0, 0, 0), coord, 5)

        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

        # Modo de foco

    def focus(self, type, particula):
        self.focused = True
        self.focustype = type
        if not particula.ativovt:
            particula.criarvortice((self.rect.x + 6, self.rect.y + 9), 5, 10, self.materia)

        # Define se constroi ou destroi

    def mold(self, tiles, orientation, particula):
        if self.focustype == "chaos":
            self.destroy(tiles, orientation, particula)
        elif self.focustype == "ordem" and self.materia > 0:
            self.create(tiles, orientation, particula)

        # cancela o foc

    def unfocus(self):
        self.focused = False


class Particulas:
    # TODO: Refazer as particula pq ta tudo desorganizado um monte de variavel desnecessaria

    def __init__(self):
        # Buraco negro
        self.lugarbn = None
        self.tamanhobn = None
        self.tempobn = None
        self.ativoburaco = False
        self.restantebn = None
        self.runtimebn = pygame.time.get_ticks()

        # Vortice
        self.lugarvt = None
        self.tamanhovt = None
        self.tempovt = None
        self.ativovt = None
        self.restantevt = None
        self.feedbackbn = False
        self.qntdvt = 1
        self.runtimevt = pygame.time.get_ticks()

    def update(self, tela, scroll):
        if self.ativoburaco:
            self.renderizarburaconegro(tela, scroll)
        # if self.ativovt:
        #     self.renderizarvortice(tela, scroll)

    def criarburaconegro(self, lugar, tempo, tamanho, feedback):
        self.tamanhobn = tamanho
        self.tempobn = tempo
        self.lugarbn = lugar
        self.restantebn = tempo
        self.feedbackbn = feedback
        self.ativoburaco = True

    def criarvortice(self, lugar, tempo, tamanho, qntd):
        # Pega informações necessarias pra começar um vortice
        self.tamanhovt = tamanho
        self.tempovt = tempo
        self.lugarvt = lugar
        self.restantevt = tempo
        self.ativovt = True
        self.qntdvt = qntd

    def renderizarburaconegro(self, tela, scroll):
        progresso = self.restantebn / self.tempobn
        if pygame.time.get_ticks() - self.runtimebn > 30:
            self.runtimebn = pygame.time.get_ticks()
            self.restantebn -= 0.8

        coordsrender = self.lugarbn[0] - scroll[0], self.lugarbn[1] - scroll[1]

        if self.feedbackbn:
            raio = lerp(0, self.tamanhobn, progresso)
            pygame.draw.circle(tela, (112, 55, 127), coordsrender, raio)
            raio2 = lerp(self.tamanhobn, 0, progresso)
            pygame.draw.circle(tela, (62, 33, 55), coordsrender, raio2)
        else:
            raio = lerp(0, self.tamanhobn, progresso)
            pygame.draw.circle(tela, (112, 55, 127), coordsrender, raio, 3)
            raio2 = lerp(0, self.tamanhobn * 1.2, progresso)
            pygame.draw.circle(tela, (62, 33, 55), coordsrender, raio2, 1)

        if self.restantebn < 0:
            self.ativoburaco = False

    def renderizarvortice(self, tela, scroll, qntd, pos):
        # TODO: Gambiarrei o codigo todo pra terminar logo, arrumar dps
        self.lugarvt = pos
        self.qntdvt = qntd

        progresso = self.restantevt / self.tempovt
        if pygame.time.get_ticks() - self.runtimevt > 30:
            self.runtimevt = pygame.time.get_ticks()
            self.restantevt -= 0.2

        if self.qntdvt > 0:
            divangulo = 360 / self.qntdvt

        for orbe in range(self.qntdvt):
            angulo = lerp(0.1 + divangulo * orbe, 360 + divangulo * orbe, progresso)
            y = self.tamanhovt * math.sin(math.radians(angulo))
            x = y / math.tan(math.radians(angulo))

            coordsrender = self.lugarvt[0] + x - scroll[0], self.lugarvt[1] + y - scroll[1]

            pygame.draw.circle(tela, (112, 55, 127), coordsrender, 3)
            pygame.draw.circle(tela, (62, 33, 55), coordsrender, 3, 1)

        if self.restantevt < 0:
            self.restantevt = self.tempovt


if __name__ == "__main__":
    theApp = TapeApp()
    theApp.on_execute()
