import logging
import os
import sys
import requests
import tweepy
from datetime import datetime

#################################### Logging ####################################

# Create log file if it doesnt exist
if not os.path.exists("$HOME/x-football-score-app/logs.txt"):
    with open(f"$HOME/x-football-score-app/logs.txt", 'w'):
        pass

# Set log info
logging.basicConfig(
    filename="$HOME/x-football-score-app/logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)s)"
)

logging.info(
    "************************* Script has started.. **********************")

#################################### Variables ####################################

# API-Football endpoint
url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

# File to store fixture IDs
fixture_ids_file = "$HOME/x-football-score-app/completed-fixture-ids.txt"
all_fixture_ids_file = "$HOME/x-football-score-app/all-fixture-ids.txt"
completed_file = "$HOME/x-football-score-app/completed.txt"

# Pass X secrets from environment variables
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
ur_token = os.environ.get("UR_TOKEN")

# Pass API-FOOTBALL secrets from environment variables
x_rapid_api_key = os.environ.get("X_RAPID_API_KEY")

#################################### Functions ####################################
# Check if script should stop running for the day
if os.path.exists(completed_file):
    logging.info("Script complete for the day..Exiting..")
    logging.info(
    "************************* Script complete.. *************************")
    sys.exit(0)

# Get live fixture information by date
def get_fixtures_by_date(api_url, date):
    querystring = {"league": "39", "season": "2023",
                   "timezone": "America/Los_Angeles", "date": date}
    headers = {"X-RapidAPI-Key": x_rapid_api_key,
               "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        if response.status_code == 200:
            fixtures_data = response.json()
            return fixtures_data.get('response', [])
        else:
            logging.error(
                f"Failed to retrieve fixtures. Status code: {response.status_code}.")
            sys.exit(1)
    except requests.RequestException as e:
        logging.error(f"Error making the request: {e}")
        sys.exit(1)

# Store all fixture ids for the day
def store_fixture_ids(fixtures, all_fixture_ids_file):
    if not os.path.isfile(all_fixture_ids_file):
        logging.info(f"File {all_fixture_ids_file} not found. Creating it..")
        try:
            with open(all_fixture_ids_file, 'a') as file:
                for fixture_info in fixtures:
                    fixture = fixture_info['fixture']
                    fixture_id = fixture['id']
                    file.write(str(fixture_id) + '\n')
            logging.info(f"Fixture IDs for today stored in {all_fixture_ids_file}")
        except IOError as e:
            logging.error(f"Error: Unable to write to {all_fixture_ids_file}. {e}")
            sys.exit(1)

# Parse response and send tweet
def print_fixture_status(fixture):
    fixture_id = fixture['fixture']['id']
    fixture_date_str = fixture['fixture']['date']
    fixture_date = datetime.strptime(fixture_date_str, '%Y-%m-%dT%H:%M:%S%z')
    formatted_date = fixture_date.strftime('%Y-%m-%d %H:%M:%S %Z')

    home_team = fixture['teams']['home']['name']
    away_team = fixture['teams']['away']['name']
    status = fixture['fixture']['status']['long']

    logging.info(
        f"{formatted_date}: {home_team} vs {away_team} - Status: {status}")

    # Check if the fixture is complete and tweet score if it has not been sent already
    if status == 'Match Finished' and not is_fixture_id_sent(fixture_id,fixture_ids_file):
        home_goals = fixture['goals']['home']
        away_goals = fixture['goals']['away']

        logging.info(
            f"Sending tweet. . . FULL TIME: {home_team} {home_goals} - {away_goals} {away_team}")
        tweet = f"FULL TIME: {home_team} {home_goals} - {away_goals} {away_team}"
        send_tweet(tweet)
        mark_fixture_id_as_sent(fixture_id)


# Get fixture IDS for completed fixtures
def is_fixture_id_sent(fixture_id,fixture_ids_file):
        if not os.path.exists(fixture_ids_file):
            logging.info(f"File {fixture_ids_file} not found. Creating it..")
            file = open(fixture_ids_file,"w")
        try:
            with open(fixture_ids_file, 'r') as file:
                sent_fixture_ids = set(map(int, file.readlines()))
                return fixture_id in sent_fixture_ids
        except IOError as e:
                logging.error(f"Error: Unable to read {fixture_ids_file}. {e}")
                sys.exit(1)

# Append fixture IDs for completed fixtures
def mark_fixture_id_as_sent(fixture_id):
    with open(fixture_ids_file, 'a') as file:
        file.write(str(fixture_id) + '\n')

# Compare fixture files
def compare_fixture_files(all_fixture_ids_file, fixture_ids_file):
    try:
        with open(all_fixture_ids_file, 'r') as f1, open(fixture_ids_file, 'r') as f2:
            # Read fixture IDs from the files
            all_fixture_ids = set(map(int, f1.readlines()))
            completed_fixture_ids = set(map(int, f2.readlines()))

            # Compare the sets of fixture IDs
            return all_fixture_ids == completed_fixture_ids
    except IOError as e:
        logging.error(f"Error: Unable to read from the files. {e}")
        sys.exit(1)

# Send tweet
def send_tweet(tweet):
    # Authenticate to tweepy
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    try:
        client.create_tweet(text=tweet, user_auth=True)
    except tweepy.errors.TweepyException as e:
        logging.error(str(e))
        sys.exit(1)
    else:
        logging.info("Tweet sent!")

###################################################################################

if __name__ == "__main__":
    # Get the current date
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Get fixtures for the current date
    fixtures = get_fixtures_by_date(url, current_date)
    get_fixtue_ids = store_fixture_ids(fixtures, all_fixture_ids_file)

    if fixtures:
        for fixture in fixtures:
            print_fixture_status(fixture)
    else:
        logging.info(f"No fixtures found for today..Removing {all_fixture_ids_file}.")
        os.remove(all_fixture_ids_file)
        if not os.path.exists(completed_file):
            with open(completed_file, 'w'):
                pass
        logging.info(
            "************************* Script complete.. *************************")
        sys.exit(0)
    
    #Check if all fixtures have been tweeted fir the day
    compare = compare_fixture_files(all_fixture_ids_file, fixture_ids_file)
    logging.info("Checking if all matches have been tweeted for today..")
    if compare == True:
        logging.info("All fixtures tweeted for the day..Removing fixture files..")
        if not os.path.exists(completed_file):
            with open(completed_file, 'w'):
                pass
        logging.info(
           "************************* Script complete.. *************************")
        os.remove(fixture_ids_file)
        os.remove(all_fixture_ids_file)
    else:
        logging.info(
            "************************* Script complete.. *************************")
        sys.exit(69)