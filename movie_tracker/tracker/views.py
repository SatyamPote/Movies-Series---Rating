import csv
from django.shortcuts import render
from django.http import HttpResponse
from .forms import SearchForm
import requests
from django.conf import settings
from .models import Movie, WebSeries
import datetime
import os

def home(request):
    """
    Displays the search form and handles the search logic.
    """
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['search_term']
            movie_data = search_movie_data(search_term)  # Attempt to search Movie
            series_data = search_series_data(search_term)  # Attempt to search Series

            if movie_data:
                return render(request, 'tracker/display.html', {'form': form, 'movie': movie_data, 'is_series': False, 'search_term': search_term})
            elif series_data:
                return render(request, 'tracker/display.html', {'form': form, 'series': series_data, 'is_series': True, 'search_term': search_term})
            else:
                return render(request, 'tracker/display.html', {'form': form, 'error': 'Movie/Series not found', 'search_term': search_term})

    else:
        form = SearchForm()
    return render(request, 'tracker/display.html', {'form': form})

def search_movie_data(search_term):
    """Fetches movie data from TMDb and OMDb."""
    tmdb_api_key = settings.TMDB_API_KEY
    omdb_api_key = settings.OMDB_API_KEY
    youtube_api_key = settings.YOUTUBE_API_KEY

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
                        'release_date': omdb_data.get('Released'),
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
                            youtube_video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={trailer_id}&key={youtube_api_key}"
                            try:
                                youtube_video_response = requests.get(youtube_video_url)
                                youtube_video_response.raise_for_status()
                                youtube_video_data = youtube_video_response.json()

                                if youtube_video_data['items']:
                                    video_details = youtube_video_data['items'][0]
                                    combined_data['comment_count'] = video_details['statistics'].get('commentCount')
                                    combined_data['like_count'] = video_details['statistics'].get('likeCount')
                                    combined_data['upload_date'] = video_details['snippet'].get('publishedAt') #The date
                            except requests.exceptions.RequestException as e:
                                print(f"YouTube video details request failed: {e}")
                            except Exception as e:
                                print(f"An unexpected error occurred during YouTube video details API call: {e}")

                    except requests.exceptions.RequestException as e:
                        print(f"YouTube API request failed: {e}")
                    except Exception as e:
                        print(f"An unexpected error occurred during YouTube API call: {e}")

                    return combined_data
                else:
                    print(f"OMDb API request failed")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"OMDb API request failed: {e}")
                return None
            except Exception as e:
                print(f"OMDb An unexpected error occurred during OMDb API call: {e}")
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
            series_data = tmdb_data['results'][0]

            tv_id = series_data['id']
            seasons = []

            # Iterate through season numbers and call API for each season
            for season_number in range(1, 20):  # Limit to 5 seasons for demonstration
                try:
                    season_url = f"https://api.themoviedb.org/3/tv/{tv_id}/season/{season_number}?api_key={tmdb_api_key}&language=en-US"
                    season_response = requests.get(season_url)
                    season_response.raise_for_status()
                    season_data = season_response.json()

                    episodes = []

                    if season_data.get('episodes'):
                        for episode in season_data['episodes']:
                            episodes.append({
                                'episode_number': episode['episode_number'],
                                'episode_name': episode['name'],
                                'episode_rating': episode.get('vote_average', 'N/A'),  # rating
                            })

                    seasons.append({
                        'season_number': season_data['season_number'],
                        'episodes': episodes
                    })

                except requests.exceptions.RequestException as e:
                    print(f"TMDb Season API request failed for season {season_number}: {e}")
                    break

            combined_data = {
                'title': series_data['name'],
                'tmdb_id': series_data['id'],
                'genre': 'N/A',  # You would fetch genre data from TMDb using the series ID
                'language': series_data['original_language'],
                'rating': None,  # No rating from this
                'first_air_date': None,  # You would fetch this data from TMDb using the series ID
                'overview': series_data['overview'],
                'seasons': seasons,
                'is_series': True,  # Boolean value to say its a series or Movie
                'image_url': get_tvshow_images(tv_id)
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
                    youtube_video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={trailer_id}&key={youtube_api_key}"
                    try:
                        youtube_video_response = requests.get(youtube_video_url)
                        youtube_video_response.raise_for_status()
                        youtube_video_data = youtube_video_response.json()

                        if youtube_video_data['items']:
                            video_details = youtube_video_data['items'][0]
                            combined_data['comment_count'] = video_details['statistics'].get('commentCount')
                            combined_data['like_count'] = video_details['statistics'].get('likeCount')
                            combined_data['upload_date'] = video_details['snippet'].get('publishedAt') #The date
                    except requests.exceptions.RequestException as e:
                        print(f"YouTube video details request failed: {e}")
                    except Exception as e:
                        print(f"An unexpected error occurred during YouTube video details API call: {e}")

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
            writer.writerow(['Title', 'Language', 'Overview', 'Likes', 'Comments', 'Upload Date', 'Season Number', 'Episode Number', 'Episode Name', 'Episode Rating'])
            for season in series_data['seasons']:
                for episode in season['episodes']:
                     writer.writerow([
                         series_data['title'],
                         series_data['language'],
                         series_data['overview'],
                         series_data.get('like_count', ''),
                         series_data.get('comment_count', ''),
                         series_data.get('upload_date', ''),
                         season['season_number'],
                         episode['episode_number'],
                         episode['episode_name'],
                         episode['episode_rating'],
                ])
            return response

        else:
            return HttpResponse("Movie/Series data not found.")

    else:
        return HttpResponse("Invalid request.")