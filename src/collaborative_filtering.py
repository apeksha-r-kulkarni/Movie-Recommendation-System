# src/collaborative_filtering.py
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def create_user_movie_matrix(df):
    """
    Returns a pivot table: rows=userId, columns=movieId, values=rating
    """
    matrix = df.pivot_table(index="userId", columns="movieId", values="rating")
    return matrix

def get_similar_users(user_id, matrix, top_k=5):
    """
    Compute cosine similarity between users. Returns top_k similar user IDs (excluding the user itself).
    """
    mat = matrix.fillna(0)
    sim = cosine_similarity(mat)
    sim_df = pd.DataFrame(sim, index=mat.index, columns=mat.index)
    # sort desc, drop self
    sims = sim_df[user_id].sort_values(ascending=False)
    sims = sims.drop(user_id, errors="ignore")
    return sims.head(top_k)

def recommend(user_id, matrix, n=5):
    """
    Recommend n movieIds for user_id based on similar users' average ratings.
    Returns a pandas Series of movieId -> score (descending).
    """
    similar = get_similar_users(user_id, matrix, top_k=5)
    if similar.empty:
        return pd.Series(dtype=float)
    similar_users = similar.index.tolist()
    # average ratings from similar users
    sim_ratings = matrix.loc[similar_users]
    avg_scores = sim_ratings.mean(axis=0)
    # remove movies the user has already rated
    user_rated = matrix.loc[user_id].dropna().index if user_id in matrix.index else []
    avg_scores = avg_scores.drop(labels=user_rated, errors="ignore")
    # sort and return top n
    return avg_scores.sort_values(ascending=False).head(n)
