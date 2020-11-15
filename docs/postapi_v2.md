# Post Doc

- /api/v2/post/*int:id*/
 - **GET** Returns post schema (json):

    Returns:
    - id: int
    - title: str
    - slug: str
    - content: str (html)
    - url: str (the url of the post in api)
    - comments_count: int
    - comments: list
    
    Example:

    ```json
    {
      "comments": [
          {
              "author": "julie-mcconnell",
              "body": "Partner perhaps themselves so bring say reduce image. Quality or election foreign best. Difficult positive leave loss news."
          },
          {
              "author": "kristin-chen",
              "body": "Buy order time might quickly citizen wrong. Charge yard rule main stuff democratic audience.\nFall expect laugh building. Investment marriage way general could book. Feeling order also trade dinner."
          }
      ],
      "comments_count": 2,
      "content": "<p>Have arrive commercial poor under. World include sure protect military there act.</p>",
      "id": 2,
      "slug": "actually-quite",
      "title": "actually quite",
      "url": "http://127.0.0.1:5000/api/v2/post/2/"
    }
    ```
  - **PUT** Updates the post  
    Accepts: *application/json*  
    Status: *204*, *403*, *400*  
    Example:
    ```json
    {
      "title": "new title",
      "content": "<p>New Content</p>",
      "private": true
    }
    ```

  - **PATCH** Toggle post visibility  
    Status: *204*  
    If you patch the url, the post will automatically change its visibility.

  - **DELETE** Deletes the post  
    Status: *204*

- /api/v2/post/new/
  - **POST** Creates a post from post data  
    Accepts: *application/json*  
    Status: *200* or *403*  
    Example post value:
    ```json
    {
      "title": "skill draw",
      "content": "<p>Where else record two. Forget so usually role. Almost company able maintain do process.</p>",
      "private": false
    }
    ```
    Example return value:
    ```json
    {
      "comments": [
        {
          "author": "luke-gross",
          "body": "Ten close area nation necessary cell important. Attorney effort describe environmental. Already new on no price."
        }
      ],
      "comments_count": 1,
      "content": "Where else record two. Forget so usually role. Almost company able maintain do process.",
      "id": 15,
      "slug": "skill-draw",
      "title": "skill draw",
      "url": "http://127.0.0.1:5000/api/v2/post/15/"
    }
    ```
