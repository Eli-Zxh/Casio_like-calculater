import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import cairo
from math import sqrt
from concurrent.futures import ThreadPoolExecutor
import time
def read_AST(operators:list, times:int = 0):#读取AST，传递参数给各显示函数
    i=0#这个AST设计的好处是，可以直接从左到右读写，从左到右便是显示顺序和计算顺序
    while i < len(operators) - 1:
        part = operators[i]
        if isinstance(part, list):#如果是列表，递归处理
            read_AST(part,times + 1)
            i += 1
            continue
        elif part == r'\frac':
            LatexRenderer.render_frac(operators[i+1],operators[i+2],times)
            i += 3
            continue
        elif part:
            pass
                

class RenderContext:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y  # 基线位置

class FontMetrics:
    def __init__(self):
        self.cache = {}
    
    def get_extents(self, ctx, text):
        if text not in self.cache:
            extents = ctx.text_extents(text)
            self.cache[text] = extents
        return self.cache[text]

font_metrics = FontMetrics()

class LatexRenderer:
    def __init__(self, font_size=12):
        self.style = {
            'font_size': font_size,
            'h_spacing': 5,  # 水平间距
            'v_spacing': 8   # 垂直间距
        }
        self.font_map = [
            ("DejaVu Math TeX Gyre", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
            ("Noto Sans CJK SC", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ]
        self.dirty_nodes = set()  # 记录需要重新布局的节点
        self.debug = False  # 调试模式开关
    
    def _select_font_for_text(self, ctx, text):
        # 检测字符是否需要回退字体（示例逻辑）
        for char in text:
            if ord(char) > 0x2FFF:  # 非拉丁字符范围
                ctx.select_font_face(
                    "Noto Sans CJK SC",
                    cairo.FONT_SLANT_NORMAL,
                    cairo.FONT_WEIGHT_NORMAL
                )
                return
        # 默认数学字体
        ctx.select_font_face(
            "DejaVu Math TeX Gyre",
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL
        )

    def render(self, ast, output_file):
        try:
            layout = self.layout_node(ast)
            surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                int(layout['width']),
                int(layout['height'] + layout['depth'])
            )
            ctx = cairo.Context(surface)
            ctx.set_source_rgb(0, 0, 0)  # 黑色
            ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(self.style['font_size'])
            
            # 初始化渲染上下文（动态指针）
            context = RenderContext(10, layout['baseline'] + 10)  # 留边距
            self.render_node(ctx, layout, context)
            
            surface.write_to_png(output_file)
        except Exception as e:
            print(f"渲染失败: {e}")

    def layout_node(self, node):
        node_hash = str(node)  # 简单哈希，实际应使用更高效的序列化
        if node_hash in self.layout_cache:
            return self.layout_cache[node_hash]
        
        # 计算布局...
        result = self._layout_node(node)
        self.layout_cache[node_hash] = result
        return result
    
    def _layout_node(self, node):
        if isinstance(node, list) and node:
            # 处理命令节点
            if node[0].startswith('\\'):
                cmd = node[0][1:]
                if cmd == 'frac':
                    return self.layout_frac(node[1], node[2])
                elif cmd == 'abs':
                    return self.layout_abs(node[1])
                elif cmd == 'sqrt':
                    return self.layout_sqrt(node[1:])
                # ... 其他命令
            # 处理运算符
            elif node in ('+', '-', '\\times'):
                return self.layout_operator(node)
        # 处理普通文本
        return self.layout_text(str(node))

    def layout_text(self, text):
        # 使用 Cairo 测量文本
        ctx = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0))
        self._select_font_for_text(ctx, text)
        ctx.set_font_size(self.style['font_size'])
        
        # 获取文本的度量信息
        extents = ctx.text_extents(text)
        ascent = ctx.font_extents()[2]  # 基线到顶部的距离
        
        return {
            'type': 'text',
            'width': extents.x_advance,
            'height': ascent,
            'depth': -extents.y_bearing - ascent,  # 深度为基线以下的距离
            'baseline': ascent,
            'content': text
        }

    def layout_operator(self, operator):
        # 假设操作符是单个字符
        return self.layout_text(operator)

    def layout_frac(self, num, den):
        num_layout = self.layout_node(num)
        den_layout = self.layout_node(den)
        line_thickness = 2
        padding = 4
        
        return {
            'type': 'frac',
            'width': max(num_layout['width'], den_layout['width']) + 2*padding,
            'height': num_layout['height'] + line_thickness//2 + padding,
            'depth': den_layout['depth'] + line_thickness//2 + padding,
            'baseline': num_layout['height'] + line_thickness//2 + padding,
            'children': [num_layout, den_layout]
        }

    def layout_abs(self, content):
        content_layout = self.layout_node(content)
        line_width = 3  # 绝对值竖线宽度
        spacing = 4
        
        return {
            'type': 'abs',
            'width': content_layout['width'] + 2*(line_width + spacing),
            'height': content_layout['height'],
            'depth': content_layout['depth'],
            'baseline': content_layout['baseline'],
            'children': [content_layout]
        }

    def layout_sqrt(self, args):
        # 参数可能是 [根指数, 被开方数] 或 [被开方数]
        if len(args) == 1:
            content = args[0]
            index = None
        else:
            index, content = args[0], args[1]
        
        content_layout = self.layout_node(content)
        
        # 计算根号符号的尺寸
        sqrt_height = content_layout['height'] + content_layout['depth']
        sqrt_ascent = 0.6 * sqrt_height  # 根号顶部弯曲部分高度
        
        # 如果有根指数，计算其布局
        index_layout = self.layout_node(index) if index else None
        
        # 总宽度 = 根号宽度 + 内容宽度 + 间距
        width = 15 + content_layout['width'] + 5  # 根号预留宽度
        if index_layout:
            width += index_layout['width'] + 2
        
        # 总高度 = 根号高度 + 内容基线调整
        height = sqrt_ascent + content_layout['height']
        depth = content_layout['depth']
        
        return {
            'type': 'sqrt',
            'width': width,
            'height': height,
            'depth': depth,
            'baseline': content_layout['baseline'] + sqrt_ascent,
            'content': content_layout,
            'index': index_layout
        }

    def render_node(self, ctx, layout, context):
        if self.debug:
            ctx.save()
            ctx.set_source_rgba(1, 0, 0, 0.2)
            ctx.rectangle(
                context.x,
                context.y - layout['height'],
                layout['width'],
                layout['height'] + layout['depth']
            )
            ctx.fill()
            ctx.restore()
        
        if layout['type'] == 'text':
            self.render_text(ctx, layout, context)
        elif layout['type'] == 'frac':
            self.render_frac(ctx, layout, context)
        elif layout['type'] == 'sqrt':
            self.render_sqrt(ctx, layout, context)
        elif layout['type'] == 'abs':
            self.render_abs(ctx, layout, context)
        # ...其他类型处理

    def render_text(self, ctx, layout, context):
        self._select_font_for_text(ctx, layout['content'])
        ctx.move_to(context.x, context.y)
        ctx.show_text(layout['content'])
        context.x += layout['width']

    def render_frac(self, ctx, layout, context):
        # 绘制分数线
        line_y = context.y - layout['baseline']
        ctx.move_to(context.x, line_y)
        ctx.line_to(context.x + layout['width'], line_y)
        ctx.stroke()
        
        # 绘制分子分母
        num = layout['children'][0]
        den = layout['children'][1]
        x_center = context.x + (layout['width'] - num['width'])/2
        self.render_node(ctx, num, RenderContext(x_center, context.y - layout['baseline'] - num['depth']))
        
        x_center = context.x + (layout['width'] - den['width'])/2
        self.render_node(ctx, den, RenderContext(x_center, context.y + den['height'] - den['baseline']))

    def render_abs(self, ctx, layout, context):
        content = layout['children'][0]
        line_width = 3
        spacing = 4
        
        # 绘制左侧竖线
        ctx.move_to(context.x, context.y - content['height'])
        ctx.line_to(context.x, context.y + content['depth'])
        ctx.stroke()
        
        # 绘制内容
        self.render_node(ctx, content, RenderContext(context.x + line_width + spacing, context.y))
        
        # 绘制右侧竖线
        ctx.move_to(context.x + layout['width'], context.y - content['height'])
        ctx.line_to(context.x + layout['width'], context.y + content['depth'])
        ctx.stroke()

    def render_sqrt(self, ctx, layout, context):
        # 基线位置调整
        content_y = context.y - layout['baseline'] + layout['content']['baseline']
        
        # 绘制根号符号
        sqrt_height = layout['content']['height'] + layout['content']['depth']
        ctx.move_to(context.x, content_y - 0.6 * sqrt_height)
        ctx.curve_to(
            context.x + 5, content_y - sqrt_height,
            context.x + 10, content_y - sqrt_height,
            context.x + 15, content_y
        )
        ctx.line_to(context.x + 15 + layout['content']['width'], content_y)
        ctx.stroke()
        
        # 绘制根指数（如果有）
        if layout['index']:
            self.render_node(ctx, layout['index'], RenderContext(context.x + 5, content_y - sqrt_height - 5))
        
        # 绘制被开方内容
        self.render_node(ctx, layout['content'], RenderContext(context.x + 15, content_y))

    def mark_dirty(self, node_path):
        # 根据节点路径标记脏节点
        self.dirty_nodes.add(tuple(node_path))
    
    def incremental_layout(self, root):
        # 仅重新计算脏节点及其父节点
        if not self.dirty_nodes:
            return
        # 示例：递归检查路径
        def _traverse(node, path):
            if tuple(path) in self.dirty_nodes:
                new_layout = self.layout_node(node)
                # 更新布局并清除脏标记
                self.dirty_nodes.remove(tuple(path))
                return new_layout
            # ...递归处理子节点
        return _traverse(root, [])

    def layout_node_parallel(self, node):
        if isinstance(node, list) and node[0].startswith('\\'):
            # 对无依赖的子节点并行处理
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.layout_node, child) for child in node[1:]]
                children_layouts = [f.result() for f in futures]
            return self._combine_command_layout(node[0], children_layouts)
        else:
            return self.layout_node(node)

    def _combine_command_layout(self, cmd, children_layouts):
        # 根据命令组合子节点布局
        if cmd == 'frac':
            return self.layout_frac(children_layouts[0], children_layouts[1])
        elif cmd == 'abs':
            return self.layout_abs(children_layouts[0])
        elif cmd == 'sqrt':
            return self.layout_sqrt(children_layouts)
        # ... 其他命令
        return None

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时: {time.time() - start:.3f}s")
        return result
    return wrapper

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