import logging
import sys
print(sys.path)
from src.scan import scanner
from src.cloud import mail

logger = logging.getLogger('src.main')

if __name__ == "__main__":
    # Start the scanner.
    logger.info('Starting followed fiction thread scanner...')
    # Load follow list
    f = scanner.load_follow_list()
    if f is not None:
        # Load history
        h = scanner.History(scanner.load_history())
        # Scanner object
        s = scanner.Scanner()
        # Execute scan and get notifications in return
        n = s.scan(f, h)
        if len(n) != 0:
            # have something to notify
            mail.send_notification(n)
        # write history to file
        scanner.write_history(h.get_history())
    logger.info('Scanning process ended.')
