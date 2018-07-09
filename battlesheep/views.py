import json
import random

from django.shortcuts import HttpResponse, render
from django.urls import reverse
from django.views import View

from battlesheep.forms import ShipForm, ShotForm
from battlesheep.models import BOARD_SIZE, Game, Ship, Shot


def query2json(query, columns, item_url, args):
    data = []
    for g in query:
        temp = {att: getattr(g, att) for att in columns}
        temp['url'] = reverse(item_url, args=(args + [g.id]))
        data.append(temp)
    return json.dumps({'status': True, 'data': data}, indent=2)


def home(request):
    return render(request, 'home.html')


class GameListView(View):
    def get(self, request):
        cols = ('id', 'started', 'ended')
        query = Game.objects.all().order_by('-id')
        data = query2json(query, cols, 'game', [])
        return HttpResponse(data, content_type='application/json')

    def post(self, request):
        g = Game()
        g.save()
        return HttpResponse(
            json.dumps({'status': True, 'url': reverse('game', args=[g.id])}, sort_keys=True),
            content_type='application/json'
        )

    def delete(self, request):
        game_id = request.DELETE['game_id']
        g = Game.objects.get(pk=game_id)
        g.delete()
        return HttpResponse(
            json.dumps({'status': True}, sort_keys=True),
            content_type='application/json'
        )


class GameBoardView(View):
    def get(self, request, game_id):
        game = Game.objects.get(pk=game_id)
        board = '\n'.join(' '.join(p for p in line) for line in json.loads(game.board))
        return render(
            request, 'board.html',
            {'game': game, 'board': board, }
        )


class GameRandomView(View):
    def get(self, request):
        game = Game()
        game.save()

        data = {'game': game.id}
        for k, name in Ship.SHIP_NAMES:
            while True:
                data['kind'] = k
                data['direction'] = random.choice(Ship.DIRECTIONS)[0]
                data['x'] = random.choice(range(BOARD_SIZE))
                data['y'] = random.choice(range(BOARD_SIZE))
                form = ShipForm(data)
                if form.is_valid():
                    form.save()
                    break
        return HttpResponse(
            json.dumps({
                'status': True,
                'url': reverse('game', args=[game.id])},
                sort_keys=True
            ),
            content_type='application/json'
        )


class GameDetailView(View):
    def get(self, request, game_id):
        cols = ('id', 'board', 'started', 'ended')
        gs = Game.objects.get(pk=game_id)
        data = json.dumps({
            'status': True,
            'data': {k: getattr(gs, k) for k in cols},
            'urls': {
                'board_view': reverse('game_board', args=[game_id]),
                'ships': reverse('ships', args=[game_id]),
                'shots': reverse('shots', args=[game_id])
            },
        }, indent=2, sort_keys=True)
        return HttpResponse(data, content_type='application/json')


class ShipListView(View):
    def get(self, request, game_id):
        cols = ('id', 'x', 'y')
        query = Ship.objects.filter(game=game_id).order_by('-id')
        data = query2json(query, cols, 'ship', [game_id])
        return HttpResponse(data, content_type='application/json')

    def post(self, request, game_id):
        data = request.POST.dict()
        data['game'] = game_id
        form = ShipForm(data)
        if form.is_valid():
            ship = form.save()
        else:
            data = json.dumps({'status': False, 'error': list(form.errors_list())})
            return HttpResponse(data, content_type='application/json')

        data = query2json([ship], self.cols, 'ship', [game_id])
        return HttpResponse(data, content_type='application/json')

    def delete(self, request, game_id):
        ship_id = request.DELETE['ship_id']
        ship = Ship.objects.get(pk=ship_id)
        # can only edit ships before the first shot
        err = None
        if not ship.game.ended and ship.game.started:
            err = 'Can\'t remove ships from a started game.'
        else:
            try:
                ShipForm.delete(ship)
            except Exception as e:
                err = str(e)
        if err is not None:
            data = {'status': False, 'error': list(str(err))}
        else:
            data = {'status': True, 'data': 'Object "{}" removed.'.format(ship_id)}
        return HttpResponse(json.dumps(data), content_type='application/json')


class ShipDetailView(View):
    cols = ('kind', 'x', 'y', 'direction')

    def get(self, request, game_id, ship_id):
        ship = Ship.objects.get(pk=ship_id)
        data = query2json([ship], self.cols, 'ship', [game_id])
        return HttpResponse(data, content_type='application/json')


class ShotDetailView(View):
    cols = ('x', 'y')

    def get(self, request, game_id, shot_id):
        shot = Shot.objects.get(pk=shot_id)
        data = query2json([shot], self.cols, 'shot', [game_id])
        return HttpResponse(data, content_type='application/json')


class ShotListView(View):
    cols = ('x', 'y')

    def get(self, request, game_id):
        query = Shot.objects.filter(game=game_id).order_by('-id')
        data = query2json(query, self.cols, 'shot', [game_id])
        return HttpResponse(data, content_type='application/json')

    def post(self, request, game_id):
        data = request.POST.dict()
        data['game'] = game_id
        form = ShotForm(data)
        if form.is_valid():
            shot = form.save()
        else:
            data = {'status': False, 'error': list(form.errors_list())}
            return HttpResponse(json.dumps(data), content_type='application/json')

        # assuming obj is a model instance
        data = query2json([shot], self.cols, 'shot', [game_id])
        return HttpResponse(data, content_type='application/json')

    def delete(self, request, game_id):
        shot_id = request.DELETE['shot_id']
        shot = Shot.objects.get(pk=shot_id)
        # can only remove shots before the first one
        err = None
        if not shot.game.ended and shot.game.started:
            err = 'Can\'t remove shots from a started game.'
        else:
            try:
                ShotForm.delete(shot)
            except Exception as e:
                err = str(e)
        if err is not None:
            data = {'status': False, 'error': list(str(err))}
        else:
            data = {'status': True, 'data': 'Object "{}" removed.'.format(shot_id)}
        return HttpResponse(json.dumps(data), content_type='application/json')
