# this file deals with our city-level data

def create(name: str):
    if not isinstance(name, str):
        raise ValueError(f'Bad type for {type(name)=}')