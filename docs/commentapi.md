# Comment Doc

The document for comment web api.

- /api/v1/comment/*int:comment_id*/
  - **GET** Returns a comment schema  
    Status: 200  
    Example Return Value:
    ``` json
    {
      "author": {
        "id": 11,
        "kind": "User",
        "last_seen": "Sun, 08 Nov 2020 02:04:42 GMT",
        "member_since": "Sun, 08 Nov 2020 02:04:42 GMT",
        "name": "Charles Gutierrez",
        "url": "http://example.com/api/v1/user/11/",
        "username": "charles-gutierrez"
      },
      "body": "They pattern image yard. Remember sort star call paper. Character imagine yeahminute.\nAgain participant official grow collection. Value positive explain.",
      "post": {
        "comments": [
          {
            "author": "charles-gutierrez",
            "body": "They pattern image yard. Remember sort star call paper. Character imagine yeah minute.\nAgain participant official grow collection. Value positive explain."
          },
          {
            "author": "stephen-james",
            "body": "Fall from hard six general one. Effect enough these clearly. Position measure model reality else if. Window hour those store."
          }
        ],
        "comments_count": 3,
        "content": "Ok body unit past. Cover general reach build source actually husband.",
        "id": 11,
        "slug": "eight-simple",
        "title": "eight simple",
        "url": "http://example.com/api/v1/post/11/"
      }
    }
    ```
  - **DELETE** Deletes a comment  
    Status: 204  

- /api/v1/comment/new/
  - **POST** Creates a comment from input json  
    Accept: *application/json*  
    Status: *201*  
    Example:
    ```json
    {
      "body": "The body of the comment",
      "post_id": 1
    }
    ```
