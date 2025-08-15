import logging
import os

def setup_logger(name, log_file, level=logging.DEBUG):
    """Create a logger that writes DEBUG+ messages to a file."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # File handler
    fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    fh.setLevel(level)
    
    # Formatter
    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    
    # Attach handler
    logger.addHandler(fh)
    return logger

if __name__ == "__main__":
    log_path = "logs/app.log"
    log = setup_logger(__name__, log_path)
    
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("A warning occurred")
    log.error("An error happened", exc_info=True)
    log.critical("Critical issue!")
