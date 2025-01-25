import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class LaTeXEditor:
    def __init__(self, root):
        self.root = root
        self.root.title('LaTeX Editor')
        self.root.geometry('600x400')

        # 创建一个 Text 小部件用于输入 LaTeX 表达式
        self.latex_input = tk.Text(self.root, height=5, width=60, font=('Arial', 14))
        self.latex_input.pack(pady=10)
        self.latex_input.bind('<KeyRelease>', self.update_latex)

        # 创建一个 Figure 和 Axes 用于显示 LaTeX 表达式
        self.fig, self.ax = plt.subplots()
        self.ax.axis('off')  # 关闭坐标轴
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(pady=10)

        # 初始化显示
        self.update_latex()

        # 初始化指针位置
        self.pointer_x, self.pointer_y = 0.5, 0.5

        # 绑定键盘事件
        # self.root.bind('<Up>', self.move_up)
        # self.root.bind('<Down>', self.move_down)
        # self.root.bind('<Left>', self.move_left)
        # self.root.bind('<Right>', self.move_right)

    def update_latex(self, event=None):
        # 清除之前的绘图
        self.ax.clear()
        self.ax.axis('off')

        # 获取输入框中的 LaTeX 表达式
        latex_expr = self.latex_input.get("1.0", tk.END).strip()

        try:
            # 渲染 LaTeX 表达式
            self.annotation = self.ax.text(self.pointer_x, self.pointer_y, f"${latex_expr}$", fontsize=20, ha='center', va='center')
            self.fig.canvas.draw()
        except Exception as e:
            print(f"Error rendering LaTeX: {e}")

    def move_up(self, event):
        self.pointer_y += 0.05
        self.update_latex()

    def move_down(self, event):
        self.pointer_y -= 0.05
        self.update_latex()

    def move_left(self, event):
        self.pointer_x -= 0.05
        self.update_latex()

    def move_right(self, event):
        self.pointer_x += 0.05
        self.update_latex()

if __name__ == "__main__":
    root = tk.Tk()
    editor = LaTeXEditor(root)
    root.mainloop()