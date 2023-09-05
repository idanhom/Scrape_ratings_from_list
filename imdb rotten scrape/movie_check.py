from bs4 import BeautifulSoup
from selenium import webdriver
import re
import json
from urllib.parse import quote_plus
from rottentomatoes import Movie
import pandas as pd
from html import unescape
import time


class WebScraper:
    """Class to fetch movie details from IMDb and Rotten Tomatoes."""
    
    imdb_url = "https://www.imdb.com"
    
    def __init__(self):
        """Initialize the webdriver."""
        self.driver = webdriver.Firefox()
    
    def close_browser(self):
        """Close the browser window."""
        self.driver.quit()
    
    def get_details(self, search):
        """Get rating, short description, genres, and IMDb link of a movie from IMDb."""
        imdb_id = self.get_id_from_search(search)
        if not imdb_id:
            return None, None, None, None

        source = self.get_page(self.imdb_url + "/title/" + imdb_id)
        if source:
            details = json.loads(source.find('script', type='application/ld+json').string)
            rating = details.get("aggregateRating", {}).get("ratingValue", None)
            description = details.get("description", None)
            genres = details.get("genre", None)

            # If description is not available, fetch it from the main page content
            if not description:
                description_block = source.find('div', class_='summary_text')
                if description_block:
                    description = description_block.get_text(strip=True)
                    
            # Convert genres to string if it's a list
            if isinstance(genres, list):
                genres = ', '.join(genres)
            imdb_link = self.imdb_url + "/title/" + imdb_id
            # Decode HTML entities in the description
            description = unescape(description) if description else None
            return rating, description, genres, imdb_link
        return None, None, None, None

    def get_id_from_search(self, search):
        """Fetch IMDb ID of a movie using the title."""
        if not search:
            return None
        # Check if the search string is already an IMDb ID
        if re.match(r"^tt\\d{7,}$", search):
            return search
        source = self.get_page(self.imdb_url + "/find?q=" + quote_plus(search))
        if source:
            result = source.find('div', {'class': 'ipc-metadata-list-summary-item__tc'}).a
            return result["href"].split("/")[2]
        return None

    def get_page(self, url):
        """Fetch and return the parsed HTML content of a given URL."""
        self.driver.get(url)
        time.sleep(5)  # Delay to avoid too many rapid requests
        return BeautifulSoup(self.driver.page_source, 'html.parser')


def fetch_movie_ratings(movie_list):
    """Fetch ratings, description, genres, and links from IMDb and Rotten Tomatoes for a list of movies with capitalized titles."""
    imdb = WebScraper()
    results = []
    
    not_found_imdb = []
    not_found_rt = []
    
    fetched_imdb = 0
    fetched_rt = 0
    
    for movie in movie_list:
        # Capitalize each word in the movie title
        formatted_movie_title = movie.title()
        print(f"Processing movie: {formatted_movie_title}")
        
        try:
            imdb_rating, description, genres, imdb_link = imdb.get_details(movie)
            
            if imdb_rating:
                fetched_imdb += 1
                print(f"Found {formatted_movie_title} on IMDb with rating {imdb_rating}.")
            else:
                not_found_imdb.append(formatted_movie_title)
                print(f"Did not find {formatted_movie_title} on IMDb.")
            
            if description:
                print(f"Fetched description for {formatted_movie_title} from IMDb.")
            else:
                print(f"Did not fetch description for {formatted_movie_title} from IMDb.")
                
        except Exception as e:
            print(f"Error processing {formatted_movie_title} on IMDb: {e}")
        
        rt_rating = None
        rt_link = f"https://www.rottentomatoes.com/m/{movie.lower().replace(' ', '_')}"
        try:
            rt_movie = Movie(movie_title=movie)
            rt_rating = rt_movie.tomatometer
            
            if rt_rating is not None:
                fetched_rt += 1
                print(f"Found {formatted_movie_title} on Rotten Tomatoes with rating {rt_rating}.")
            else:
                not_found_rt.append(formatted_movie_title)
                print(f"Did not find {formatted_movie_title} on Rotten Tomatoes.")
            
            # If IMDb description is missing, attempt to get description from Rotten Tomatoes
            if not description:
                description = rt_movie.details.get('synopsis', None)
                if description:
                    print(f"Fetched description for {formatted_movie_title} from Rotten Tomatoes.")
                else:
                    print(f"Did not fetch description for {formatted_movie_title} from Rotten Tomatoes.")
        except Exception as e:
            not_found_rt.append(formatted_movie_title)
            print(f"Error processing {formatted_movie_title} on Rotten Tomatoes: {e}")

        results.append((formatted_movie_title, description, genres, imdb_rating, imdb_link, rt_rating, rt_link))
    
    # Close the browser after fetching all ratings
    imdb.close_browser()

    summary = {
        "total_movies": len(movie_list),
        "fetched_imdb": fetched_imdb,
        "fetched_rt": fetched_rt,
        "not_found_imdb": not_found_imdb,
        "not_found_rt": not_found_rt
    }
    return results, summary

def save_to_csv(data, file_path):
    """Save fetched movie details, ratings, and links to a CSV file with escaped semicolons."""
    
    # Convert data into a DataFrame
    df = pd.DataFrame(data, columns=["Movie Title", "Description", "Genres", "IMDb Rating", "IMDb Link", "Rotten Tomatoes Rating", "Rotten Tomatoes Link"])
    
    # Escape semicolons in the 'Description' column
    df["Description"] = df["Description"].str.replace(';', '[semicolon]')
    
    # Sort by movie title and set the index
    df = df.sort_values(by="Movie Title")
    df.set_index("Movie Title", inplace=True)
    
    # Transpose and save to CSV
    df_transposed = df.transpose()
    df_transposed.to_csv(file_path, sep='\t', header=True)
    


def main():
    """Main execution function."""
    # Read the movie list and remove duplicates
    with open(r'C:\Users\pson9\Documents\Python projects\imdb rotten scrape\movie_list.txt', 'r') as file:
        movies = list(set(line.strip() for line in file))

    # Fetch ratings and get summary
    movie_ratings, summary = fetch_movie_ratings(movies)
    save_to_csv(movie_ratings, r'C:\Users\pson9\Documents\Python projects\imdb rotten scrape\movie_ratings.csv')

    # Print summary
    print("\nRating fetch completed!")
    print(f"Total movies processed: {summary['total_movies']}")
    print(f"Ratings fetched from IMDb: {summary['fetched_imdb']}")
    print(f"Ratings fetched from Rotten Tomatoes: {summary['fetched_rt']}")
    if summary['not_found_imdb']:
        print("Movies not found on IMDb:")
        for movie in summary['not_found_imdb']:
            print(f"- {movie}")
    if summary['not_found_rt']:
        print("Movies not found on Rotten Tomatoes:")
        for movie in summary['not_found_rt']:
            print(f"- {movie}")

if __name__ == "__main__":
    main()
