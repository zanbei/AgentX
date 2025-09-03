from .doc_convert import mcp


def main() -> None:
    mcp.run(transport="http", host="0.0.0.0", port=6000)


if __name__ == "__main__":
    main()
