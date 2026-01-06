
class TextScreen:
    def __init__(self, title: str, pages: list[str]):
        self.title = title
        self.pages = pages

    def show(self):
        print("\n" + "=" * 40)
        print(self.title.upper())
        print("=" * 40)

        for page in self.pages:
            print("\n" + page)
            input("\n...")
