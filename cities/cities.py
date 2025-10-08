# this file deals with our city-level data

cities_cache={}

def create(name: str):
    if not isinstance(name, str):
        raise ValueError(f'Bad type for {type(name)=}')
    if not name.strip():
        raise ValueError("Missing required 'name' field for city.")		
    new_id = str(len(city_cache) + 1)
    record = {"name": name.strip()}
   
 city_cache[new_id] = record
    return new_id
