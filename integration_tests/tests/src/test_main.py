import json
import requests

if (lambda: True)():
    federation_url = "http://federation:3000/graphql"
    serviceA_url = "http://service_a:3000/graphql"
    serviceB_url = "http://service_b:3000/graphql"
    serviceC_url = "http://service_c:3000/graphql"
    serviceD_url = "http://service_d:3000/graphql"
else:
    federation_url = "http://127.0.0.1:3000/graphql"
    serviceA_url = "http://127.0.0.1:3001/graphql"
    serviceB_url = "http://127.0.0.1:3002/graphql"
    serviceC_url = "http://127.0.0.1:3003/graphql"
    serviceD_url = "http://127.0.0.1:3004/graphql"


def test_integrate_simple_schema():
    query = {
        "query": """
            query {
                goodbye
            }
        """,
        "variables": {},
    }
    response = requests.post(federation_url, json=query)
    assert response.status_code == 200
    data = json.loads(response.content)["data"]
    assert data["goodbye"] == "See ya!"


def test_external_types():
    query = {
        "query": """
            query {
                posts {
                    title
                    text {
                       id
                       body
                       color
                    }
                    files {
                       id
                       name
                    }
                    author {
                        id
                        primaryEmail
                    }
                }
                articles {
                    id
                    text
                    author {
                        id
                        primaryEmail
                    }
                }
            }
        """,
        "variables": {},
    }
    response = requests.post(
        federation_url,
        json=query,
    )
    assert response.status_code == 200
    data = json.loads(response.content)["data"]
    posts = data["posts"]
    articles = data["articles"]

    assert 4 == len(posts)
    assert [{"id": 1, "name": "file_1"}] == posts[0]["files"]
    assert {"id": 1, "body": "funny_text_1", "color": 3} == posts[0]["text"]
    assert [{"id": 2, "name": "file_2"}, {"id": 3, "name": "file_3"}] == posts[1][
        "files"
    ]
    assert {"id": 2, "body": "funny_text_2", "color": 4} == posts[1]["text"]
    assert posts[2]["files"] is None
    assert {"id": 3, "body": "funny_text_3", "color": 5} == posts[2]["text"]
    assert {"id": 1001, "primaryEmail": "frank@frank.com",} == posts[
        3
    ]["author"]

    assert articles == [
        {
            "id": 1,
            "text": "some text",
            "author": {"id": 5, "primaryEmail": "name_5@gmail.com"},
        }
    ]


def fetch_sdl(service_name):
    query = {
        "query": """
            query {
                _service {
                    sdl
                }
            }
        """,
        "variables": {},
    }
    response = requests.post(service_name, json=query)
    assert response.status_code == 200

    text = response.json()["data"]["_service"]["sdl"]
    while "  " in text:
        text = text.replace("  ", " ")

    return text


def test_key_decorator_applied_by_exact_match_only():
    sdl = fetch_sdl(serviceB_url)
    assert 'type FileNode @key(fields: "id")' in sdl
    assert 'type FileNodeAnother @key(fields: "id")' not in sdl


def test_mutation_is_accessible_in_federation():
    # this mutation is created in service_b
    mutation = """
    mutation {
        funnyMutation {
            result
        }
    }"""

    response = requests.post(federation_url, json={"query": mutation})
    assert response.status_code == 200
    assert "errors" not in response.json()
    assert response.json()["data"]["funnyMutation"]["result"] == "Funny"


def test_multiple_key_decorators_apply_multiple_key_annotations():
    sdl = fetch_sdl(serviceB_url)
    assert 'type User @key(fields: "primaryEmail") @key(fields: "id")' in sdl


def test_avoid_duplication_of_key_decorator():
    sdl = fetch_sdl(serviceA_url)
    assert 'extend type FileNode @key(fields: "id") {' in sdl


def test_requires():
    query = {
        "query": """
            query {
                articles {
                    id
                    text
                    author {
                        uppercaseEmail
                    }
                }
            }
        """,
        "variables": {},
    }
    response = requests.post(
        federation_url,
        json=query,
    )
    assert response.status_code == 200
    data = json.loads(response.content)["data"]
    articles = data["articles"]

    assert articles == [
        {"id": 1, "text": "some text", "author": {"uppercaseEmail": "NAME_5@GMAIL.COM"}}
    ]


def test_provides():
    """
    articles -> w/o provide (get age value from service b)
    articlesWithAuthorAgeProvide -> w/ provide (get age value from service c)

    :return:
    """
    query = {
        "query": """
                query {
                    articles {
                        id
                        text
                        author {
                            age
                        }
                    }
                    articlesWithAuthorAgeProvide {
                        id
                        text
                        author {
                            age
                        }
                    }
                }
            """,
        "variables": {},
    }
    response = requests.post(
        federation_url,
        json=query,
    )
    assert response.status_code == 200
    data = json.loads(response.content)["data"]
    articles = data["articles"]
    articles_with_age_provide = data["articlesWithAuthorAgeProvide"]

    assert articles == [{"id": 1, "text": "some text", "author": {"age": 17}}]

    assert articles_with_age_provide == [
        {"id": 1, "text": "some text", "author": {"age": 18}}
    ]
