# src/app_streamlit.py
import streamlit as st
import pandas as pd

# import your existing modules
from load_data import load_all
from preprocess import merge_data, clean
from popularity_model import popular_movies
from genre_analysis import popular_genres
from collaborative_filtering import create_user_movie_matrix, recommend

st.set_page_config(page_title="Movie Recommendation System — Streamlit Demo", layout="wide")


# ---------------------------
# LOAD + PREPARE
# ---------------------------
@st.cache_data
def load_and_prepare():
    movies, ratings = load_all()
    df = merge_data(movies, ratings)
    df = clean(df)
    return df


# ---------------------------
# POPULAR MOVIES
# ---------------------------
def show_popular_movies(df, top_n=10):
    st.subheader(f"Top {top_n} Movies (by average rating)")
    top = popular_movies(df, top_n=top_n)

    tmp = df[["movie_name", "genre"]].drop_duplicates()
    movie_genre_map = tmp.groupby("movie_name")["genre"].agg(
        lambda s: "|".join({g for v in s for g in str(v).split("|")})
    ).to_dict()

    top_df = top.reset_index()
    top_df.columns = ["movie_name", "rating"]
    top_df["Genre"] = top_df["movie_name"].map(movie_genre_map)

    top_df.index = top_df.index + 1
    top_df.index.name = "S.No"
    top_df = top_df.rename(columns={"movie_name": "Movie", "rating": "Avg Rating"})
    st.table(top_df[["Movie", "Genre", "Avg Rating"]])


# ---------------------------
# GENRES (GLOBAL)
# ---------------------------
def show_genres(df, top_n=10):
    st.subheader("Genres by average rating")

    genres = popular_genres(df)
    st.bar_chart(genres.head(top_n))

    genre_df = genres.reset_index()
    genre_df.columns = ["Genre", "Avg Rating"]
    genre_df.index = genre_df.index + 1
    st.table(genre_df.head(top_n))


# ---------------------------
# USER GENRE ANALYSIS (ROBUST)
# ---------------------------
@st.cache_data
def get_user_genre_stats(df, user_id, min_ratings_for_genre=1):

    user_df = df[df["userId"] == user_id].copy()
    if user_df.empty:
        return pd.DataFrame()

    def normalize(x):
        if isinstance(x, list):
            return x
        if pd.isna(x):
            return ["Unknown"]
        return [g.strip() for g in str(x).split("|") if g.strip()]

    user_df["genre_list"] = user_df["genre"].apply(normalize)
    user_df = user_df.explode("genre_list")
    user_df = user_df.rename(columns={"genre_list": "genre_clean"})

    user_df["genre_clean"] = user_df["genre_clean"].astype(str).str.strip()
    user_df.loc[user_df["genre_clean"] == "", "genre_clean"] = "Unknown"

    agg = user_df.groupby("genre_clean")["rating"].agg(["count", "mean"]).reset_index()
    agg.columns = ["genre", "count_ratings", "avg_rating"]

    agg = agg[agg["count_ratings"] >= min_ratings_for_genre]
    if agg.empty:
        return pd.DataFrame()

    agg["weighted_score"] = agg["avg_rating"] * agg["count_ratings"]
    agg = agg.sort_values("weighted_score", ascending=False)
    return agg.reset_index(drop=True)


def show_user_top_genres(df, user_id, top_n=5, method="weighted_score", min_ratings_for_genre=1):
    st.subheader(f"Top genres for user {user_id}")

    stats = get_user_genre_stats(df, user_id, min_ratings_for_genre)
    if stats.empty:
        st.info("No genre statistics available for this user.")
        return

    top_stats = stats.sort_values(method, ascending=False).head(top_n)

    display = top_stats.copy()
    display.index = display.index + 1
    display.index.name = "S.No"
    st.table(display[["genre", "count_ratings", "avg_rating", "weighted_score"]])

    st.bar_chart(top_stats.set_index("genre")[[method]])

    # -----------------------------------
    # REMOVED: “Top movies rated by user”
    # -----------------------------------


# ---------------------------
# RECOMMENDATIONS
# ---------------------------
def show_recommendations(df, user_id, n):
    st.subheader(f"Recommendations for user {user_id}")

    matrix = create_user_movie_matrix(df)
    if user_id not in matrix.index:
        st.warning("User not in matrix.")
        return

    recs = recommend(user_id, matrix, n=n)
    if recs is None or len(recs) == 0:
        st.info("No recommendations found.")
        return

    tmp = df[["movieId", "movie_name", "genre"]].drop_duplicates()
    genre_map = tmp.groupby("movieId")["genre"].first().to_dict()
    name_map = tmp.set_index("movieId")["movie_name"].to_dict()

    rows = []
    for mid, score in recs.items():
        rows.append({
            "Movie ID": mid,
            "Movie Name": name_map.get(mid, "Unknown"),
            "Genre": genre_map.get(mid, "Unknown"),
            "Score": score
        })

    rec_df = pd.DataFrame(rows)
    rec_df.index = rec_df.index + 1
    st.table(rec_df)


# ---------------------------
# MAIN APP
# ---------------------------
def main():
    st.title("Movie Recommendation System — Streamlit Demo")

    df = load_and_prepare()

    st.sidebar.header("Controls")
    user_list = sorted(df["userId"].unique())
    user_id = st.sidebar.selectbox("Select user", user_list)
    n_recs = st.sidebar.slider("Number of recommendations", 1, 10, 5)

    st.sidebar.markdown("---")
    genre_method = st.sidebar.selectbox("Genre ranking method",
                                        ["weighted_score", "count_ratings", "avg_rating"])
    top_genres_n = st.sidebar.number_input("Top N genres", 1, 20, 5)
    min_ratings = st.sidebar.slider("Min ratings per genre", 1, 10, 1)

    show_popular_movies(df, 10)
    st.write("---")

    show_genres(df, 10)
    st.write("---")

    show_user_top_genres(df, user_id, top_genres_n, genre_method, min_ratings)
    st.write("---")

    show_recommendations(df, user_id, n_recs)


if __name__ == "__main__":
    main()
