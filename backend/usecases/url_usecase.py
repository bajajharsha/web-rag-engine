# usecase to write the business logic to ingest url
# It will be using services and repositories to implement the business logic


class UrlUsecase:
    def __init__(self):
        pass

    async def ingest_url(self, url: str):
        print(f"URL Usecase: {url}")
        # Step 1: Validate URL
        # TODO: Step 2 - Create job entry in database
        # TODO: Step 3 - Push to Redis queue
        # TODO: Step 4 - Return job ID and status

        return {"message": "URL validation successful"}
