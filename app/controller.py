import pickle
import numpy as np
import pandas as pd
from surprise import SVD
from numpy.linalg import norm
from scipy.spatial.distance import cosine

model = pickle.load(open("app/model.pkl", "rb"))
item_to_row_idx: dict[any, int] = model.trainset._raw2inner_id_items

def get_vector_by_book_title(book_title: str, trained_model: SVD) -> np.array:
    """Returns the latent features of a book in the form of a numpy array"""
    book_row_idx = trained_model.trainset._raw2inner_id_items[book_title]
    return trained_model.qi[book_row_idx]


all_books_names = list(item_to_row_idx)


def get_id_from_partial_name(partial) -> list:
    exist = []

    for name in all_books_names:
        if not name.isnumeric():
            if name.lower().__eq__(partial.lower()):
                exist = []
                exist.append(name)
                break
            elif partial.lower() in name.lower():
                # print(name, "|", all_books_names.index(name))
                exist.append(name)
            else:
                continue

    return exist


def cosine_similarity(vector_a: np.array, vector_b: np.array) -> float:
    """Returns a float indicating the similarity between two vectors"""
    cosine = np.dot(vector_a, vector_b) / (norm(vector_a) * norm(vector_b))
    return cosine


def display_recommendation(similarity_table):
    similarity_table = pd.DataFrame(
        similarity_table, columns=["vector cosine similarity", "book title"]
    ).sort_values("vector cosine similarity", ascending=False)
    return similarity_table["book title"].iloc[1:6]


def display_item(df: pd.DataFrame):
    item_to_row_idx_df = pd.DataFrame(
        list(item_to_row_idx.items()),
        columns=["Book name", "model.qi row idx"],
    ).set_index("Book name")
    return item_to_row_idx_df


def get_top_similarities(book_title: str, model: SVD) -> pd.DataFrame:
    # Get the first book vector
    book_vector: np.array = get_vector_by_book_title(book_title, model)
    # print(book_vector)
    similarity_table = []

    # Iterate over every possible movie and calculate similarity
    for other_book_title in model.trainset._raw2inner_id_items.keys():
        other_book_vector = get_vector_by_book_title(other_book_title, model)

        # Get the second movie vector, and calculate similarity
        similarity_score = cosine_similarity(other_book_vector, book_vector)
        similarity_table.append((similarity_score, other_book_title))

    # sort movies by ascending similarity
    return display_recommendation(sorted(similarity_table))


books_image = pd.read_csv("app/book_image.csv")
books_title = display_item(item_to_row_idx)
joined_df = books_title.join(books_image.set_index("title"), on="Book name")
high_rate_book = pd.read_csv("app/book_high.csv")

def find_book_image(book_list: list) -> list:
    image_url_list = []
    for i in range(len(book_list)):
        image_url = list(joined_df[joined_df.index == book_list[i]]["image_url"])[0]
        image_url_list.append(image_url)

    return image_url_list
