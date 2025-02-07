import cairo
from math import sqrt
from concurrent.futures import ThreadPoolExecutor
import time

class FontMetrics:
    def __init__(self):
        self.cache = {}

    def get_extents(self, ctx, text):
        if text not in self.cache:
            extents = ctx.text_extents(text)
            self.cache[text] = extents
        return self.cache[text]

class RenderContext:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y  # 基线位置

class LatexRenderer:
    def __init__(self, font_size=12):
        self.style = {
            'font_size': font_size,
            'h_spacing': 5,  # 水平间距
            'v_spacing': 8,  # 垂直间距
            'matrix_col_spacing': 10,  # 矩阵列间距
            'matrix_row_spacing': 10  # 矩阵行间距
        }
        self.font_map = [
            ("DejaVu Math TeX Gyre", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
            ("Noto Sans CJK SC", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ]
        self.layout_cache = {}
        self.dirty_nodes = set()  # 记录需要重新布局的节点
        self.macros = {}  # 存储自定义命令
        self.debug = False  # 调试模式

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

        layout = None
        if isinstance(node, list) and node[0].startswith('\\'):
            cmd = node[0][1:]
            if cmd in self.macros:
                layout = self.macros[cmd](self, node[1:])
            elif cmd == 'frac':
                layout = self.layout_frac(node[1], node[2])
            elif cmd == 'abs':
                layout = self.layout_abs(node[1])
            elif cmd == 'sqrt':
                layout = self.layout_sqrt(node[1:])
            elif cmd == 'int':
                layout = self.layout_int(node[1:])
            elif cmd == 'sum' or cmd == 'prod':
                layout = self.layout_sum_prod(cmd, node[1:])
            elif cmd == 'matrix':
                layout = self.layout_matrix(node[1:])
            elif cmd == 'bracket':
                layout = self.layout_bracket(node[1], node[2])
        elif isinstance(node, list):
            layout = self.layout_horizontal(node)
        elif isinstance(node, str):
            if '^' in node or '_' in node:
                layout = self.parse_sup_sub(node)
            elif r'\frac' in node:
                layout = self.parse_frac(node)
            else:
                layout = self.layout_text(node)

        if layout:
            self.layout_cache[node_hash] = layout
        return layout

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
        elif layout['type'] == 'int':
            self.render_int(ctx, layout, context)
        elif layout['type'] == 'sum' or layout['type'] == 'prod':
            self.render_sum_prod(ctx, layout, context)
        elif layout['type'] == 'matrix':
            self.render_matrix(ctx, layout, context)
        elif layout['type'] == 'bracket':
            self.render_bracket(ctx, layout, context)
        elif layout['type'] == 'horizontal':
            self.render_horizontal(ctx, layout, context)
        elif layout['type'] == 'space':
            self.render_space(ctx, layout, context)
        elif layout['type'] == 'hash':
            self.render_hash(ctx, layout, context)
        elif layout['type'] == 'chem_reaction':
            self.render_chem_reaction(ctx, layout, context)

    def layout_frac(self, num, den):
        num_layout = self.layout_node(num)
        den_layout = self.layout_node(den)
        line_thickness = 2
        padding = 4

        return {
            'type': 'frac',
            'width': max(num_layout['width'], den_layout['width']) + 2 * padding,
            'height': num_layout['height'] + line_thickness // 2 + padding,
            'depth': den_layout['depth'] + line_thickness // 2 + padding,
            'baseline': num_layout['height'] + line_thickness // 2 + padding,
            'children': [num_layout, den_layout]
        }

    def render_frac(self, ctx, layout, context):
        # 绘制分数线
        line_y = context.y - layout['baseline']
        ctx.move_to(context.x, line_y)
        ctx.line_to(context.x + layout['width'], line_y)
        ctx.stroke()

        # 绘制分子分母
        num = layout['children'][0]
        den = layout['children'][1]
        x_center = context.x + (layout['width'] - num['width']) / 2
        self.render_node(ctx, num, RenderContext(x_center, context.y - layout['baseline'] - num['depth']))

        x_center = context.x + (layout['width'] - den['width']) / 2
        self.render_node(ctx, den, RenderContext(x_center, context.y + den['height'] - den['baseline']))

    def layout_abs(self, content):
        content_layout = self.layout_node(content)
        line_width = 3  # 绝对值竖线宽度
        spacing = 4

        return {
            'type': 'abs',
            'width': content_layout['width'] + 2 * (line_width + spacing),
            'height': content_layout['height'],
            'depth': content_layout['depth'],
            'baseline': content_layout['baseline'],
            'children': [content_layout]
        }

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

    def layout_sqrt(self, args):
        if len(args) not in (1, 2):
            raise ValueError("\\sqrt requires 1 or 2 arguments")
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

    def layout_int(self, args):
        # 参数结构: [下限, 上限, 积分变量, 被积表达式]
        lower, upper, var, expr = args
        lower_layout = self.layout_node(lower)
        upper_layout = self.layout_node(upper)
        var_layout = self.layout_node(var)
        expr_layout = self.layout_node(expr)

        # 积分符号尺寸（假设固定）
        int_symbol_width = 20
        int_symbol_height = 40

        # 上下限在符号的上下方
        limits_spacing = 5
        total_width = max(lower_layout['width'], upper_layout['width']) + int_symbol_width + expr_layout['width']

        # 总高度由符号和表达式决定
        total_height = upper_layout['height'] + int_symbol_height + lower_layout['depth'] + limits_spacing
        baseline = upper_layout['height'] + int_symbol_height // 2

        return {
            'type': 'int',
            'width': total_width,
            'height': total_height,
            'depth': expr_layout['depth'],
            'baseline': baseline,
            'lower': lower_layout,
            'upper': upper_layout,
            'var': var_layout,
            'expr': expr_layout
        }

    def render_int(self, ctx, layout, context):
        # 绘制积分符号（简化版，实际需用贝塞尔曲线绘制）
        int_symbol_top = context.y - layout['baseline'] + layout['upper']['height'] + 5
        ctx.move_to(context.x, int_symbol_top)
        ctx.line_to(context.x + 10, int_symbol_top - 20)
        ctx.line_to(context.x + 20, int_symbol_top)
        ctx.stroke()

        # 绘制上下限
        self.render_node(ctx, layout['upper'], RenderContext(context.x - layout['upper']['width'] // 2, int_symbol_top - 25))
        self.render_node(ctx, layout['lower'], RenderContext(context.x - layout['lower']['width'] // 2, int_symbol_top + 25))

        # 绘制积分变量和表达式
        self.render_node(ctx, layout['var'], RenderContext(context.x + 25, context.y))
        self.render_node(ctx, layout['expr'], RenderContext(context.x + 25 + layout['var']['width'] + 5, context.y))

    def layout_sum_prod(self, node_type, args):
        # 参数结构: [下限, 上限, 表达式]
        lower, upper, expr = args
        lower_layout = self.layout_node(lower)
        upper_layout = self.layout_node(upper)
        expr_layout = self.layout_node(expr)

        # 符号尺寸（假设固定）
        symbol_width = 25
        symbol_height = 30 if node_type == 'sum' else 35

        # 上下标布局
        limits_spacing = 5
        total_width = max(lower_layout['width'], upper_layout['width']) + symbol_width + expr_layout['width']

        # 总高度
        total_height = upper_layout['height'] + symbol_height + lower_layout['depth'] + limits_spacing
        baseline = upper_layout['height'] + symbol_height // 2

        return {
            'type': node_type,
            'width': total_width,
            'height': total_height,
            'depth': expr_layout['depth'],
            'baseline': baseline,
            'lower': lower_layout,
            'upper': upper_layout,
            'expr': expr_layout
        }

    def render_sum_prod(self, ctx, layout, context):
        # 绘制符号（简化版，实际需用贝塞尔曲线绘制）
        symbol_top = context.y - layout['baseline'] + layout['upper']['height'] + 5
        ctx.move_to(context.x, symbol_top)
        ctx.line_to(context.x + 10, symbol_top - 20)
        ctx.line_to(context.x + 20, symbol_top)
        ctx.stroke()

        # 绘制上下限
        self.render_node(ctx, layout['upper'], RenderContext(context.x - layout['upper']['width'] // 2, symbol_top - 25))
        self.render_node(ctx, layout['lower'], RenderContext(context.x - layout['lower']['width'] // 2, symbol_top + 25))

        # 绘制表达式
        self.render_node(ctx, layout['expr'], RenderContext(context.x + 25, context.y))

    def layout_matrix(self, rows):
        # 每行的列数必须一致（假设输入已校验）
        col_count = len(rows[0])
        row_layouts = [self.layout_matrix_row(row) for row in rows]

        # 计算每列的最大宽度和每行的最大高度
        col_widths = [0] * col_count
        row_heights = [0] * len(rows)
        for i, row in enumerate(row_layouts):
            for j, cell in enumerate(row):
                col_widths[j] = max(col_widths[j], cell['width'])
                row_heights[i] = max(row_heights[i], cell['height'] + cell['depth'])

        # 总尺寸
        total_width = sum(col_widths) + (col_count - 1) * self.style['matrix_col_spacing']
        total_height = sum(row_heights) + (len(rows) - 1) * self.style['matrix_row_spacing']

        return {
            'type': 'matrix',
            'width': total_width,
            'height': total_height,
            'depth': 0,
            'baseline': row_heights[0] // 2,  # 矩阵基线通常在第一行中间
            'col_widths': col_widths,
            'row_heights': row_heights,
            'rows': row_layouts
        }

    def layout_matrix_row(self, cells):
        return [self.layout_node(cell) for cell in cells]

    def render_matrix(self, ctx, layout, context):
        x_start = context.x
        y_start = context.y - layout['baseline']

        # 绘制单元格
        for i, row in enumerate(layout['rows']):
            y = y_start + sum(layout['row_heights'][:i]) + i * self.style['matrix_row_spacing']
            x = x_start
            for j, cell in enumerate(row):
                # 计算单元格位置
                cell_x = x + (layout['col_widths'][j] - cell['width']) / 2
                cell_y = y + (layout['row_heights'][i] - cell['height'] - cell['depth']) / 2
                self.render_node(ctx, cell, RenderContext(cell_x, cell_y))
                x += layout['col_widths'][j] + self.style['matrix_col_spacing']

        # 绘制矩阵括号（示例：方括号）
        bracket_width = 10
        ctx.move_to(x_start - bracket_width, y_start)
        ctx.line_to(x_start - 5, y_start)
        ctx.line_to(x_start - 5, y_start + layout['height'])
        ctx.line_to(x_start - bracket_width, y_start + layout['height'])
        ctx.stroke()

        ctx.move_to(x_start + layout['width'] + 5, y_start)
        ctx.line_to(x_start + layout['width'] + bracket_width, y_start)
        ctx.line_to(x_start + layout['width'] + bracket_width, y_start + layout['height'])
        ctx.line_to(x_start + layout['width'] + 5, y_start + layout['height'])
        ctx.stroke()

        context.x += layout['width'] + 2 * bracket_width

    def layout_bracket(self, content, bracket_type='('):
        content_layout = self.layout_node(content)

        # 括号高度 = 内容总高度（height + depth）
        bracket_height = content_layout['height'] + content_layout['depth']
        
        content_layout['depth']

        # 括号宽度（假设固定比例）
        bracket_width = 10 + 0.1 * bracket_height

        return {
            'type': 'bracket',
            'width': 2 * bracket_width + content_layout['width'],
            'height': content_layout['height'],
            'depth': content_layout['depth'],
            'baseline': content_layout['baseline'],
            'content': content_layout,
            'bracket_height': bracket_height,
            'bracket_type': bracket_type
        }

    def render_bracket(self, ctx, layout, context):
        # 绘制左括号
        bracket_width = (layout['width'] - layout['content']['width']) / 2
        self._draw_bracket(ctx, context.x, context.y - layout['baseline'], 
                          bracket_width, layout['bracket_height'], 
                          layout['bracket_type'], is_left=True)
        
        # 绘制内容
        content_x = context.x + bracket_width
        self.render_node(ctx, layout['content'], RenderContext(content_x, context.y))
        
        # 绘制右括号
        self._draw_bracket(ctx, context.x + layout['width'] - bracket_width, 
                          context.y - layout['baseline'], 
                          bracket_width, layout['bracket_height'], 
                          layout['bracket_type'], is_left=False)
        
        context.x += layout['width']

    def _draw_bracket(self, ctx, x, y, width, height, bracket_type, is_left):
        # 示例：绘制圆括号（实际需用贝塞尔曲线）
        if bracket_type == '(':
            if is_left:
                ctx.move_to(x + width, y)
                ctx.curve_to(x, y, x, y + height, x + width, y + height)
            else:
                ctx.move_to(x, y)
                ctx.curve_to(x + width, y, x + width, y + height, x, y + height)
        elif bracket_type == '[':
            ctx.move_to(x, y)
            ctx.line_to(x + width, y)
            ctx.move_to(x, y + height)
            ctx.line_to(x + width, y + height)
        ctx.stroke()

    def layout_horizontal(self, nodes):
        total_width = 0
        max_height = 0
        max_depth = 0
        children_layouts = []

        for node in nodes:
            child_layout = self.layout_node(node)
            children_layouts.append(child_layout)
            total_width += child_layout['width'] + self.style['h_spacing']
            max_height = max(max_height, child_layout['height'])
            max_depth = max(max_depth, child_layout['depth'])

        # 减去最后一个元素的额外间距
        total_width -= self.style['h_spacing']

        return {
            'type': 'horizontal',
            'width': total_width,
            'height': max_height,
            'depth': max_depth,
            'baseline': max_height,  # 基线对齐为最大高度
            'children': children_layouts
        }

    def render_horizontal(self, ctx, layout, context):
        # 合并相邻文本
        text_buffer = []
        current_x = context.x

        for child in layout['children']:
            if child['type'] == 'text':
                text_buffer.append((current_x, child))
            else:
                if text_buffer:
                    self._flush_text_buffer(ctx, text_buffer, context.y)
                    text_buffer = []
                self.render_node(ctx, child, RenderContext(current_x, context.y))
            current_x += child['width'] + self.style['h_spacing']

        if text_buffer:
            self._flush_text_buffer(ctx, text_buffer, context.y)

    def _flush_text_buffer(self, ctx, buffer, y):
        full_text = ''.join([node['content'] for _, node in buffer])
        x_start = buffer[0][0]
        ctx.move_to(x_start, y)
        ctx.show_text(full_text)

    def layout_space(self):
        return {
            'type': 'space',
            'width': 20,  # 预设空格宽度
            'height': 0,
            'depth': 0,
            'baseline': 0
        }

    def render_space(self, ctx, layout, context):
        context.x += layout['width']  # 仅移动指针，不绘制内容

    def layout_hash(self):
        return {
            'type': 'hash',
            'width': 15,
            'height': 15,
            'depth': 0,
            'baseline': 10
        }

    def render_hash(self, ctx, layout, context):
        # 绘制红色方块
        ctx.save()
        ctx.set_source_rgb(1, 0, 0)
        ctx.rectangle(context.x, context.y - layout['baseline'], layout['width'], layout['height'])
        ctx.fill()
        ctx.restore()
        context.x += layout['width']

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

    def render_text(self, ctx, layout, context):
        self._select_font_for_text(ctx, layout['content'])
        ctx.move_to(context.x, context.y)
        ctx.show_text(layout['content'])
        context.x += layout['width']

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

    def layout_chem_reaction(self, reactants, products):
        # 布局示例：2H₂ + O₂ → 2H₂O
        reactant_layouts = [self.layout_node(r) for r in reactants]
        product_layouts = [self.layout_node(p) for p in products]

        # 添加箭头（→）
        arrow_layout = self.layout_text('→')

        # 组合水平布局
        return self.layout_horizontal(
            reactant_layouts + [arrow_layout] + product_layouts
        )

    def render_chem_reaction(self, ctx, layout, context):
        # 绘制上下标（如 H₂）
        for child in layout['children']:
            if child['type'] == 'chem_symbol':
                self.render_chem_symbol(ctx, child, context)
            else:
                self.render_node(ctx, child, context)

    def render_chem_symbol(self, ctx, layout, context):
        # 示例：渲染化学符号（假设 layout 包含 sub 和 sup 字段）
        self.render_text(ctx, layout['base'], context)
        if 'sub' in layout:
            sub_layout = self.layout_node(layout['sub'])
            sub_context = RenderContext(context.x, context.y + sub_layout['height'])
            self.render_node(ctx, sub_layout, sub_context)
            context.x += sub_layout['width']
        if 'sup' in layout:
            sup_layout = self.layout_node(layout['sup'])
            sup_context = RenderContext(context.x, context.y - sup_layout['depth'])
            self.render_node(ctx, sup_layout, sup_context)
            context.x += sup_layout['width']

    def parse_sup_sub(self, latex):
        # 简单解析上下标
        import re
        pattern = re.compile(r'([a-zA-Z]+)(\^?)(\{?)([^\{\}]*)(\}?)(_?)(\{?)([^\{\}]*)(\}?)')
        match = pattern.match(latex)
        if not match:
            return self.layout_text(latex)

        base, hat, hat_open, sup, hat_close, underscore, sub_open, sub, sub_close = match.groups()
        base_layout = self.layout_text(base)
        sup_layout = self.layout_text(sup) if sup else None
        sub_layout = self.layout_text(sub) if sub else None

        return {
            'type': 'chem_symbol',
            'base': base_layout,
            'sup': sup_layout,
            'sub': sub_layout
        }

    def parse_frac(self, latex):
        # 简单解析分数
        import re
        pattern = re.compile(r'\\frac\{([^\}]*)\}\{([^\}]*)\}')
        match = pattern.match(latex)
        if not match:
            return self.layout_text(latex)

        num, den = match.groups()
        return ['\\frac', num, den]

    def define_macro(self, name, handler):
        self.macros[name] = handler

    def mark_dirty(self, node_path):
        # 根据节点路径标记脏节点
        self.dirty_nodes.add(tuple(node_path))

    def incremental_layout(self, root):
        # 仅重新计算脏节点及其父节点
        if not self.dirty_nodes:
            return

        def _traverse(node, path):
            if tuple(path) in self.dirty_nodes:
                new_layout = self.layout_node(node)
                # 更新布局并清除脏标记
                self.dirty_nodes.remove(tuple(path))
                return new_layout
            # ...递归处理子节点
            return node

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
        if cmd == '\\frac':
            return self.layout_frac(children_layouts[0], children_layouts[1])
        elif cmd == '\\abs':
            return self.layout_abs(children_layouts[0])
        elif cmd == '\\sqrt':
            return self.layout_sqrt(children_layouts)
        elif cmd == '\\int':
            return self.layout_int(children_layouts)
        elif cmd == '\\sum' or cmd == '\\prod':
            return self.layout_sum_prod(cmd, children_layouts)
        elif cmd == '\\matrix':
            return self.layout_matrix(children_layouts)
        elif cmd == '\\bracket':
            return self.layout_bracket(children_layouts[0], children_layouts[1])
        else:
            raise ValueError(f"未知命令: {cmd}")

# 示例：定义 \color 命令
def handle_color(renderer, args):
    color = args[0]
    content = renderer.layout_node(args[1])
    return {
        **content,
        'color': color  # 在渲染阶段应用颜色
    }

# 使用示例
renderer = LatexRenderer()
renderer.define_macro('color', handle_color)

latex = r"\frac{1}{2} + x^2"
ast = ['\\frac', '1', '2', '+', 'x', '^', '2']
layout_data = renderer.layout_node(ast)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 100)
ctx = cairo.Context(surface)
ctx.set_font_size(12)
renderer.render_node(ctx, layout_data, RenderContext(10, 50))
import tkinter as tk
from PIL import Image, ImageTk

def render_to_tkinter(ast, width=400, height=200):
    renderer = LatexRenderer(font_size=12)
    layout = renderer.layout_node(ast)
    
    # 创建 Cairo 图形表面
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)  # 白色背景
    ctx.paint()
    ctx.set_source_rgb(0, 0, 0)  # 黑色
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(renderer.style['font_size'])
    
    # 初始化渲染上下文（动态指针）
    context = RenderContext(10, layout['baseline'] + 10)  # 留边距
    renderer.render_node(ctx, layout, context)
    
    # 将 Cairo 图形表面转换为 PIL 图像
    buf = surface.get_data()
    image = Image.frombuffer("RGBA", (width, height), buf, "raw", "RGBA", 0, 1)
    
    # 创建 Tkinter 窗口
    root = tk.Tk()
    root.title("LaTeX Renderer")
    root.geometry(f"{width}x{height}")
    
    # 将 PIL 图像转换为 Tkinter 图像
    tk_image = ImageTk.PhotoImage(image)
    
    # 创建标签并显示图像
    label = tk.Label(root, image=tk_image)
    label.image = tk_image  # 保持对图像的引用
    label.pack()
    
    # 运行 Tkinter 主循环
    root.mainloop()

# 使用示例
latex = r"\frac{1}{2} + x^2"
ast = ['\\frac', '1', '2']
render_to_tkinter(ast)