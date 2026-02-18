def calculate_efficiency(completed, total):
    """Return progress percentage safely."""
    if total == 0:
        return 0
    return round((completed / total) * 100, 2)
