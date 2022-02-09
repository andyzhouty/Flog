# User Doc (API V1)

## How to login the web api (HTTPBasicAuth)
1. Login with username / password
If you use httpie, you can auth by this
```bash
http 127.0.0.1:5000/api/v1/user/1/ -a <username>:<password>
```

2. Login with auth token (recommended)
To get the auth token, you need to **GET**
`/api/v1/auth/token` to get the token using the username / password auth method mentioned above.

Note that the token will expire in an hour for security, so you should
get another valid auth token at least once an hour.

## User operations
- /api/v1/user/*int:user_id*/:  
  - **GET**: Returns user schema (json):  

    Returns:
    - id: int  
      User ID
    - url: str  
      Show current url
    - kind: 'User'  
      Show that the return value is 'User' kind
    - username: str  
      The user's username
    - member_since: str  
      The user's registration time
    - last_seen: str  
      The user's last login time
    - name: str  
      The user's name
    - location: str  
      The user's location(set by user)
    - about_me: str  
      The user's about_me(set by user)

    Example Value:

    ```json
    {
        "id": 2,
        "kind": "User",
        "last_seen": "Fri, 30 Oct 2020 12:36:07 GMT",
        "location": "Shanghai, China",
        "member_since": "Fri, 30 Oct 2020 12:36:07 GMT",
        "name": "Kent Reyes",
        "url": "http://127.0.0.1:5000/api/v1/user/2/",
        "username": "kent-reyes"
    }
    ```

    Status: **200**

    - **PUT**: Updates user profile (only json is accepted)

        Arguments(optional):
          - username : str
          - name: str
          - location: str
          - about_me: str

        Json like this is accepted:

        ```json
        {
            "username": "example",
            "name": "Example",
            "location": "NY City, USA",
            "about_me": "Hello, World!"
        }
        ```

        Status: **204**

    - **DELETE**: Deletes current user  
        Example Value: `User 1 deleted.`  
        Status: **200**

## Collecting a post
URL: /api/v1/*any(collect,uncollect)*/*int:post_id*/  
Method: **GET**  
Status: *200*  
Returns: str  
Example:`Post id 12 collected.`
