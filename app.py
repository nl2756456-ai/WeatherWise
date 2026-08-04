"""
app.py

Application entry point. Validates configuration, sets up logging,
and launches the WeatherWise UI.
"""

import logging
import sys
import tkinter.messagebox as messagebox

import config
from ui import WeatherWiseApp


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger("weatherwise")

    try:
        config.validate_config()
    except RuntimeError as e:
        logger.error(str(e))
        try:
            messagebox.showerror("WeatherWise - Configuration error", str(e))
        except Exception:
            pass
        sys.exit(1)

    app = WeatherWiseApp()
    app.mainloop()


if __name__ == "__main__":
    main()
