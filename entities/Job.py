class Job:
    def __init__(self, title: str, description: str) -> None:
        self.title: str = title
        self.description: str = description
        # TODO: self.effect: Effect = effect