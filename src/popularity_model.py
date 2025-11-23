# src/popularity_model.py
def popular_movies(df, top_n=10):
    """
    Return top_n movies by average rating.
    Groups by movie_name.
    """
    return df.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(top_n)
