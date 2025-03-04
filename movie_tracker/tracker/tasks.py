from celery import shared_task
from django.conf import settings
import requests
from .models import Movie, WebSeries
from django.utils import timezone
import datetime

@shared_task
def fetch_movie_data():
    """
    Fetches movie data from TMDb and OMDb (example).  Handle errors gracefully.
    """
    tmdb_api_key = settings.TMDB_API_KEY
    omdb_api_key = settings.OMDB_API_KEY
    youtube_api_key = settings.YOUTUBE_API_KEY  # Get YouTube API key from settings

    # Example TMDb call (replace with your actual logic)
    tmdb_url = f"https://api.themoviedb.org/3/movie/popular?api_key={tmdb_api_key}&language=en-US&page=1"
    try:
        tmdb_response = requests.get(tmdb_url)
        tmdb_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        tmdb_data = tmdb_response.json()

        for movie_data in tmdb_data['results']:
            try:
                # Check if the movie already exists based on tmdb_id
                if Movie.objects.filter(tmdb_id=movie_data['id']).exists():
                    print(f"Movie with tmdb_id {movie_data['id']} already exists. Skipping.")
                    continue  # Skip to the next movie if it already exists

                movie = Movie(
                    title=movie_data['title'],
                    tmdb_id=movie_data['id'],
                    language=movie_data['original_language'],
                    overview=movie_data['overview'],
                )

                # Fetch additional details from OMDb using the title
                omdb_url = f"http://www.omdbapi.com/?t={movie_data['title']}&apikey={omdb_api_key}"
                omdb_response = requests.get(omdb_url)
                omdb_response.raise_for_status()
                omdb_data = omdb_response.json()

                if omdb_data.get('Response') == 'True':
                    movie.omdb_id = omdb_data.get('imdbID')
                    movie.rating = float(omdb_data.get('imdbRating', 0.0)) if omdb_data.get('imdbRating', 'N/A') != 'N/A' else None
                    movie.genre = omdb_data.get('Genre')

                    release_date_str = omdb_data.get('Released', None)
                    if release_date_str and release_date_str != "N/A":
                        try:
                            # Attempt to parse the release date
                            movie.release_date = datetime.datetime.strptime(release_date_str, '%d %b %Y').date()
                        except ValueError:
                            # Handle different date formats or parsing errors
                            print(f"Error parsing release date: {release_date_str}")
                            movie.release_date = None  # Or set to a default date

                    else:
                        movie.release_date = None # set none if N/A or empty

                # Basic YouTube Trailer Search (Example)
                youtube_search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={movie_data['title']} trailer&key={youtube_api_key}&maxResults=1"  # Limited to 1 result
                try:
                    youtube_response = requests.get(youtube_search_url)
                    youtube_response.raise_for_status()
                    youtube_data = youtube_response.json()

                    if youtube_data['items']:
                        trailer_id = youtube_data['items'][0]['id']['videoId']
                        movie.trailer_id = trailer_id #store trailer to DB
                        print(f"Found trailer for {movie_data['title']}: https://www.youtube.com/watch?v={trailer_id}")


                except requests.exceptions.RequestException as e:
                    print(f"YouTube API request failed: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred during YouTube API call: {e}")


                movie.save()
                print(f"Movie '{movie.title}' added/updated successfully.")

            except Exception as e:
                print(f"Error processing movie '{movie_data['title']}': {e}")

    except requests.exceptions.RequestException as e:
        print(f"TMDb API request failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


@shared_task
def fetch_series_data():
    """Fetches web series data from TMDb (example). Handle errors gracefully."""
    tmdb_api_key = settings.TMDB_API_KEY

    # Example TMDb call (replace with your actual logic)
    tmdb_url = f"https://api.themoviedb.org/3/tv/popular?api_key={tmdb_api_key}&language=en-US&page=1"
    try:
        tmdb_response = requests.get(tmdb_url)
        tmdb_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        tmdb_data = tmdb_response.json()

        for series_data in tmdb_data['results']:
            try:
                # Check if the series already exists based on tmdb_id
                if WebSeries.objects.filter(tmdb_id=series_data['id']).exists():
                    print(f"Series with tmdb_id {series_data['id']} already exists. Skipping.")
                    continue  # Skip to the next series if it already exists

                series = WebSeries(
                    title=series_data['name'],
                    tmdb_id=series_data['id'],
                    language=series_data['original_language'],
                    overview=series_data['overview'],
                )

                # You might want to fetch more details, e.g., from OMDb or a dedicated series API
                # and populate other fields like genre, rating, first_air_date, etc.

                series.save()
                print(f"Series '{series.title}' added/updated successfully.")

            except Exception as e:
                print(f"Error processing series '{series_data['name']}': {e}")

    except requests.exceptions.RequestException as e:
        print(f"TMDb API request failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")