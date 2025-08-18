import argparse
import os
from download_filings import download_filings
from agent_runner import make_agent, ask
from config import DATA_DIR

def main():
    parser = argparse.ArgumentParser(description="RAG Agent for SEC 10-K Q&A")
    parser.add_argument("--download", action="store_true", help="Download (or re-check) the 10-K PDFs/HTMLs")
    parser.add_argument("--q", type=str, default="Which company had the highest operating margin in 2023?",
                        help="Your question for the agent")
    args = parser.parse_args()

    if args.download:
        os.makedirs(DATA_DIR, exist_ok=True)
        download_filings()

    agent = make_agent()
    result_json = ask(agent, args.q)
    print(result_json)

if __name__ == "__main__":
    main()
