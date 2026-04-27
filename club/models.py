from django.db import models
from django.contrib.auth.models import User


class League(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def points(self):
        return self.wins * 3 + self.draws

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Match(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, related_name='home', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away', on_delete=models.CASCADE)

    date = models.DateField()
    time = models.TimeField()
    stadium = models.CharField(max_length=100, default='Main Stadium')  

    score1 = models.IntegerField(default=0)
    score2 = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"



class Sector(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='gray')
    price = models.IntegerField(default=500)  # 👈 ВОТ ЭТО ГЛАВНОЕ

    def __str__(self):
        return self.name
    
class Seat(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    number = models.IntegerField()

    def __str__(self):
        return f"{self.sector} - {self.number}"
    


class Ticket(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    price = models.IntegerField()
    is_sold = models.BooleanField(default=False)

    qr_code = models.ImageField(upload_to='qr/', null=True, blank=True)

    

    def __str__(self):
        return f"{self.match} - {self.seat}"
    


class MatchSector(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)

    price = models.IntegerField()      # цена для этого матча
    capacity = models.IntegerField()  # сколько мест доступно

    def __str__(self):
        return f"{self.match} - {self.sector}"
    



