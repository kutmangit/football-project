from django.urls import path
from . import views

urlpatterns = [
    # Главная
    path('', views.home, name='home'),

    # Лиги → Команды → Игроки
    path('leagues/', views.leagues, name='leagues'),
    path('teams/<int:league_id>/', views.teams, name='teams'),
    path('players/<int:team_id>/', views.players, name='players'),

    # Матчи и таблицы
    path('matches/', views.matches, name='matches'),
    path('tables/', views.tables, name='tables'),

    # Билеты
    path('tickets/', views.tickets, name='tickets'),
    path('buy/<int:id>/', views.buy_ticket, name='buy_ticket'),

    # CRUD
    path('add/', views.add_player),
    path('edit/<int:id>/', views.edit_player),
    path('delete/<int:id>/', views.delete_player),

    # Панель
    path('dashboard/', views.dashboard, name='dashboard'),

    path('profile/', views.profile, name='profile'),

    path('match/<int:match_id>/seats/', views.select_seat, name='seats'),

    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('add-league/', views.add_league),

    path('user/', views.user_home, name='user_home'),
    path('add-team/', views.add_team),

    path('add-match/', views.add_match, name='add_match'),
    path('add-ticket/', views.add_ticket),

    path('generate-tickets/<int:match_id>/', views.generate_tickets, name='generate_tickets'),
    path('create-stadium/', views.create_stadium, name='create_stadium'),

    path('edit-tickets/<int:match_id>/', views.edit_tickets, name='edit_tickets'),

    path('tickets/<int:match_id>/', views.match_tickets, name='match_tickets'),
    

    path('edit-match/<int:id>/', views.edit_match, name='edit_match'),
    path('delete-match/<int:id>/', views.delete_match, name='delete_match'),
    
    path('checkout/<int:ticket_id>/', views.checkout, name='checkout'),

    path('matches/upcoming/', views.upcoming_matches, name='upcoming_matches'),
    path('matches/past/', views.past_matches, name='past_matches'),

    # ЛИГИ
path('league/edit/<int:id>/', views.edit_league, name='edit_league'),
path('league/delete/<int:id>/', views.delete_league, name='delete_league'),

# КОМАНДЫ
path('team/edit/<int:id>/', views.edit_team, name='edit_team'),
path('team/delete/<int:id>/', views.delete_team, name='delete_team'),

]