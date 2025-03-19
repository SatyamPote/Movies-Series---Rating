import csv
from django.shortcuts import render
from django.http import HttpResponse
from .forms import SearchForm
import requests
from django.conf import settings
from .models import Movie, WebSeries
import datetime
import os
import logging
from googleapiclient.discovery import build # this should not require to be installed, but make sure it is.

# Get an instance of a logger
logger = logging.getLogger(__name__)

def home(request):
    """
    Displays the search form and handles the search logic.
    """
    tmdb_api_key = settings.TMDB_API_KEY
    omdb_api_key = settings.OMDB_API_KEY
    youtube_api_key = settings.YOUTUBE_API_KEY

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            logger.info(f"Searching for: {search_term}")
            movie_data = search_movie_data(search_term, tmdb_api_key, omdb_api_key, youtube_api_key)
            series_data = search_series_data(search_term, tmdb_api_key, youtube_api_key)

            if movie_data:
                logger.info(f"Movie found: {movie_data['title']}")
                return render(request, 'tracker/display.html', {'form': form, 'movie': movie_data, 'is_series': False, 'search_term': search_term})
            elif series_data:
                logger.info(f"Series found: {series_data['title']}")
                return render(request, 'tracker/display.html', {'form': form, 'series': series_data, 'is_series': True, 'search_term': search_term})
            else:
                logger.warning(f"Movie/Series not found for: {search_term}")
                return render(request, 'tracker/display.html', {'form': form, 'error': 'Movie/Series not found', 'search_term': search_term})

    else:
        form = SearchForm()
    return render(request, 'tracker/display.html', {'form': form})

def search_movie_data(search_term, tmdb_api_key, omdb_api_key, youtube_api_key):
    """Fetches movie data from TMDb and OMDb."""

    tmdb_search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&language=en-US&query={search_term}&page=1&include_adult=false"

    try:
        tmdb_response = requests.get(tmdb_search_url)
        tmdb_response.raise_for_status()
        tmdb_data = tmdb_response.json()

        if tmdb_data['results']:
            # Take the first result
            movie_data = tmdb_data['results'][0]

            omdb_url = f"http://www.omdbapi.com/?t={movie_data['title']}&apikey={omdb_api_key}"

            try:
                omdb_response = requests.get(omdb_url)
                omdb_response.raise_for_status()
                omdb_data = omdb_response.json()

                if omdb_data.get('Response') == 'True':
                    combined_data = {
                        'title': movie_data['title'],
                        'tmdb_id': movie_data['id'],
                        'omdb_id': omdb_data.get('imdbID'),
                        'genre': omdb_data.get('Genre'),
                        'language': movie_data['original_language'],
                        'rating': float(omdb_data.get('imdbRating', 0.0)) if omdb_data.get('imdbRating', 'N/A') != 'N/A' else None,
                        'release_date': movie_data['overview'],
                        'overview': movie_data['overview'],
                        'is_series': False,
                        'image_url': get_movie_images(movie_data['id'])
                    }

                    youtube_search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={movie_data['title']} trailer&key={youtube_api_key}&maxResults=1"
                    try:
                        youtube_response = requests.get(youtube_search_url)
                        youtube_response.raise_for_status()
                        youtube_data = youtube_response.json()

                        if youtube_data['items']:
                            trailer_id = youtube_data['items'][0]['id']['videoId']
                            combined_data['trailer_id'] = trailer_id

                            # Fetch YouTube video details
                            combined_data['comment_count'], combined_data['like_count'], combined_data['upload_date'] = get_video_statistics(trailer_id, youtube_api_key)

                    except requests.exceptions.RequestException as e:
                        print(f"YouTube API request failed: {e}")
                    except Exception as e:
                        print(f"An unexpected error occurred during YouTube API call: {e}")

                    return combined_data
                else:
                    print(f"OMDb API request failed: {omdb_data.get('Error')}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"OMDb API request failed: {e}")
                return None

        else:
            print(f"TMDb API request failed")
            return None

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

    except Exception as e:
        print(f"An unexpected error occurred during TMDb API call: {e}")
        return None

def search_series_data(search_term):
    """Fetches series data from TMDb and includes season and episode details."""
    tmdb_api_key = settings.TMDB_API_KEY
    youtube_api_key = settings.YOUTUBE_API_KEY

    tmdb_search_url = f"https://api.themoviedb.org/3/search/tv?api_key={tmdb_api_key}&language=en-US&query={search_term}&page=1&include_adult=false"

    try:
        tmdb_response = requests.get(tmdb_search_url)
        tmdb_response.raise_for_status()
        tmdb_data = tmdb_response.json()

        if tmdb_data['results']:
            # Take the first result
            series_data = tmdb_data['results'][0]

            # Fetch tvshow images
            image_url = get_tvshow_images(series_data['id'])

            # Combine data from TMDb
            combined_data = {
                'title': series_data['name'],
                'tmdb_id': series_data['id'],
                'language': series_data['original_language'],
                'overview': series_data['overview'],
                'is_series': True,
                'image_url': image_url
            }

            youtube_search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={series_data['name']} trailer&key={youtube_api_key}&maxResults=1"
            try:
                youtube_response = requests.get(youtube_search_url)
                youtube_response.raise_for_status()
                youtube_data = youtube_response.json()

                if youtube_data['items']:
                    trailer_id = youtube_data['items'][0]['id']['videoId']
                    combined_data['trailer_id'] = trailer_id
                # Fetch YouTube video details
                combined_data['comment_count'], combined_data['like_count'], combined_data['upload_date'] = get_video_statistics(trailer_id, youtube_api_key)

            except requests.exceptions.RequestException as e:
                print(f"YouTube API request failed: {e}")
            except Exception as e:
                print(f"An unexpected error occurred during YouTube API call: {e}")

            return combined_data
        else:
            print(f"TMDb Series API: no results found")
            return None

    except requests.exceptions.RequestException as e:
        print(f"TMDb Series API request failed: {e}")
        return None

    except Exception as e:
        print(f"An unexpected error occurred during TMDb API call: {e}")
        return None

def get_movie_images(movie_id):
    """Get six images of a movie from TMDB."""
    tmdb_api_key = settings.TMDB_API_KEY
    try:
        image_url = [] #image url list
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={tmdb_api_key}" #Movie image api
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['posters']: #Check images exits in the API or NOT
             for image in data['posters'][:6]: #image limit to 6
                image_url.append(f"https://image.tmdb.org/t/p/w500/{image['file_path']}") #path of the image
        return image_url
    except Exception as e:
        print(f"TMDb image API request failed: {e}")
        return None

def get_tvshow_images(tv_id):
    """Get six images of a tvshow from TMDB."""
    tmdb_api_key = settings.TMDB_API_KEY
    try:
        image_url = [] #image url list
        url = f"https://api.themoviedb.org/3/tv/{tv_id}/images?api_key={tmdb_api_key}" #Tvshow image api
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['posters']: #Check images exits in the API or NOT
             for image in data['posters'][:6]: #image limit to 6
                image_url.append(f"https://image.tmdb.org/t/p/w500/{image['file_path']}") #path of the image
        return image_url
    except Exception as e:
        print(f"TMDb image API request failed: {e}")
        return None

def export_movie_csv(request):
    if request.method == 'POST' and request.POST.get('search_term'):
        search_term = request.POST['search_term']
        movie_data = search_movie_data(search_term)
        series_data = search_series_data(search_term)
        is_series = request.POST.get('is_series') == 'True'

        response = HttpResponse(content_type='text/csv')

        if movie_data and not is_series:
            response['Content-Disposition'] = f'attachment; filename="{movie_data["title"]}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Title', 'Genre', 'Language', 'Rating', 'Release Date', 'Overview', 'Likes', 'Comments', 'Upload Date'])
            writer.writerow([
                movie_data['title'],
                movie_data['genre'],
                movie_data['language'],
                movie_data['rating'],
                movie_data['release_date'],
                movie_data['overview'],
                movie_data.get('like_count', ''),
                movie_data.get('comment_count', ''),
                movie_data.get('upload_date', ''),
            ])
            return response

        elif series_data and is_series:
            response['Content-Disposition'] = f'attachment; filename="{series_data["title"]}.csv"'
            writer = csv.writer(response)

            # Write general series information
            writer.writerow(['Title', 'Language', 'Overview', 'Likes', 'Comments', 'Upload Date'])
            writer.writerow([
                series_data['title'],
                series_data['language'],
                series_data['overview'],
                series_data.get('like_count', ''),
                series_data.get('comment_count', ''),
                series_data.get('upload_date', ''),
            ])
            return response
        else:
            return HttpResponse("Movie/Series data not found.")

    else:
        return HttpResponse("Invalid request.")
def get_video_id(video_url):
    """Extracts the Video ID from a YouTube URL"""
    if "watch?v=" in video_url:
        return video_url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[-1].split("?")[0]
    return None

def get_video_statistics(video_id, api_key):
    """Fetches total likes and comments"""
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(
            part="statistics",
            id=video_id
        )
        response = request.execute()

        if "items" in response and response["items"]:
            stats = response["items"][0]["statistics"]
            return int(stats.get("likeCount", 0)), int(stats.get("commentCount", 0)), response["items"][0]['snippet']['publishedAt']
        else:
            print("No video found or no statistics available.")
            return 0, 0, None

    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        return 0, 0, None  # Return 0 or handle the error appropriately

def estimate_likes(video_id, api_key, start_date, end_date):
    """Estimates likes gained in a specific date range"""
    total_likes, _ = get_video_statistics(video_id, api_key)

    # Assuming the video gains likes linearly over time
    upload_date = datetime.date.today() - datetime.timedelta(days=365)  # Example assumption: video is 1 year old
    days_since_upload = (datetime.date.today() - upload_date).days
    total_days_selected = (end_date - start_date).days

    if days_since_upload > 0:
        estimated_likes = int((total_likes / days_since_upload) * total_days_selected)
    else:
        estimated_likes = 0
    return estimated_likes

def query_like_count(request):
    """
    Allows querying the like count for a specific date.
    """

    if request.method == 'GET':
        form = DateForm(request.GET)
        if form.is_valid():
            selected_date = form.cleaned_data['date']
            try:
                # Retrieve the like count for the specified date.
                # You'll need to adjust the logic here based on how you're storing the data

                like_count_entry = VideoLikeCount.objects.filter(timestamp__date=selected_date).first() #First Entry
                if like_count_entry:
                    like_count = like_count_entry.like_count
                else:
                   like_count = "No data found for this date."
            except VideoLikeCount.DoesNotExist:
                like_count = "No data found for this date."
            except Exception as e:
                like_count = f"Error retrieving data: {e}"
        else:
            like_count = None
            selected_date = None
    else:
        form = DateForm()

    context = {
        'form': form,
        'like_count': like_count,
        'selected_date': selected_date,
    }
    return render(request, 'tracker/display.html', context)