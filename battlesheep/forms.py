from collections import namedtuple
import json
import operator

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from battlesheep.models import Game, Ship, Shot


Position = namedtuple('Position', 'x, y')


def ship_positions(ship):
    if isinstance(ship, Ship):
        data = {
            'direction': ship.direction,
            'x': ship.x,
            'y': ship.y,
            'kind': ship.kind
        }
    else:
        data = ship

    if data['direction'] == 'n':
        ops = (operator.sub, lambda a, b: a)
    elif data['direction'] == 's':
        ops = (operator.add, lambda a, b: a)
    elif data['direction'] == 'e':
        ops = (lambda a, b: a, operator.add)
    elif data['direction'] == 'w':
        ops = (lambda a, b: a, operator.sub)

    return (
        Position(ops[0](data['x'], i), ops[1](data['y'], i))
        for i in range(Ship.SHIP_SIZES[data['kind']])
    )


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = '__all__'

    def errors_list(self):
        for errors in self.errors.values():
            for err in errors:
                yield err


class ShipForm(ModelForm):
    class Meta:
        model = Ship
        fields = '__all__'

    def errors_list(self):
        for errors in self.errors.values():
            for err in errors:
                yield err

    def clean(self):
        data = super().clean()

        if data['game'].ended:
            # game ended, nothing more to do
            raise ValidationError(
                'Can\'t do anything in an ended game.'
            )
        elif data['game'].started:
            # can only edit ships before the first shot
            raise ValidationError(
                'Can\'t edit/add ships in a started game.'
            )

        area = json.loads(data['game'].board)
        for p in ship_positions(data):
            try:
                if area[p.x][p.y] != '*':
                    raise ValidationError(
                        'Position [%(x)s, %(y)s] already contains a ship.',
                        params={'x': p.x, 'y': p.y}
                    )
            except IndexError:
                raise ValidationError(
                    'Can\'t place ship outside the game board [%(x)s, %(y)s].',
                    params={'x': p.x, 'y': p.y}
                )
            area[p.x][p.y] = data['kind']
        data['game'].board = json.dumps(area)
        data['game'].save()

    @classmethod
    def delete(cls, ship):
        area = json.loads(ship.game.board)
        data = ship.game
        for p in ship_positions(data):
            area[p.x][p.y] = '*'
        ship.game.board = json.dumps(area)
        ship.game.save()
        ship.delete()


class ShotForm(ModelForm):
    class Meta:
        model = Shot
        fields = ('game', 'x', 'y')

    def errors_list(self):
        for errors in self.errors.values():
            for err in errors:
                yield err

    def clean(self):
        data = super().clean()

        if data['game'].ended:
            # game ended, nothing more to do
            raise ValidationError(
                'Can\'t do anything in an ended game.'
            )

        # after the first shot, the game is started: no more editions
        if not data['game'].started:
            data['game'].started = True
            data['game'].save()

        board = json.loads(data['game'].board)
        if board[data['x']][data['y']] == '*':
            board[data['x']][data['y']] = ' '
        else:
            board[data['x']][data['y']] = 'X'
            # check if all ships were sunk: end game
            if all(
                v not in Ship.SHIP_SIZES.keys()
                for line in board
                for v in line
            ):
                data['game'].ended = True
        data['game'].board = json.dumps(board)
        data['game'].save()

    @classmethod
    def delete(cls, shot):
        area = json.loads(shot.game.board)
        area[shot.x][shot.y] = '*'
        shot.game.board = json.dumps(area)
        shot.game.save()
        shot.delete()
