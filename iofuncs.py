import pickle

def pickle_to_file(obj, filename: str, directory: str = 'pickled_strategies'): 
    
    assert filename.endswith('.pkl'), "File name has to end with .pkl extension!"
    full_path = f'{directory}/{filename}'
    with open(full_path, 'wb') as f: 
        pickle.dump(obj, f)

def open_pickle(filepath: str): 

    with open(filepath, 'rb') as f: 
        obj = pickle.load(f)

    return obj
