Movie Scraper
This script is designed to fetch movie details, including ratings, descriptions, and genres, from IMDb and Rotten Tomatoes. It accepts a list of movie titles and generates a CSV file containing the collected data.

Features:
Fetches movie details from IMDb.
Fetches ratings from Rotten Tomatoes.
Returns a CSV file with the movie details.
Provides a summary of fetched data.
Prerequisites:
Ensure that the following packages are installed. You can install them using pip:

Copy code
pip install beautifulsoup4 selenium pandas rottentomatoes
Additionally, you need to have the geckodriver for Firefox. Make sure it's in the system's PATH or specify its location in the script.

How to use:
Prepare the Movie List: The script reads the list of movies from a file named movie_list.txt. Each line of this file should contain one movie title.

Run the Script: Simply execute the script using Python:

Copy code
python movie_scraper.py
Check the Results: After the script has run, it will generate a file named movie_ratings.csv containing the fetched movie details. The script will also print a summary of the fetched data, listing movies not found on either IMDb or Rotten Tomatoes.
Notes:
The script uses Selenium with the Firefox driver, so it will open a Firefox window while it's running.
To avoid being rate-limited or blocked, the script introduces a delay between requests. This means it might take a while to process a large list of movies.
Rotten Tomatoes links are generated based on the movie title's format; however, this might not always lead to the correct link. The script attempts to fetch the rating and details using the provided rottentomatoes package.
Possible Improvements:
Introduce command-line arguments to specify input and output files.
Add error handling for the possible absence of geckodriver.
Allow the user to choose between different web drivers (e.g., Chrome, Edge).
Add caching to avoid fetching data for the same movie multiple times.
