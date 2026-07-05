"""Tests for chunking service."""

from app.services.chunking import chunk_text

def test_chunk_text_empty():
    assert chunk_text("") == []

def test_chunk_text_short():
    text = "This is a short text."
    chunks = chunk_text(text, chunk_size=2000, overlap=200)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_text_paragraph_boundary():
    # Two paragraphs, each exactly 10 characters.
    # Total length = 10 + 2 (\n\n) + 10 = 22 characters.
    # We set chunk size to 15, so it should split at the paragraph.
    p1 = "1234567890"
    p2 = "abcdefghij"
    text = f"{p1}\n\n{p2}"
    
    # overlap = 2
    chunks = chunk_text(text, chunk_size=15, overlap=2)
    assert len(chunks) == 2
    assert chunks[0] == p1
    # next start is break_point + 2, so p2 starts right away.
    assert chunks[1] == p2

def test_chunk_text_sentence_boundary():
    # Two sentences, each 10 characters (including space)
    p1 = "12345678."
    p2 = "abcdefgh."
    text = f"{p1} {p2}"  # length = 9 + 1 + 9 = 19
    
    chunks = chunk_text(text, chunk_size=15, overlap=2)
    assert len(chunks) == 2
    assert chunks[0] == p1
    # Overlap of 2 means start is pulled back by 2 from the next_start (which was 10)
    # So start becomes 8. text[8:] is ". abcdefgh."
    assert chunks[1] == ". abcdefgh."

def test_chunk_text_hard_split():
    # One long word
    text = "1234567890abcdefghij" # 20 chars
    
    # chunk_size=10, overlap=2
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    # chunk 1: 0 to 10 -> "1234567890"
    # overlap 2 means next starts at 10 - 2 = 8
    # chunk 2: 8 to 18 -> "90abcdefgh"
    # chunk 3: 16 to 20 -> "ghij"
    assert len(chunks) == 3
    assert chunks[0] == "1234567890"
    assert chunks[1] == "90abcdefgh"
    assert chunks[2] == "ghij"
