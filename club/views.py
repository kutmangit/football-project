from django.shortcuts import render
from .models import Player
from .forms import PlayerForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Player, Team
from .forms import *

def home(request):
    return render(request, 'club/home.html')

@staff_member_required
def add_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = PlayerForm()
    return render(request, 'club/form.html', {'form': form})

@staff_member_required
def edit_player(request, id):
    player = Player.objects.get(id=id)
    form = PlayerForm(request.POST or None, request.FILES or None, instance=player)

    if form.is_valid():
        form.save()
        return redirect('/')

    return render(request, 'club/form.html', {'form': form})

@staff_member_required
def delete_player(request, id):
    player = Player.objects.get(id=id)
    player.delete()
    return redirect('/')

from django.db.models import F, ExpressionWrapper, IntegerField

def table(request):
    teams = Team.objects.annotate(
        points_calc=ExpressionWrapper(
            F('wins') * 3 + F('draws'),
            output_field=IntegerField()
        )
    ).order_by('-points_calc')

    return render(request, 'club/table.html', {'teams': teams})

@staff_member_required
def dashboard(request):
    return render(request, 'club/dashboard.html')

from .models import Match

from .models import Ticket

def matches(request):
    matches = Match.objects.all()

    data = []
    for m in matches:
        has_tickets = Ticket.objects.filter(match=m).exists()

        data.append({
            'match': m,
            'has_tickets': has_tickets
        })

    return render(request, 'club/matches.html', {'data': data})

from .models import Ticket

def tickets(request):
    tickets = Ticket.objects.all()
    return render(request, 'club/tickets.html', {'tickets': tickets})

from .models import League, Team, Player

def leagues(request):
    leagues = League.objects.all()
    return render(request, 'club/leagues.html', {'leagues': leagues})


def teams(request, league_id):
    league = League.objects.get(id=league_id)
    teams = Team.objects.filter(league=league)
    return render(request, 'club/teams.html', {'teams': teams, 'league': league})


def players(request, team_id):
    team = Team.objects.get(id=team_id)
    players = Player.objects.filter(team=team)
    return render(request, 'club/players.html', {'players': players, 'team': team})

from django.utils.timezone import now

from django.utils.timezone import now
from .models import League, Match

from .models import League, Match, Ticket
import datetime
from .models import League, Match, Ticket

def matches(request):
    leagues = []

    for league in League.objects.all():
        upcoming = []
        past = []

        for match in Match.objects.filter(league=league):

            tickets = Ticket.objects.filter(match=match)
            total = tickets.count()
            sold = tickets.filter(is_sold=True).count()

            data = {
                'obj': match,
                'has_tickets': total > 0,
                'total_tickets': total,
                'sold_tickets': sold
            }

            if match.date >= datetime.date.today():
                upcoming.append(data)
            else:
                past.append(data)

        leagues.append({
            'league': league,
            'upcoming': upcoming,
            'past': past
        })

    return render(request, 'club/matches.html', {'leagues': leagues})


def tables(request):
    leagues = League.objects.all()
    return render(request, 'club/tables.html', {'leagues': leagues})

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'club/dashboard.html')

from django.shortcuts import get_object_or_404



@staff_member_required
def dashboard(request):
    matches = Match.objects.all()
    return render(request, 'club/dashboard.html', {'matches': matches})

@login_required
def buy_ticket(request, id):
    ticket = get_object_or_404(Ticket, id=id)

    if not ticket.is_sold:
        ticket.is_sold = True
        ticket.save()

    return redirect('/tickets/')




@login_required
def profile(request):
    upcoming = []
    past = []

    for ticket in Ticket.objects.filter(user=request.user):
        if ticket.match.date >= datetime.date.today():
            upcoming.append(ticket)
        else:
            past.append(ticket)

    return render(request, 'club/profile.html', {
        'upcoming': upcoming,
        'past': past
    })


@login_required
def select_seat(request, match_id):
    match = Match.objects.get(id=match_id)
    tickets = Ticket.objects.filter(match=match)

    return render(request, 'club/seats.html', {
        'match': match,
        'tickets': tickets
    })

@login_required
def buy_seat(request, match_id, seat):
    match = Match.objects.get(id=match_id)

    ticket, created = Ticket.objects.get_or_create(
        match=match,
        seat=seat,
        defaults={
            'user': request.user,
            'is_sold': True,
            'price': 1000,
            'sector': 'A'
        }
    )

    if not created:
        return redirect('/matches/')  # уже занято

    return redirect('/profile/')


@staff_member_required
def admin_panel(request):
    leagues = League.objects.all()
    teams = Team.objects.all()
    matches = Match.objects.all()

    return render(request, 'club/admin_panel.html', {
        'leagues': leagues,
        'teams': teams,
        'matches': matches
    })



@staff_member_required
def add_league(request):
    form = LeagueForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/leagues/')
    return render(request, 'club/form.html', {'form': form})


from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('/login/')

    return render(request, 'club/register.html', {'form': form})


from django.contrib.auth.decorators import login_required


import qrcode
from django.core.files import File
import os
from django.conf import settings

@login_required
def buy_ticket(request, id):
    ticket = Ticket.objects.get(id=id)

    if ticket.is_sold:
        return redirect(f'/tickets/{ticket.match.id}/')

    if request.user.is_staff:
        return redirect('/')

    # 💳 ФЕЙКОВАЯ ОПЛАТА (пока просто подтверждение)
    ticket.user = request.user
    ticket.is_sold = True
    ticket.save()

    # 🎟 СОЗДАНИЕ QR
    data = f"""
    Match: {ticket.match}
    Seat: {ticket.seat}
    User: {request.user.username}
    """

    qr = qrcode.make(data)

    path = os.path.join(settings.MEDIA_ROOT, f"qr_{ticket.id}.png")
    qr.save(path)

    # сохраняем в модель
    with open(path, 'rb') as f:
        ticket.qr_code.save(f"qr_{ticket.id}.png", File(f))

    ticket.save()

    return redirect('/profile/')

@login_required
def user_home(request):
    return render(request, 'club/user_home.html')

def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/dashboard/')
        else:
            return redirect('/user/')
    
    return render(request, 'club/home.html')


@staff_member_required
def add_team(request):
    form = TeamForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/dashboard/')
    return render(request, 'club/form.html', {'form': form})


@staff_member_required
def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)

        if form.is_valid():
            match = form.save()

            # количество мест
            vip_count = int(request.POST.get('vip_count', 0))
            a_count = int(request.POST.get('a_count', 0))
            b_count = int(request.POST.get('b_count', 0))

            # цены
            vip_price = int(request.POST.get('vip_price', 1500))
            a_price = int(request.POST.get('a_price', 800))
            b_price = int(request.POST.get('b_price', 500))

            vip_seats = Seat.objects.filter(sector__name='VIP')[:vip_count]
            a_seats = Seat.objects.filter(sector__name='A')[:a_count]
            b_seats = Seat.objects.filter(sector__name='B')[:b_count]

            for seat in vip_seats:
                Ticket.objects.create(match=match, seat=seat, price=vip_price)

            for seat in a_seats:
                Ticket.objects.create(match=match, seat=seat, price=a_price)

            for seat in b_seats:
                Ticket.objects.create(match=match, seat=seat, price=b_price)

            return redirect('/matches/')
    else:
        form = MatchForm()

    return render(request, 'club/add_match.html', {'form': form})


@staff_member_required
def add_ticket(request):
    form = TicketForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('/dashboard/')
    return render(request, 'club/form.html', {'form': form})
    


from .models import Ticket, Seat, Match

@staff_member_required
def generate_tickets(request, match_id):
    match = Match.objects.get(id=match_id)

    # чтобы не дублировались билеты
    if Ticket.objects.filter(match=match).exists():
        return redirect('/dashboard/')

    seats = Seat.objects.all()

    for seat in seats:
        Ticket.objects.create(
            match=match,
            seat=seat,
            price=seat.sector.price
        )

    return redirect('/dashboard/')


from .models import Sector, Seat
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.admin.views.decorators import staff_member_required
from .models import Match, Seat, Ticket, Sector

@staff_member_required
def create_stadium(request):
    if Sector.objects.exists():
        return redirect('/dashboard/')

    vip = Sector.objects.create(name='VIP', color='gold')
    a = Sector.objects.create(name='A', color='blue')
    b = Sector.objects.create(name='B', color='green')

    for i in range(1, 21):
        Seat.objects.create(sector=vip, number=i)

    for i in range(1, 51):
        Seat.objects.create(sector=a, number=i)
        Seat.objects.create(sector=b, number=i)

    return redirect('/dashboard/')


from django.shortcuts import render, redirect, get_object_or_404

@staff_member_required
def edit_tickets(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # если уже есть купленные билеты — нельзя менять
    if Ticket.objects.filter(match=match, is_sold=True).exists():
        return redirect('/matches/')
    


    if request.method == 'POST':
        count = request.POST.get('count')

        if not count:
            return render(request, 'club/edit_tickets.html', {
                'match': match,
                'error': 'Введите количество мест'
            })

        count = int(count)

        # удаляем старые билеты
        Ticket.objects.filter(match=match).delete()


        seats = Seat.objects.all()[:count]

        # защита: если мест меньше чем count
        if not seats:
            return render(request, 'club/edit_tickets.html', {
                'match': match,
                'error': 'Нет мест в базе (создай стадион)'
            })

        for seat in seats:
            Ticket.objects.create(
                match=match,
                seat=seat,
                price=500
            )

        return redirect('/matches/')

    return render(request, 'club/edit_tickets.html', {'match': match})
    
    

    
    
    

from django.shortcuts import render, get_object_or_404
from .models import Match, Ticket
from .models import Match, Ticket

def match_tickets(request, match_id):
    match = Match.objects.get(id=match_id)

    tickets = Ticket.objects.filter(match=match)\
        .select_related('seat__sector')\
        .order_by('seat__sector__id')

    return render(request, 'club/match_tickets.html', {
        'match': match,
        'tickets': tickets
    })


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def edit_match(request, id):
    match = Match.objects.get(id=id)

    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)

        if form.is_valid():
            form.save()

            # ❗ если билеты уже проданы — нельзя менять
            if not Ticket.objects.filter(match=match, is_sold=True).exists():

                vip_count = int(request.POST.get('vip_count', 0))
                a_count = int(request.POST.get('a_count', 0))
                b_count = int(request.POST.get('b_count', 0))

                vip_price = int(request.POST.get('vip_price', 1500))
                a_price = int(request.POST.get('a_price', 800))
                b_price = int(request.POST.get('b_price', 500))

                # удаляем старые билеты
                Ticket.objects.filter(match=match).delete()

                vip_seats = Seat.objects.filter(sector__name='VIP')[:vip_count]
                a_seats = Seat.objects.filter(sector__name='A')[:a_count]
                b_seats = Seat.objects.filter(sector__name='B')[:b_count]

                for seat in vip_seats:
                    Ticket.objects.create(match=match, seat=seat, price=vip_price)

                for seat in a_seats:
                    Ticket.objects.create(match=match, seat=seat, price=a_price)

                for seat in b_seats:
                    Ticket.objects.create(match=match, seat=seat, price=b_price)

            return redirect('/matches/')
    else:
        form = MatchForm(instance=match)

    return render(request, 'club/edit_match.html', {'form': form})


@staff_member_required
def delete_match(request, id):
    match = Match.objects.get(id=id)
    match.delete()
    return redirect('/matches/')



import json
from django.shortcuts import render
from .models import Match, Ticket

def match_detail(request, match_id):
    match = Match.objects.get(id=match_id)
    tickets = Ticket.objects.filter(match=match).select_related('seat__sector')
    
    # Группировка билетов по секторам
    sectors_data = {}
    for ticket in tickets:
        sector = ticket.seat.sector
        sector_id = sector.id
        
        if sector_id not in sectors_data:
            sectors_data[sector_id] = {
                'id': sector_id,
                'name': sector.name,
                'price': sector.price,  # Цена берется из модели Sector
                'tickets': []
            }
        
        sectors_data[sector_id]['tickets'].append({
            'id': ticket.id,
            'number': ticket.seat.number,
            'is_sold': ticket.is_sold,
            'sector_id': sector_id
        })
    
    context = {
        'match': match,
        'tickets_json': json.dumps(sectors_data, ensure_ascii=False),
        'stadium_name': 'National Stadium'
    }
    
    return render(request, 'club/match_detail.html', context)




import qrcode
import os
from django.conf import settings

if not os.path.exists(settings.MEDIA_ROOT):
    os.makedirs(settings.MEDIA_ROOT)

@login_required
def checkout(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)

    if ticket.is_sold:
        return redirect(f'/tickets/{ticket.match.id}/')

    if request.method == 'POST':
        ticket.is_sold = True
        ticket.user = request.user
        ticket.save()

        # 🔥 создаем папку если нет
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        # 🔥 QR
        qr_data = f"Ticket #{ticket.id} | {ticket.match} | Seat {ticket.seat}"
        img = qrcode.make(qr_data)

        path = os.path.join(settings.MEDIA_ROOT, f"qr_{ticket.id}.png")
        img.save(path)

        return redirect('/profile/')

    return render(request, 'club/checkout.html', {'ticket': ticket})


import datetime

def upcoming_matches(request):
    leagues = []

    for league in League.objects.all():
        matches = Match.objects.filter(
            league=league,
            date__gte=datetime.date.today()
        )

        leagues.append({
            'league': league,
            'matches': matches
        })

    return render(request, 'club/upcoming_matches.html', {'leagues': leagues})


def past_matches(request):
    leagues = []

    for league in League.objects.all():
        matches = Match.objects.filter(
            league=league,
            date__lt=datetime.date.today()
        )

        leagues.append({
            'league': league,
            'matches': matches
        })

    return render(request, 'club/past_matches.html', {'leagues': leagues})


@staff_member_required
def edit_league(request, id):
    league = get_object_or_404(League, id=id)

    form = LeagueForm(request.POST or None, instance=league)

    if form.is_valid():
        form.save()
        return redirect('/leagues/')

    return render(request, 'club/form.html', {'form': form})


@staff_member_required
def delete_league(request, id):
    league = get_object_or_404(League, id=id)
    league.delete()
    return redirect('/leagues/')


@staff_member_required
def edit_team(request, id):
    team = get_object_or_404(Team, id=id)

    form = TeamForm(request.POST or None, instance=team)

    if form.is_valid():
        form.save()
        return redirect(f'/teams/{team.league.id}/')

    return render(request, 'club/form.html', {'form': form})


@staff_member_required
def delete_team(request, id):
    team = get_object_or_404(Team, id=id)
    league_id = team.league.id
    team.delete()
    return redirect(f'/teams/{league_id}/')