from pydantic import BaseModel


class Settings(BaseModel):
    data_dir: str = "DSAssignmentDataSet"
    movies_csv: str = "netflix_movies_detailed_up_to_2025.csv"
    tv_csv: str = "netflix_tv_shows_detailed_up_to_2025.csv"
    default_limit: int = 20
