import json
import requests
from sympy import sympify, sqrt
from sympy.core.sympify import SympifyError

URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama2"  # Adjust if needed
LOG_FILE = "chat_log.txt"

print("Welcome to the Math & AI Chat")
print("Type a math expression or a question.")
print("Type END to exit.\n")

def log_interaction(question, answer):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("Question: " + question.strip() + "\n")
        f.write("Answer: " + answer.strip() + "\n")
        f.write("-" * 60 + "\n")

while True:
    user_input = input("Your input: ")

    if user_input.strip().lower() == "end":
        print("Exiting. Goodbye.")
        break

    # Try to evaluate math
    try:
        expr = sympify(user_input)
        result = expr.evalf()
        print(f"\nMath result:\n{user_input} = {result}\n")
        log_interaction(user_input, f"{user_input} = {result}")
        continue

    except SympifyError:
        pass  # Not a math expression

    # Otherwise, send to LLM
    data = {
        "model": MODEL_NAME,
        "prompt": user_input,
        "stream": True
    }

    try:
        response = requests.post(URL, json=data, stream=True)

        if response.status_code == 200:
            print("\nModel response:\n")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    try:
                        json_data = json.loads(decoded_line)
                        part = json_data.get("response", "")
                        print(part, end="", flush=True)
                        full_response += part
                    except json.JSONDecodeError:
                        continue
            print("\n" + "-" * 50 + "\n")
            log_interaction(user_input, full_response)

        else:
            print("API error – status code:", response.status_code)
            print("Details:", response.text)

    except requests.exceptions.RequestException as e:
        print("Connection error:")
        print(e)