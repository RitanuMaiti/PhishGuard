def generate_signals(features):
    """
    Generate human-readable security signals
    from extracted URL features.
    """

    signals = []

    # URL structure
    if features["url_length"] > 100:
        signals.append({
            "type": "warning",
            "title": "Very long URL",
            "description": "The URL is unusually long and may contain excessive tracking or deceptive path components."
        })

    # IP address
    if features["has_ip"] == 1:
        signals.append({
            "type": "danger",
            "title": "IP address used instead of domain",
            "description": "The URL points directly to an IP address rather than using a normal domain name."
        })

    # HTTPS
    if features["has_https"] == 0:
        signals.append({
            "type": "warning",
            "title": "No HTTPS",
            "description": "The URL does not use HTTPS encryption."
        })

    # @ symbol
    if features["has_at_symbol"] == 1:
        signals.append({
            "type": "danger",
            "title": "Suspicious @ symbol",
            "description": "An @ symbol can be abused to disguise the actual destination of a URL."
        })

    # URL encoding
    if features["has_url_encoding"] == 1:
        signals.append({
            "type": "warning",
            "title": "Encoded characters detected",
            "description": "The URL contains percent-encoded characters."
        })

    # Subdomains
    if features["has_many_subdomains"] == 1:
        signals.append({
            "type": "warning",
            "title": "Multiple subdomains",
            "description": "The URL contains an unusually deep subdomain structure."
        })

    if features["has_long_subdomain"] == 1:
        signals.append({
            "type": "warning",
            "title": "Long subdomain",
            "description": "The subdomain is unusually long."
        })

    # Domain characteristics
    if features["has_numeric_domain"] == 1 and features["has_ip"] == 0:
        signals.append({
            "type": "warning",
            "title": "Numeric-heavy domain",
            "description": "The registered domain contains an unusually high proportion of numeric characters."
        })

    if features["registered_domain_hyphens"] > 0:
        signals.append({
            "type": "warning",
            "title": "Hyphenated domain",
            "description": "The registered domain contains hyphens."
        })

    if features["registered_domain_digit_ratio"] > 0.3:
        signals.append({
            "type": "warning",
            "title": "High digit ratio",
            "description": "A large proportion of the registered domain consists of digits."
        })

    # Entropy
    if features["registered_domain_entropy"] > 3.5:
        signals.append({
            "type": "warning",
            "title": "Unusual domain complexity",
            "description": "The registered domain has a high character entropy."
        })

    # Suspicious keywords
    keyword_checks = [
        (
            "has_login",
            "Login keyword",
            "The URL contains a login-related keyword."
        ),
        (
            "has_verify",
            "Verification keyword",
            "The URL contains a verification-related keyword."
        ),
        (
            "has_account",
            "Account keyword",
            "The URL contains an account-related keyword."
        ),
        (
            "has_secure",
            "Security keyword",
            "The URL contains a security-related keyword."
        ),
        (
            "has_update",
            "Update keyword",
            "The URL contains an update-related keyword."
        ),
        (
            "has_payment",
            "Payment keyword",
            "The URL contains a payment-related keyword."
        ),
    ]

    for feature, title, description in keyword_checks:
        if features[feature] == 1:
            signals.append({
                "type": "warning",
                "title": title,
                "description": description
            })

    return signals