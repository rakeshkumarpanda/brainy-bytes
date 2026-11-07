# 6.4 Desktop windows with tkinter
# Example "event_loop_model" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from collections import deque

# A pretend event queue. A real one is filled by the operating system: clicks, keys, timers, redraws.
events = deque([("click", "button"), ("key", "a"), ("timer", "tick"), ("key", "Return"), ("close", "")])
handlers = {}


def bind(kind, function):
    handlers[kind] = function


def on_click(detail):
    print("clicked the", detail)


def on_key(detail):
    print("key pressed:", detail)


bind("click", on_click)
bind("key", on_key)

while events:                              # this is what mainloop() does, again and again
    kind, detail = events.popleft()
    if kind == "close":
        print("window closed, so mainloop returns")
        break
    handler = handlers.get(kind)
    if handler is None:
        print("no handler for", kind, "so nothing happens")
    else:
        handler(detail)
