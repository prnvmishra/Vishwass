import requests

test_text = """
We are pleased to offer you the role of Intern at Google Private Limited.
Your expected salary is Rs. 15,000 per month.
Reach out to hr@google.com for questions.
Note: You must pay a registration fee to confirm.
"""

files = {'file': ('test.pdf', test_text, 'application/pdf')}
response = requests.post('http://127.0.0.1:8000/analyze', files=files)
print(response.json())
