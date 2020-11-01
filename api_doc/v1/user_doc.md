# User Doc
## URL Routing:
- /api/v1/user/\<int:id>:  
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

        - PUT: Updates user profile (only json is accepted)

            Arguments(optional):
            - username : str
            - name: str
            - location: str
            - about_me: str
