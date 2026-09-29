from urllib.parse import urlparse
import math
import re

import tldextract


SUSPICIOUS_KEYWORDS = [
    "login",
    "verify",
    "account",
    "secure",
    "update",
    "payment",
]


def calculate_entropy(value: str) -> float:
    """Calculate Shannon entropy of a string."""

    if not value:
        return 0.0

    frequencies = {}

    for char in value:
        frequencies[char] = frequencies.get(char, 0) + 1

    length = len(value)

    entropy = 0.0

    for count in frequencies.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy


def extract_features(url: str) -> dict:
    """Extract lexical and structural features from a URL."""

    parsed = urlparse(url)

    domain = parsed.netloc.split(":")[0]
    path = parsed.path
    query = parsed.query

    hostname = domain.lower()

    # ---------------------------------------------------------
    # Public Suffix List domain parsing
    # ---------------------------------------------------------

    extracted = tldextract.extract(hostname)

    subdomain = extracted.subdomain

    # Use the current tldextract API
    registered_domain = (
        extracted.top_domain_under_public_suffix
    )

    public_suffix = extracted.suffix

    subdomain_parts = (
        subdomain.split(".")
        if subdomain
        else []
    )

    num_subdomains = len(subdomain_parts)

    # ---------------------------------------------------------
    # Basic URL statistics
    # ---------------------------------------------------------

    url_length = len(url)
    domain_length = len(domain)
    path_length = len(path)
    query_length = len(query)

    num_letters = sum(
        char.isalpha()
        for char in url
    )

    num_digits = sum(
        char.isdigit()
        for char in url
    )

    special_characters = set(
        "!@#$%^&*()_+=[]{}|;:'\",<>?/~`"
    )

    num_special_chars = sum(
        char in special_characters
        for char in url
    )

    num_dots = url.count(".")
    num_hyphens = url.count("-")

    # ---------------------------------------------------------
    # URL security indicators
    # ---------------------------------------------------------

    has_ip = int(
        bool(
            re.fullmatch(
                r"(?:\d{1,3}\.){3}\d{1,3}",
                domain,
            )
        )
    )

    has_https = int(
        parsed.scheme.lower() == "https"
    )

    has_at_symbol = int(
        "@" in url
    )

    has_double_slash = int(
        "//" in path
    )

    has_url_encoding = int(
        bool(
            re.search(
                r"%[0-9a-fA-F]{2}",
                url,
            )
        )
    )

    # ---------------------------------------------------------
    # Ratios
    # ---------------------------------------------------------

    digit_ratio = (
        num_digits / url_length
        if url_length
        else 0.0
    )

    letter_ratio = (
        num_letters / url_length
        if url_length
        else 0.0
    )

    special_char_ratio = (
        num_special_chars / url_length
        if url_length
        else 0.0
    )

    # ---------------------------------------------------------
    # Overall domain characteristics
    # ---------------------------------------------------------

    domain_entropy = calculate_entropy(
        domain
    )

    registered_domain_length = len(
        registered_domain
    )

    subdomain_length = len(
        subdomain
    )

    public_suffix_length = len(
        public_suffix
    )

    has_many_subdomains = int(
        num_subdomains >= 3
    )

    has_long_subdomain = int(
        subdomain_length >= 20
    )

    has_numeric_domain = int(
        bool(
            re.search(
                r"\d",
                domain,
            )
        )
    )

    # ---------------------------------------------------------
    # Registered-domain-specific characteristics
    # ---------------------------------------------------------

    registered_domain_digits = sum(
        char.isdigit()
        for char in registered_domain
    )

    registered_domain_letters = sum(
        char.isalpha()
        for char in registered_domain
    )

    registered_domain_hyphens = (
        registered_domain.count("-")
    )

    registered_domain_entropy = (
        calculate_entropy(
            registered_domain
        )
    )

    registered_domain_digit_ratio = (
        registered_domain_digits
        / len(registered_domain)
        if registered_domain
        else 0.0
    )

    registered_domain_hyphen_ratio = (
        registered_domain_hyphens
        / len(registered_domain)
        if registered_domain
        else 0.0
    )

    # ---------------------------------------------------------
    # Suspicious keyword features
    # ---------------------------------------------------------

    url_lower = url.lower()

    keyword_features = {
        f"has_{keyword}": int(
            keyword in url_lower
        )
        for keyword in SUSPICIOUS_KEYWORDS
    }

    # ---------------------------------------------------------
    # Final feature dictionary
    # ---------------------------------------------------------

    features = {
        "url_length": url_length,
        "domain_length": domain_length,
        "path_length": path_length,
        "query_length": query_length,
        "num_subdomains": num_subdomains,
        "num_dots": num_dots,
        "num_hyphens": num_hyphens,
        "num_digits": num_digits,
        "num_letters": num_letters,
        "num_special_chars": num_special_chars,

        "has_ip": has_ip,
        "has_https": has_https,
        "has_at_symbol": has_at_symbol,
        "has_double_slash": has_double_slash,
        "has_url_encoding": has_url_encoding,

        "digit_ratio": digit_ratio,
        "letter_ratio": letter_ratio,
        "special_char_ratio": special_char_ratio,

        "domain_entropy": domain_entropy,

        "registered_domain_length":
            registered_domain_length,

        "subdomain_length":
            subdomain_length,

        "public_suffix_length":
            public_suffix_length,

        "has_many_subdomains":
            has_many_subdomains,

        "has_long_subdomain":
            has_long_subdomain,

        "has_numeric_domain":
            has_numeric_domain,

        "registered_domain_entropy":
            registered_domain_entropy,

        "registered_domain_digits":
            registered_domain_digits,

        "registered_domain_letters":
            registered_domain_letters,

        "registered_domain_hyphens":
            registered_domain_hyphens,

        "registered_domain_digit_ratio":
            registered_domain_digit_ratio,

        "registered_domain_hyphen_ratio":
            registered_domain_hyphen_ratio,
    }

    features.update(keyword_features)

    return features


if __name__ == "__main__":

    test_urls = [
        "https://drive.google.com/",
        "https://drive.google.com.evil-site.com/login",
        "https://coxgo.weebly.com/",
        "https://sanef.termot.top/",
        "https://example.co.uk",
    ]

    for test_url in test_urls:

        print("\n" + "=" * 60)

        print("URL:")
        print(test_url)

        extracted = tldextract.extract(
            urlparse(test_url).netloc.split(":")[0]
        )

        print("\nDomain Information:")

        print(
            f"Subdomain         : "
            f"{extracted.subdomain}"
        )

        print(
            f"Registered domain : "
            f"{extracted.top_domain_under_public_suffix}"
        )

        print(
            f"Public suffix     : "
            f"{extracted.suffix}"
        )

        print("\nExtracted Features:")

        features = extract_features(
            test_url
        )

        for name, value in features.items():
            print(
                f"{name:35} : {value}"
            )