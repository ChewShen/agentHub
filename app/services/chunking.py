"""Chunking service.

Responsibilities:
- Split extracted document text into manageable chunks.
"""

import logging

logger = logging.getLogger(__name__)

CHUNK_SIZE_CHARS = 2000
CHUNK_OVERLAP_CHARS = 200


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    """Split text into chunks with overlap, snapping to natural boundaries.
    
    Attempts to break chunks at paragraph (\n\n) or sentence (. ) boundaries.
    If no natural boundary is found near the end of the chunk size, falls back
    to word boundaries (space), and finally a hard character split.
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        
        if end >= text_length:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break
            
        # Search for a natural boundary in the last part of the chunk
        # Look backwards from 'end' to try to find a boundary
        search_start = start
        
        break_point = text.rfind("\n\n", search_start, end)
        boundary_len = 2
        add_char = ""
        
        if break_point == -1:
            break_point = text.rfind(". ", search_start, end)
            add_char = "." if break_point != -1 else ""
            
        if break_point == -1:
            break_point = text.rfind(" ", search_start, end)
            boundary_len = 1
            add_char = ""
            
        if break_point != -1 and break_point > start:
            # Natural boundary found
            chunk = text[start:break_point].strip() + add_char
            next_start = break_point + boundary_len
        else:
            # Hard character split fallback
            chunk = text[start:end].strip()
            next_start = end
            
        if chunk:
            chunks.append(chunk)
            
        # Move start forward for the next chunk, accounting for overlap
        # Overlap is applied backwards from the next_start point
        # To prevent infinite loops, we must always advance by at least 1 character
        start = max(start + 1, next_start - overlap)
        
    return chunks
