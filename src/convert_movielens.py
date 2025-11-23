# convert_movielens.py
# Usage: python convert_movielens.py --input_dir "../ml-100k/ml-100k" --out_dir "../data"

import os
import csv
import argparse

def load_genres(genre_path):
    genres = []
    with open(genre_path, encoding='latin-1') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 2:
                genres.append(parts[0])
    return genres

def convert_items(u_item_path, u_genre_path, out_movies_path):
    genres = load_genres(u_genre_path)
    movies = []
    with open(u_item_path, encoding='latin-1') as f:
        for line in f:
            parts = line.strip().split('|')
            movie_id = parts[0]
            title = parts[1]
            # genre flags start at index 5 (0-based) through 5+len(genres)-1
            flags = parts[5:5+len(genres)]
            movie_genres = [g for g, flag in zip(genres, flags) if flag == '1']
            genre_str = "|".join(movie_genres) if movie_genres else "Unknown"
            movies.append((movie_id, title, genre_str))
    # write CSV
    with open(out_movies_path, "w", newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(["movieId", "movie_name", "genre"])
        for mid, title, g in movies:
            writer.writerow([mid, title, g])
    print(f"Wrote movies -> {out_movies_path}")

def convert_ratings(u_data_path, out_ratings_path):
    # u.data is tab-separated: user_id  item_id  rating  timestamp
    with open(u_data_path, encoding='latin-1') as f:
        rows = [line.strip().split('\t') for line in f if line.strip()]
    with open(out_ratings_path, "w", newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(["userId", "movieId", "rating"])
        for user, movie, rating, _ in rows:
            writer.writerow([user, movie, rating])
    print(f"Wrote ratings -> {out_ratings_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True, help="path to extracted ml-100k folder (containing u.data, u.item, u.genre)")
    parser.add_argument("--out_dir", default="../data", help="where to write movies.csv and ratings.csv")
    args = parser.parse_args()

    input_dir = args.input_dir
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    u_item = os.path.join(input_dir, "u.item")
    u_data = os.path.join(input_dir, "u.data")
    u_genre = os.path.join(input_dir, "u.genre")

    convert_items(u_item, u_genre, os.path.join(out_dir, "movies.csv"))
    convert_ratings(u_data, os.path.join(out_dir, "ratings.csv"))
