# 🎬 Movies-Series---Rating

A Django-based web application that allows users to:

- 🔍 Search for movies and web series  
- 📃 View detailed information (images, trailers, ratings, plot, and more)  
- 📄 Export movie and series data to CSV files  
- 🎨 Enjoy a clean and user-friendly interface  

Powered by external APIs:

- [TMDb (The Movie Database)](https://www.themoviedb.org/)  
- [OMDb API](http://www.omdbapi.com/)  
- [YouTube Data API](https://developers.google.com/youtube/v3)

---

## 🔗 Live Demo

**URL:** [https://satyampote.pythonanywhere.com/](https://satyampote.pythonanywhere.com/)

---

## 🧩 Features

- 🔍 **Search Movies/Series** – Type any title and get instant results  
- 📃 **View Details** – Plot, cast, ratings, poster, trailer, and more  
- 🖼️ **Images & Trailers** – Watch YouTube trailers and see TMDb posters  
- 📄 **Export to CSV** – Save search results for future use  
- 🌐 **API Integration** – Combines data from TMDb, OMDb, and YouTube  
- 🎨 **User-Friendly Interface** – Built with clean HTML/CSS (Bootstrap optional)

---

## 📸 Screenshots

![Image](https://github.com/user-attachments/assets/c12f4a96-72c8-462c-8375-2114c838845a)
![Image](https://github.com/user-attachments/assets/4dec2172-eb35-47db-90fd-f419d9abb8ee)
![Image](https://github.com/user-attachments/assets/2ab9eea2-0b31-422c-85af-72c4c4ccab57)
![Image](https://github.com/user-attachments/assets/2638d7c0-304d-4fa6-93bd-f7f2d0fe4a80)
![Image](https://github.com/user-attachments/assets/b119a07e-f6d0-4982-b929-3c565f7900d2)

---

## ⚙️ Installation

### 1. Clone the Repository

<pre><code class="language-bash">
git clone https://github.com/SatyamPote/Movies-Series---Rating.git
cd Movies-Series---Rating
</code></pre>

### 2. Create and Activate Virtual Environment

<pre><code class="language-bash">
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
</code></pre>

### 3. Install Dependencies

<pre><code class="language-bash">
pip install -r requirements.txt
</code></pre>

---

## 🔐 Configuration

### API Keys

Get your API keys from:

- [TMDb](https://www.themoviedb.org/)  
- [OMDb](http://www.omdbapi.com/)  
- [YouTube Data API](https://console.cloud.google.com/)

### Environment Variables

Create a `.env` file or set environment variables:

<pre><code class="language-env">
TMDB_API_KEY=your_tmdb_api_key
OMDB_API_KEY=your_omdb_api_key
YOUTUBE_API_KEY=your_youtube_api_key
</code></pre>

Alternatively, add the keys in `settings.py` (not recommended for production).

---

## 🚀 Usage

### 1. Apply Migrations

<pre><code class="language-bash">
python manage.py migrate
</code></pre>

### 2. Start Development Server

<pre><code class="language-bash">
python manage.py runserver
</code></pre>

### 3. Visit the App

Go to [http://localhost:8000/](http://localhost:8000/) in your browser.

### 4. Search for Movies/Series

Use the search bar to explore any title and view detailed results.

---

## 📤 Exporting Data

Click the **"Export to CSV"** button on the results page to download a CSV file of your search results.

---

## 🛠️ Technologies Used

- **Backend:** Django, Python  
- **Frontend:** HTML, CSS, Bootstrap (optional)  
- **APIs:** TMDb, OMDb, YouTube Data API  
- **Other:** CSV Export, Requests, dotenv

---

## 🤝 Contributing

Contributions are welcome!  
Feel free to open an issue or submit a pull request to improve the project.

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

## 🙏 Acknowledgements

- [TMDb](https://www.themoviedb.org/)  
- [OMDb](http://www.omdbapi.com/)  
- [YouTube Data API](https://developers.google.com/youtube)  
- [Django Docs](https://docs.djangoproject.com/) and the awesome Django community

---

If you found this project useful, please ⭐️ the repo and share it!  
Feel free to fork, clone, and build your own version!
