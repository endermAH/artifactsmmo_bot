class Log:

    @staticmethod
    def info(message):
        print(f"\x1b[34;20m[INFO]\x1b[0m: {message}")
    
    @staticmethod
    def error(message):
        print(f"\x1b[31;20m[ERROR]\x1b[0m: {message}")

    @staticmethod
    def debug(message):
        print(f"[DEBUG]: {message}")