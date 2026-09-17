def season_codes ( start_year = 1993, end_year = 2026):
    """1993 -> '9394', 2026 -> '2627'. end_year is the START year of the last season."""
    codes = []
    for y in range(start_year,end_year + 1):
        yy = y % 100
        nn =  (y+1)%100
        codes.append(f"{yy:02d}{nn:02d}")
    return codes


if __name__ == "__main__":
    codes = season_codes()
    print(f"{len(codes)} seasons")
    print(codes[:3], "...", codes[-3:])
