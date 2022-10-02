class EditorErr(Exception):
    """A nice exception class for debugging."""

    def __init__(self, message):
        # The error (e+m)
        super().__init__("An editor error is occurred." if not message else message)

