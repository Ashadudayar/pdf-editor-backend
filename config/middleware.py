class DisableXFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Remove X-Frame-Options for media files
        if request.path.startswith('/media/'):
            response.headers.pop('X-Frame-Options', None)
        
        return response