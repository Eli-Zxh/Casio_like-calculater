import tkinter as tk
import subprocess
import shlex
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class CasioUI:
    def __init__(self, root):#初始化计算器界面
        self.root = root
        self.root.title('Casio')
        self.root.geometry('525x600+100+100')#宽520，高600，位置100，100
        self.root["background"] = '#2d2c32'#设置背景颜色黑色
        self.font = ('宋体', 30)
        self.font_16 = ('宋体', 16)
        self.font_12 = ('宋体', 12)

        # 初始化用于显示的StringVar变量
        self.input_num = tk.StringVar()
        self.input_num.set('')
        self.latex_display = tk.StringVar()
        self.latex_display.set('')
        self.output_num = tk.StringVar()
        self.output_num.set('')

        # 设置界面的各个部分
        self._setup_input_display()
        self._setup_latex_display()
        self._setup_output_display()
        self._setup_buttons()
        self._setup_special_operators()

    def _setup_buttons(self):#按钮显示、位置、大小、颜色和背景颜色以及传参设置
        buttons = [
            ('OPTN', 4, 1, 5, self.font_16, '#36353c', '#c9c9cb', 'OPTN'),
            ('CALC', 4, 6, 5, self.font_16, '#36353c', '#c9c9cb', 'CALC'),
            ('∫', 4, 21, 5, self.font_16, '#36353c', '#c9c9cb', '∫'),
            ('x', 4, 26, 5, self.font_16, '#36353c', '#c9c9cb', 'x'),
            ('—', 5, 1, 5, self.font_16, '#36353c', '#c9c9cb', '—'),
            ('√', 5, 6, 5, self.font_16, '#36353c', '#c9c9cb', '^0.5'),
            ('x²', 5, 11, 5, self.font_16, '#36353c', '#c9c9cb', '^2'),
            ('xº', 5, 16, 5, self.font_16, '#36353c', '#c9c9cb', '^'),
            ('logₒ▫', 5, 21, 5, self.font_16, '#36353c', '#c9c9cb', 'log'),
            ('ln', 5, 26, 5, self.font_16, '#36353c', '#c9c9cb', 'ln'),
            ('(-)', 6, 1, 5, self.font_16, '#36353c', '#c9c9cb', '-'),
            ('°′″', 6, 6, 5, self.font_16, '#36353c', '#c9c9cb', '°′″'),
            ('x⁻¹', 6, 11, 5, self.font_16, '#36353c', '#c9c9cb', '1/'),
            ('sin', 6, 16, 5, self.font_16, '#36353c', '#c9c9cb', 'sin'),
            ('cos', 6, 21, 5, self.font_16, '#36353c', '#c9c9cb', 'cos'),
            ('tan', 6, 26, 5, self.font_16, '#36353c', '#c9c9cb', 'tan'),
            ('STO', 7, 1, 5, self.font_16, '#36353c', '#c9c9cb', 'STO'),
            ('ENG', 7, 6, 5, self.font_16, '#36353c', '#c9c9cb', 'ENG'),
            ('(', 7, 11, 5, self.font_16, '#36353c', '#c9c9cb', '('),
            (')', 7, 16, 5, self.font_16, '#36353c', '#c9c9cb', ')'),
            ('S⇔D', 7, 21, 5, self.font_16, '#36353c', '#c9c9cb', 'S⇔D'),
            ('M+', 7, 26, 5, self.font_16, '#36353c', '#c9c9cb', 'M+'),
            ('7', 8, 1, 6, self.font_16, '#efefef', None, '7'),
            ('8', 8, 7, 6, self.font_16, '#efefef', None, '8'),
            ('9', 8, 13, 6, self.font_16, '#efefef', None, '9'),
            ('DEL', 8, 19, 6, self.font_16, '#0c39b1', '#e3f3e4', 'DEL'),
            ('AC', 8, 25, 6, self.font_16, '#0c39b1', '#e3f3e4', 'AC'),
            ('4', 9, 1, 6, self.font_16, '#efefef', None, '4'),
            ('5', 9, 7, 6, self.font_16, '#efefef', None, '5'),
            ('6', 9, 13, 6, self.font_16, '#efefef', None, '6'),
            ('×', 9, 19, 6, self.font_16, '#efefef', None, '*'),
            ('÷', 9, 25, 6, self.font_16, '#efefef', None, '/'),
            ('1', 10, 1, 6, self.font_16, '#efefef', None, '1'),
            ('2', 10, 7, 6, self.font_16, '#efefef', None, '2'),
            ('3', 10, 13, 6, self.font_16, '#efefef', None, '3'),
            ('+', 10, 19, 6, self.font_16, '#efefef', None, '+'),
            ('-', 10, 25, 6, self.font_16, '#efefef', None, '-'),
            ('0', 11, 1, 6, self.font_16, '#efefef', None, '0'),
            ('·', 11, 7, 6, self.font_16, '#efefef', None, '.'),
            ('×10ˣ', 11, 13, 6, self.font_16, '#efefef', None, '*10^'),
            ('Ans', 11, 19, 6, self.font_16, '#efefef', None, 'Ans'),
            ('=', 11, 25, 6, self.font_16, '#efefef', None, '='),
        ]
       
        for btn_text, row, col, colspan, font, bg, fg, cmd_text in buttons:#遍历按钮完成显示
            button = tk.Button(self.root, text=btn_text, width=5, font=font, relief=tk.FLAT, bg=bg, fg=fg)
            button.grid(row=row, column=col, columnspan=colspan, padx=4, pady=2)
            self._assign_command(button, cmd_text)
    
    def _assign_command(self, button, btn_text):#按钮绑定事件
        if btn_text in '0123456789+-':
            button.config(command=lambda: self.click_button(btn_text, 0))
        elif btn_text == 'DEL':
            button.config(command=self.clearone)
        elif btn_text == 'AC':
            button.config(command=self.clearall)
        elif btn_text == '=':
            button.config(command=self.calculate)
        else:
            button.config(command=lambda: self.click_button(btn_text, 0))

    def click_button(self, x, y):#输入框添加规则函数，设置y以遍适应特殊操作符的输入运算
        #如'ANS''STO'、'ENG'、'('、')'、'S⇔D'、'M+'
        if y == 0:
            self.input_num.set(self.input_num.get() + x)

    def clearone(self):#删除一个字符，DEL键的功能
        string = self.input_num.get()
        self.input_num.set(string[:-1])

    def clearall(self):#清空输入框和输出框，AC键的功能
        self.input_num.set('')
        self.latex_display.set('')
        self.output_num.set('')

class latexdisplay:
    def _setup_input_display(self):
        """
        设置输入显示框。
        
        创建一个输入框控件，并配置其属性，如文本变量、字体和宽度等。
        将输入框放置在窗口的指定位置，并绑定键盘释放事件以实时更新LaTeX显示。
        """
        # 创建输入框控件，设置其属性
        self.input_entry = tk.Entry(self.root,
                                    textvariable=self.input_num, font=self.font_16, width=23,
                                    justify=tk.LEFT)
        # 将输入框放置在窗口网格的指定位置，并设置 padding
        self.input_entry.grid(row=1, column=1, columnspan=30, padx=10, pady=5)
        # 绑定键盘释放事件到更新LaTeX显示的方法
        self.input_entry.bind('<KeyRelease>', self.update_latex_display)

    def _setup_latex_display(self):#LaTeX显示环境
        self.latex_fig, self.latex_ax = plt.subplots(figsize=(5, 1.0))  # 调整大小为5x1英寸
        self.latex_ax.axis('off')  
        self.latex_canvas = FigureCanvasTkAgg(self.latex_fig, master=self.root)
        self.latex_canvas.get_tk_widget().grid(row=2, column=1, columnspan=30, padx=10, pady=5)

    def _setup_output_display(self):#输出显示界面
        self.output_fig, self.output_ax = plt.subplots(figsize=(5, 0.5))  # 调整大小为5x0.5英寸
        self.output_ax.axis('off')  
        self.output_canvas = FigureCanvasTkAgg(self.output_fig, master=self.root)
        self.output_canvas.get_tk_widget().grid(row=3, column=1, columnspan=30, padx=10, pady=5)

    def update_latex_display(self, event=None):#更新latex显示的函数，适应输入框运算
        # 清除之前的绘图
        self.latex_ax.clear()
        self.latex_ax.axis('off')

        # 获取输入框中的 LaTeX 表达式
        latex_expr = self.input_num.get().strip()

        try:
            # 渲染 LaTeX 表达式
            self.latex_ax.text(0.5, 0.5, f"${latex_expr}$", fontsize=16, ha='center', va='center')
            self.latex_fig.canvas.draw()
        except Exception as e:
            print(f"Error rendering LaTeX: {e}")

    def update_output_display(self):#更新输出框的函数，适应输出框运算
        # 清除之前的绘图
        self.output_ax.clear()
        self.output_ax.axis('off')

        # 获取输出框中的 LaTeX 表达式
        output_expr = self.output_num.get().strip()

        try:
            # 渲染 LaTeX 表达式
            self.output_ax.text(0.5, 0.5, f"${output_expr}$", fontsize=16, ha='center', va='center')
            self.output_fig.canvas.draw()
        except Exception as e:
            print(f"Error rendering LaTeX: {e}")

class CasioCalculator:
    def calculate(self):#计算函数，目前调用qalculate计算引擎
        string = self.input_num.get()
        string_list = list(string)
        for i in string_list:
            if i in self.special_list:
                order = string_list.index(i)
                string_list[order] = self.special_dict[i]
        string = ''.join(string_list)

        result = subprocess.Popen(shlex.split('./qalculate/qalc.exe'), stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=True, universal_newlines=True)
        result.stdin.write(f'{string}\n')
        result.stdin.close()
        return_code = result.wait()
        qalc_result = result.stdout.read()
        qalc_result_list = qalc_result.split('\n')
        output_result = qalc_result_list[2]
        print(output_result)

        output_result = re.sub(r'\x1b\[[0-9;]*m', '', output_result)
        output_result = output_result.encode('utf-8')
        ANS_list = output_result.split(b' ')
        ANS = ANS_list[-1].decode('utf-8')
        self.output_num.set(ANS)

        self.update_output_display()

        error_result = result.stderr.read() if result.stderr else None
        if error_result:
            print(f"错误信息：{error_result}")

class latexcut:
    GH_letters = [r'\alpha',r'\beta',r'\chi',r'\delta',r'\epsilon',r'\eta',r'\gamma',r'\iota',
                  r'\kappa',r'\lambda',r'\mu',r'\nu',r'ο',r'\omega',r'\phi',r'\pi',
                  r'\psi',r'\rho',r'\sigma',r'\tau',r'\theta',r'upsilon',r'\xi',r'\zeta',
                  r'\digamma',r'\varepsilon',r'\varkappa',r'\varphi',r'\varpi',r'\varrho',r'\varsigma',r'\vartheta',
                  r'\Delta',r'\Gamma',r'\Lambda',r'\Omega',r'\Phi',r'\Pi',r'\Psi',r'\Sigma',
                  r'\Theta',r'\Upsilon',r'\Xi',r'\aleph',r'\beth',r'daleth',r'\gimel']
    special_operators = [r'\frac',r'\sqrt',r'\int',r'\sum',r'\prod',r'\log',r'\lim',r'\limsup',r'\liminf',r'\sin',r'\cos',r'\tan',
                        r'\sec',r'\csc',r'\cot',r'\sinh',r'\cosh',r'\tanh',r'\arcsin',r'\arccos',r'\arctan',r'\exp',r'\ln',r'\lg',
                        r'\arg',r'\coth',r'\deg',r'\det',r'\dim',r'\gcd',r'\hom',r'\max',r'\sup',r'\ker',r'\inf',r'\min',r'\Pr',r'\abs']
    operators = [r'+', r'-', r'=', r'\div', r'\times', r'\cdot']
    def find_matching_braces(s, start, brace_type='{}'):#匹配括号,s为字符串，start为起始位置，brace_type为括号类型，返回匹配的括号位置
            stack = []
            open_brace, close_brace = brace_type
            for i in range(start, len(s)):
                if s[i] == open_brace:
                    stack.append(i)
                elif s[i] == close_brace:
                    if stack:
                        stack.pop()
                        if not stack:
                            return i
            return -1

    def find_start_position(string,start_index):#寻找起始位置
        brace_map = {'(','[','{','_','^'}
        for i in range(start_index,len(string)):
            if string[i] in brace_map:
                return i-1
            elif i < len(string)-1:
                continue
        return len(string)

    def find_character_position(string: str, target: str,start_index = 0):#寻找字符位置
        stack = []
        in_map = {'(','[','{'}
        out_map = {')',']','}'}
        if target in out_map or target in in_map:
            for i in range(len(string)):
                if string[i] == target:
                    return i
        for i in range(start_index,len(string)):
            if string[i] == target and not stack:
                return i
            elif string[i] in in_map:
                stack.append(string[i])
            elif string[i] in out_map:
                stack.pop()
        return -1
    def _setup_operators(string: str):
        """字符处理切割为运算块（严格保持分割逻辑，修复减号分割问题）"""
        # 第零步：预处理非法字符和绝对值替换
        string = string.replace(" ", "").replace("\n", "")
        if "#" in string:
            raise ValueError("invalid character")
    
        # 绝对值替换逻辑（保持不变）
        pipe_indices = [i for i, c in enumerate(string) if c == "|"]
        if len(pipe_indices) % 2 != 0:
            raise ValueError("invalid absolute expression")
        if pipe_indices:
            string = AbsProcessor().process(string)
    
        # 第一步：基于括号栈的运算符分割（严格保持原始逻辑）
        Parentheses_stack = []
        Square_brackets_stack = []
        Braces_stack = []
        positions = [0]  # 必须包含起始位置

        for index, char in enumerate(string):
            # 括号栈更新（保持原始逻辑）
            match char:
                case '(':
                    Parentheses_stack.append(char)
                case ')':
                    if not Parentheses_stack:
                        raise ValueError("Mismatched parentheses")
                    Parentheses_stack.pop()
                case '[':
                    Square_brackets_stack.append(char)
                case ']':
                    if not Square_brackets_stack:
                        raise ValueError("Mismatched brackets")
                    Square_brackets_stack.pop()
                case '{':
                    Braces_stack.append(char)
                case '}':
                    if not Braces_stack:
                        raise ValueError("Mismatched braces")
                    Braces_stack.pop()

            # 运算符分割逻辑（关键修复点）
            if not Parentheses_stack and not Square_brackets_stack and not Braces_stack:
                if char in ('+', '='):
                    positions.append(index)
                    positions.append(index + 1)  # 运算符后分割
                elif char == '-':
                    # 严格判定负号条件（保持项目原有逻辑）
                    is_negative = (
                        index == 0 or
                        string[index-1] in latexcut.operators + ['(', '[', '{', 'E'] or
                        (string[index-1] == 'E' and index >= 2 and string[index-2].isdigit())
                    )
                    if not is_negative:
                        positions.append(index)
                        positions.append(index + 1)  # 减号单独分割

        positions.append(len(string))  # 确保包含末尾

         # 检查栈是否为空，确保括号匹配
        if Parentheses_stack or Square_brackets_stack or Braces_stack:
            raise ValueError("Mismatched brackets or parentheses")

        # 第二步：提取分割块（严格按原始项目格式）
        parts = []
        for i in range(1, len(positions)):
            part = string[positions[i-1]:positions[i]]
            if part:  # 保留空字符串以匹配原有逻辑
                parts.append(part)
    
        # 第三步：修复运算符粘连问题（如 "-\\frac" 拆分为 "-" 和 "\\frac"）
        final_parts = []
        for part in parts:
            if part.startswith('-') and len(part) > 1 and part[1] != '\\':
                # 处理类似 "-123" 的情况
                final_parts.append(part)
            elif part.startswith('-') and len(part) > 1:
                # 分割 "-\\frac" 为 "-" 和 "\\frac"
                final_parts.append('-')
                final_parts.append(part[1:])
            else:
                final_parts.append(part)
    
        return final_parts
    
    def _setup_special(string: str):
        #第二步，对于每个分割的部分，做运算块判定，对满足运算块判定的部分去运算块重复第一步
        i = 0
        operator_replacements = []
        while i < len(string):
            match string[i]:
                case '-':#负号，直接合并到operator_replacements中，并跳过
                    operator_replacements.append('-')
                    i += 1
                    continue
                case '\\':
                    if i+6 <= len(string) and string[i:i+4] == r'\div':#2.1运算符不能按照latexcut.find_start_position切开，给予单独判断
                        if operator_replacements[-1] == r'\times':#2.2如果前一个运算符是乘号，则替换为除号
                            operator_replacements[-1] = r'\div'#替换为除号
                        else:operator_replacements.append(r'\div')#识别为除号
                        i += 4
                        continue
                    elif i+6 < len(string) and string[i:i+5] == r'\cdot':
                        if operator_replacements[-1] == r'\times':#2.2如果前一个运算符是乘号，则替换为点乘
                            operator_replacements[-1] = r'\cdot'#替换为点乘
                        else:operator_replacements.append(r'\cdot')#识别为点乘
                        i += 5
                        continue
                    elif i+6 < len(string) and string[i:i+6] == r'\times':
                        if operator_replacements[-1] != r'\times':#2.2如果前一个运算符是乘号，则替换为叉乘
                            operator_replacements.append(r'\times')#识别为叉乘
                        else:pass#否则不增加叉乘符号 
                        i += 6
                        continue
                    start_index = latexcut.find_start_position(string, i)#找第一个任意括号，分割运算符函数
                    match string[i:start_index]:
                        case r'\frac': #分式
                            operator_replacements.append(r'\frac')#标识为分式
                            if string[i+5] == '{':#找第一个括号{}，如果没有，立刻报错
                                end_index = latexcut.find_matching_braces(string, i + 5, '{}')#找第一个括号对应的}位置
                                if end_index >= len(string):raise ValueError("invalid expression")#必须有第二个括号的补丁
                                if end_index != -1 and string[end_index] == '{':#找分式的第二个括号{}，如果没有，立刻报错
                                    operator_replacements.append(string[i+6:end_index-1])#识别分子
                                    end_index2 = latexcut.find_matching_braces(string, end_index, '{}')#找第二个括号对应的}位置,如果没有，立刻报错
                                    if end_index2 != -1:
                                        operator_replacements.append(string[end_index+1:end_index2-1])#识别分母
                                        i = end_index2#跳过原本分式结构
                                        if i < len(string):#如果不是运算块末尾
                                            operator_replacements.append(r'\times')#添加乘法标识
                                        continue
                                    else:
                                        raise ValueError("invalid expression")
                                else:
                                    raise ValueError("invalid expression")
                            else:
                                raise ValueError("invalid expression")
                        case r'\sqrt':#根式
                            operator_replacements.append(r'\sqrt')#标识为根式
                            match string[i+5]:
                                case '[':#非二次根式
                                    end_index = latexcut.find_matching_braces(string, i + 4, '[]')#找根式幂次的]对应位置
                                    if end_index != -1 and string[end_index] == '{':#找根式幂次对应的括号，判断下一个字符为根式括号，如不满足立刻报错
                                        if (i+6 < end_index-2 and string[i+6:end_index-2].isdigit()) or (i+6 == end_index-2 and string[i+6].isdigit()):#判断根式是否为数字
                                            operator_replacements.append(string[i+6:end_index-1])#识别根式幂次
                                            end_index2 = latexcut.find_matching_braces(string, end_index -1, '{}')#找根式表达式括号}对应位置，如果没有，立刻报错
                                            if end_index2 != -1:
                                                operator_replacements.append(string[end_index + 1:end_index2-1])#识别根式
                                                i = end_index2#跳过原本根式结构
                                                if i < len(string):#如果不是运算块末尾
                                                    operator_replacements.append(r'\times')#添加乘法标识
                                                continue
                                            else: raise ValueError("invalid expression")
                                        else:
                                            raise ValueError("invalid expression")
                                    else: raise ValueError("invalid expression")
                                case '{':#二次根式
                                    operator_replacements.append('2')#识别为二次根式
                                    end_index = latexcut.find_matching_braces(string, i + 5, '{}')#找根式表达式的}对应位置
                                    if end_index != -1:#找根式幂次对应的括号，如不满足立刻报错
                                        operator_replacements.append(string[i+6:end_index-1])#把整个根式添加到替换列表中
                                        i = end_index + 1#跳过原本根式结构
                                        if i < len(string):#如果不是运算块末尾
                                            operator_replacements.append(r'\times')#添加乘法标识
                                        continue
                                    else: raise ValueError("invalid expression")
                                case _: raise ValueError("invalid expression")#根式后无{}或者[]，立刻报错
                        case r'\int':
                            operator_replacements.append(r'\int')#标识为积分
                            match string[i+4]:
                                case '_'|'^':#定积分
                                    int_string = string[i+4:]#切开积分
                                    down_index = latexcut.find_character_position(int_string,'_')#找积分下限
                                    if int_string[down_index + 1] == '{':#非单字符
                                        down_end_index = latexcut.find_matching_braces(int_string, down_index + 1, '{}')#找积分下限对应的括号
                                        operator_replacements.append(int_string[down_index + 2:down_end_index-1])#识别积分下限
                                    elif int_string[down_index + 1].isalpha() or int_string[down_index + 1].isdigit():#单字符识别
                                        down_end_index = down_index + 2#下限为单字符
                                        operator_replacements.append(int_string[down_index])
                                    else: raise ValueError("invalid down limit")
                                    up_index = latexcut.find_character_position(int_string,'^')#找积分上限
                                    if int_string[up_index + 1] == '{':#非单字符
                                        up_end_index = latexcut.find_matching_braces(int_string, up_index + 1, '{}')#找积分上限对应的括号
                                        operator_replacements.append(int_string[up_index + 2:up_end_index -1])#识别积分上限
                                    elif int_string[up_index + 1].isalpha() or int_string[up_index + 1].isdigit():#单字符识别
                                        up_end_index = up_index + 2
                                        operator_replacements.append(int_string[up_index])
                                    else: raise ValueError("invalid up limit")
                                    tag_index = max(down_end_index,up_end_index)#取下限和上限的最大值
                                    int_string = int_string[tag_index:]
                                case '{':#不定积分
                                    operator_replacements.append('')#下限传空
                                    operator_replacements.append('')#上限传空
                                    int_string = string[i+4:]#切开积分表达式
                                    tag_index = 0#下限和上限为空
                            expression_index = latexcut.find_character_position(int_string,'{')#找积分表达式，不定积分与定积分处理表达式方式相同
                            if expression_index != -1:
                                end_index = latexcut.find_matching_braces(int_string, expression_index, '{}')#找积分表达式的}对应位置
                                int_string = int_string[expression_index+1:end_index-1]#切开表达式
                                d_index = latexcut.find_character_position(int_string,'d')#找微分变量，如果不存在默认为x,如果存在，必须在积分表达式末尾
                                if d_index != -1:#如果为特殊积分变量
                                    d_string = int_string[d_index+1:]#切开积分变量表达式
                                    if d_string[0] == '{' or d_string == '(':
                                        operator_replacements.append(d_string[1:-1])#去括号，识别积分变量
                                    else:operator_replacements.append(int_string[d_index + 1:])#识别积分变量
                                else: operator_replacements.append('x')#默认为x
                                operator_replacements.append(int_string[:d_index])#识别积分表达式
                                i = end_index + 4 + tag_index#跳过原本积分结构
                                if i < len(string):#如果不是运算块末尾
                                    operator_replacements.append(r'\times')#添加乘法标识
                            else: raise ValueError("invalid expression")#无表达式，立刻报错
                        case r'\sum'|r'\prod':#累加与累乘处理方式相同
                            operator_replacements.append(string[i:start_index])#标识为累加/累乘
                            sum_string = string[start_index:]
                            down_index = latexcut.find_character_position(sum_string,'_')#找下限
                            if down_index != -1:
                                if sum_string[down_index + 1] == '{':#非单字符
                                    down_end_index = latexcut.find_matching_braces(sum_string, down_index + 1, '{}')#找下限对应的括号
                                    if down_end_index == -1:raise ValueError("invalid down limit")#无对应的括号，立刻报错
                                    down_expression = sum_string[down_index + 2:down_end_index-1]#单列下限方程
                                    equal_index = latexcut.find_character_position(down_expression,'=')#找等号
                                    if equal_index != -1:#定值求和
                                        operator_replacements.append(down_expression[:equal_index])#识别求和变量
                                        operator_replacements.append(down_expression[equal_index + 1:])#识别下限
                                    else:
                                        operator_replacements.append(down_expression[down_index + 1:down_end_index-1])#识别求和变量
                                        is_variable = True
                                        operator_replacements.append('')#不定求和下限记录为空
                                elif sum_string[down_index + 1].isdigit():#允许单数字下标
                                    operator_replacements.append('i')#此时求和变量必须为i
                                    operator_replacements.append(sum_string[down_index + 1:])#识别下限
                                else: raise ValueError("invalid down limit")
                            else: raise ValueError("invalid down limit")#不允许没有求和下限
                            up_index = latexcut.find_character_position(sum_string,'^')#找上限
                            if up_index != -1:
                                if sum_string[up_index + 1] == '{':#非单字符
                                    up_end_index = latexcut.find_matching_braces(sum_string, up_index + 1, '{}')#找上限对应的括号
                                    if up_end_index == -1: raise ValueError("invalid up limit")#不允许没有上限
                                    operator_replacements.append(sum_string[up_index + 2:up_end_index-1])#识别上限
                                elif sum_string[up_index + 1].isalpha() or sum_string[up_index + 1].isdigit():#允许单字符
                                    operator_replacements.append(sum_string[up_index + 1])#识别上限
                                else: raise ValueError("invalid up limit")
                            else: 
                                if is_variable:operator_replacements.append('')#不定求和记为空
                                else: raise ValueError("invalid up limit")
                            end_index = max(down_end_index,up_end_index)#取下限和上限的最大值
                            sum_string = sum_string[end_index:]
                            expression_index = latexcut.find_character_position(sum_string,'{')#找表达式,不允许单字符
                            if expression_index != -1:
                                expr_end_index = latexcut.find_matching_braces(sum_string, expression_index, '{}')#找表达式的}对应位置
                                operator_replacements.append(sum_string[expression_index+1:expr_end_index-1])#识别表达式
                            else: raise ValueError("invalid expression")#无表达式，立刻报错
                            i = end_index + start_index + expr_end_index#跳过原本累加结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append('\times')#添加乘法标识
                        case r'\log':#普通对数函数
                            operator_replacements.append(r'\log')
                            down_index = latexcut.find_character_position(string, '_')#找下标
                            if down_index != -1:
                                if string[down_index+1] == '{':#多字符
                                    end_index = latexcut.find_matching_braces(string, down_index, '{}')#找到对应下标括号
                                    operator_replacements.append(string[down_index+2:end_index - 1])#识别底数
                                else: operator_replacements.append(string[down_index])#单字符识别下标
                            else: operator_replacements.append('10')#默认底为10
                            start_braces_index = latexcut.find_character_position(string,'(')#找真数
                            if start_braces_index != -1:
                                end_index = latexcut.find_matching_braces(string,start_braces_index,'()')#找到对应括号
                                operator_replacements.append(string[start_braces_index+1:end_index-1])#识别真数
                            else: raise ValueError(f'invalid function log')
                            i = end_index + 1#跳过原本函数结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append(r'\times')#添加乘法标识
                        case r'\lim'|r'\limsup'|r'\liminf':#极限，不区分左右
                            operator_replacements.append(r'\lim')
                            down_index = latexcut.find_character_position(string, '_')#找下标
                            if down_index != -1:
                                if string[down_index + 1] == '{':#非单字符
                                    down_end_index = latexcut.find_matching_braces(string, down_index + 1, '{}')#找下限对应的括号
                                    down_expression = string[down_index + 2:down_end_index-1]#单列下限方程
                                    index = down_expression.find(r'\rightarrow')#不允许变量嵌套极限，找右箭头
                                    if index != -1:
                                        operator_replacements.append(down_expression[:index])#识别变量
                                        operator_replacements.append(down_expression[index+11:])#识别下限
                                    else: raise ValueError("invalid down limit")
                                    lim_expression = string[down_end_index:]#切出表达式，直接切分
                                    if lim_expression[0] == '{':
                                        end_index = latexcut.find_matching_braces(lim_expression, 0, '{}')#找表达式的}对应位置
                                        if end_index == -1: raise ValueError("invalid expression")#不允许没有表达式
                                        operator_replacements.append(lim_expression[1:end_index-1])#识别表达式
                                    else: raise ValueError("invalid expression")#无表达式，立刻报错
                                else: raise ValueError("invalid down limit")
                            else: raise ValueError("invalid limit")#不允许没有极限下限
                            i = end_index + down_end_index#跳过原本函数结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append(r'\times')#添加乘法标识
                        case r'\sin'|r'\cos'|r'\tan'|r'\sec'|r'\csc'|r'\cot'|r'\sinh'|r'\cosh'|r'\tanh'|r'\arcsin'|r'\arccos'|r'\arctan'|r'\exp'|r'\ln'|r'\lg'|r'\arg'|r'\coth'|r'\deg'|r'\factorial':#所有三类函数
                            func = string[i:start_index] 
                            operator_replacements.append(func)#添加第三类函数对应标识
                            if string[start_index + 1] == '^':#此种函数允许幂次前置
                                if string[start_index+2] == '{':#非单字符上标
                                    end_up_index = latexcut.find_matching_braces(string, start_index + 2, '{}')#找上标对应的}位置
                                    power_string = string[start_index + 3:end_up_index-1]#切出上标 
                                else:#单字符上标
                                    end_up_index = start_index + 2
                                    power_string = string[start_index+2]#切出上标
                            start_braces_index = latexcut.find_character_position(string,'(')#找到第一个括号
                            if start_braces_index != -1:
                                end_index = latexcut.find_matching_braces(string,start_braces_index,'()')#找到对应括号
                                operator_replacements.append(string[start_braces_index+1:end_index-1])#切开识别数字或函数
                                try:
                                    if power_string:
                                        operator_replacements.append('^')#添加幂次
                                        operator_replacements.append(power_string)#识别上标
                                except:pass
                            else: raise ValueError(f'invalid function {func}')
                            i = end_index + 1#跳过原本函数结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append(r'\times')#添加乘法标识
                        case r'\FACT':#分解质因子
                            operator_replacements.append(r'\FACT')#添加分解质因子标识
                            if string[start_index] == '(':#如果是括号
                                end_index = latexcut.find_matching_braces(string, start_index, '()')
                                operator_replacements.append(string[start_index+1:end_index -1])#识别分解质因子表达式
                                i = end_index
                                if i < len(string):#如果不是运算块末尾
                                    operator_replacements.append(r'\times')#添加乘法标识
                            else: raise ValueError('invalid function FACT')
                        case r'\det':
                            raise ValueError("常规模式暂不支持行列式运算")
                        case r'\dim':
                            raise ValueError("常规模式暂不支持矩阵维度运算")
                        case r'\gcd':#最大公约数，辗转相除
                            operator_replacements.append(r'\gcd')#添加辗转相除函数标识
                            gcd_string = string[start_index:]
                            start_braces_index = latexcut.find_character_position(gcd_string,'(')#找到第一个括号
                            if start_braces_index != -1:
                                end_index = latexcut.find_matching_braces(gcd_string,start_braces_index,'()')#找到对应括号
                                comma_index = gcd_string.find(',')#找逗号
                                operator_replacements.append(gcd_string[start_braces_index+1:comma_index])#切出式子1
                                operator_replacements.append(gcd_string[comma_index+1:end_index-1])#切出式子2
                            else: raise ValueError("invalid func gcd")#无辗转相除式，立刻报错
                            i = end_index + 4#跳过原本函数结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append(r'\times')#添加乘法标识
                        case r'\hom':
                            raise ValueError("你觉得这个计算器能算范畴论吗？(恼)")
                        case r'\max'|r'\sup':#最大值
                            operator_replacements.append(r'\max')#添加最大值标识
                            if string[start_index] == '{':
                                end_index = latexcut.find_matching_braces(string, start_index + 1, '{}')#找表达式的}对应位置
                                min_string = string[start_index + 2:end_index-1]#切出集合
                                parts = min_string.split(',')#切出集合元素
                                for part in parts:
                                    operator_replacements.append(part)#识别每个数字
                            else: raise ValueError("invalid number")#无表达式，立刻报错
                            i = end_index#跳过原本函数结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append(r'\times')#添加乘法标识
                        case r'\ker':
                            raise ValueError("暂不支持矩阵核运算")
                        case r'\Ran'|r'\Rnd'|r'\Ranint':
                            raise ValueError("暂不支持随机数运算")
                        case r'\inf'|r'\min':#最小值
                            operator_replacements.append(r'\min')#添加最小值标识
                            if string[start_index+1] == '{':
                                end_index = latexcut.find_matching_braces(string, start_index + 1, '{}')#找表达式的}对应位置
                                min_string = string[start_index + 2:end_index-1]#切出集合
                                parts = min_string.split(',')#切出集合元素
                                for part in parts:
                                    operator_replacements.append(part)#识别每个数字
                            else: raise ValueError("invalid number")#无表达式，立刻报错
                            i = end_index + 1#跳过原本函数结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append(r'\times')#添加乘法标识
                        case r'\Pr':
                            raise ValueError("请使用C,P,A上下标格式计算排列组合")
                        case r'\abs':
                            operator_replacements.append(r'\abs')#添加绝对值标识
                            if string[start_index] == '(':#如果是括号
                                end_index = latexcut.find_matching_braces(string, start_index - 1, '()')
                                operator_replacements.append(string[start_index+1:end_index-1])#识别绝对值表达式
                                i = end_index
                                if i < len(string):#如果不是运算块末尾
                                    operator_replacements.append(r'\times')#添加乘法标识
                            else: raise ValueError("invalid func abs")#无绝对值式，立刻报错
                        case _ if string[i:start_index] in latexcut.GH_letters: 
                            operator_replacements.append(string[i:start_index])#识别希腊字母
                            continue
                case r'(':#括号
                    end_index = latexcut.find_matching_braces(string, i, '()')#找到括号对应)位置，如果没有则报错
                    operator_replacements.append(string[i+1:end_index-1])#把整个括号添加到替换列表中
                    i = end_index#跳过原本括号结构
                    if i < len(string):#如果不是运算块末尾
                        operator_replacements.append(r'\times')#添加乘法标识
                    continue
                case r'{':#大括号
                    end_index = latexcut.find_matching_braces(string, i, '{}')#找到括号对应}位置，如果没有则报错
                    operator_replacements.append(string[i+1:end_index-1])#把整个括号添加到替换列表中
                    i = end_index + 1#跳过原本括号结构
                    if i < len(string):#如果不是运算块末尾
                        operator_replacements.append(r'\times')#添加乘法标识
                    continue
                case r'^':#幂次
                    if operator_replacements[-1] == r'\times':#如果之前标记上了乘法
                        operator_replacements[-1] = r'^'#替换为幂次
                    else:operator_replacements.append(r'^')#添加幂次标识，幂次无需添加乘法标识
                    i += 1
                    continue
                # case r'|':#绝对值
                #     operator_replacements.append('\absolute')#添加绝对值标识，绝对值无需添加乘法标识
                #     absolute_string = string[i + 1:]#获取绝对值字符串
                #     end_index = i + latexcut.find_character_position(absolute_string, '|')#找到绝对值对应)位置，如果没有则报错
                #     if end_index != i-1:
                #         operator_replacements.append(string[i:end_index])
                #     else:raise ValueError("invalid absolute value expression")
                #     i = end_index + 1#跳过原本绝对值结构
                #     if i < len(string):#如果不是运算块末尾
                #         operator_replacements.append('\times')#添加乘法标识
                #     continue
                case r'C'|r'P'|r'A':#排列组合符号
                    operator_replacements.append(string[i])#添加排列组合运算符
                    match string[i+1]:
                            case '_':#下标
                                if i+2 < len(string):
                                    if string[i+2] == '{':#非单字符下标
                                        end_down_index = latexcut.find_matching_braces(string, i + 2, '{}')#找下标对应的}位置
                                        operator_replacements.append(string[i+3:end_down_index])#识别排列组合下标
                                    else:
                                        end_down_index = i + 2#单字符下标
                                        operator_replacements.append(string[i+2])#识别排列组合下标
                                if end_down_index + 2 < len(string):
                                    if string[end_down_index + 1] == '^':#下标后有上标
                                        if string[end_down_index + 2] == '{':#非单字符
                                            end_index = latexcut.find_matching_braces(string, end_down_index + 2, '{}')#找到对应的右括号
                                            if end_up_index == -1:
                                                raise ValueError("missing ')'")
                                            operator_replacements.append(string[end_down_index + 3:end_up_index-1])
                                        else:#单字符
                                            end_index = end_down_index + 2
                                            operator_replacements.append(string[end_down_index + 2])#识别上标
                                else:raise ValueError("invalid combinatorics calculation")#下标后无上标，报错
                                i = end_index + 1#跳过该字符
                                if i < len(string):#如果不是运算块末尾
                                    operator_replacements.append(r'\times')#添加乘法标识
                                continue 
                            case '^':#上标,先上标后下标的字母写法是被允许的
                                if i+2 < len(string):#如果不是末尾
                                    if string[i+2] == '{':#非单字符上标
                                        end_up_index = latexcut.find_matching_braces(string, i + 2, '{}')#找上标对应的}位置
                                        power_string = string[i+3:end_index-1]#切出上标 
                                    else:#单字符上标
                                        end_up_index = i + 2
                                        power_string = string[i+2]#切出上标
                                if end_up_index + 1 < len(string):#如果不是末尾
                                    if string[end_up_index+1] == '_':#如果后面还有下标
                                        if end_up_index+2 < len(string) and string[end_up_index+2] == '{':#非单字符下标
                                            end_index = latexcut.find_matching_braces(string, end_up_index + 2, '{}')#找下标对应的}位置
                                            operator_replacements.append(string[end_up_index+3:end_index])#识别下标
                                            operator_replacements.append(power_string)#添加上标
                                        else:
                                            end_index = end_up_index + 2
                                            operator_replacements.append(string[end_index])#识别下标
                                            operator_replacements.append(power_string)#添加上标
                                    else:raise ValueError("invalid combinatorics calculation")#没有下标，报错
                                i = end_index + 1#跳过原本根式结构
                                if i < len(string):#如果不是运算块末尾
                                    operator_replacements.append(r'\times')#添加乘法标识
                                continue
                            case _:#没有上下标
                                raise ValueError("invalid variable")#报错
                case _ if string[i].isnumeric():#数字,包括小数
                    start_index = i
                    while i < len(string) and (string[i].isnumeric() or string[i] == '.'):#如果后面还有数字，就一直添加
                        i += 1
                    else: end_index = i
                    num_string = string[start_index:end_index]
                    if end_index < len(string):#如果不是末尾
                        if string[end_index] == '!':#识别阶乘
                            if '.' not in num_string:#如果不是小数
                                i+=1#跳过!
                                operator_replacements.append(r'\factorial')#添加阶乘标识
                            else:
                                raise ValueError("invalid factorial")
                        elif string[end_index] == r'E':#科学计数法
                            if end_index+1 >= len(string):raise ValueError("invalid scientific notation")
                            SN_index = len(string)#初始赋值为末尾
                            for i in range(end_index+1,len(string)):#遍历，寻找计数法的末尾
                                if i== end_index+1 and string[i] in ['+','-']:#允许第一个为负号
                                    continue
                                elif i == len(string)-1:#如果遍历完
                                    SN_index = len(string)-1
                                elif string[i].isdigit():#数字继续遍历
                                    continue
                                else:#遇到非数字，结束遍历
                                    SN_index = i-1
                                    break
                            SN_string = string[end_index:SN_index+1]#获取科学计数法字符串
                            end_index = SN_index + 1
                        elif string[end_index] == r'%':#百分号
                            SN_string = 'E-2'#记作10^-2
                            end_index += 1
                    try:#如果存在科学计数法
                        if SN_string:
                            operator_replacements.append(num_string + SN_string)#添加科学计数法,没有则跳过，无视报错
                    except:operator_replacements.append(string[start_index:end_index])#添加数字
                    i = end_index + 1
                    if i < len(string):#如果不是运算块末尾
                        operator_replacements.append(r'\times')#添加乘法标识
                    continue
                case _ if string[i].isalpha():#字母，允许上下标顺序自由
                    if i+1 < len(string):#如果不是最后一个字符
                        match string[i+1]:
                            case '_':#下标
                                if i+2 < len(string):
                                    if string[i+2] == '{':#非单字符下标
                                        end_index = latexcut.find_matching_braces(string, i + 2, '{}')#找下标对应的}位置
                                        operator_replacements.append(string[i:end_index])#识别字母
                                        i = end_index#跳过该字符
                                    else:
                                        end_index = i + 2
                                        operator_replacements.append(string[i:i+3])#识别字母
                                        i = end_index#跳过该字符
                            case '^':#上标,先上标后下标的字母写法是被允许的
                                if i+2 < len(string):#如果不是末尾
                                    if string[i+2] == '{':#非单字符上标
                                        end_up_index = latexcut.find_matching_braces(string, i + 2, '{}')#找上标对应的}位置
                                        power_string = string[i+3:end_index]#切出上标 
                                    else:#单字符上标
                                        end_up_index = i + 2
                                        power_string = string[i+2]#切出上标
                                if end_up_index + 1 < len(string):#如果不是末尾
                                    if string[end_up_index+1] == '_':#如果后面还有下标
                                        if end_up_index+2 < len(string) and string[end_up_index+2] == '{':#非单字符下标
                                            end_index = latexcut.find_matching_braces(string, end_up_index + 2, '{}')#找下标对应的}位置
                                            operator_replacements.append(string[i]+string[end_up_index+1:end_index])#识别字母以及对应下标
                                            operator_replacements.append('^')#添加幂次标识
                                            operator_replacements.append(power_string)#添加幂次
                                        else:
                                            end_index = end_up_index + 2
                                            operator_replacements.append(string[i]+'_'+string[end_index])#识别字母以及对应下标
                                            operator_replacements.append('^')#添加幂次标识
                                            operator_replacements.append(power_string)#添加幂次    
                            case _:#没有上下标
                                operator_replacements.append(string[i])#识别字母
                                end_index = i
                    else:
                        operator_replacements.append(string[i])#识别字母
                        end_index = i
                    i = end_index + 1#跳过该字符
                    if i < len(string):#如果不是运算块末尾
                        operator_replacements.append(r'\times')#添加乘法标识
                    continue
        return operator_replacements

class AbsProcessor:
    def __init__(self):
        self.pipe_stack = []  # 记录未匹配的 | 位置
        self.brace_stacks = {"()": 0, "[]": 0, "{}": 0}  # 记录括号层级

    def process(self, s: str) -> str:
        chars = list(s)
        output = []
        i = 0
        while i < len(chars):
            c = chars[i]
            # 更新括号栈状态
            match c:
                case "(":
                    self.brace_stacks["()"] += 1
                case ")":
                    if self.brace_stacks["()"] == 0:
                        raise ValueError("Mismatched parentheses")
                    self.brace_stacks["()"] -= 1
                case "[":
                    self.brace_stacks["[]"] += 1
                case "]":
                    if self.brace_stacks["[]"] == 0:
                        raise ValueError("Mismatched brackets")
                    self.brace_stacks["[]"] -= 1
                case "{":
                    self.brace_stacks["{}"] += 1
                case "}":
                    if self.brace_stacks["{}"] == 0:
                        raise ValueError("Mismatched braces")
                    self.brace_stacks["{}"] -= 1
            
            # 处理绝对值符号 |（仅在括号栈为0时允许匹配）
            if c == "|" and not self.brace_stacks["()"] and not self.brace_stacks["[]"] and not self.brace_stacks["{}"]:
                if not self.pipe_stack:
                    # 外层 | 入栈
                    self.pipe_stack.append(i)
                else:
                    # 匹配到外层 |，替换为 \abs()
                    start = self.pipe_stack.pop()
                    content = "".join(chars[start+1:i])
                    # 递归处理内部可能存在的嵌套绝对值
                    content = self.process(content)  # 关键点：递归处理
                    # 替换起始 | 和结束 | 之间的内容
                    output.append("\\abs(")
                    output.extend(list(content))
                    output.append(")")
                    i += 1  # 跳过原结束 |
                    continue
            
            # 处理括号内的绝对值符号
            if c == "(" or c == "[" or c == "{":
                # 找到匹配的括号结束位置
                brace_type = c + {")": "(", "]": "[", "}": "{"}[c]
                end_index = latexcut.find_matching_braces(s, i, brace_type)
                if end_index == -1:
                    raise ValueError(f"Mismatched {brace_type}")
                
                # 递归处理括号内的内容
                inner_content = s[i+1:end_index-1]
                processed_inner_content = self.process(inner_content)
                
                # 添加处理后的括号内容
                output.append(c)
                output.extend(processed_inner_content)
                output.append({")": "(", "]": "[", "}": "{"}[c])
                
                i = end_index  # 跳过已处理的括号内容
                continue

            if not self.pipe_stack:# 如果绝对值栈为空，才添加原字符
                output.append(c)
            i += 1
        return "".join(output)

if __name__ == "__main__":
    root = tk.Tk()
    calculator = CasioCalculator(root)
    root.mainloop()