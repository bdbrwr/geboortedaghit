# ToenOp1.nl – Dutch Birthday Hit Finder 🎶
_A web app to find out what song was #1 on the Dutch charts on your birthday. (Or any other day)_

[Live site: toenop1.nl](https://toenop1.nl)

## About

**ToenOp1.nl** is a nostalgic and fun web app that shows you the #1 hit song in the Netherlands on any given date. Whether you’re looking up your own birthdate, a friend’s birthday, or just feeling curious — this app lets you dive into Dutch pop history with ease.

This project is a recreation of a website that once existed, but which I can no longer find. It used to show what song was number 1 in the Dutch charts on the day you were born — or any day, really. When I recently tried to find it again, all I could find were U.S.-based or international chart sites.

For my first personal project, I decided to rebuild it, with a focus on the Dutch Top 40. It’s a simple tool with a local touch, meant to bring back that small joy of musical nostalgia.

> We are still looking for a reliable source for chart data before 1965.

## Features

- Enter any date and instantly see the song that topped the Dutch charts.
- Fast, mobile-friendly design.
- Covers chart history going back to 1965.
- Hosted live at [toenop1.nl](https://toenop1.nl)

## Tech Stack

- **Python** (Flask-style app)
- **SQLite** for local data storage
- **HTML/CSS** for the frontend, as Flask renders HTML dynamcially

## Running Locally

### 1. Prerequisites

Ensure the following are installed on your machine:

- Python 3.9 or higher
- [SQLite](https://www.sqlite.org/download.html)

### 2. Clone the Repository

```bash
git clone https://github.com/bdbrwr/geboortedaghit.git
cd geboortedaghit
```

### 3. Create a Virtual Environment and Install Dependencies

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file and adjust the values as needed:

```bash
cp .env.example .env
```

### 5. Initialize the Database

Before running the app, create and populate the database:

```bash
python src/create_database.py
python src/get-charts-top40.py
```

You can run these scripts every so often to fill the Spotify and YouTube links:

```bash
python src/get-spotify-links.py 
python src/get-youtube-links.py
```

This sets up the schema and fills it with historical chart data.

### 6. Start the Application

```bash
python run.py
```

Then open your browser and go to: [http://localhost:5000](http://localhost:5000)

---

## 7. To Do

- Swap to UV
- Implement actual tracking on website
- URL paths to actual dates
- Suggested dates (18th birthday from birthday, 9 months before etc)

---

## Contributing

Suggestions, fixes, and improvements are very welcome. If you’d like to contribute, feel free to fork the repo, open an issue, or submit a pull request.
