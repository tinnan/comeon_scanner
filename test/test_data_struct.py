from pprint import pprint

obj = {
  "29111": [
    "ตอนที่ 1 - 29111",
    "ตอนที่ 3 - 29111",
    "ตอนที่ 4 - 29111",
    "ตอนที่ 5 - 29111"
  ],
  "31321": [
    "ตอนที่ 1 - 31321",
    "ตอนที่ 3 - 31321",
    "ตอนที่ 4 - 31321",
    "ตอนที่ 5 - 31321"
  ],
  "99999": [
    "ฟฟฟฟ",
    "หหหหห",
    "กกกกกก"
  ],
  "00000": None
}

pprint(obj)

obj['8x741'] = []

pprint(obj)

obj.get('8x741').append('หกีรหก')

pprint(obj)

obj.get("00000")

pprint(obj)
print([e[1] for e in list(enumerate(obj))])