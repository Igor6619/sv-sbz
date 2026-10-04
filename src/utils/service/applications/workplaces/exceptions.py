
class WorkplacesBadRequestsEroor(Exception):
    def __init__(self, url: str, **kwarks):
        super().__init__(f"Error request to {url}", kwarks)