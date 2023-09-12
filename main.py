from fastapi import FastAPI
from fastapi.responses import JSONResponse
from github.Auth import GitAppAuth
from argparse import ArgumentParser
from uvicorn import run

app = FastAPI(title="Label Manager")


def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-id", "--app_id", help="The ID of your GitHub App", required=True, type=int
    )
    parser.add_argument(
        "-p", "--port", help="The port this app will run on", required=True, type=int
    )

    return parser.parse_args()


@app.webhooks.post("/github")
async def bot(payload: str):
    global git

    repo_name = payload["repo"]["name"]
    pr_number = payload["pull_request"]["number"]
    owner = payload["repository"]["owner"]["login"]

    git.place_labels(labels=["WIP", "meme"], repo_name=repo_name, pr_number=pr_number)


def main():
    args = get_args()
    global git
    git = GitAppAuth(app_id=args.app_id)
    run(app, host="localhost", port=args.port)


if __name__ == "__main__":
    main()
