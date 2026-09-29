def calculate_risk_score(features, model_probability, signals):
    ml_score = model_probability * 70
    signal_score = 0

    if features["has_ip"] == 1:
        signal_score += 10

    if features["has_at_symbol"] == 1:
        signal_score += 10

    if features["has_many_subdomains"] == 1:
        signal_score += 5

    if features["has_long_subdomain"] == 1:
        signal_score += 4

    if features["has_url_encoding"] == 1:
        signal_score += 3

    if features["registered_domain_entropy"] > 3.5:
        signal_score += 4

    suspicious_keywords = (
        features["has_login"]
        + features["has_verify"]
        + features["has_account"]
        + features["has_secure"]
        + features["has_update"]
        + features["has_payment"]
    )

    signal_score += min(
        suspicious_keywords * 3,
        12,
    )

    if features["has_https"] == 0:
        signal_score += 3

    score = ml_score + signal_score
    score = min(max(score, 0), 100)

    if score >= 80:
        level = "HIGH"
    elif score >= 50:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": round(score, 1),
        "level": level,
        "ml_probability": round(model_probability, 4),
        "adjustments": signal_score,
        "signals_count": len(signals),
    }