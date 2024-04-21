import json
# Sample JSON string
json_string = '{"name": "John", "age": 30, "city": "New York"}'

# Using json.loads() to parse the JSON string
parsed_json = json.loads(json_string)

print(parsed_json)
# Accessing the parsed JSON data
print("Name:", parsed_json['name'])
print("Age:", parsed_json['age'])
print("City:", parsed_json['city'])
