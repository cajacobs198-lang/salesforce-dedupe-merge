from sfdedupe.normalize import norm_name, norm_domain


def test_norm_name_strips_suffixes_and_punctuation():
    assert norm_name("Acme, Inc.") == norm_name("ACME Inc")
    assert norm_name("Stripe Payments Europe Ltd") == "stripe payments europe"


def test_norm_domain():
    assert norm_domain("www.Stripe.COM") == "stripe.com"
    assert norm_domain("") == ""
