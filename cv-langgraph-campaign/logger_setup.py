import logging, os

def setup_logger(name, log_file, level=logging.DEBUG):
    """Create a logger that writes DEBUG+ messages to a file,
    and also prints colored output to the console."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # — FILE HANDLER (no color) —
    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fh.setLevel(level)
    file_fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(file_fmt)
    logger.addHandler(fh)

    # — CONSOLE HANDLER (with color) —
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # \033[32m = green; \033[0m = reset
    color_fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] \033[32m%(filename)s\033[0m: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(color_fmt)
    logger.addHandler(ch)

    return logger

if __name__ == "__main__":
    LOG_PATH = "logs/app.log"
    log = setup_logger(__name__, LOG_PATH)
    log.debug("Debug message")
    log.info("Info message")
    log.error("Error message")
