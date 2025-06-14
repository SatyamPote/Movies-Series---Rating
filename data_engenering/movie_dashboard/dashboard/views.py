# dashboard/views.py

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import requests
from googleapiclient.discovery import build
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import csv
import json
from datetime import datetime

# --- NEW: Function to generate the detailed text analysis ---
def generate_detailed_analysis(sorted_data, verdict):
    """Generates a human-readable text analysis of the results."""
    if not verdict or 'best_bet' not in verdict:
        return {}

    analysis = {}
    best_movie = verdict['best_bet']
    flop_movie = verdict.get('potential_flop') # Use .get() in case there's only one movie

    # --- Analysis for the Best Bet ---
    best_score = f"{best_movie.get('total_score', 0):.1f}"
    best_views = f"{best_movie['youtube_stats'].get('views', 0):,}" # Format with commas
    best_likes = f"{best_movie['youtube_stats'].get('likes', 0):,}"
    best_rating = (best_movie.get('tmdb_rating', 0) + best_movie.get('omdb_rating', 0)) / 2 if best_movie.get('tmdb_rating') and best_movie.get('omdb_rating') else best_movie.get('tmdb_rating') or best_movie.get('omdb_rating')
    
    best_text = (
        f"<strong>{best_movie['title']}</strong> emerges as the clear frontrunner with an impressive <strong>Hype Score of {best_score}/100</strong>. "
        f"Its success is built on a solid foundation of both critical acclaim (averaging a {best_rating:.1f}/10 rating) and exceptional online buzz. "
        f"The official trailer has captured significant audience attention, amassing <strong>{best_views} views</strong> and <strong>{best_likes} likes</strong>. "
        f"This strong combination of positive reviews and high public engagement suggests a high probability of commercial and critical success."
    )
    analysis['best_bet_analysis'] = best_text

    # --- Analysis for the Potential Flop ---
    if flop_movie and flop_movie['title'] != best_movie['title']:
        flop_score = f"{flop_movie.get('total_score', 0):.1f}"
        flop_views = f"{flop_movie['youtube_stats'].get('views', 0):,}"
        flop_rating = (flop_movie.get('tmdb_rating', 0) + flop_movie.get('omdb_rating', 0)) / 2 if flop_movie.get('tmdb_rating') and flop_movie.get('omdb_rating') else flop_movie.get('tmdb_rating') or flop_movie.get('omdb_rating')
        
        flop_text = (
            f"On the other end of the spectrum, <strong>{flop_movie['title']}</strong> faces an uphill battle, reflected in its low Hype Score of <strong>{flop_score}/100</strong>. "
            f"The primary concerns stem from weaker audience engagement online, with only <strong>{flop_views} trailer views</strong>. "
        )
        if flop_rating < 5:
            flop_text += f"This is compounded by lukewarm critic ratings, averaging just <strong>{flop_rating:.1f}/10</strong>. "
        flop_text += "To improve its prospects, a significant marketing push to boost online visibility and generate positive word-of-mouth will be necessary."
        analysis['flop_analysis'] = flop_text

    # --- Key Insights based on data comparison ---
    insights = []
    if len(sorted_data) > 1:
        # Insight 1: Engagement Efficiency (Likes per 1000 Views)
        for movie in sorted_data:
            views = movie['youtube_stats'].get('views', 0)
            likes = movie['youtube_stats'].get('likes', 0)
            movie['likes_per_1k_views'] = (likes / views * 1000) if views > 0 else 0
        most_efficient = max(sorted_data, key=lambda x: x['likes_per_1k_views'])
        insights.append(
            f"<strong>Engagement Efficiency:</strong> <strong>{most_efficient['title']}</strong> shows the most efficient engagement, earning "
            f"<strong>{most_efficient['likes_per_1k_views']:.1f} likes for every 1,000 views</strong>. This indicates a highly dedicated and passionate early audience."
        )

        # Insight 2: Data Dominance
        total_views = sum(m['youtube_stats'].get('views', 0) for m in sorted_data) or 1
        best_movie_view_share = (best_movie['youtube_stats'].get('views', 0) / total_views) * 100
        if best_movie_view_share > 50:
            insights.append(
                f"<strong>Market Dominance:</strong> The winner, <strong>{best_movie['title']}</strong>, isn't just leading—it's dominating the online conversation, "
                f"capturing over <strong>{best_movie_view_share:.0f}%</strong> of the total trailer views among the titles analyzed."
            )
            
    analysis['key_insights'] = insights
    return analysis

# --- MODIFIED VIEW: Now calls the analysis function ---
def dashboard_view(request):
    context = {}
    if request.method == 'POST':
        movie_names_raw = request.POST.get('movie_names', '')
        selected_metric = request.POST.get('metric_select', 'views')
        titles = [title.strip() for title in movie_names_raw.split('\n') if title.strip()]
        
        all_data = []
        for title in titles:
            movie_data = get_movie_data(title)
            trailer_id, yt_stats = get_youtube_data(movie_data['title'])
            movie_data['trailer_id'] = trailer_id
            movie_data['youtube_stats'] = yt_stats
            all_data.append(movie_data)
        
        sorted_data, verdict = calculate_scores_and_verdict(all_data)
        context['movies_data'] = sorted_data
        context['verdict'] = verdict
        context['movie_names_raw'] = movie_names_raw

        # --- NEW: Call the analysis generator and add to context ---
        if sorted_data:
            context['detailed_analysis'] = generate_detailed_analysis(sorted_data, verdict)

        # (The rest of the view remains the same)
        if all_data:
            graphs = {}
            metric_title = selected_metric.title()
            graphs['bar'] = create_graph(all_data, selected_metric, 'bar', f'{metric_title} Comparison')
            graphs['pie'] = create_graph(all_data, selected_metric, 'pie', f'{metric_title} Distribution')
            graphs['line'] = create_graph(all_data, selected_metric, 'line', f'{metric_title} Trend')
            graphs['area'] = create_graph(all_data, selected_metric, 'area', f'{metric_title} Volume')
            graphs['scatter'] = create_scatter_plot(all_data, 'views', 'likes', 'Engagement Rate (Views vs. Likes)')
            
            context['graphs'] = graphs
            context['selected_metric'] = selected_metric
            
    return render(request, 'dashboard/index.html', context)

#
# --- ALL OTHER FUNCTIONS (create_graph, download_csv, etc.) REMAIN THE SAME ---
# --- You should already have them in your file. I'm omitting them here for brevity. ---
#

# --- (Make sure these functions are still in your views.py) ---
def create_graph_formats(plt_figure):
    formats = {}
    buf = io.BytesIO(); plt_figure.savefig(buf, format='svg'); buf.seek(0); formats['svg'] = base64.b64encode(buf.read()).decode('utf-8'); buf.close()
    buf = io.BytesIO(); plt_figure.savefig(buf, format='png'); buf.seek(0); formats['png'] = base64.b64encode(buf.read()).decode('utf-8'); buf.close()
    buf = io.BytesIO(); plt_figure.savefig(buf, format='jpeg'); buf.seek(0); formats['jpeg'] = base64.b64encode(buf.read()).decode('utf-8'); buf.close()
    plt.close(plt_figure)
    return formats
def create_graph(data, metric, chart_type, title):
    labels = [item['title'] for item in data]; values = [item['youtube_stats'].get(metric, 0) for item in data]
    fig = plt.figure(figsize=(10, 5))
    if chart_type == 'bar': plt.bar(labels, values, color='skyblue')
    elif chart_type == 'pie':
        if sum(values) > 0: plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90); plt.axis('equal')
        else: plt.text(0.5, 0.5, 'No data to display', ha='center', va='center')
    elif chart_type == 'line': plt.plot(labels, values, marker='o', linestyle='-')
    elif chart_type == 'area': plt.fill_between(labels, values, color="skyblue", alpha=0.4); plt.plot(labels, values, color="Slateblue", alpha=0.6, marker='o')
    plt.ylabel(metric.title()); plt.xticks(rotation=15, ha="right"); plt.title(title); plt.tight_layout()
    return create_graph_formats(fig)
def create_scatter_plot(data, x_metric, y_metric, title):
    x_values = [item['youtube_stats'].get(x_metric, 0) for item in data]; y_values = [item['youtube_stats'].get(y_metric, 0) for item in data]; labels = [item['title'] for item in data]
    fig = plt.figure(figsize=(10, 6)); plt.scatter(x_values, y_values, alpha=0.7, s=100)
    for i, label in enumerate(labels): plt.annotate(label, (x_values[i], y_values[i]), textcoords="offset points", xytext=(0,10), ha='center')
    plt.title(title); plt.xlabel(x_metric.title()); plt.ylabel(y_metric.title()); plt.grid(True); plt.tight_layout()
    return create_graph_formats(fig)
def _get_data_for_download(request):
    movie_names_raw = request.POST.get('movie_names', ''); titles = [title.strip() for title in movie_names_raw.split('\n') if title.strip()]
    all_data = []
    for title in titles:
        movie_data = get_movie_data(title)
        _, yt_stats = get_youtube_data(movie_data.get('title', title)); movie_data['youtube_stats'] = yt_stats; all_data.append(movie_data)
    sorted_data, _ = calculate_scores_and_verdict(all_data)
    return sorted_data
def download_csv(request):
    if request.method != 'POST': return render(request, 'dashboard/index.html')
    sorted_data = _get_data_for_download(request)
    response = HttpResponse(content_type='text/csv'); timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response['Content-Disposition'] = f'attachment; filename="movie_analysis_{timestamp}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Rank', 'Title', 'Total Score', 'TMDB Rating', 'OMDB Rating', 'YouTube Views', 'YouTube Likes', 'YouTube Comments', 'Description'])
    for i, movie in enumerate(sorted_data): writer.writerow([i + 1, movie.get('title'), f"{movie.get('total_score', 0):.2f}", movie.get('tmdb_rating'), movie.get('omdb_rating'), movie['youtube_stats'].get('views'), movie['youtube_stats'].get('likes'), movie['youtube_stats'].get('comments'), movie.get('overview')])
    return response
def download_json(request):
    if request.method != 'POST': return render(request, 'dashboard/index.html')
    sorted_data = _get_data_for_download(request); timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response = JsonResponse(sorted_data, safe=False, json_dumps_params={'indent': 4})
    response['Content-Disposition'] = f'attachment; filename="movie_analysis_{timestamp}.json"'
    return response
def get_movie_data(title):
    data = {'title': title}
    try:
        tmdb_url = f"https://api.themoviedb.org/3/search/multi?api_key={settings.TMDB_API_KEY}&query={title}"; tmdb_response = requests.get(tmdb_url).json()
        if tmdb_response.get('results'):
            result = tmdb_response['results'][0]
            data['poster_path'] = f"https://image.tmdb.org/t/p/w500{result.get('poster_path')}"; data['tmdb_rating'] = result.get('vote_average', 0); data['title'] = result.get('name') or result.get('title'); data['overview'] = result.get('overview', 'No description available.')
        else: data['poster_path'], data['tmdb_rating'], data['overview'] = '', 0, 'No data found.'
    except Exception as e: data['poster_path'], data['tmdb_rating'], data['overview'] = '', 0, 'Error fetching data.'
    try:
        omdb_url = f"http://www.omdbapi.com/?t={data.get('title', title)}&apikey={settings.OMDB_API_KEY}"; omdb_response = requests.get(omdb_url).json()
        if omdb_response.get('Response') == 'True' and omdb_response.get('imdbRating') != 'N/A': data['omdb_rating'] = float(omdb_response.get('imdbRating', 0))
        else: data['omdb_rating'] = 0
    except Exception as e: data['omdb_rating'] = 0
    return data
def get_youtube_data(query):
    try:
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY); search_request = youtube.search().list(q=f"{query} official trailer", part='snippet', maxResults=1, type='video'); search_response = search_request.execute()
        if not search_response.get('items'): return None, {}
        video_id = search_response['items'][0]['id']['videoId']; video_request = youtube.videos().list(part='statistics', id=video_id); video_response = video_request.execute(); stats = video_response['items'][0]['statistics']
        return video_id, {'views': int(stats.get('viewCount', 0)), 'likes': int(stats.get('likeCount', 0)), 'comments': int(stats.get('commentCount', 0))}
    except Exception as e: return None, {}
def calculate_scores_and_verdict(movies_data):
    if not movies_data: return movies_data, {}
    weights = {'views': 0.30, 'likes': 0.25, 'comments': 0.15, 'rating': 0.30}
    max_views = max(d['youtube_stats'].get('views', 0) for d in movies_data) or 1; max_likes = max(d['youtube_stats'].get('likes', 0) for d in movies_data) or 1; max_comments = max(d['youtube_stats'].get('comments', 0) for d in movies_data) or 1
    for movie in movies_data:
        views_score = (movie['youtube_stats'].get('views', 0) / max_views) * 100; likes_score = (movie['youtube_stats'].get('likes', 0) / max_likes) * 100; comments_score = (movie['youtube_stats'].get('comments', 0) / max_comments) * 100
        tmdb_r, omdb_r = movie.get('tmdb_rating', 0) or 0, movie.get('omdb_rating', 0) or 0
        avg_rating = (tmdb_r + omdb_r) / 2 if tmdb_r and omdb_r else tmdb_r or omdb_r
        rating_score = (avg_rating / 10) * 100; movie['total_score'] = ((views_score * weights['views']) + (likes_score * weights['likes']) + (comments_score * weights['comments']) + (rating_score * weights['rating']))
    sorted_movies = sorted(movies_data, key=lambda x: x['total_score'], reverse=True)
    verdict = {}
    if sorted_movies:
        verdict['best_bet'] = sorted_movies[0]; verdict['potential_flop'] = sorted_movies[-1] if len(sorted_movies) > 1 else sorted_movies[0]
    return sorted_movies, verdict