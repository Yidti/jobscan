# search_params.py

import json

def get_filter_params(role, keyword, selected_cities, isnew, selected_jobexp, model, order, asc):

    def get_values(selected, mapping):
        codes = [mapping[item] for item in selected]
        values = ','.join(map(str, codes))
        return values
    
    # Load search params mapping from JSON file
    with open('./config/search_params_mapping.json', 'r', encoding='utf-8') as file:
        mappings = json.load(file)

    # custom filter search
    role_code = mappings['ro_mapping'].get(role)
    area = get_values(selected_cities, mappings['city_mapping'])
    isnew_code = mappings['isnew_mapping'].get(isnew)
    jobexp = get_values(selected_jobexp, mappings['jobexp_mapping'])
    model_code = mappings['model_mapping'].get(model)
    order_code = mappings['order_mapping'].get(order)
    asc_code = mappings['asc_mapping'].get(asc)

    filter_params = {
        'ro': role_code,
        'keyword': keyword,
        'area': area,
        'isnew': isnew_code,
        'jobexp': jobexp,
        'mode': model_code,
        'order': order_code,
        'asc': asc_code,
    }

    return filter_params

if __name__ == "__main__":
    # 如果直接執行，可以做一些測試或其他操作
    pass