import json

# Load results
with open('student_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find Daniel's results
daniel_results = [s for s in data['students'] if s['student_username'] == 'daniel']
print(f'Daniel results: {len(daniel_results)}')

for r in daniel_results:
    print(f'Daniel exam {r["exam_id"]}: {r["percentage"]}% - {r["mastery_level"]} - {r["exam_title"]}')

