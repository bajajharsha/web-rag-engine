from typing import Any, Dict, List

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


class ChunkingUsecase:
    """
    Usecase for chunking markdown content
    Two-stage approach:
    1. Split by markdown headers (preserves structure)
    2. Split large sections recursively (ensures size limits)
    """

    def __init__(self):
        # Stage 1: Markdown header splitter
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False,  # Keep headers in chunks
        )

        # Stage 2: Recursive character splitter
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Max characters per chunk
            chunk_overlap=200,  # Overlap for context continuity
            length_function=len,
            separators=["\n\n", "\n", " ", ""],  # Try these separators in order
        )

    async def chunk_markdown(
        self, markdown_content: str, url: str, job_id: str
    ) -> List[Dict[str, Any]]:
        try:
            print(f"📄 Starting chunking for {len(markdown_content)} characters")

            # Stage 1: Split by markdown headers
            md_header_splits = self.markdown_splitter.split_text(markdown_content)
            print(f"Stage 1: Split into {len(md_header_splits)} header-based sections")
            print(
                f"DEBUG: Type of first split: {type(md_header_splits[0]) if md_header_splits else 'empty'}"
            )

            # Stage 2: Further split large sections
            final_chunks = []
            for i, doc in enumerate(md_header_splits):
                # Extract content and metadata from Document object
                page_content = (
                    doc.page_content if hasattr(doc, "page_content") else str(doc)
                )
                doc_metadata = doc.metadata if hasattr(doc, "metadata") else {}

                # Convert metadata to plain dict (remove any Document objects)
                clean_metadata = {}
                for key, value in doc_metadata.items():
                    if hasattr(value, "__dict__"):
                        # Skip complex objects
                        clean_metadata[key] = str(value)
                    else:
                        clean_metadata[key] = value

                # If section is too large, split it further
                if len(page_content) > self.recursive_splitter._chunk_size:
                    sub_chunks = self.recursive_splitter.split_text(page_content)
                    for j, sub_chunk in enumerate(sub_chunks):
                        final_chunks.append(
                            {
                                "content": sub_chunk,
                                "metadata": {
                                    **clean_metadata,  # Use cleaned metadata
                                    "url": url,
                                    "job_id": job_id,
                                    "chunk_index": len(final_chunks),
                                    "section_index": i,
                                    "sub_chunk_index": j,
                                    "chunk_size": len(sub_chunk),
                                },
                            }
                        )
                else:
                    # Section is small enough, keep as is
                    final_chunks.append(
                        {
                            "content": page_content,
                            "metadata": {
                                **clean_metadata,  # Use cleaned metadata
                                "url": url,
                                "job_id": job_id,
                                "chunk_index": len(final_chunks),
                                "section_index": i,
                                "chunk_size": len(page_content),
                            },
                        }
                    )

            print(f"✅ Stage 2: Final chunks created: {len(final_chunks)}")
            print(
                f"📊 Average chunk size: {sum(c['metadata']['chunk_size'] for c in final_chunks) // len(final_chunks)} characters"
            )

            return final_chunks

        except Exception as e:
            print(f"❌ Error chunking markdown: {str(e)}")
            # Fallback: Simple chunking if markdown splitting fails
            return await self._fallback_chunking(markdown_content, url, job_id)

    async def _fallback_chunking(
        self, content: str, url: str, job_id: str
    ) -> List[Dict[str, Any]]:
        """
        Fallback chunking strategy if markdown splitting fails
        Uses only recursive character splitter
        """
        print("⚠️ Using fallback chunking strategy")
        try:
            chunks = self.recursive_splitter.split_text(content)
            return [
                {
                    "content": chunk,
                    "metadata": {
                        "url": url,
                        "job_id": job_id,
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "fallback": True,
                    },
                }
                for i, chunk in enumerate(chunks)
            ]
        except Exception as e:
            print(f"❌ Fallback chunking also failed: {str(e)}")
            return []
