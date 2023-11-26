"""Module for the main entrypoint to the application."""


from .app import app

__all__ = ["main"]


def main() -> None:
    """Main function entrypoint for the application"""
    app.run(host='0.0.0.0', port=8000, debug=True)


if __name__ == "__main__":
    main()
