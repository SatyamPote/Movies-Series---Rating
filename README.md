# Movie & Web Series Tracker

## Overview

This is a Django-based web application that allows you to search for movies and web series, view details about them (including images and trailers), and export the data to CSV files. It utilizes external APIs like TMDb, OMDb, and YouTube Data API to fetch and display the information.


## Features

*   **Search:** Find movies and web series by title.
*   **Detailed Information:** View key details like genre, language, rating, release date/first air date, and overview.
*   **Images:** Display posters for movies and series from TMDb.
*   **Trailers:** Embed YouTube trailers.
*   **Season and Episode Data:** (If API Access Configured) Display season and episode information for web series.
*   **CSV Export:** Export movie and series data to CSV files.
*   **Background processing:** The data fetching has been created asynchronous so the web pages loads with out any problem

## Technology Stack

*   **Backend:**
    *   [Django] (Python) - Core web framework.
    *   Python - Programming language.
    *   SQLite (Default) - Database for storing data.
    *   [Celery] - Asynchronous task queue for data fetching.
    *   Redis - Message broker for Celery.
*   **Frontend:**
    *   HTML - Page structure.
    *   CSS - Styling.

## API Usage

This project uses the following APIs:

*   [TMDb API (The Movie Database)] - For movie and web series metadata.
*   [OMDb API (Open Movie Database)] - For movie details (Note: Not reliable for series).
*   [YouTube Data API] - For fetching trailers.

API Keys are required for these services. Store your API keys securely in a `.env` file or environment variables.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <YourProjectName>
    cd <YourProjectName>
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**

    *   Create a `.env` file in the project root.
    *   Add your API keys:

        ```
        DJANGO_SECRET_KEY=your_django_secret_key
        TMDB_API_KEY=your_tmdb_api_key
        OMDB_API_KEY=your_omdb_api_key
        YOUTUBE_API_KEY=your_youtube_api_key
        CELERY_BROKER_URL=redis://localhost:6379/0
        CELERY_RESULT_BACKEND=redis://localhost:6379/0
        DJANGO_DEBUG=True
        ```

    *   Make sure `.env` is in your `.gitignore` file to prevent committing your API keys.

5.  **Apply migrations:**

    ```bash
    python manage.py makemigrations tracker
    python manage.py migrate
    ```

6.  **Start Redis:**

    *   Ensure Redis is installed and running.

7.  **Start Celery worker (in a separate terminal):**

    ```bash
    celery -A movie_tracker worker -l info
    ```

8.  **Start the Django development server:**

    ```bash
    python manage.py runserver
    ```

9.  **Access the Application:**

    *   Open your web browser and go to `http://127.0.0.1:8000/`

## Contributing

Contributions are welcome! Feel free to submit pull requests with bug fixes, new features, or improvements to the documentation.

## Contact

*   LinkedIn: [Satyam Pote](https://www.linkedin.com/in/satyam-pote)
*   Gmail: [satyampote9999@gmail.com](mailto:satyampote9999@gmail.com)

## License

MIT License

**Disclaimer**: The code depends on working API access. Please follow instructions to ensure the appropriate environment has been built.
