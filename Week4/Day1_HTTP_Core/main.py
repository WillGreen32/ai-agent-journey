# main.py
from src.http.core import HttpClient, HttpError

def main():
    # Pass base_url directly to avoid any .env surprises
    client = HttpClient(base_url="https://jsonplaceholder.typicode.com")

    # --- Test GET ---
    print("=== GET /users ===")
    users = client.get("/users")
    print("Users count:", len(users))
    print("First user object:", users[0])           # full dict
    print("First user name:", users[0]["name"])     # single field

    # --- Test GET with query params (bonus) ---
    print("\n=== GET /posts?userId=1 ===")
    posts = client.get("/posts", params={"userId": 1})
    print("Posts by user 1:", len(posts))
    print("Sample post:", posts[0])

    # --- Test POST ---
    print("\n=== POST /posts ===")
    payload = {"title": "Hello", "body": "World", "userId": 1}
    new_post = client.post("/posts", payload)
    print("Created (simulated):", new_post)  # JSONPlaceholder simulates creation

    # --- Negative test (expect HttpError) ---
    print("\n=== GET /does-not-exist (expect error) ===")
    try:
        client.get("/does-not-exist")
    except HttpError as e:
        print("Caught:", e)

if __name__ == "__main__":
    main()
