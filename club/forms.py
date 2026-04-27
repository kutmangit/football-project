from django import forms
from .models import League, Team, Player, Match, Ticket


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = '__all__'


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        league = cleaned_data.get('league')
        home = cleaned_data.get('home_team')
        away = cleaned_data.get('away_team')

        if home and league and home.league != league:
            raise forms.ValidationError("Home team не из этой лиги")

        if away and league and away.league != league:
            raise forms.ValidationError("Away team не из этой лиги")

        if home == away:
            raise forms.ValidationError("Команды не могут быть одинаковыми")

    def clean(self):
        cleaned_data = super().clean()
        league = cleaned_data.get('league')
        home = cleaned_data.get('home_team')
        away = cleaned_data.get('away_team')

        if home and league and home.league != league:
            raise forms.ValidationError("Home team не из этой лиги")

        if away and league and away.league != league:
            raise forms.ValidationError("Away team не из этой лиги")

        if home == away:
            raise forms.ValidationError("Команды не могут совпадать")

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        exclude = ['user', 'is_sold']