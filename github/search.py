from dataclasses import dataclass
from argparse import ArgumentParser
import sys
import re
import click
import requests
import time
from urllib.parse import unquote_plus

@dataclass
class Repository:
    name: str
    result_urls: set[str]
    url: str
    stars: int = -1

    def __str__(self):
        return "{name}\n - stars: {stars},\n - url: {url},\n - results: {results_url}".format(
            name=click.style(self.name, bold=True),
            stars=click.style(self.stars, fg="yellow", bold=True),
            url=click.style(self.url, fg="blue", underline=True),
            results_url=click.style(self.result_urls, fg="blue", underline=True)
        )

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    @staticmethod
    def repos_from_search(search_results: list) -> set["Repository"]:
        repos: dict[str, Repository] = {}
        with click.progressbar(search_results, label="Parsing query results") as bar:
            for result in search_results:
                result_url = result["html_url"]
                repo_data = result["repository"]
                repository = Repository(
                    name=repo_data["full_name"],
                    result_urls= {result_url},
                    url=repo_data["html_url"],
                    stars=repo_data["stargazers_count"] if "stargazers_count" in repo_data else -1,
                )
                if repository.url in repos:
                    repos[repository.url].result_urls |= repository.result_urls
                else:
                    repos[repository.url] = repository
                bar.update(1)
        return set(repos.values())

class GithubApi:
    def __init__(self, token):
        self.__session = requests.Session()
        self.__session.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }


    def search(self, query: str):
        url = f"https://api.github.com/search/code?q={query}&per_page=100"
        next_page_pattern = re.compile(r'(?<=<)([\S]*)(?=>; rel=\"next\")', re.IGNORECASE)
        pages_fetched = 0
        pages_remaining = True
        results = []
        while pages_remaining:
            try:
                response = self.__session.get(url)
                requests_remaining = response.headers["x-ratelimit-remaining"]
                if response.status_code == 429 or int(requests_remaining) == 0:
                    start = int(time.time())
                    now = start
                    cooldown = 60 # seconds
                    while now - start <= cooldown:
                        click.secho(f"\rReached Github Search rate limit (10 req/minute). Have to sleep for {cooldown-int(now-start)} seconds!", fg="red", nl=False)
                        now = int(time.time())
                        time.sleep(1)
                    continue
                result = response.json()["items"]
            except requests.RequestException:
                print("Request failed.")
                return set()
            except KeyError:
                # 'items' is mandatory in the response. Something went wrong if it is not found
                return set()
            else:
                pages_fetched += 1
                results.extend(result)
                if "link" not in response.headers:
                    break
                link_header = response.headers["link"]
                pages_remaining = ('rel=\"next\"' in link_header)
                if (pages_remaining):
                    click.secho(f"\rMore results remaining. Fetched {pages_fetched} pages. Fetching next page of results...", fg="yellow", nl=False)
                    match = next_page_pattern.search(link_header)
                    if match:
                        url = unquote_plus(match[0])
                    else:
                        break # failed to extract the next page, better exit
        click.secho("\nSuccess! Parsing query results.", fg="green")
        return Repository.repos_from_search(results)

    def star_count(self, repo_name: str) -> int:
        url =  "https://api.github.com/repos/" + repo_name
        try:
            response = self.__session.get(url)
            return response.json()["stargazers_count"]
        except requests.RequestException:
            print("Request failed.")
            return -1
        except KeyError:
            return -1

def main():
    parser = ArgumentParser()
    parser.add_argument("-k", "--api-key", required=True, help="Github API Key (classic token). Get one at: https://github.com/settings/tokens")
    args = parser.parse_args(sys.argv[1:])

    api = GithubApi(args.api_key)
    while True:
        try:
            query = click.prompt('Enter a search query', type=str, prompt_suffix=">")
            click.secho("Running query...")
            repos = api.search(query)
            if not repos:
                continue
            with click.progressbar(repos, label="Populating star count for repositories (slow due to rate-limit, stretch a little)") as bar:
                for repo in repos:
                    bar.update(1)
                    if repo.stars != -1:
                        continue
                    repo.stars = api.star_count(repo.name)
            repos = sorted([r for r in repos if r.stars >= 500], key=lambda repo: repo.stars)
            click.secho("Repositories matching query: ", bold=True)
            print("\n".join(str(r) for r in repos))
        except (KeyboardInterrupt, click.exceptions.Abort):
            print("\nExiting...")
            return

if __name__ == "__main__":
    main()
