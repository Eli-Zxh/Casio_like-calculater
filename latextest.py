GH_letters = [r'\alpha',r'\beta',r'\chi',r'\delta',r'\epsilon',r'\eta',r'\gamma',r'\iota',
                  r'\kappa',r'\lambda',r'\mu',r'\nu',r'ο',r'\omega',r'\phi',r'\pi',
                  r'\psi',r'\rho',r'\sigma',r'\tau',r'\theta',r'upsilon',r'\xi',r'\zeta',
                  r'\digamma',r'\varepsilon',r'\varkappa',r'\varphi',r'\varpi',r'\varrho',r'\varsigma',r'\vartheta',
                  r'\Delta',r'\Gamma',r'\Lambda',r'\Omega',r'\Phi',r'\Pi',r'\Psi',r'\Sigma',
                  r'\Theta',r'\Upsilon',r'\Xi',r'\aleph',r'\beth',r'daleth',r'\gimel',r'\infty',r'+\infty',r'-\infty']
special_operators = [r'\frac',r'\sqrt',r'\int',r'\sum',r'\prod',r'\log',r'\lim',r'\limsup',r'\liminf',r'\sin',r'\cos',r'\tan',
                    r'\sec',r'\csc',r'\cot',r'\sinh',r'\cosh',r'\tanh',r'\arcsin',r'\arccos',r'\arctan',r'\exp',r'\ln',r'\lg',
                    r'\arg',r'\coth',r'\deg',r'\det',r'\dim',r'\gcd',r'\hom',r'\max',r'\sup',r'\ker',r'\inf',r'\min',r'\Pr',r'\abs']
operators = [r'+', r'-', r'=', r'\div', r'\times', r'\cdot',r'^']

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
                case "|":
                    if not self.pipe_stack:#外层入栈
                        self.pipe_stack.append((i,self.brace_stacks["()"],self.brace_stacks["[]"],self.brace_stacks["{}"]))
                    else:
                        start,a,b,c = self.pipe_stack[-1]#提取上一个 | 的状态
                        if self.brace_stacks["()"] == a and self.brace_stacks["[]"] == b and self.brace_stacks["{}"] == c:
                            self.pipe_stack.pop()# 匹配到内层 |，替换为 \abs()
                            output[start] = "\\abs("
                            output.append(")")
                            i += 1# 跳过原结束 |
                            continue
                        else:
                            self.pipe_stack.append((i,self.brace_stacks["()"],self.brace_stacks["[]"],self.brace_stacks["{}"]))
            output.append(c)# 如果绝对值栈为空，才添加原字符
            i += 1
        if self.pipe_stack or self.brace_stacks["()"] or self.brace_stacks["[]"] or self.brace_stacks["{}"]:raise ValueError("Mismatched absolute expression")#任何一个栈不为空，则报错，‘四大皆空’
        return "".join(output)

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
                    string[index-1] in operators + ['(', '[', '{', 'E'] or
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
'''
def _setup_special(string: str):
    i = 0
    operator_replacements = []
    GH_letters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

    while i < len(string):
        match string[i]:
            case '-':
                operator_replacements.append('-')
                i += 1
                continue
            case '\\':
                if i + 6 <= len(string) and string[i:i + 4] == r'\div':
                    if operator_replacements[-1] == r'\times':
                        operator_replacements[-1] = r'\div'
                    else:
                        operator_replacements.append(r'\div')
                    i += 4
                    continue
                elif i + 6 < len(string) and string[i:i + 5] == r'\cdot':
                    if operator_replacements[-1] == r'\times':
                        operator_replacements[-1] = r'\cdot'
                    else:
                        operator_replacements.append(r'\cdot')
                    i += 5
                    continue
                elif i + 6 < len(string) and string[i:i + 6] == r'\times':
                    if operator_replacements[-1] != r'\times':
                        operator_replacements.append(r'\times')
                    i += 6
                    continue
                start_index = find_start_position(string, i)
                match string[i:start_index]:
                    case r'\frac':
                        handle_fraction(string, i, operator_replacements)
                    case r'\sqrt':
                        handle_sqrt(string, i, operator_replacements)
                    case r'\int':
                        handle_integral(string, i, operator_replacements)
                    case r'\sum'|r'\prod':
                        handle_sum_prod(string, i, operator_replacements)
                    case r'\log':
                        handle_log(string, i, operator_replacements)
                    case r'\lim'|r'\limsup'|r'\liminf':
                        handle_limit(string, i, operator_replacements)
                    case r'\sin'|r'\cos'|r'\tan'|r'\sec'|r'\csc'|r'\cot'|r'\sinh'|r'\cosh'|r'\tanh'|r'\arcsin'|r'\arccos'|r'\arctan'|r'\exp'|r'\ln'|r'\lg'|r'\arg'|r'\coth'|r'\deg'|r'\factorial':
                        handle_trig_functions(string, i, start_index, operator_replacements)
                    case r'\FACT':
                        handle_fact(string, i, operator_replacements)
                    case r'\gcd':
                        handle_gcd(string, i, operator_replacements)
                    case r'\max'|r'\sup':
                        handle_max(string, i, operator_replacements)
                    case r'\min':
                        handle_min(string, i, operator_replacements)
                    case r'\abs':
                        handle_abs(string, i, operator_replacements)
                    case _ if string[i:start_index] in GH_letters:
                        operator_replacements.append(string[i:start_index])
                        continue
            case r'(':
                handle_parentheses(string, i, operator_replacements)
            case r'{':
                handle_braces(string, i, operator_replacements)
            case r'^':
                handle_power(operator_replacements)
            case r'C'|r'P'|r'A':
                handle_combinatorics(string, i, operator_replacements)
            case _ if string[i].isnumeric():
                handle_number(string, i, operator_replacements)
            case _ if string[i].isalpha():
                handle_letter(string, i, operator_replacements)
        i += 1

    return operator_replacements

def handle_fraction(string, i, operator_replacements):
    operator_replacements.append(r'\frac')
    if string[i + 5] == '{':
        end_index = find_matching_braces(string, i + 5, '{}')
        if end_index >= len(string):
            raise ValueError("invalid expression")
        if end_index != -1 and string[end_index] == '{':
            operator_replacements.append(string[i + 6:end_index - 1])
            end_index2 = find_matching_braces(string, end_index, '{}')
            if end_index2 != -1:
                operator_replacements.append(string[end_index + 1:end_index2 - 1])
                if end_index2 < len(string):
                    operator_replacements.append(r'\times')
            else:
                raise ValueError("invalid expression")
        else:
            raise ValueError("invalid expression")
    else:
        raise ValueError("invalid expression")

def handle_sqrt(string, i, operator_replacements):
    operator_replacements.append(r'\sqrt')
    match string[i + 5]:
        case '[':
            end_index = find_matching_braces(string, i + 4, '[]')
            if end_index != -1 and string[end_index] == '{':
                if (i + 6 < end_index - 2 and string[i + 6:end_index - 2].isdigit()) or (i + 6 == end_index - 2 and string[i + 6].isdigit()):
                    operator_replacements.append(string[i + 6:end_index - 1])
                    end_index2 = find_matching_braces(string, end_index - 1, '{}')
                    if end_index2 != -1:
                        operator_replacements.append(string[end_index + 1:end_index2 - 1])
                        if end_index2 < len(string):
                            operator_replacements.append(r'\times')
                    else:
                        raise ValueError("invalid expression")
                else:
                    raise ValueError("invalid expression")
            else:
                raise ValueError("invalid expression")
        case '{':
            operator_replacements.append('2')
            end_index = find_matching_braces(string, i + 5, '{}')
            if end_index != -1:
                operator_replacements.append(string[i + 6:end_index - 1])
                if end_index < len(string):
                    operator_replacements.append(r'\times')
            else:
                raise ValueError("invalid expression")
        case _:
            raise ValueError("invalid expression")

def handle_integral(string, i, operator_replacements):
    operator_replacements.append(r'\int')
    match string[i + 4]:
        case '_' | '^':
            int_string = string[i + 4:]
            down_index = find_character_position(int_string, '_')
            if int_string[down_index + 1] == '{':
                down_end_index = find_matching_braces(int_string, down_index + 1, '{}')
                operator_replacements.append(int_string[down_index + 2:down_end_index - 1])
            elif int_string[down_index + 1].isalpha() or int_string[down_index + 1].isdigit():
                down_end_index = down_index + 2
                operator_replacements.append(int_string[down_index])
            else:
                raise ValueError("invalid down limit")
            up_index = find_character_position(int_string, '^')
            if int_string[up_index + 1] == '{':
                up_end_index = find_matching_braces(int_string, up_index + 1, '{}')
                operator_replacements.append(int_string[up_index + 2:up_end_index - 1])
            elif int_string[up_index + 1].isalpha() or int_string[up_index + 1].isdigit():
                up_end_index = up_index + 2
                operator_replacements.append(int_string[up_index])
            else:
                raise ValueError("invalid up limit")
            tag_index = max(down_end_index, up_end_index)
            int_string = int_string[tag_index:]
        case '{':
            operator_replacements.append('')
            operator_replacements.append('')
            int_string = string[i + 4:]
            tag_index = 0
    expression_index = find_character_position(int_string, '{')
    if expression_index != -1:
        end_index = find_matching_braces(int_string, expression_index, '{}')
        int_string = int_string[expression_index + 1:end_index - 1]
        d_index = find_character_position(int_string, 'd')
        if d_index != -1:
            d_string = int_string[d_index + 1:]
            if d_string[0] == '{' or d_string == '(':
                operator_replacements.append(d_string[1:-1])
            else:
                operator_replacements.append(int_string[d_index + 1:])
        else:
            operator_replacements.append('x')
        operator_replacements.append(int_string[:d_index])
        if end_index + 4 + tag_index < len(string):
            operator_replacements.append(r'\times')
    else:
        raise ValueError("invalid expression")

def handle_sum_prod(string, i, operator_replacements):
    operator_replacements.append(string[i:i + 4])
    sum_string = string[i + 4:]
    down_index = find_character_position(sum_string, '_')
    if down_index != -1:
        if sum_string[down_index + 1] == '{':
            down_end_index = find_matching_braces(sum_string, down_index + 1, '{}')
            if down_end_index == -1:
                raise ValueError("invalid down limit")
            down_expression = sum_string[down_index + 2:down_end_index - 1]
            equal_index = find_character_position(down_expression, '=')
            if equal_index != -1:
                operator_replacements.append(down_expression[:equal_index])
                operator_replacements.append(down_expression[equal_index + 1:])
            else:
                operator_replacements.append(down_expression)
                is_variable = True
                operator_replacements.append('')
        elif sum_string[down_index + 1].isdigit():
            operator_replacements.append('i')
            operator_replacements.append(sum_string[down_index + 1:])
        else:
            raise ValueError("invalid down limit")
    else:
        raise ValueError("invalid down limit")
    up_index = find_character_position(sum_string, '^')
    if up_index != -1:
        if sum_string[up_index + 1] == '{':
            up_end_index = find_matching_braces(sum_string, up_index + 1, '{}')
            if up_end_index == -1:
                raise ValueError("invalid up limit")
            operator_replacements.append(sum_string[up_index + 2:up_end_index - 1])
        elif sum_string[up_index + 1].isalpha() or sum_string[up_index + 1].isdigit():
            operator_replacements.append(sum_string[up_index + 1])
        else:
            raise ValueError("invalid up limit")
    else:
        if is_variable:
            operator_replacements.append('')
        else:
            raise ValueError("invalid up limit")
    end_index = max(down_end_index, up_end_index)
    sum_string = sum_string[end_index:]
    expression_index = find_character_position(sum_string, '{')
    if expression_index != -1:
        expr_end_index = find_matching_braces(sum_string, expression_index, '{}')
        operator_replacements.append(sum_string[expression_index + 1:expr_end_index - 1])
    else:
        raise ValueError("invalid expression")
    if end_index + i + expr_end_index < len(string):
        operator_replacements.append(r'\times')

def handle_log(string, i, operator_replacements):
    operator_replacements.append(r'\log')
    down_index = find_character_position(string, '_')
    if down_index != -1:
        if string[down_index + 1] == '{':
            end_index = find_matching_braces(string, down_index, '{}')
            operator_replacements.append(string[down_index + 2:end_index - 1])
        else:
            operator_replacements.append(string[down_index])
    else:
        operator_replacements.append('10')
    start_braces_index = find_character_position(string, '(')
    if start_braces_index != -1:
        end_index = find_matching_braces(string, start_braces_index, '()')
        operator_replacements.append(string[start_braces_index + 1:end_index - 1])
    else:
        raise ValueError(f'invalid function log')
    if end_index + 1 < len(string):
        operator_replacements.append(r'\times')

def handle_limit(string, i, operator_replacements):
    operator_replacements.append(r'\lim')
    down_index = find_character_position(string, '_')
    if down_index != -1:
        if string[down_index + 1] == '{':
            down_end_index = find_matching_braces(string, down_index + 1, '{}')
            down_expression = string[down_index + 2:down_end_index - 1]
            index = down_expression.find(r'\rightarrow')
            if index != -1:
                operator_replacements.append(down_expression[:index])
                operator_replacements.append(down_expression[index + 11:])
            else:
                raise ValueError("invalid down limit")
            lim_expression = string[down_end_index:]
            if lim_expression[0] == '{':
                end_index = find_matching_braces(lim_expression, 0, '{}')
                if end_index == -1:
                    raise ValueError("invalid expression")
                operator_replacements.append(lim_expression[1:end_index - 1])
            else:
                raise ValueError("invalid expression")
        else:
            raise ValueError("invalid down limit")
    else:
        raise ValueError("invalid limit")
    if end_index + down_end_index < len(string):
        operator_replacements.append(r'\times')

def handle_trig_functions(string, i, start_index, operator_replacements):
    func = string[i:start_index]
    operator_replacements.append(func)
    if string[start_index + 1] == '^':
        if string[start_index + 2] == '{':
            end_up_index = find_matching_braces(string, start_index + 2, '{}')
            power_string = string[start_index + 3:end_up_index - 1]
        else:
            end_up_index = start_index + 2
            power_string = string[start_index + 2]
    start_braces_index = find_character_position(string, '(')
    if start_braces_index != -1:
        end_index = find_matching_braces(string, start_braces_index, '()')
        operator_replacements.append(string[start_braces_index + 1:end_index - 1])
        try:
            if power_string:
                operator_replacements.append('^')
                operator_replacements.append(power_string)
        except:
            pass
    else:
        raise ValueError(f'invalid function {func}')
    if end_index + 1 < len(string):
        operator_replacements.append(r'\times')

def handle_fact(string, i, operator_replacements):
    operator_replacements.append(r'\FACT')
    if string[i + 4] == '(':
        end_index = find_matching_braces(string, i + 4, '()')
        operator_replacements.append(string[i + 5:end_index - 1])
        if end_index < len(string):
            operator_replacements.append(r'\times')
    else:
        raise ValueError('invalid function FACT')

def handle_gcd(string, i, operator_replacements):
    operator_replacements.append(r'\gcd')
    gcd_string = string[i + 4:]
    start_braces_index = find_character_position(gcd_string, '(')
    if start_braces_index != -1:
        end_index = find_matching_braces(gcd_string, start_braces_index, '()')
        comma_index = gcd_string.find(',')
        operator_replacements.append(gcd_string[start_braces_index + 1:comma_index])
        operator_replacements.append(gcd_string[comma_index + 1:end_index - 1])
    else:
        raise ValueError("invalid func gcd")
    if end_index + 4 < len(string):
        operator_replacements.append(r'\times')

def handle_max(string, i, operator_replacements):
    operator_replacements.append(r'\max')
    if string[i + 4] == '{':
        end_index = find_matching_braces(string, i + 5, '{}')
        min_string = string[i + 6:end_index - 1]
        parts = min_string.split(',')
        for part in parts:
            operator_replacements.append(part)
    else:
        raise ValueError("invalid number")
    if end_index < len(string):
        operator_replacements.append(r'\times')

def handle_min(string, i, operator_replacements):
    operator_replacements.append(r'\min')
    if string[i + 4] == '{':
        end_index = find_matching_braces(string, i + 5, '{}')
        min_string = string[i + 6:end_index - 1]
        parts = min_string.split(',')
        for part in parts:
            operator_replacements.append(part)
    else:
        raise ValueError("invalid number")
    if end_index + 1 < len(string):
        operator_replacements.append(r'\times')

def handle_abs(string, i, operator_replacements):
    operator_replacements.append(r'\abs')
    if string[i + 4] == '(':
        end_index = find_matching_braces(string, i + 4, '()')
        operator_replacements.append(string[i + 5:end_index - 1])
        if end_index < len(string):
            operator_replacements.append(r'\times')
    else:
        raise ValueError("invalid func abs")

def handle_parentheses(string, i, operator_replacements):
    end_index = find_matching_braces(string, i, '()')
    operator_replacements.append(string[i + 1:end_index - 1])
    if end_index < len(string):
        operator_replacements.append(r'\times')

def handle_braces(string, i, operator_replacements):
    end_index = find_matching_braces(string, i, '{}')
    operator_replacements.append(string[i + 1:end_index - 1])
    if end_index + 1 < len(string):
        operator_replacements.append(r'\times')

def handle_power(operator_replacements):
    if operator_replacements[-1] == r'\times':
        operator_replacements[-1] = r'^'
    else:
        operator_replacements.append(r'^')

def handle_combinatorics(string, i, operator_replacements):
    operator_replacements.append(string[i])  # 添加排列组合运算符
    if i + 1 < len(string):
        match string[i + 1]:
            case '_':  # 下标
                if i + 2 < len(string):
                    if string[i + 2] == '{':  # 非单字符下标
                        end_down_index = find_matching_braces(string, i + 2, '{}')  # 找下标对应的}位置
                        operator_replacements.append(string[i + 3:end_down_index])  # 识别排列组合下标
                    else:
                        end_down_index = i + 2  # 单字符下标
                        operator_replacements.append(string[i + 2])  # 识别排列组合下标
                if end_down_index + 2 < len(string):
                    if string[end_down_index + 1] == '^':  # 下标后有上标
                        if string[end_down_index + 2] == '{':  # 非单字符
                            end_index = find_matching_braces(string, end_down_index + 2, '{}')  # 找到对应的右括号
                            if end_index == -1:
                                raise ValueError("missing ')'")
                            operator_replacements.append(string[end_down_index + 3:end_index - 1])  # 识别上标
                        else:  # 单字符
                            end_index = end_down_index + 2
                            operator_replacements.append(string[end_down_index + 2])  # 识别上标
                else:
                    raise ValueError("invalid combinatorics calculation")  # 下标后无上标，报错
                if end_index < len(string):
                    operator_replacements.append(r'\times')  # 添加乘法标识
            case '^':  # 上标, 先上标后下标的字母写法是被允许的
                if i + 2 < len(string):  # 如果不是末尾
                    if string[i + 2] == '{':  # 非单字符上标
                        end_up_index = find_matching_braces(string, i + 2, '{}')  # 找上标对应的}位置
                        power_string = string[i + 3:end_up_index - 1]  # 切出上标
                    else:  # 单字符上标
                        end_up_index = i + 2
                        power_string = string[i + 2]  # 切出上标
                if end_up_index + 1 < len(string):  # 如果不是末尾
                    if string[end_up_index + 1] == '_':  # 如果后面还有下标
                        if end_up_index + 2 < len(string) and string[end_up_index + 2] == '{':  # 非单字符下标
                            end_index = find_matching_braces(string, end_up_index + 2, '{}')  # 找下标对应的}位置
                            operator_replacements.append(string[end_up_index + 3:end_index])  # 识别下标
                            operator_replacements.append(power_string)  # 添加上标
                        else:
                            end_index = end_up_index + 2
                            operator_replacements.append(string[end_index])  # 识别下标
                            operator_replacements.append(power_string)  # 添加上标
                    else:
                        raise ValueError("invalid combinatorics calculation")  # 没有下标，报错
                if end_index < len(string):
                    operator_replacements.append(r'\times')  # 添加乘法标识
            case _:
                raise ValueError("invalid variable")  # 报错

def handle_number(string, i, operator_replacements):
    start_index = i
    while i < len(string) and (string[i].isnumeric() or string[i] == '.'):
        i += 1
    num_string = string[start_index:i]
    
    if i < len(string):
        if string[i] == '!':  # 识别阶乘
            if '.' not in num_string:  # 如果不是小数
                i += 1  # 跳过 '!'
                operator_replacements.append(num_string)
                operator_replacements.append(r'!')  # 添加阶乘标识
            else:
                raise ValueError("invalid factorial")
        elif string[i] == 'E':  # 科学计数法
            if i + 1 >= len(string):
                raise ValueError("invalid scientific notation")
            SN_index = len(string)  # 初始赋值为末尾
            for j in range(i + 1, len(string)):  # 遍历，寻找计数法的末尾
                if j == i + 1 and string[j] in ['+', '-']:  # 允许第一个为负号
                    continue
                elif j == len(string) - 1:  # 如果遍历完
                    SN_index = len(string) - 1
                elif string[j].isdigit():  # 数字继续遍历
                    continue
                else:  # 遇到非数字，结束遍历
                    SN_index = j - 1
                    break
            SN_string = string[i:SN_index + 1]  # 获取科学计数法字符串
            i = SN_index + 1
            operator_replacements.append(num_string + SN_string)  # 添加科学计数法
        elif string[i] == '%':  # 百分号
            operator_replacements.append(num_string)
            operator_replacements.append(r'\times')  # 添加乘法标识
            operator_replacements.append('0.01')  # 添加百分号转换
            i += 1  # 跳过 '%'
        else:
            operator_replacements.append(num_string)  # 添加数字
    else:
        operator_replacements.append(num_string)  # 添加数字
    
    if i < len(string):  # 如果不是运算块末尾
        operator_replacements.append(r'\times')  # 添加乘法标识
    
    return i

def handle_letter(string, i, operator_replacements):
    if i + 1 < len(string):
        match string[i + 1]:
            case '_':  # 下标
                if i + 2 < len(string):
                    if string[i + 2] == '{':  # 非单字符下标
                        end_index = find_matching_braces(string, i + 2, '{}')  # 找下标对应的}位置
                        if end_index == -1:
                            raise ValueError("invalid subscript")
                        subscript = string[i + 3:end_index - 1]  # 识别下标
                        i = end_index  # 跳过该字符
                    else:
                        subscript = string[i + 2]  # 识别单字符下标
                        i += 2  # 跳过该字符
                else:
                    raise ValueError("invalid subscript")
                operator_replacements.append(f"{string[i]}_{{{subscript}}}")  # 识别字母及下标
            case '^':  # 上标
                if i + 2 < len(string):
                    if string[i + 2] == '{':  # 非单字符上标
                        end_index = find_matching_braces(string, i + 2, '{}')  # 找上标对应的}位置
                        if end_index == -1:
                            raise ValueError("invalid superscript")
                        superscript = string[i + 3:end_index - 1]  # 识别上标
                        i = end_index  # 跳过该字符
                    else:
                        superscript = string[i + 2]  # 识别单字符上标
                        i += 2  # 跳过该字符
                else:
                    raise ValueError("invalid superscript")
                operator_replacements.append(f"{string[i]}^{{{superscript}}}")  # 识别字母及上标
            case _:
                operator_replacements.append(string[i])  # 识别字母
                i += 1  # 跳过该字符
    else:
        operator_replacements.append(string[i])  # 识别字母
        i += 1  # 跳过该字符
    
    if i < len(string):  # 如果不是运算块末尾
        operator_replacements.append(r'\times')  # 添加乘法标识
    
    return i
'''
def _setup_special(string: str):
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
        #第二步，对于每个分割的部分，做运算块判定，对满足运算块判定的部分去运算块重复第一步
        i = 0
        operator_replacements = []
        while i < len(string):
            match string[i]:
                case r'*':#乘号，直接合并到operator_replacements中，记为叉乘，并跳过
                    if operator_replacements[-1] != r'\times':#2.2如果前一个运算符是乘号，则替换为叉乘
                        operator_replacements.append(r'\times')#识别为叉乘
                    else:pass#否则不增加叉乘符号
                    i += 1#2.2跳过乘号
                    continue
                case r'/':#除号，直接合并到operator_replacements中
                    if operator_replacements[-1] == r'\times':#2.2如果前一个运算符是乘号，则替换为除号
                        operator_replacements[-1] = r'\div'#替换为除号
                    else:operator_replacements.append(r'\div')#识别为除号
                    i += 1#2.2跳过除号
                    continue
                case '-'|'+':#正负号，直接合并到operator_replacements中，并跳过，对于正负无穷单独识别
                    try:
                        if i+2 < len(string) and string[i+2] == '\\' and i+7 < len(string) and string[i+3:i+7] == r'\infty':#2.1负无穷
                            operator_replacements.append(string[i]+r'\infty')
                            i += 7
                            continue
                    except:pass
                    operator_replacements.append(string[i])
                    i += 1
                    continue
                case '\\':
                    if i+6 <= len(string) and string[i:i+4] == r'\div':#2.1运算符不能按照find_start_position切开，给予单独判断
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
                    start_index = find_start_position(string, i)#找第一个任意括号，分割运算符函数
                    match string[i:start_index]:
                        case r'\frac': #分式
                            operator_replacements.append(r'\frac')#标识为分式
                            if string[i+5] == '{':#找第一个括号{}，如果没有，立刻报错
                                end_index = find_matching_braces(string, i + 5, '{}')#找第一个括号对应的}位置
                                if end_index >= len(string):raise ValueError("invalid expression")#必须有第二个括号的补丁
                                if end_index != -1 and string[end_index] == '{':#找分式的第二个括号{}，如果没有，立刻报错
                                    operator_replacements.append(string[i+6:end_index-1])#识别分子
                                    end_index2 = find_matching_braces(string, end_index, '{}')#找第二个括号对应的}位置,如果没有，立刻报错
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
                                    end_index = find_matching_braces(string, i + 4, '[]')#找根式幂次的]对应位置
                                    if end_index != -1 and string[end_index] == '{':#找根式幂次对应的括号，判断下一个字符为根式括号，如不满足立刻报错
                                        if (i+6 < end_index-2 and string[i+6:end_index-2].isdigit()) or (i+6 == end_index-2 and string[i+6].isdigit()):#判断根式是否为数字
                                            operator_replacements.append(string[i+6:end_index-1])#识别根式幂次
                                            end_index2 = find_matching_braces(string, end_index -1, '{}')#找根式表达式括号}对应位置，如果没有，立刻报错
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
                                    end_index = find_matching_braces(string, i + 5, '{}')#找根式表达式的}对应位置
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
                                    down_index = find_character_position(int_string,'_')#找积分下限
                                    if int_string[down_index + 1] == '{':#非单字符
                                        down_end_index = find_matching_braces(int_string, down_index + 1, '{}')#找积分下限对应的括号
                                        operator_replacements.append(int_string[down_index + 2:down_end_index-1])#识别积分下限
                                    elif int_string[down_index + 1].isalpha() or int_string[down_index + 1].isdigit():#单字符识别
                                        down_end_index = down_index + 2#下限为单字符
                                        operator_replacements.append(int_string[down_index + 1])
                                    else: raise ValueError("invalid down limit")
                                    up_index = find_character_position(int_string,'^')#找积分上限
                                    if int_string[up_index + 1] == '{':#非单字符
                                        up_end_index = find_matching_braces(int_string, up_index + 1, '{}')#找积分上限对应的括号
                                        operator_replacements.append(int_string[up_index + 2:up_end_index -1])#识别积分上限
                                    elif int_string[up_index + 1].isalpha() or int_string[up_index + 1].isdigit():#单字符识别
                                        up_end_index = up_index + 2
                                        operator_replacements.append(int_string[up_index + 1])
                                    else: raise ValueError("invalid up limit")
                                    tag_index = max(down_end_index,up_end_index)#取下限和上限的最大值
                                    int_string = int_string[tag_index:]
                                case '{':#不定积分
                                    operator_replacements.append('')#下限传空
                                    operator_replacements.append('')#上限传空
                                    int_string = string[i+4:]#切开积分表达式
                                    tag_index = 0#下限和上限为空
                            expression_index = find_character_position(int_string,'{')#找积分表达式，不定积分与定积分处理表达式方式相同
                            if expression_index != -1:
                                end_index = find_matching_braces(int_string, expression_index, '{}')#找积分表达式的}对应位置
                                int_string = int_string[expression_index+1:end_index-1]#切开表达式
                                d_index = find_character_position(int_string,'d')#找微分变量，如果不存在默认为x,如果存在，必须在积分表达式末尾
                                if d_index != -1:#如果为特殊积分变量
                                    d_string = int_string[d_index+1:]#切开积分变量表达式
                                    if d_string[0] == '{' or d_string == '(':
                                        operator_replacements.append(d_string[1:-1])#去括号，识别积分变量
                                    else:operator_replacements.append(int_string[d_index + 1:])#识别积分变量
                                else: 
                                    operator_replacements.append('x')#默认为x
                                    d_index = len(int_string)
                                operator_replacements.append(int_string[:d_index])#识别积分表达式
                                i = end_index + 4 + tag_index#跳过原本积分结构
                                if i < len(string):#如果不是运算块末尾
                                    operator_replacements.append(r'\times')#添加乘法标识
                            else: raise ValueError("invalid expression")#无表达式，立刻报错
                        case r'\sum'|r'\prod':#累加与累乘处理方式相同
                            operator_replacements.append(string[i:start_index])#标识为累加/累乘
                            sum_string = string[start_index:]
                            down_index = find_character_position(sum_string,'_')#找下限
                            if down_index != -1:
                                if sum_string[down_index + 1] == '{':#非单字符
                                    down_end_index = find_matching_braces(sum_string, down_index + 1, '{}')#找下限对应的括号
                                    if down_end_index == -1:raise ValueError("invalid down limit")#无对应的括号，立刻报错
                                    down_expression = sum_string[down_index + 2:down_end_index-1]#单列下限方程
                                    equal_index = find_character_position(down_expression,'=')#找等号
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
                            up_index = find_character_position(sum_string,'^')#找上限
                            if up_index != -1:
                                if sum_string[up_index + 1] == '{':#非单字符
                                    up_end_index = find_matching_braces(sum_string, up_index + 1, '{}')#找上限对应的括号
                                    if up_end_index == -1: raise ValueError("invalid up limit")#不允许没有上限
                                    operator_replacements.append(sum_string[up_index + 2:up_end_index-1])#识别上限
                                elif sum_string[up_index + 1].isalpha() or sum_string[up_index + 1].isdigit():#允许单字符
                                    operator_replacements.append(sum_string[up_index + 1])#识别上限
                                    up_end_index = up_index + 2
                                else: raise ValueError("invalid up limit")
                            else: 
                                if is_variable:operator_replacements.append('')#不定求和记为空
                                else: raise ValueError("invalid up limit")
                            end_index = max(down_end_index,up_end_index)#取下限和上限的最大值
                            sum_string = sum_string[end_index:]
                            expression_index = find_character_position(sum_string,'{')#找表达式,不允许单字符
                            if expression_index != -1:
                                expr_end_index = find_matching_braces(sum_string, expression_index, '{}')#找表达式的}对应位置
                                operator_replacements.append(sum_string[expression_index+1:expr_end_index-1])#识别表达式
                            else: raise ValueError("invalid expression")#无表达式，立刻报错
                            i = end_index + start_index + expr_end_index#跳过原本累加结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append('\times')#添加乘法标识
                        case r'\log':#普通对数函数
                            operator_replacements.append(r'\log')
                            down_index = find_character_position(string, '_')#找下标
                            if down_index != -1:
                                if string[down_index+1] == '{':#多字符
                                    end_index = find_matching_braces(string, down_index, '{}')#找到对应下标括号
                                    operator_replacements.append(string[down_index+2:end_index - 1])#识别底数
                                else: operator_replacements.append(string[down_index])#单字符识别下标
                            else: operator_replacements.append('10')#默认底为10
                            start_braces_index = find_character_position(string,'(')#找真数
                            if start_braces_index != -1:
                                end_index = find_matching_braces(string,start_braces_index,'()')#找到对应括号
                                operator_replacements.append(string[start_braces_index+1:end_index-1])#识别真数
                            else: raise ValueError(f'invalid function log')
                            i = end_index + 1#跳过原本函数结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append(r'\times')#添加乘法标识
                        case r'\lim'|r'\limsup'|r'\liminf':#极限，不区分左右
                            operator_replacements.append(r'\lim')
                            down_index = find_character_position(string, '_')#找下标
                            if down_index != -1:
                                if string[down_index + 1] == '{':#非单字符
                                    down_end_index = find_matching_braces(string, down_index + 1, '{}')#找下限对应的括号
                                    down_expression = string[down_index + 2:down_end_index-1]#单列下限方程
                                    index = down_expression.find(r'\rightarrow')#不允许变量嵌套极限，找右箭头
                                    if index != -1:
                                        operator_replacements.append(down_expression[:index])#识别变量
                                        operator_replacements.append(down_expression[index+11:])#识别下限
                                    else: raise ValueError("invalid down limit")
                                    lim_expression = string[down_end_index:]#切出表达式，直接切分
                                    if lim_expression[0] == '{':
                                        end_index = find_matching_braces(lim_expression, 0, '{}')#找表达式的}对应位置
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
                                    end_up_index = find_matching_braces(string, start_index + 2, '{}')#找上标对应的}位置
                                    power_string = string[start_index + 3:end_up_index-1]#切出上标 
                                else:#单字符上标
                                    end_up_index = start_index + 2
                                    power_string = string[start_index+2]#切出上标
                            start_braces_index = find_character_position(string,'(')#找到第一个括号
                            if start_braces_index != -1:
                                end_index = find_matching_braces(string,start_braces_index,'()')#找到对应括号
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
                                end_index = find_matching_braces(string, start_index, '()')
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
                            start_braces_index = find_character_position(gcd_string,'(')#找到第一个括号
                            if start_braces_index != -1:
                                end_index = find_matching_braces(gcd_string,start_braces_index,'()')#找到对应括号
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
                                end_index = find_matching_braces(string, start_index + 1, '{}')#找表达式的}对应位置
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
                            if string[start_index] == '{':
                                end_index = find_matching_braces(string, start_index + 1, '{}')#找表达式的}对应位置
                                min_string = string[start_index + 2:end_index-1]#切出集合
                                parts = min_string.split(',')#切出集合元素
                                for part in parts:
                                    operator_replacements.append(part)#识别每个数字
                            else: raise ValueError("invalid number")#无表达式，立刻报错
                            i = end_index#跳过原本函数结构
                            if i < len(string):#如果不是运算块末尾
                                operator_replacements.append(r'\times')#添加乘法标识
                        case r'\Pr':
                            raise ValueError("请使用C,P,A上下标格式计算排列组合")
                        case r'\abs':
                            operator_replacements.append(r'\abs')#添加绝对值标识
                            if string[start_index] == '(':#如果是括号
                                end_index = find_matching_braces(string, start_index - 1, '()')
                                operator_replacements.append(string[start_index+1:end_index-1])#识别绝对值表达式
                                i = end_index
                                if i < len(string):#如果不是运算块末尾
                                    operator_replacements.append(r'\times')#添加乘法标识
                            else: raise ValueError("invalid func abs")#无绝对值式，立刻报错
                        case _ if string[i:start_index] in GH_letters: 
                            operator_replacements.append(string[i:start_index])#识别希腊字母
                            continue
                case r'(':#括号
                    end_index = find_matching_braces(string, i, '()')#找到括号对应)位置，如果没有则报错
                    operator_replacements.append(string[i+1:end_index-1])#把整个括号添加到替换列表中
                    i = end_index#跳过原本括号结构
                    if i < len(string):#如果不是运算块末尾
                        operator_replacements.append(r'\times')#添加乘法标识
                    continue
                case r'[':#中括号
                    end_index = find_matching_braces(string, i, '[]')#找到括号对应]位置，如果没有则报错
                    operator_replacements.append(string[i+1:end_index-1])#把整个括号添加到替换列表中
                    i = end_index#跳过原本括号结构
                    if i < len(string):#如果不是运算块末尾
                        operator_replacements.append(r'\times')#添加乘法标识
                case r'{':#大括号
                    end_index = find_matching_braces(string, i, '{}')#找到括号对应}位置，如果没有则报错
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
                #     end_index = i + find_character_position(absolute_string, '|')#找到绝对值对应)位置，如果没有则报错
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
                                        end_down_index = find_matching_braces(string, i + 2, '{}')#找下标对应的}位置
                                        operator_replacements.append(string[i+3:end_down_index])#识别排列组合下标
                                    else:
                                        end_down_index = i + 2#单字符下标
                                        operator_replacements.append(string[i+2])#识别排列组合下标
                                if end_down_index + 2 < len(string):
                                    if string[end_down_index + 1] == '^':#下标后有上标
                                        if string[end_down_index + 2] == '{':#非单字符
                                            end_index = find_matching_braces(string, end_down_index + 2, '{}')#找到对应的右括号
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
                                        end_up_index = find_matching_braces(string, i + 2, '{}')#找上标对应的}位置
                                        power_string = string[i+3:end_index-1]#切出上标 
                                    else:#单字符上标
                                        end_up_index = i + 2
                                        power_string = string[i+2]#切出上标
                                if end_up_index + 1 < len(string):#如果不是末尾
                                    if string[end_up_index+1] == '_':#如果后面还有下标
                                        if end_up_index+2 < len(string) and string[end_up_index+2] == '{':#非单字符下标
                                            end_index = find_matching_braces(string, end_up_index + 2, '{}')#找下标对应的}位置
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
                                end_index+=1#跳过!
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
                    i = end_index
                    if i < len(string):#如果不是运算块末尾
                        operator_replacements.append(r'\times')#添加乘法标识
                    continue
                case _ if string[i].isalpha():#字母，允许上下标顺序自由
                    if i+1 < len(string):#如果不是最后一个字符
                        match string[i+1]:
                            case '_':#下标
                                if i+2 < len(string):
                                    if string[i+2] == '{':#非单字符下标
                                        end_index = find_matching_braces(string, i + 2, '{}')#找下标对应的}位置
                                        operator_replacements.append(string[i:end_index - 1])#识别字母
                                        i = end_index#跳过该字符
                                    else:
                                        end_index = i + 2
                                        operator_replacements.append(string[i:i+3])#识别字母
                                        i = end_index#跳过该字符
                            case '^':#上标,先上标后下标的字母写法是被允许的
                                if i+2 < len(string):#如果不是末尾
                                    if string[i+2] == '{':#非单字符上标
                                        end_up_index = find_matching_braces(string, i + 2, '{}')#找上标对应的}位置
                                        power_string = string[i+3:end_up_index-1]#切出上标 
                                    else:#单字符上标
                                        end_up_index = i + 3
                                        power_string = string[i+2]#切出上标
                                if end_up_index < len(string):#如果不是末尾
                                    if string[end_up_index] == '_':#如果后面还有下标
                                        if end_up_index+2 < len(string) and string[end_up_index+1] == '{':#非单字符下标
                                            end_index = find_matching_braces(string, end_up_index + 2, '{}') - 1#找下标对应的}位置
                                            operator_replacements.append(string[i]+string[end_up_index:end_index])#识别字母以及对应下标
                                            operator_replacements.append('^')#添加幂次标识
                                            operator_replacements.append(power_string)#添加幂次
                                        else:#单字符下标
                                            end_index = end_up_index + 1
                                            operator_replacements.append(string[i]+'_'+string[end_index])#识别字母以及对应下标
                                            operator_replacements.append('^')#添加幂次标识
                                            operator_replacements.append(power_string)#添加幂次
                                    else:#如果后面没有下标
                                        operator_replacements.append(string[i])#识别字母
                                        operator_replacements.append('^')#添加幂次标识
                                        operator_replacements.append(power_string)#添加幂次
                                        end_index = end_up_index -1
                                else:#如果上标结束之后超索引，说明字符已经结束
                                    operator_replacements.append(string[i])#识别字母
                                    operator_replacements.append('^')#添加幂次标识
                                    operator_replacements.append(power_string)#添加幂次
                                    end_index = end_up_index -1
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

import re

# 预编译科学计数法正则（支持 .5e7 和 1E3 等格式）
SCIENTIFIC_NOTATION_REGEX = re.compile(
    r'^[+-]?(?:\d+\.?\d*|\.\d+)(?:[E][+-]?\d+)?$'  # 允许纯数字（如 123）和科学计数法
)

def is_final_list(operator: list|str):
    """第三步，判断是否为最终的可计算的列表"""
    allowed_prefixes = set(GH_letters + special_operators + operators)
    if isinstance(operator, str):  # 如果是字符串，则直接返回
        if operator == '':  # 空字符跳过
            return True, ''
        
        # 2. 校验数字（含科学计数法）
        if isinstance(operator, str) and SCIENTIFIC_NOTATION_REGEX.match(operator):
            return True, ''
        
        # 3. 校验运算符/希腊字母/单英文字符
        if operator in allowed_prefixes or (len(operator) == 1 and operator.isalpha()):
            return True, ''
        
        # 4. 校验带下标的变量（如 x_{i} 或 \alpha_{0}）
        if '_' in operator:
            parts = operator.split('_', 1)
            prefix, subscript = parts[0], parts[1]
            # 允许希腊字母或普通字母作为前缀
            if (prefix in GH_letters or prefix.isalpha()) and subscript.startswith('{'):
                end = find_matching_braces(operator, operator.index('{'), '{}')
                if end != -1 and operator[end - 1] == '}' and end == len(operator):
                    return True, ''
            elif (prefix in GH_letters or prefix.isalpha()) and len(subscript) == 1:
                return True, ''
        return False, operator
    for item in operator:
        if item == '':  # 空字符跳过
            continue
        
        # 1. 校验列表
        if isinstance(item, list):  # 检查是否为列表
            result, error_item = is_final_list(item)  # 递归调用
            if not result:
                return False, item
            continue
        
        # 2. 校验数字（含科学计数法）
        if isinstance(item, str) and SCIENTIFIC_NOTATION_REGEX.match(item):
            continue
        
        # 3. 校验运算符/希腊字母/单英文字符
        if item in allowed_prefixes or (len(item) == 1 and item.isalpha()):
            continue
        
        # 4. 校验带下标的变量（如 x_{i} 或 \alpha_{0}）
        if '_' in item:
            parts = item.split('_', 1)
            prefix, subscript = parts[0], parts[1]
            # 允许希腊字母或普通字母作为前缀
            if (prefix in GH_letters or prefix.isalpha()) and subscript.startswith('{'):
                end = find_matching_braces(item, item.index('{'), '{}')
                if end != -1 and item[end - 1] == '}' and end == len(item):
                    continue
            elif (prefix in GH_letters or prefix.isalpha()) and len(subscript) == 1:
                continue
        
        # 5. 非法字符判定
        return False, item
    
    return True, ''

#第四步，递归处理，转为最终计算列表
def latex_to_list(string: str|list):
    if isinstance(string, str):  # 如果输入是一个字符串
        try:
            if is_final_list(string)[0]:#最终元素，不处理
                return string
            elif is_multi_operators(string):#多运算块，切割
                parts = _setup_operators(string)
            else:#单运算块，切割识别
                parts = _setup_special(string)
            while not is_final_list(parts)[0]:
                parts[parts.index(is_final_list(parts)[1])] = latex_to_list(is_final_list(parts)[1])#非最终列表，递归
                continue
            else: return parts#最终列表，返回
        except Exception as e:
            raise e
    elif isinstance(string, list):  # 如果输入是一个列表
        try:
            pass
        except Exception as e:return e

def is_multi_operators(string: str):#判断是否为多运算块
    stack = []
    brace_pairs = {'(': ')', '[': ']', '{': '}'}
    for i in range(len(string)):
        char = string[i]
        if char in brace_pairs.keys():
            stack.append(char)
        elif char in brace_pairs.values():
            if not stack or brace_pairs[stack.pop()] != char:
                return -1  # 括号不匹配
        if char in ['+','-','='] and not stack and i!=0:  # 仅在栈为空时匹配
            return True
    return False

def find_matching_braces(s, start, brace_type='{}'):
    """匹配括号,s为字符串，start为起始位置，brace_type为括号类型，返回匹配的括号位置"""
    if len(brace_type) != 2 or brace_type[0] not in '({[<' or brace_type[1] not in ')}]>':
        raise ValueError(f"Invalid brace type: {brace_type}")
    open_brace, close_brace = brace_type
    stack = []
    for i in range(start, len(s)):
        if s[i] == open_brace:
            stack.append(i)
        elif s[i] == close_brace:
            if not stack:
                return -1  # 提前发现不匹配
            stack.pop()
            if not stack:
                return i+1 #返回匹配的括号位置，而非索引
    return -1  # 明确返回-1表示未找到

def find_start_position(string, start_index):
    """寻找起始位置"""
    brace_map = {'(', '[', '{', '_', '^'}
    # 处理起始索引越界
    if start_index >= len(string):
        return len(string)
    # 直接遍历，无需嵌套条件
    for i in range(start_index, len(string)):
        if string[i] in brace_map:
            return i  # 直接返回目标字符位置，无需-1
    return len(string)

def find_character_position(string: str, target: str, start_index=0):
    """寻找字符位置（考虑括号嵌套）"""
    stack = []
    brace_pairs = {'(': ')', '[': ']', '{': '}'}
    if target in brace_pairs.values() or target in brace_pairs.keys():
        for i in range(len(string)):
            if string[i] == target:
                return i
    for i in range(start_index, len(string)):
        char = string[i]
        if char in brace_pairs.keys():
            stack.append(char)
        elif char in brace_pairs.values():
            if not stack or brace_pairs[stack.pop()] != char:
                return -1  # 括号不匹配
        if char == target and not stack:  # 仅在栈为空时匹配
            return i
    return -1

# import time
# import threading

# class TimeoutError(Exception):
#     """自定义异常，用于处理超时情况"""
#     pass

# def _setup_special_with_timeout(string: str, timeout: float = 1.0):
#     """带超时功能的 _setup_special 函数"""
#     result = [None]  # 用于存储结果
#     error = [None]   # 用于存储异常

#     def target():
#         try:
#             result[0] = _setup_special(string)
#         except Exception as e:
#             error[0] = e

#     thread = threading.Thread(target=target)
#     thread.start()
#     thread.join(timeout)

#     if thread.is_alive():
#         thread.join()  # 确保线程结束
#         raise TimeoutError("处理时间超过1秒，可能进入死循环")
    
#     if error[0]:
#         raise error[0]
    
#     return result[0]

if __name__ == '__main__':
    expressions = [
        r'\frac{|a - b| + |c + d|}{|e - f|} - \sqrt{|g|}',
        r"|2 + 3| + (4 - 5) \times \frac{6} {|7 + 8|}",
        r"|a - b| + |c + d|",
        r'\int_{|a|}^{|b|}{ |x| dx} + \int_{|c|}^{|d|}{ |\sin(x)| dx}',
        r"\sum_{|i|=1}^{|n|}{ |i^2| }+ \prod_{|j|=1}^{|m|} {|j|}",
        r"\sqrt[|3|]{|x|} + \sqrt{|y|} + \sqrt[|4|]{|z|}",
        r"\ln(|2|) + \log_{|2|}(|8|) + \exp(|1|)",
        r"\frac{|a - b| + |c + d|}{|e - f|} - \sqrt{|g|} ",
        r"\int_{|a|}^{|b|} {|x| dx} + \int_{|c|}^{|d|} {|\sin(x)| dx }",
        r"\frac{(|a - b| + (|c + d|))}{(|e - f|)} - \sqrt{(|g|)}",
        r"\int_{(|a|)}^{(|b|)} {(|x|) dx} + \int_{(|c|)}^{(|d|)}{ (|\sin(x)|) dx}",
        r"\frac{\sum_{i=1}^n{i^2}}{2} - \sqrt[3]{-\abs{5}} = \alpha_{0}",
        r"\sum_{k=1}^\infty{\frac{k}{2^k}",
        r"1E-5 + (x - y) - -1E-5 + (x + y)",
        r"-2 + 3 - (4 - 5) * [6 / {7 + 8}]",  # 包含负号
        r"\frac{-|a - b| + |c + d|}{|e - f|} - \sqrt{-|g|}",  # 包含负号
        r"\int_{-|a|}^{|b|} {-|x| dx} + \int_{|c|}^{-|d|} {|\sin(-x)| dx}",  # 包含负号
        r"\sum_{-|i|=1}^{|n|} -|i^2| + \prod_{|j|=1}^{-|m|} |j|",  # 包含负号
        r"\sqrt[|-3|]{-|x|} + \sqrt{-|y|} / \sqrt[|4|]{-|z|}",  # 包含负号
        r"\ln(-|2|) + \log_{-|2|}(|8|) + \exp(-|1|)",  # 包含负号
        r"|(|x| + |y|)| - \frac{\abs{\ln(2)}}{3} = 0", 
        r"5*6*(8+9\div56)",
        ]
    # 运行测试
    for expr in expressions:
        try:
            result = latex_to_list(expr)
            print(result)
        except Exception as e:
            print(f"Error processing '{expr}': {e}")
            continue