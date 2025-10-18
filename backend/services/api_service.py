import httpx
from fastapi import HTTPException, status


class ApiService:
    def __init__(self) -> None:
        self.timeout = httpx.Timeout(
            connect=120,  # Time to establish a connection
            read=240,  # Time to read the response
            write=124020,  # Time to send data
            pool=120,  # Time to wait for a connection from the pool
        )

    async def get(
        self, url: str, headers: dict = None, data: dict = None
    ) -> httpx.Response:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=data)
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError:
                    return response.text
        except httpx.RequestError as exc:
            error_msg = f"An error occurred while requesting {exc.request.url!r}."
            raise HTTPException(status_code=500, detail=error_msg)
        except httpx.HTTPStatusError as exc:
            error_msg = f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
            raise HTTPException(status_code=exc.response.status_code, detail=error_msg)

    async def post(
        self,
        url: str,
        headers: dict = None,
        data: dict = None,
        files: dict = None,
    ) -> httpx.Response:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                if files:
                    response = await client.post(
                        url, headers=headers, data=data, files=files
                    )
                else:
                    response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            error_msg = f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
            raise HTTPException(status_code=exc.response.status_code, detail=error_msg)
        except httpx.RequestError as exc:
            error_msg = f"Request error while accessing {exc.request.url!r}: {str(exc)}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg,
            )
        except Exception as exc:
            error_msg = f"Unexpected error in post: {str(exc)}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg
            )

    # async def post_stream(
    #     self,
    #     url: str,
    #     headers: dict = None,
    #     data: dict = None,
    # ):
    #     client = None
    #     try:
    #         client = httpx.AsyncClient(timeout=self.timeout, verify=False)

    #         # Make the request with stream=True
    #         request = client.build_request("POST", url, headers=headers, json=data)
    #         response = await client.send(request, stream=True)
    #         response.raise_for_status()

    #         # Stream the response content
    #         buffer = ""
    #         async for chunk in response.aiter_bytes():
    #             if chunk:
    #                 # Decode bytes to string
    #                 text = chunk.decode("utf-8", errors="ignore")
    #                 buffer += text
    #                 # Split by double newlines to get complete SSE events
    #                 while "\n\n" in buffer:
    #                     event, buffer = buffer.split("\n\n", 1)
    #                     if event.strip():
    #                         yield event

    #         # Process any remaining content in buffer
    #         if buffer.strip():
    #             yield buffer

    #     except httpx.HTTPStatusError as exc:
    #         # Close the response if it exists
    #         if "response" in locals():
    #             await response.aclose()
    #         # Don't try to access response.text on streaming responses
    #         await self.error_repo.log_error(
    #             error=exc,
    #             additional_context={
    #                 "file": "api_service.py",
    #                 "method": "POST_STREAM",
    #                 "url": url,
    #                 "status_code": exc.response.status_code,
    #                 "operation": "api_service.post_stream",
    #             },
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Streaming API request failed with error: {str(exc)}",
    #         )
    #     except httpx.RequestError as exc:
    #         # Close the response if it exists
    #         if "response" in locals():
    #             await response.aclose()
    #         await self.error_repo.log_error(
    #             error=exc,
    #             additional_context={
    #                 "file": "api_service.py",
    #                 "method": "POST_STREAM",
    #                 "url": url,
    #                 "operation": "api_service.post_stream",
    #             },
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Streaming API request failed with error: {str(exc)}",
    #         )
    #     except Exception as exc:
    #         # Close the response if it exists
    #         if "response" in locals():
    #             await response.aclose()
    #         await self.error_repo.log_error(
    #             error=exc,
    #             additional_context={
    #                 "file": "api_service.py",
    #                 "method": "POST_STREAM",
    #                 "url": url,
    #                 "operation": "api_service.post_stream",
    #             },
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Streaming API request failed with error: {str(exc)}",
    #         )
    #     finally:
    #         # Always close the client
    #         if client:
    #             await client.aclose()
