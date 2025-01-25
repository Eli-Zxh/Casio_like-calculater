import re
def _setup_special_operators(string):#字符处理规则
        if '#' in string:#不允许出现#号
            ValueError("invalid expression")
        elif ' ' in string:#不允许存在空格
            string = string.replace(' ', '')
        elif '\n' in string:#不允许存在换行符
            string = string.replace('\n', '')
        #第一步，\frac{}{},\sqrt[]{},\sqrt{},()为运算块判定，按照运算块外的+-=分割string
        i = 0
        operator_replacements = []
        while i < len(string):
            if string[i]=='\\':
                    print(string[i:i+5])
                    if string[i:i+5] == r'\frac': #分式
                            print(string[i+5])
                            if string[i+5] == '{':#找第一个括号{}，如果没有，立刻报错
                                end_index = find_matching_braces(string, i + 5, '{}')#找第一个括号对应的}位置
                                print(end_index)
                                if end_index != -1 and string[end_index + 1] == '{':#找分式的第二个括号{}，如果没有，立刻报错
                                    end_index = find_matching_braces(string, end_index + 1, '{}')#找第二个括号对应的}位置,如果没有，立刻报错
                                    print(end_index)
                                    if end_index != -1:
                                        operator_replacements.append(string[i:end_index])#把整个分式添加到替换列表中
                                        string = string[:i] + '#' * (end_index - i + 1) + string[end_index + 1:]#替换为#占位
                                        i = end_index + 1#跳过原本分式结构
                                        print(string)
                                        continue
                                    else:
                                        raise ValueError("invalid expression")
                                else:
                                    raise ValueError("invalid expression")
                            else:
                                raise ValueError("invalid expression")
                    elif string[i:i+5]==r'\sqrt':#根式
                            match string[i+5]:
                                case '[':#非二次根式
                                    end_index = find_matching_braces(string, i + 5, '[]')#找根式幂次的]对应位置
                                    print(end_index)
                                    if end_index != -1 and string[end_index + 1] == '{' and string[i+7,end_index-1].isdigit():#找根式幂次对应的括号，判断根式是否为数字，判断下一个字符为根式括号，如不满足立刻报错
                                        end_index = find_matching_braces(string, end_index + 1, '{}')#找根式表达式括号}对应位置，如果没有，立刻报错
                                        if end_index != -1:
                                            operator_replacements.append(string[i:end_index])#把整个根式添加到替换列表中
                                            string = string[:i] + '#' * (end_index - i + 1) + string[end_index + 1:]#替换为#占位
                                            i = end_index + 1#跳过原本根式结构
                                            print(string)
                                            continue
                                        else:
                                            print(string)
                                            raise ValueError("invalid expression")
                                    else: 
                                        print(string)
                                        raise ValueError("invalid expression")
                                case '{':
                                    end_index = find_matching_braces(string, i + 5, '{}')#找根式表达式的}对应位置
                                    if end_index != -1:#找根式幂次对应的括号，如不满足立刻报错
                                        operator_replacements.append(string[i:end_index])#把整个根式添加到替换列表中
                                        string = string[:i] + '#' * (end_index - i + 1) + string[end_index + 1:]#替换为#占位
                                        i = end_index + 1#跳过原本根式结构
                                        print(string)
                                        continue
                                    else: 
                                        print(string)
                                        raise ValueError("invalid expression")
                                case _: 
                                    print(string)
                                    raise ValueError("invalid expression")#根式后无{}或者[]，立刻报错
                    else: 
                            i += 2 #不属于这三类运算块，跳过次运算块
                            continue
            elif  string[i]==r'(':#括号
                    print(string[i:i+5])
                    end_index = find_matching_braces(string, i, '()')#找到括号对应)位置，如果没有则报错
                    print(end_index)
                    if end_index != -1:
                        operator_replacements.append(string[i:end_index])#把整个括号添加到替换列表中
                        string = string[:i] + '#' * (end_index - i + 1) + string[end_index + 1:]#替换为#占位
                        i = end_index + 1#跳过原本括号结构
                        print(string)
                        continue
                    else:
                        print(string)
                        raise ValueError("invalid expression")
            else: i += 1 #不属于会影响递归分割的情况，跳过
        parts = re.split(r'(?<=[^\\]\+)|(?<=[^\\]-)|(?<=[^\\]=)', string)# 按照 +-= 分割字符串
        parts = [part for part in parts if part]
        print(parts)
        hash_positions = [i for i, part in enumerate(parts) if part == '#']# 找到所有 # 号的位置
        for index, hash_pos in enumerate(hash_positions):
            parts[hash_pos] = operator_replacements[index]
        #第二步，对于每个分割的部分，做运算块判定，对满足运算块判定的部分去运算块重复第一步
        for part in parts:
            # print(part)
            pass
        return parts
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
print(_setup_special_operators(r'\frac{\frac{abc}{xyz}+\ln(2)}{x_0^2}-\frac{\sqrt{abc}}{2}=\overline{abc}+\sum_{i=1}^n{i^2+i}'))