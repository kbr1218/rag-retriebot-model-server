# wrapup_response_schema.py
# response_schema.py
from langchain.output_parsers import ResponseSchema

# 🎬 Movie Detail Response Schema
movie_detail_schema = ResponseSchema(
    name="movies_detail",
    description="A list of movies with their full metadata, including title, genre, director, and reason for recommendation.",
    type="list",
    items=[
        ResponseSchema(name="asset_id", description="Unique identifier of the VOD content."),
        ResponseSchema(name="movie_id", description="Movie ID from the database."),
        ResponseSchema(name="title", description="Title of the movie."),
        ResponseSchema(name="original_title", description="Original title of the movie."),
        ResponseSchema(name="genre", description="Genres of the movie, separated by commas."),
        ResponseSchema(name="adult", description="Indicates whether the movie is for adults (True/False)."),
        ResponseSchema(name="runtime", description="Total runtime of the movie in minutes."),
        ResponseSchema(name="release_year", description="Year the movie was released."),
        ResponseSchema(name="release_date", description="Exact release date of the movie."),
        ResponseSchema(name="actors", description="Main actors in the movie, separated by commas."),
        ResponseSchema(name="director", description="Director of the movie."),
        ResponseSchema(name="orgnl_cntry", description="Country where the movie was produced."),
        ResponseSchema(name="original_language", description="Language the movie was originally filmed in."),
        ResponseSchema(name="vote_average", description="Average user rating (out of 10)."),
        ResponseSchema(name="vote_count", description="Total number of votes received."),
        ResponseSchema(name="popularity", description="Popularity score of the movie."),
        ResponseSchema(name="poster_path", description="URL of the movie's poster."),
        ResponseSchema(name="backdrop_path", description="URL of the movie's backdrop image."),
        ResponseSchema(name="overview", description="Brief summary of the movie."),
        ResponseSchema(name="reason", description="Reason why this movie was recommended to the user.")
    ]
)

# Chatbot Response Schema
chatbot_response_schema = ResponseSchema(
    name="response",
    description="The chatbot's natural language response summarizing the recommended movies."
)