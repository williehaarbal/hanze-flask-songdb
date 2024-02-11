country_icon_list = {
    'Netherlands': 'nl',
    'Germany': 'de',
    'United Kingdom': 'gb',
    'Sweden': 'se',
    'Poland': 'pl',
    'Belgium': 'be',
    'USA': 'us',
    'France': 'fr',
    'Other': None
}

class p_err():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


    msg = None
    def __init__(self, msg) -> None:
        self.msg = f"{self.FAIL}{msg}{self.END}"
        print(self.msg)

    def __repr__(self) -> str:
        return self.msg

class p_note():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    CYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


    msg = None
    def __init__(self, msg) -> None:
        self.msg = f"{self.CYAN}{msg}{self.END}"
        print(self.msg)

    def __repr__(self) -> str:
        return self.msg
