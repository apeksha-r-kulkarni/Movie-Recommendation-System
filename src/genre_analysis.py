# src/genre_analysis.py
def popular_genres(df):
    """
    Handle genre strings separated by '|' or single genre.
    Returns genres ranked by average rating.
    """
    # make a copy to avoid modifying original
    tmp = df.copy()
    tmp["genre"] = tmp["genre"].astype(str).str.split("|")
    exploded = tmp.explode("genre")
    result = exploded.groupby("genre")["rating"].mean().sort_values(ascending=False)
    return result
