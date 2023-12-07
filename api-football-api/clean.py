import logging
import os
import sys

log_file = "$HOME/x-football-score-app/logs.txt"
completed_file = "$HOME/x-football-score-app/completed.txt"

# Create log file if it doesnt exist
if not os.path.exists(log_file):
    with open(log_file, 'w'):
        pass

# Set log info
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)s)"
)

# Delete completed file if it exists
if os.path.exists(completed_file):
    try:
        logging.info(
        "*********************** Starting daily cleanup.. ***********************")
        os.remove(completed_file)
        logging.info(
        "*********************** Cleanup completed. ***********************")
    except IOError as e:
        logging.error(f"Error: Unable to delete completed.txt. {e}")