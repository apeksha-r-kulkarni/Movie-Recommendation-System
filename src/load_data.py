# src/load_data.py
import pandas as pd
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def load_movies(path=None):
    candidates = ["movies.csv", "movies_data.csv", "movies_dataset.csv"]
    if path:
        candidates = [path] + candidates
    for fn in candidates:
        p = os.path.join(DATA_DIR, fn)
        if os.path.exists(p):
            print(f"Loading movies from: {p}")
            return pd.read_csv(p)
    raise FileNotFoundError(f"No movies file found in {DATA_DIR}. Tried: {candidates}")

def load_ratings(path=None):
    candidates = ["ratings.csv", "ratings_data.csv"]
    if path:
        candidates = [path] + candidates
    for fn in candidates:
        p = os.path.join(DATA_DIR, fn)
        if os.path.exists(p):
            print(f"Loading ratings from: {p}")
            return pd.read_csv(p)
    raise FileNotFoundError(f"No ratings file found in {DATA_DIR}. Tried: {candidates}")

def load_all():
    movies = load_movies()
    ratings = load_ratings()
    return movies, ratings
