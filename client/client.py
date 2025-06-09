#!/usr/bin/env python3
import argparse
import sys
from ollama import Client

def main():
    parser = argparse.ArgumentParser(description='Chat with Ollama models')
    parser.add_argument('-u', '--url', default='http://localhost:11434', help='Ollama server URL')
    parser.add_argument('-c', '--content', default='In Oracle Database, give me a query that return the system date', help='Chat message content')
    parser.add_argument('-m', '--model', default='llama3.2:3b', help='Model name to use')
    args = parser.parse_args()

    if not (args.url.startswith('http://') or args.url.startswith('https://')):
        print("Error: URL must start with http:// or https://", file=sys.stderr)
        sys.exit(1)

    try:
        client = Client(host=args.url)
        message = {'role': 'user', 'content': args.content}

        contentStream = client.chat(
            model=args.model,
            messages=[message],
            stream=True,
        )

        for chunk in contentStream:
            print(chunk['message']['content'], end='', flush=True)
        print()  # Add newline after output
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()