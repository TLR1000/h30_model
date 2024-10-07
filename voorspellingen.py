import pandas as pd
import numpy as np
from scipy.stats import poisson
import sys
import os

# Functie om wedstrijduitslagen te lezen
def read_match_results(file_path):
    try:
        df = pd.read_csv(file_path)
        required_columns = {'HomeTeam', 'AwayTeam', 'HomeGoals', 'AwayGoals'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Het bestand moet de kolommen {required_columns} bevatten.")
        return df
    except FileNotFoundError:
        print(f"Bestand {file_path} niet gevonden.")
        sys.exit(1)
    except Exception as e:
        print(f"Fout bij het lezen van {file_path}: {e}")
        sys.exit(1)

# Functie om thuisvoordeel te berekenen
def calculate_home_advantage(df):
    total_home_goals = df['HomeGoals'].sum()
    total_away_goals = df['AwayGoals'].sum()
    home_advantage = total_home_goals / total_away_goals
    return home_advantage

# Functie om data voor Poisson model voor te bereiden
def prepare_poisson_data(df):
    # Totale gemiddelden berekenen
    total_matches = df.shape[0]
    total_goals = df['HomeGoals'].sum() + df['AwayGoals'].sum()
    league_avg_goals = total_goals / (2 * total_matches)

    # Teamstatistieken berekenen
    teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
    team_stats = pd.DataFrame({'Team': teams})

    # Doelpunten voor en tegen
    goals_scored = df.groupby('HomeTeam')['HomeGoals'].sum().add(
        df.groupby('AwayTeam')['AwayGoals'].sum(), fill_value=0)
    goals_conceded = df.groupby('HomeTeam')['AwayGoals'].sum().add(
        df.groupby('AwayTeam')['HomeGoals'].sum(), fill_value=0)
    matches_played = df['HomeTeam'].value_counts().add(
        df['AwayTeam'].value_counts(), fill_value=0)

    team_stats = team_stats.set_index('Team')
    team_stats['GoalsScored'] = goals_scored
    team_stats['GoalsConceded'] = goals_conceded
    team_stats['MatchesPlayed'] = matches_played

    # Gemiddeld aantal gescoorde en tegendoelpunten per team
    team_stats['AvgGoalsScored'] = team_stats['GoalsScored'] / team_stats['MatchesPlayed']
    team_stats['AvgGoalsConceded'] = team_stats['GoalsConceded'] / team_stats['MatchesPlayed']

    # Aanvalskracht en verdedigingssterkte berekenen
    team_stats['AttackStrength'] = team_stats['AvgGoalsScored'] / league_avg_goals
    team_stats['DefenseStrength'] = team_stats['AvgGoalsConceded'] / league_avg_goals

    # Eventuele deling door nul voorkomen
    team_stats.fillna(0, inplace=True)

    return team_stats, league_avg_goals

# Functie om verwachte doelpunten te berekenen
def predict_expected_goals(team_stats, home_team, away_team, league_avg_goals, home_advantage):
    home_attack = team_stats.loc[home_team, 'AttackStrength']
    home_defense = team_stats.loc[home_team, 'DefenseStrength']
    away_attack = team_stats.loc[away_team, 'AttackStrength']
    away_defense = team_stats.loc[away_team, 'DefenseStrength']

    # Verwachte doelpunten
    lambda_home = home_attack * away_defense * league_avg_goals * home_advantage
    lambda_away = away_attack * home_defense * league_avg_goals

    return lambda_home, lambda_away

# Functie om wedstrijdresultaat te voorspellen
def predict_match_outcome(lambda_home, lambda_away, max_goals=11):
    # Mogelijke doelpuntenaantallen
    home_goals = np.arange(0, max_goals+1)
    away_goals = np.arange(0, max_goals+1)

    # Kansenmatrix opstellen
    prob_matrix = np.outer(poisson.pmf(home_goals, lambda_home), poisson.pmf(away_goals, lambda_away))

    # Kansen op winst, gelijkspel, verlies
    home_win_prob = np.tril(prob_matrix, -1).sum()
    draw_prob = np.trace(prob_matrix)
    away_win_prob = np.triu(prob_matrix, 1).sum()

    # Meest waarschijnlijke uitslag
    max_prob_index = np.unravel_index(prob_matrix.argmax(), prob_matrix.shape)
    most_probable_score = (home_goals[max_prob_index[0]], away_goals[max_prob_index[1]])

    return home_win_prob, draw_prob, away_win_prob, most_probable_score

# Hoofdprogramma
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python voorspellingen.py <invoerbestand>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Wedstrijduitslagen lezen
    match_results = read_match_results(input_file)

    # Thuisvoordeel berekenen
    home_advantage = calculate_home_advantage(match_results)

    # Data voorbereiden
    team_stats, league_avg_goals = prepare_poisson_data(match_results)

    # Komende wedstrijden definiëren
    # Hier ga ik ervan uit dat je de fixtures in het script zelf definieert.
    fixtures = pd.DataFrame({
        'HomeTeam': ['Victoria', 'Victoria', 'Victoria', 'Hudito', 'Hudito', 'Forcial', 'HDM', 'HDM', 'Cartouche', 'Voorne', 'Voorne', 'Barendrecht'],
        'AwayTeam': ['Hudito', 'Forcial', 'Roomburg', 'Forcial', 'HDM', 'Cartouche', 'Cartouche', 'Voorne', 'Barendrecht', 'Barendrecht', 'Roomburg', 'Roomburg']
    })

    # Controleren of alle teams in de fixtures bestaan in de teamstatistieken
    all_teams = set(team_stats.index)
    fixture_teams = set(fixtures['HomeTeam']).union(set(fixtures['AwayTeam']))

    missing_teams = fixture_teams - all_teams
    if missing_teams:
        print(f"De volgende teams uit de fixtures zijn niet gevonden in de teamstatistieken: {missing_teams}")
        sys.exit(1)

    # Voorspellingen genereren
    predictions = []

    for index, row in fixtures.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']

        lambda_home, lambda_away = predict_expected_goals(
            team_stats, home_team, away_team, league_avg_goals, home_advantage)

        home_win_prob, draw_prob, away_win_prob, most_probable_score = predict_match_outcome(
            lambda_home, lambda_away, max_goals=12)

        predictions.append({
            'Wedstrijd': f"{home_team} vs {away_team}",
            'Verwachte Doelpunten': f"{lambda_home:.2f} - {lambda_away:.2f}",
            'Meest Waarschijnlijke Uitslag': f"{most_probable_score[0]} - {most_probable_score[1]}",
            'Winstkansen': f"{home_win_prob*100:.1f}% - {draw_prob*100:.1f}% - {away_win_prob*100:.1f}%"
        })

    predictions_df = pd.DataFrame(predictions)

    # Uitvoerbestandnaam bepalen
    base_name = os.path.basename(input_file)
    name_part = base_name.split('_')[-1].split('.')[0]  # Deel na de '_', zonder extensie
    output_file = f"voorspellingen_{name_part}.csv"

    # Voorspellingen opslaan
    predictions_df.to_csv(output_file, index=False)
    print(f"Voorspellingen zijn opgeslagen in '{output_file}'")
