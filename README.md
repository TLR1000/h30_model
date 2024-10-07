# Voorspellingsscript voor Veldhockeywedstrijden

Dit script is een Python-programma dat historische wedstrijduitslagen analyseert om toekomstige veldhockeywedstrijden te voorspellen. Het maakt gebruik van statistische modellen, met name het Poisson-regressiemodel, om zowel de verwachte uitslag als de kans op winst, gelijkspel of verlies te berekenen.

## Functionaliteiten

### 1. Invoer van Wedstrijduitslagen

- **Bestandsinvoer**: Het script leest een invoerbestand (CSV-formaat) met historische wedstrijduitslagen. De bestandsnaam wordt als parameter meegegeven bij het starten van het script.
- **Vereiste Kolommen**: Het invoerbestand moet de volgende kolommen bevatten:
  - `HomeTeam`
  - `AwayTeam`
  - `HomeGoals`
  - `AwayGoals`

### 2. Berekening van Teamstatistieken

- **Gemiddelde Doelpunten**: Voor elk team worden statistieken berekend, zoals het gemiddelde aantal gescoorde en tegendoelpunten per wedstrijd.
- **Aanval en Verdediging**: De aanvalskracht en verdedigingssterkte van elk team worden bepaald ten opzichte van het competitiegemiddelde.
- **Thuisvoordeel**: Het thuisvoordeel wordt berekend door het totale aantal thuisdoelpunten te delen door het totale aantal uitdoelpunten.

### 3. Voorspelling van Wedstrijden

- **Fixtures**: Komende wedstrijden (fixtures) worden gedefinieerd binnen het script.
- **Verwachte Doelpunten**: Voor elke wedstrijd worden de verwachte doelpunten (lambda-waarden) voor het thuis- en uitteam berekend, rekening houdend met de aanvalskracht, verdedigingssterkte en het thuisvoordeel.
- **Maximale Doelpunten**: Het maximale aantal te beschouwen doelpunten is ingesteld op 12 om realistische uitslagen te genereren.

### 4. Berekening van Waarschijnlijkheden

- **Poisson-verdeling**: Met behulp van de Poisson-verdeling worden de kansen op elk mogelijk aantal doelpunten berekend.
- **Winstkansen**: De totale kansen op winst, gelijkspel en verlies worden bepaald.
- **Meest Waarschijnlijke Uitslag**: De meest waarschijnlijke uitslag en de bijbehorende waarschijnlijkheid worden geïdentificeerd.
- **Voorspelling**: De waarschijnlijkheid van de voorspelde winnaar of gelijkspel wordt weergegeven.

### 5. Output en Opslag van Resultaten

- **Bestandsuitvoer**: De voorspellingen worden opgeslagen in een CSV-bestand genaamd `voorspellingen_xxxx.csv`, waarbij `xxxx` het gedeelte van de invoerbestandsnaam is na de underscore (bijv. `h30` van `uitslagen_h30.txt`).
- **Inhoud van de Output**: Per wedstrijd bevat de output:
  - Verwachte doelpunten voor beide teams.
  - Meest waarschijnlijke uitslag en de kans daarop.
  - Voorspelling van de winnaar of een gelijkspel, met de bijbehorende waarschijnlijkheid.
  - Winstkansen voor het thuisteam, gelijkspel en het uitteam.

### 6. Gebruiksgemak

- **Batchbestand**: Een batchbestand (`.bat`) is voorzien om het script eenvoudig te starten met het gewenste invoerbestand.
- **Validatie**: Het script controleert op consistentie en valideert of alle teams in de fixtures aanwezig zijn in de teamstatistieken.
- **Foutafhandeling**: Geïmplementeerd om gebruikers te informeren bij ontbrekende bestanden of data.

## Installatie en Gebruik

### Vereisten

- **Python**: Versie 3.x geïnstalleerd op uw systeem.
- **Python-pakketten**:
  - `pandas`
  - `numpy`
  - `scipy`

### Installatie van Pakketten

Installeer de vereiste pakketten via de command-line:

```bash
pip install pandas numpy scipy
