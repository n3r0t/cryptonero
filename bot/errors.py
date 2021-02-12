class InvalidCoinID(Exception):
    """
    Exception raised when search query requested by user doesn't return a coin.
    """
    def __init__(self, reason: str = "Specified coin by user is invalid."):
        self.reason = reason

        super(InvalidCoinID, self).__init__(reason)