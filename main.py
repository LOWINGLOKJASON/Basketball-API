# ****************************************************************
# Name: Wing Lok LO
# Link: https://replit.com/join/pohrxmygyc-lowinglokjason
# ****************************************************************

# Import packages
from fastapi import FastAPI, Request
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from fastapi.templating import Jinja2Templates
import uvicorn
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

### Players ###
# Define an endpoint to fetch data from all players
@app.get("/players")
def get_players():
  players_url = "https://www.balldontlie.io/api/v1/players"
  # Make a GET request
  players_response = requests.get(players_url)
  # Parse the JSON response
  player = players_response.json()
  # Get players information
  players_df = pd.DataFrame(player['data'])
  # Process and transform the data as needed
  return players_df.to_json(orient='records')

### Teams ###
# Insert team's url
teams_url = "https://www.balldontlie.io/api/v1/teams"
# Make a GET request
teams_response = requests.get(teams_url)
# Parse the JSON response
teams_data = teams_response.json()
# Get teams information
teams_df = pd.DataFrame(teams_data['data'])
# Define an endpoint to fetch data from all teams
@app.get("/teams")
def get_teams():
  # Process and transform the data as needed
  return teams_df.to_json(orient='records')

### Division ###
# Create division information of the teams
division_info_df = teams_df.groupby('division').size().reset_index(
  name='Number of teams')
# Define an endpoint to fetch data from all division
@app.get("/teams/{division}")
def division_info(division: str):
  filtered_teams = division_info_df[division_info_df["division"] == division]
  return filtered_teams.to_json(orient='records')

## Games ###
# Insert games' url
games_url = "https://www.balldontlie.io/api/v1/stats"
# Make a GET request
games_response = requests.get(games_url)
# Parse the JSON response
games_data = games_response.json()
# Get teams information
games_df = pd.DataFrame(games_data['data'])
# Define an endpoint to fetch data from all games
@app.get("/games")
def get_games():
  # Process and transform the data as needed
  return games_df.to_json(orient='records')

### Root ###
# Define an endpoint to fetch data from all teams and display a pie chart
@app.get("/", response_class=HTMLResponse)
def get_teams_with_chart(request: Request):
  # Prepare data for the pie chart
  division_counts = division_info_df['Number of teams'].tolist()
  divisions = division_info_df['division'].tolist()
  team_names = teams_df.groupby('division')['full_name'].apply(list).tolist()
  # Generate the pie chart
  plt.figure(figsize=(10, 8))
  colors = ['blue', 'orange', 'green', 'red', 'purple', 'yellow']
  patches, texts, autotexts = plt.pie(division_counts, colors=colors, startangle=90, autopct='%1.1f%%')
  plt.legend(patches, divisions, loc="best")
  plt.title('Proportion of Teams by Division')
  # Add team names as labels within each pie sector
  for i, autotext in enumerate(autotexts):
    team_names_label = '\n'.join(team_names[i])
    autotext.set_text(team_names_label)
  # Save the chart as bytes in memory
  chart_buffer = BytesIO()
  plt.savefig(chart_buffer, format='png')
  chart_buffer.seek(0)
  chart_base64 = base64.b64encode(chart_buffer.read()).decode('utf-8')
  # Render the HTML template with the chart
  return templates.TemplateResponse("index.html", {"request": request, "chart_base64": chart_base64})

if __name__ == "__main__":
  # Run the FastAPI server
  uvicorn.run(app, host="0.0.0.0", port=8000)
