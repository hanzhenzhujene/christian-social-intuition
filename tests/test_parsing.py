from christian_social_intuition.parsing import parse_explanation_text, parse_judgment_text


def test_parse_judgment_json():
    act, heart = parse_judgment_text('{"overall_problematic":"B","heart_worse":"A"}')
    assert act == "B"
    assert heart == "A"


def test_parse_judgment_fallback_letters():
    act, heart = parse_judgment_text("Overall: A\nHeart: B")
    assert act == "A"
    assert heart == "B"


def test_parse_judgment_option_prefix():
    act, heart = parse_judgment_text('{"overall_problematic":"Option A","heart_worse":"Option B"}')
    assert act == "A"
    assert heart == "B"


def test_parse_explanation_json():
    focus, text = parse_explanation_text(
        '{"focus":"motive/heart","text":"Option A reveals a colder motive even though both options try to solve the same problem."}'
    )
    assert focus == "motive/heart"
    assert text.startswith("Option A")


def test_parse_explanation_alias():
    focus, text = parse_explanation_text("Focus: consequence\nOption B causes more avoidable harm to other people.")
    assert focus == "consequences/harm"
    assert "harm" in text


def test_parse_explanation_heart_worse_alias():
    focus, text = parse_explanation_text(
        '{"focus":"heart_worse","text":"Option A reflects the worse motive and a more selfish character."}'
    )
    assert focus == "motive/heart"
    assert "selfish" in text


def test_parse_explanation_with_judgment_json_prefix():
    focus, text = parse_explanation_text(
        '{"overall_problematic":"B","heart_worse":"A"} Andy shows a selfish heart and the worse underlying motive.'
    )
    assert focus == "motive/heart"
    assert "selfish heart" in text
