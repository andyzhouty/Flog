# UserAPI Doc
## URL Routing:
- /api/v1/user/\<int:user_id>:  
    - METHODS:

        - GET: Returns user schema (json):
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

        The return value should look like this:
        ```json
        {
            "id": 2,
            "kind": "User",
            "last_seen": "Fri, 30 Oct 2020 12:36:07 GMT",
            "location": "Shanghai, China",
            "member_since": "Fri, 30 Oct 2020 12:36:07 GMT",
            "name": "Kent Reyes",
            "url": "http://example.com/api/v1/user/2/",
            "username": "kent-reyes"
        }
        ```

        - PUT: Updates user profile (only json is accepted)

            Arguments(optional):
            - username : str
            - name: str
            - location: str
            - about_me: str
