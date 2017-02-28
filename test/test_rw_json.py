import json
from pprint import pprint

with open('./history.json', encoding='utf-8') as json_data:
    data = json.load(json_data, encoding='utf-8')

pprint(data)

with open('./history.json', 'w', encoding='utf-8') as out_file:
    json.dump(data, out_file, indent=2, ensure_ascii=False)


