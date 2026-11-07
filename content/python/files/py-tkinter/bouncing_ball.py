# 6.4 Desktop windows with tkinter
# Window program "bouncing_ball" from the lesson. It opens a window, so run it on your own computer.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import tkinter as tk

WIDTH = 400
HEIGHT = 250
SIZE = 30

root = tk.Tk()
root.title("Bouncing ball")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

canvas.create_rectangle(10, 10, 130, 40, fill="#dbeafe", outline="#2563eb")
canvas.create_text(70, 25, text="Space: pause")
canvas.create_line(0, HEIGHT - 20, WIDTH, HEIGHT - 20, fill="gray", dash=(4, 2))
ball = canvas.create_oval(50, 50, 50 + SIZE, 50 + SIZE, fill="orange")

dx = 4
dy = 3
running = True


def move():
    global dx, dy
    if running:
        canvas.move(ball, dx, dy)
        x1, y1, x2, y2 = canvas.coords(ball)
        if x1 <= 0 or x2 >= WIDTH:
            dx = -dx
        if y1 <= 0 or y2 >= HEIGHT - 20:
            dy = -dy
    root.after(20, move)                 # call move again in 20 ms, about 50 times a second


def toggle(event):
    global running
    running = not running


def jump(event):
    canvas.coords(ball, event.x, event.y, event.x + SIZE, event.y + SIZE)


root.bind("<space>", toggle)
canvas.bind("<Button-1>", jump)
move()
root.mainloop()
