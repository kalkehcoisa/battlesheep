import json

from django.db import models


BOARD_SIZE = 10


class Game(models.Model):
    """
    Stores the base game info and the position of the
    ships in the game board (done in the simplest way: a column
    for each ship).
    """

    board = models.TextField(
        "The battlefield", null=True, blank=True,
        default=json.dumps([[
            '*' for i in range(BOARD_SIZE)]
            for i in range(BOARD_SIZE)
        ]),
        # editable=False
    )
    started = models.BooleanField(null=False, blank=False, default=False)
    ended = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return 'Game {game_id}'.format(
            game_id=self.id
        )


class Ship(models.Model):
    SHIP_NAMES = (
        ('a', 'Aircraft Carrier'),
        ('b', 'Battleship'),
        ('c', 'Cruiser'),
        ('s', 'Submarine'),
        ('d', 'Destroyer')
    )
    SHIP_SIZES = {
        'a': 5,
        'b': 4,
        'c': 3,
        's': 3,
        'd': 2
    }
    DIRECTIONS = (
        ('n', 'North'),
        ('s', 'South'),
        ('e', 'East'),
        ('w', 'West'),
    )

    kind = models.CharField(
        max_length=1, null=False, blank=False, choices=SHIP_NAMES
    )
    x = models.IntegerField(
        null=False, blank=False, choices=zip(range(BOARD_SIZE), range(BOARD_SIZE))
    )
    y = models.IntegerField(
        null=False, blank=False, choices=zip(range(BOARD_SIZE), range(BOARD_SIZE))
    )
    direction = models.CharField(
        null=False, blank=False, max_length=1, choices=DIRECTIONS
    )

    game = models.ForeignKey(
        Game, verbose_name='Game', related_name='ships', on_delete=models.CASCADE
    )

    def __str__(self):
        return 'Ship {shipname} ({x}, {y}) on {game_id}'.format(
            shipname=dict(self.SHIP_NAMES)[self.kind],
            game_id=self.game.id,
            x=self.x,
            y=self.y
        )


class Shot(models.Model):
    x = models.IntegerField(null=False, blank=False)
    y = models.IntegerField(null=False, blank=False)

    game = models.ForeignKey(
        Game, verbose_name='Game', related_name='shots', on_delete=models.CASCADE
    )

    def __str__(self):
        return 'Shot ({x}, {y}) on game {game_id}'.format(
            game_id=self.game.id,
            x=self.x,
            y=self.y
        )

    class Meta:
        unique_together = (('x', 'y', 'game'),)
