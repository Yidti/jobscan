# search_params.py

import json

def get_filter_params(*args):

    def get_values(value, mappings):
        codes = [mappings[key][item] for item in value if item in mappings[key]]
        values = ','.join(map(str, codes))
        return values
    
    # Load search params mapping from JSON file
    with open('./config/search_params_mapping.json', 'r', encoding='utf-8') as file:
        mappings = json.load(file)

    filter_params = {}
    for dict in args:
        key = next(iter(dict), None)
        value = dict[key]
        # print(key,value)

        if key in mappings:
            if isinstance(value, list):
                # If the value is a list, apply the mapping to each element
                mapped_values = get_values(value,mappings)
                filter_params[key] = mapped_values
            else:
                # If the value is not a list, apply the mapping directly
                filter_params[key] = mappings[key].get(value, value)
        else:
            filter_params[key] = value

    return filter_params

if __name__ == "__main__":
    # 如果直接執行，可以做一些測試或其他操作
    pass