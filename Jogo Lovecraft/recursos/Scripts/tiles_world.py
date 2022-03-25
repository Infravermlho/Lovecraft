from recursos.Scripts.spritesheet import SpriteSheet


class TileSet:

    def __init__(self, tiles_jogo):

        self.tiles_jogo = tiles_jogo
        self.tiles = []
        self.tile_size = 16
        self._load_tiles()

    def _load_tiles(self):
        filename = 'recursos/DeepForestTileset.png'
        parte_ss = SpriteSheet(filename)

        for linha in range(10):
            for coluna in range(8):
                posimag = (coluna * self.tile_size, linha * self.tile_size, self.tile_size, self.tile_size)
                tile_image = parte_ss.image_at(posimag)

                tile_info = Tile(self.tiles_jogo)
                tile_info.image = tile_image
                self.tiles.append(tile_info)

        # Info adicional sobre as tiles
        self.tiles[0].name = 'gramaE'
        self.tiles[29].colide = False
        self.tiles[30].colide = False
        self.tiles[36].colide = False
        self.tiles[52].colide = False
        self.tiles[44].colide = False
        self.tiles[74].colide = False


class Tile:

    def __init__(self, jogo):
        self.image = None
        self.name = ''
        self.colide = True
