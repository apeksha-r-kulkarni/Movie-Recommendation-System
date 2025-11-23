# src/preprocess.py
import pandas as pd

def _normalize_column(df, candidates, new_name):
    for c in candidates:
        if c in df.columns:
            if c != new_name:
                df = df.rename(columns={c: new_name})
            return df, True
    return df, False

def harmonize_columns(movies_df, ratings_df):
    movie_id_candidates = ["movieId", "movie_id", "movieID", "movieid", "id", "movie"]
    movie_name_candidates = ["title", "movie_name", "movieTitle", "name"]
    genre_candidates = ["genres", "genre"]
    user_id_candidates = ["userId", "user_id", "customer_id", "customerId", "userid"]
    rating_candidates = ["rating", "ratings", "score"]

    if movies_df is not None:
        for candidates, new in [
            (movie_id_candidates, "movieId"),
            (movie_name_candidates, "movie_name"),
            (genre_candidates, "genre")
        ]:
            movies_df, _ = _normalize_column(movies_df, candidates, new)

    if ratings_df is not None:
        for candidates, new in [
            (movie_id_candidates, "movieId"),
            (user_id_candidates, "userId"),
            (rating_candidates, "rating")
        ]:
            ratings_df, _ = _normalize_column(ratings_df, candidates, new)

    return movies_df, ratings_df

def merge_data(movies, ratings):
    movies, ratings = harmonize_columns(movies, ratings)

    print("movies.csv columns ->", list(movies.columns) if movies is not None else "None")
    print("ratings.csv columns ->", list(ratings.columns) if ratings is not None else "None")

    merged = pd.merge(ratings, movies, on="movieId", how="left", suffixes=("_r", "_m"))

    # Set unified columns
    if "movie_name_r" in merged.columns:
        merged["movie_name"] = merged["movie_name_r"]
    elif "movie_name_m" in merged.columns:
        merged["movie_name"] = merged["movie_name_m"]

    if "genre_r" in merged.columns:
        merged["genre"] = merged["genre_r"]
    elif "genre_m" in merged.columns:
        merged["genre"] = merged["genre_m"]

    if "rating_r" in merged.columns:
        merged["rating"] = merged["rating_r"]
    elif "rating_m" in merged.columns:
        merged["rating"] = merged["rating_m"]

    cols_to_drop = [c for c in merged.columns if c.endswith("_r") or c.endswith("_m")]
    merged = merged.drop(columns=cols_to_drop, errors="ignore")

    return merged

def clean(df):
    df.dropna(inplace=True)
    return df
