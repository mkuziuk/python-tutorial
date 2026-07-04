import sys

MIN_VERSION = (3, 14)


def main() -> None:
    current = sys.version_info
    current_label = f"{current.major}.{current.minor}.{current.micro}"
    required_label = ".".join(map(str, MIN_VERSION))

    if current < MIN_VERSION:
        raise SystemExit(
            f"Python {required_label}+ is required for this tutorial; found {current_label}."
        )

    print(f"Python {current_label} OK")


if __name__ == "__main__":
    main()
