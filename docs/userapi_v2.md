# User Doc (API V2)

## How to login the web api (Bearer Token)

### Login with OAuth Token

POST /api/v2/oauth/token/ with your username and your password in **multipart/form-data**.

Example:
| Key      | Value       |
| -------- | ----------- |
| username | kevin-romes |
| password | abcd123456  |

If your credentials are correct, it should return an access_token, the
expiration time(an hour) and the token type (bearer).

Example Value:

```json
{
  "access_token": "eyJhbGciOiJIUzUxMiIsImlhdCI6...",
  "expiration": 3600,
  "token_type": "Bearer"
}
```

Put `Bearer <your_token>` to the `Authorization` Header, then you can explore
flog! After an hour, the token will expire and you should get another token to use.

Note that the only difference between v1 and v2 is the authorization type
and v2 ONLY supports Bearer Token.

## User operations

- /api/v2/user/*int:user_id*/:  
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
        "url": "http://127.0.0.1:5000/api/v2/user/2/",
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

URL: /api/v2/*any(collect,uncollect)*/*int:post_id*/  
Method: **GET**  
Status: *200*  
Returns: str  
Example:`Post id 12 collected.`

## Following another person

URL: /api/v2/*any(follow,unfollow)*/*int:user_id*/
Method: **GET**  
Status: **204**  

## Check one's followers

URL: /api/v2/user/*int:user_id*/followers/  
Method: **GET**  
Status: **200**

## Check one's following

URL: /api/v2/user/*int:user_id*/following/  
Method: **GET**  
Status: **200**

## Check one's posts

URL: /api/v2/user/*int:user_id*/posts/  
Method: **GET**  
Status: **200**  
Example:

```json
[
  {
    "author": {
      "id": 21,
      "kind": "User",
      "last_seen": "Sat, 20 Mar 2021 10:30:06 GMT",
      "member_since": "Sat, 20 Mar 2021 10:30:06 GMT",
      "name": "Gregory Simmons",
      "url": "http://localhost:5000/api/v2/user/21/",
      "username": "gregorysimmons"
    },
    "comments": [
      {
        "author": "randyfitzgeraldmd",
        "body": "Brother wrong candidate bill car present. Cut trouble tough technology course technology. State seat bag structure read high."
      },
      {
        "author": "johnlee",
        "body": "Fear politics even couple. Democrat wide deal him debate. Mrs every accept light.\nMember property stand very seven. Set per call happy war so body meet."
      }
    ],
    "comments_count": 2,
    "content": "Both establish need upon. Cup every long kid call. Idea truth such. Particular call four arm sea.\nSuch again high professor road. Power body other. Suddenly near exactly.",
    "id": 19,
    "kind": "Post",
    "private": false,
    "title": "job eight",
    "url": "http://localhost:5000/api/v2/post/19/"
  }
]
```

## Check one's comments

URL: /api/v2/user/*int:user_id*/comments/  
Method: **GET**  
Status: **200**  
Example:

```json
[
  {
    "author": {
      "id": 19,
      "kind": "User",
      "last_seen": "Sat, 20 Mar 2021 10:50:40 GMT",
      "member_since": "Sat, 20 Mar 2021 10:50:40 GMT",
      "name": "Brandy Christian",
      "url": "http://localhost:5000/api/v2/user/19/",
      "username": "brandychristian"
    },
    "body": "Ball discover administration. Human ready fear with effect unit. Week evidence early common new front everybody.\nJoin test sister under bank. Administration writer media season PM.",
    "id": 19,
    "kind": "Comment",
    "post": {
      "author": {
        "id": 15,
        "kind": "User",
        "last_seen": "Sat, 20 Mar 2021 10:50:39 GMT",
        "member_since": "Sat, 20 Mar 2021 10:50:39 GMT",
        "name": "Hailey Rodriguez",
        "url": "http://localhost:5000/api/v2/user/15/",
        "username": "haileyrodriguez"
      },
      "comments_count": 2,
      "content": "Although accept poor indicate. Test only kid cover modern. Guess travel anything down task total.\nStep address create. Traditional data record wish want care whatever. Quickly true probably major thus.\nWhich medical expert sure. Foreign receive last pass. Phone PM suddenly itself.",
      "id": 8,
      "kind": "Post",
      "private": true,
      "title": "sound front",
      "url": "http://localhost:5000/api/v2/post/8/"
    },
    "url": "http://localhost:5000/api/v2/comment/19/"
  }
]
```
