# src/main.py
from load_data import load_all
from preprocess import merge_data, clean
from popularity_model import popular_movies
from genre_analysis import popular_genres
from collaborative_filtering import create_user_movie_matrix, recommend

def main():
    # Load movies + ratings
    movies, ratings = load_all()

    # Merge them properly
    df = merge_data(movies, ratings)

    # Clean merged data
    df = clean(df)

    # Diagnostics
    print("Loaded columns:", list(df.columns))
    print("\nSample rows:")
    print(df.head(8).to_string(index=False))

    # Popular movies
    print("\n=== Most Popular Movies (by avg rating) ===")
    print(popular_movies(df, top_n=10).to_string())

    # Popular genres
    print("\n\n=== Genres by average rating ===")
    print(popular_genres(df).to_string())

    # Collaborative filtering
    matrix = create_user_movie_matrix(df)
    sample_user = int(matrix.index[0])
    print(f"\n\n=== Recommendations for user {sample_user} ===")
    
    recs = recommend(sample_user, matrix, n=5)

    if recs.empty:
        print("Not enough data for CF.")
    else:
        movie_names = {mid: name for mid, name in df[["movieId", "movie_name"]].drop_duplicates().values}
        mapped = [f"{mid} - {movie_names.get(mid,'Unknown')} (score: {recs.loc[mid]:.3f})"
                  for mid in recs.index]
        print("\n".join(mapped))

if __name__ == "__main__":
    main()
