from fastapi import HTTPException


class TitleWasNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Anime was not found")
        
class TitleAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Title already exists")
        
class EpisodeAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Episode link already exists")
        
class InvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Incorrect title name or ID")
        