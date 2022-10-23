from typing import Any, Callable, Dict, List


class EventClass:
    def __init__(self, *, wildcard: bool = False):
        self.wildcard = wildcard
        self.events: Dict[str, Callable] = {}  # Event mapping

    def on(self, event: str, function: Callable) -> None:
        self.events[event] = function

    def emit_res(self, event: str, **kwargs) -> List[Any]:
        functions = self.find_in_events(event)
        results: List[Any] = []

        for function in functions:
            result = function(**kwargs)  # Call the function
            results.append(result)

        return results

    def emit(self, event: str, **kwargs) -> None:
        functions = self.find_in_events(event)

        for function in functions:
            function(**kwargs)  # Call the function

    def find_in_events(self, string: str) -> List[Callable]:
        matches: List[Callable] = []
        for key in self.events.keys():
            if (self.wildcard is True and string in key) or string == key:
                function = self.events[key]
                matches.append(function)
        return matches


