from christian_social_intuition.build_items import build_candidate_items, rebalance_option_order


def test_build_candidate_items_cleans_quoted_and_dirty_text():
    records = [
        {
            "ID": "demo-1",
            "norm": "It's wrong to grab people.",
            "situation": "Auston is at a party when he notices a guest, Bill, has a wasp on his shoulder.",
            "intention": "Auston wants to get Bill's attention so he can warn him.",
            'moral_action': '"Auston leans in and loudly says ""excuse me sir"" in the direction of Bill."',
            "moral_consequence": "Bill notices the wasp and appreciates the warning.",
            "immoral_action": "Auston grab's Bill's arm to make him stop talking.",
            "immoral_consequence": "Bill gets upset and then gets stung by the wasp.",
        }
    ]

    items = build_candidate_items(records, seed=1)
    assert len(items) == 1
    item = items[0]
    assert item.option_a.count('""') == 0
    assert 'grab\'s' not in item.option_a + item.option_b
    assert '"excuse me sir"' in item.option_a + item.option_b


def test_rebalance_option_order_balances_within_tag():
    records = []
    for idx in range(4):
        records.append(
            {
                "ID": f"demo-{idx}",
                "norm": "It's good to be kind.",
                "situation": f"Person {idx} is deciding what to do in an everyday situation.",
                "intention": "The person wants to have fun with friends.",
                "moral_action": "They speak kindly to the group.",
                "moral_consequence": "Everyone feels respected.",
                "immoral_action": "They insult the group.",
                "immoral_consequence": "Everyone feels hurt.",
            }
        )

    items = build_candidate_items(records, seed=1)
    for item in items:
        if item.moral_option == "B":
            item.option_a, item.option_b = item.option_b, item.option_a
            item.option_a_alignment, item.option_b_alignment = item.option_b_alignment, item.option_a_alignment
            item.moral_option = "A"
        item.primary_tension_tag = "motive_vs_outcome"

    rebalance_option_order(items, seed=1)
    assert sum(item.moral_option == "A" for item in items) == 2
