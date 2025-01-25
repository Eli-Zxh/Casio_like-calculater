import tkinter as tk
import subprocess
import shlex
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class CasioCalculator:
    GH_letters = ['\alpha','\beta','\chi','\delta','\epsilon','\eta','\gamma','\iota',
                  '\kappa','\lambda','\mu','\nu','ο','\omega','\phi','\pi',
                  '\psi','\rho','\sigma','\tau','\theta','upsilon','\xi','\zeta',
                  '\digamma','\varepsilon','\varkappa','\varphi','\varpi','\varrho','\varsigma','\vartheta',
                  '\Delta','\Gamma','\Lambda','\Omega','\Phi','\Pi','\Psi','\Sigma',
                  '\Theta','\Upsilon','\Xi','\aleph','\beth','daleth','\gimel']
    math_constructs = ['\frac',"f'",'\sqrt',
                       '\overline','\underline','\widehat','\widetilde',
                       '\overrightarrow','\overleftarrow','\overbrace','\underbrace']
    delimiters = ['|','\vert','\|','\vert','\Vert',#竖线
                  '\{','\}','\langle','\rangle',#左右括号
                  '\lfloor','\rfloor',
                  '\lceil','\rceil',
                  '/','\backslash',
                  '[',']',
                  '\Uparrow','\Downarrow','\uparrow','\downarrow',
                  '\llcorner','\lrcorner',
                  '\ulcorner','\urcorner']
    variables_sized_symbols = ['\sum','\prod','\coprod','\int','\oint','\iint',
                               '\biguplus','\bigcap','\bigcup',
                               '\bigoplus','\bigotimes','\bigodot',
                               '\bigvee','\bigwedge','\bigsqcup']
    standard_function_names = ['\arccos','\arcsin','\arctan','arg'
                               '\cos','\cosh','\cot','\coth',
                               '\csc','\deg','\det','\dim',
                               '\exp','\gcd','\hom','\inf',
                               '\ker','\lg','\lim','\liminf',
                               '\limsup','\ln','\log','\max',
                               '\min','\Pr','\sec','\sin',
                               '\sinh','\sup','\tan','tanh']
    binary_operators_symbols = ['\ast', '\pm', '\cap', '\lhd', '\star', '\mp', '\cup', '\rhd', '\cdot', '\amalg', '\uplus', '\triangleleft', '\circ', '\odot', '\sqcap', '\triangleright', '\bullet', '\ominus', '\sqcup', '\unlhd', '\bigcirc', '\oplus', '\wedge', '\unrhd', '\diamond', '\oslash', '\vee', '\bigtriangledown', '\times', '\otimes', '\dagger', '\bigtriangleup', '\div', '\wr', '\ddagger', '\setminus', '\centerdot', '\Box', '\barwedge', '\veebar', '\circledast', '\boxplus', '\curlywedge', '\curlyvee', '\circledcirc', '\boxminus', '\Cap', '\Cup', '\circleddash', '\boxtimes', '\bot', '\top', '\dotplus', '\boxdot', '\intercal', '\rightthreetimes', '\divideontimes', '\square', '\doublebarwedge', '\leftthreetimes', '\equiv', '\leq', '\geq', '\perp', '\cong', '\prec', '\succ', '\mid', '\neq', '\preceq', '\succeq', '\parallel', '\sim', '\ll', '\gg', '\bowtie', '\simeq', '\subset', '\supset', '\Join', '\approx', '\subseteq', '\supseteq', '\ltimes', '\asymp', '\sqsubset', '\sqsupset', '\rtimes', '\doteq', '\sqsubseteq', '\sqsupseteq', '\smile', '\propto', '\dashv', '\vdash', '\frown', '\models', '\in', '\ni', '\notin', '\approxeq', '\leqq', '\geqq', '\lessgtr', '\thicksim', '\leqslant', '\geqslant', '\lesseqgtr', '\backsim', '\lessapprox', '\gtrapprox', '\lesseqqgtr', '\backsimeq', '\lll', '\ggg', '\gtreqqless', '\triangleq', '\lessdot', '\gtrdot', '\gtreqless', '\circeq', '\lesssim', '\gtrsim', '\gtrless', '\bumpeq', '\eqslantless', '\eqslantgtr', '\backepsilon', '\Bumpeq', '\precsim', '\succsim', '\between', '\doteqdot', '\precapprox', '\succapprox', '\pitchfork', '\thickapprox', '\Subset', '\Supset', '\shortmid', '\fallingdotseq', '\subseteqq', '\supseteqq', '\smallfrown', '\risingdotseq', '\sqsubset', '\sqsupset', '\smallsmile', '\varpropto', '\preccurlyeq', '\succcurlyeq', '\Vdash', '\therefore', '\curlyeqprec', '\curlyeqsucc', '\vDash', '\because', '\blacktriangleleft', '\blacktriangleright', '\Vvdash', '\eqcirc', '\trianglelefteq', '\trianglerighteq', '\shortparallel', '\neq', '\vartriangleleft', '\vartriangleright', '\nshortparallel', '\ncong', '\nleq', '\ngeq', '\nsubseteq', '\nmid', '\nleqq', '\ngeqq', '\nsupseteq', '\nparallel', '\nleqslant', '\ngeqslant', '\nsubseteqq', '\nshortmid', '\nless', '\ngtr', '\nsupseteqq', '\nshortparallel', '\nprec', '\nsucc', '\subsetneq', '\nsim', '\npreceq', '\nsucceq', '\supsetneq', '\nVDash', '\precnapprox', '\succnapprox', '\subsetneqq', '\nvDash', '\precnsim', '\succnsim', '\supsetneqq', '\nvdash', '\lnapprox', '\gnapprox', '\varsubsetneq', '\ntriangleleft', '\lneq', '\gneq', '\varsupsetneq', '\ntrianglelefteq', '\lneqq', '\gneqq', '\varsubsetneqq', '\ntriangleright', '\lnsim', '\gnsim', '\varsupsetneqq', '\ntrianglerighteq', '\lvertneqq', '\gvertneqq']
    arrow_symbols = ['\leftarrow', '\longleftarrow', '\uparrow', '\Leftarrow', '\Longleftarrow', '\Uparrow', '\rightarrow', '\longrightarrow', '\downarrow', '\Rightarrow', '\Longrightarrow', '\Downarrow', '\leftrightarrow', '\longleftrightarrow', '\updownarrow', '\Leftrightarrow', '\Longleftrightarrow', '\Updownarrow', '\mapsto', '\longmapsto', '\nearrow', '\hookleftarrow', '\hookrightarrow', '\searrow', '\leftharpoonup', '\rightharpoonup', '\swarrow', '\leftharpoondown', '\rightharpoondown', '\nwarrow', '\rightleftharpoons', '\leadsto', '\dashrightarrow', '\dashleftarrow', '\leftleftarrows', '\leftrightarrows', '\Lleftarrow', '\twoheadleftarrow', '\leftarrowtail', '\looparrowleft', '\leftrightharpoons', '\curvearrowleft', '\circlearrowleft', '\Lsh', '\upuparrows', '\upharpoonleft', '\downharpoonleft', '\multimap', '\leftrightsquigarrow', '\rightrightarrows', '\rightleftarrows', '\rightrightarrows', '\rightleftarrows', '\twoheadrightarrow', '\rightarrowtail', '\looparrowright', '\rightleftharpoons', '\curvearrowright', '\circlearrowright', '\Rsh', '\downdownarrows', '\upharpoonright', '\downharpoonright', '\rightsquigarrow', '\nleftarrow', '\nrightarrow', '\nLeftarrow', '\nRightarrow', '\nleftrightarrow', '\nLeftrightarrow']
    miscellaneous_symbols = ['\infty', '\forall', '\Bbbk', '\wp', '\nabla', '\exists', '\bigstar', '\angle', '\partial', '\nexists', '\diagdown', '\measuredangle', '\eth', '\emptyset', '\diagup', '\sphericalangle', '\clubsuit', '\varnothing', '\Diamond', '\complement', '\diamondsuit', '\imath', '\Finv', '\triangledown', '\heartsuit', '\jmath', '\Game', '\triangle', '\spadesuit', '\ell', '\hbar', '\vartriangle', '\cdots', '\iiiint', '\hslash', '\blacklozenge', '\vdots', '\iiint', '\lozenge', '\blacksquare', '\ldots', '\iint', '\mho', '\blacktriangle', '\ddots', '\sharp', '\prime', '\blacktrinagledown', '\Im', '\flat', '\square', '\backprime', '\Re', '\natural', '\surd', '\circledS']
    math_mode = ['\acute','\bar','\Acute','\Bar'#复杂上下标单独处理
                 '\breve','\check','\Breve','\Check'
                 '\ddot','\dot','\Dot','\Ddot'
                 '\grave','\hat','\Hat','\Grave'
                 '\tilde','\vec','\Vec','\Tilde']
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
    
    def _setup_operators(string: str):#字符处理切割为运算块
        Parentheses_stack = []
        Square_brackets_stack = []
        Braces_stack = []#三个栈
        positions = []#作为记录递归运算块位置的list
        parts = []#作为最终可识别计算的文件格式，用list存储
        if '#' in string:#不允许出现#号
            ValueError("invalid expression")
        elif ' ' in string:#不允许存在空格
            string = string.replace(' ', '')
        elif '\n' in string:#不允许存在换行符
            string = string.replace('\n', '')
        #第一步，\frac{}{},\sqrt[]{},\sqrt{},()为运算块判定，按照运算块外的+-=分割string
        for index, char in enumerate(string):#用栈的方式，在栈值为0的地方按照+==分割string
            match char:#匹配括号左括号入栈，右括号出栈
                case '(':
                    Parentheses_stack.append(char)
                case '[':
                    Square_brackets_stack.append(char)
                case '{':
                    Braces_stack.append(char)
                case ')':
                    if not Parentheses_stack:
                        raise ValueError("Mismatched parentheses")
                    Parentheses_stack.pop()
                case ']':
                    if not Square_brackets_stack:
                        raise ValueError("Mismatched brackets")
                    Square_brackets_stack.pop()
                case '}':
                    if not Braces_stack:
                        raise ValueError("Mismatched braces")
                    Braces_stack.pop()
                case '+'|'-'|'=':
                    if not Parentheses_stack and not Square_brackets_stack and not Braces_stack:#在栈为空的地方，按照+==分割string
                        positions.append(index)# 记录符号的位置
            if not index:
                positions.append(0)#记录第一个符号的位置
            if index == len(string) - 1:
                positions.append(len(string))#添加最后一个部分
                if Parentheses_stack or Square_brackets_stack or Braces_stack:
                    raise ValueError("Mismatched braces")#最后做一次括号判断，栈不为空则报错
        for i,item in enumerate(positions):
            if item:
                parts.append(string[positions[i - 1] + 1:positions[i]])#分割字符串，添加到parts中
        return parts
        
    def _setup_special(string: str):
        #第二步，对于每个分割的部分，做运算块判定，对满足运算块判定的部分去运算块重复第一步
        i = 0
        operator_replacements = []
        while i < len(string):
            match string[i]:
                case '\\':
                    match string[i:i+5]:
                        case r'\frac': #分式
                            operator_replacements.append(r'\frac')#标识为分式
                            if string[i+5] == '{':#找第一个括号{}，如果没有，立刻报错
                                end_index = find_matching_braces(string, i + 5, '{}')#找第一个括号对应的}位置
                                if end_index != -1 and string[end_index + 1] == '{':#找分式的第二个括号{}，如果没有，立刻报错
                                    operator_replacements.append(string[i+6:end_index-1])#识别分子
                                    end_index2 = find_matching_braces(string, end_index + 1, '{}')#找第二个括号对应的}位置,如果没有，立刻报错
                                    if end_index2 != -1:
                                        operator_replacements.append(string[end_index+2:end_index2-1])#识别分母
                                        # string = string[:i] + '#'* (end_index - i + 1) + string[end_index + 1:]#替换为#占位
                                        # i = end_index + 1#跳过原本分式结构
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
                                    end_index = find_matching_braces(string, i + 5, '[]')#找根式幂次的]对应位置
                                    if end_index != -1 and string[end_index + 1] == '{' and string[i+6,end_index-1].isdigit():#找根式幂次对应的括号，判断根式是否为数字，判断下一个字符为根式括号，如不满足立刻报错
                                        operator_replacements.append(string[i+6:end_index-1])#识别根式幂次
                                        end_index2 = find_matching_braces(string, end_index + 1, '{}')#找根式表达式括号}对应位置，如果没有，立刻报错
                                        if end_index != -1:
                                            operator_replacements.append(string[end_index + 2:end_index2-1])#识别根式
                                            # string = string[:i] + '#'* (end_index - i + 1) + string[end_index + 1:]#替换为#占位
                                            # i = end_index + 1#跳过原本根式结构
                                            continue
                                        else:
                                            raise ValueError("invalid expression")
                                    else: raise ValueError("invalid expression")
                                case '{':#二次根式
                                    operator_replacements.append('2')#识别为二次根式
                                    end_index = find_matching_braces(string, i + 5, '{}')#找根式表达式的}对应位置
                                    if end_index != -1:#找根式幂次对应的括号，如不满足立刻报错
                                        operator_replacements.append(string[i+6:end_index-1])#把整个根式添加到替换列表中
                                        # string = string[:i] + '#'* (end_index - i + 1) + string[end_index + 1:]#替换为#占位
                                        # i = end_index + 1#跳过原本根式结构
                                        continue
                                    else: raise ValueError("invalid expression")
                                case _: raise ValueError("invalid expression")#根式后无{}或者[]，立刻报错
                        case _: 
                            i += 2 #不属于这三类运算块，跳过次运算块
                            continue
                case  r'(':#括号
                    end_index = find_matching_braces(string, i, '()')#找到括号对应)位置，如果没有则报错
                    if end_index != -1:
                        operator_replacements.append(string[i+1:end_index-1])#把整个括号添加到替换列表中
                        # string = string[:i] + '#' * (end_index - i + 1) + string[end_index + 1:]#替换为#占位
                        # i = end_index + 1#跳过原本括号结构
                        continue
                    else:
                        raise ValueError("invalid expression")
        return operator_replacements
    
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
def find_matching_braces(s, start, brace_type='{}'):#匹配括号,s为字符串，start为起始位置，brace_type为括号类型，返回匹配的括号位置
            stack = []
            brace_map = {'(': ')', '[': ']', '{': '}'}
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

if __name__ == "__main__":
    root = tk.Tk()
    calculator = CasioCalculator(root)
    root.mainloop()