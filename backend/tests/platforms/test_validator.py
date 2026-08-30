from app.platforms.validator import count_chars, is_within_limit, truncate_to_limit


def test_count_chars_caption_and_hashtags():
    assert count_chars("hello", ["#a", "#b"]) == len("hello") + len("#a #b") + 1


def test_count_chars_no_hashtags():
    assert count_chars("hello", []) == 5


def test_is_within_limit_true():
    assert is_within_limit("short caption", ["#tag"], 280) is True


def test_is_within_limit_false():
    long_caption = "x" * 300
    assert is_within_limit(long_caption, [], 280) is False


def test_truncate_to_limit_cuts_at_word_boundary():
    result = truncate_to_limit("one two three four five", 15)
    assert result == "one two three"
    assert len(result) <= 15
