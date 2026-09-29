from src.features.url_features import extract_features
from src.features.signals import generate_signals


test_urls = [
    "https://www.google.com",
    "https://drive.google.com.evil-site.com/login",
    "http://192.168.1.10/login.php?user=admin&password=123",
]


for url in test_urls:
    print("\n" + "=" * 70)
    print(f"URL: {url}")
    print("=" * 70)

    features = extract_features(url)
    signals = generate_signals(features)

    if not signals:
        print("No suspicious signals detected.")
    else:
        for signal in signals:
            print(
                f"[{signal['type'].upper()}] "
                f"{signal['title']}"
            )
            print(f"  {signal['description']}")