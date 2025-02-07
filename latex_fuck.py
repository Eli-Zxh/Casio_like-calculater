import sympy
import matplotlib as plt
import scipy
import math
import re
"""
允许的保留值
包含运算符，特殊运算符，希腊字符
本算法中占位字符为#、'$'，分别对应于显示中的指针位置，空格待填充占位符
为latextest.py文件，即latex转AST函数中，所不允许的非法字符
"""
#region 列表保留值定义
keep_operators = [r'\frac',r'\sqrt',r'\log',r'\lim',r'\limsup',r'\liminf',r'\sin',r'\cos',r'\tan',
                    r'\sec',r'\csc',r'\cot',r'\sinh',r'\cosh',r'\tanh',r'\arcsin',r'\arccos',r'\arctan',r'\exp',r'\ln',r'\lg',
                    r'\arg',r'\coth',r'\deg',r'\det',r'\dim',r'\gcd',r'\hom',r'\max',r'\sup',r'\ker',r'\inf',r'\min',r'\Pr',r'\abs']
jundge_operators = [r'\int',r'\sum',r'\prod']
operators = [r'+', r'-', r'=', r'\div', r'\times', r'\cdot',r'^']
GH_letters = [r'\alpha',r'\beta',r'\chi',r'\delta',r'\epsilon',r'\eta',r'\gamma',r'\iota',
                  r'\kappa',r'\lambda',r'\mu',r'\nu',r'ο',r'\omega',r'\phi',
                  r'\psi',r'\rho',r'\sigma',r'\tau',r'\theta',r'upsilon',r'\xi',r'\zeta',
                  r'\digamma',r'\varepsilon',r'\varkappa',r'\varphi',r'\varpi',r'\varrho',r'\varsigma',r'\vartheta',
                  r'\Delta',r'\Gamma',r'\Lambda',r'\Omega',r'\Phi',r'\Pi',r'\Psi',r'\Sigma',
                  r'\Theta',r'\Upsilon',r'\Xi',r'\aleph',r'\beth',r'daleth',r'\gimel',r'\infty',r'+\infty',r'-\infty']
Primes_number = ['2','3','5','7','11','13','17','19','23','29','31','37','41','43','47','53','59','61','67','71','73','79','83','89','97'
                 '101','103','107','109','113','127','131','137','139','149','151','157','163','167','173','179','181','191','193','197','199',
                 '193','197','199','211','223','227','229','233','239','241','251','257','263','269','271','277','281','283','293','307','311',
                 '313','317','331','337','347','349','353','359','367','373','379','383','389','397','401','409','419','421','431','433','439',
                 '443','449','457','461','463','467','479','487','491','499','503','509','521','523','541','547','557','563','569','571','577',
                 '587','593','599','601','607','613','617','619','631','641','643','647','653','659','661','673','677','683','691','701','709',
                 '719','727','733','739','743','751','757','761','769','773','787','797','809','811','821','823','827','829','839','853','857',
                 '859','863','877','881','883','887','907','911','919','929','937','941','947','953','967','971','977','983','991','997','1009',
                 '1013','1019']#列出1000以内的素数列表，便于读写
square_number = ['0','1','4','9','16','25','36','49','64','81','100','121','144','169','196','225','256','289','324','361','400','441','484','529',
                 '576','625','676','729','784','841','900','961','1024','1089','1156','1225','1296','1369','1444','1521','1600','1681','1764',
                 '1849','1936','2025','2116','2209','2304','2401','2500','2601','2704','2809','2916','3025','3136','3249','3364','3481','3600',
                 '3721','3844','3969','4096','4225','4356','4489','4624','4761','4900','5041','5184','5329','5476','5625','5776','5929','6084',
                 '6241','6400','6561','6724','6889','7056','7225','7396','7569','7744','7921','8100','8281','8464','8649','8836','9025','9216',
                 '9409','9604','9801','10000']
#endregion
"""
能影响最终结果输出的类函数
只包含三种类
分数分式为一类
根式为一类
表达式为一类
其他允许作为最终的输出的包括：圆周率π，自然对数的底e，可选择性保留的第三类函数，仅包含ln(x),sin(x),tan(x),e指数，且仅允许其简单嵌套
对于每个类，需要定义最简结果判读函数，判断是否为最简结果，以及对应AST转换规范，以及对应的latex输出函数规范
"""
#region 计算的类函数部分class definition  
"""
"""
class numfrac:#分数类
    def __init__(self,numerator: str,denominator: str) -> None:
        self.numerator = numerator
        self.denominator = denominator
        self.simplify()
        self.is_final_output()
        self.to_AST()
    
    def simplify(self):#分数最简结果
        #分数最简结果
        if self.numerator.isdigit() and self.denominator.isdigit():
            self.numerator = int(self.numerator)
            self.denominator = int(self.denominator)
            pass
        pass#等待列表优化，不宜每次调用gcd函数判读

    def is_final_output(self):#判断是否为最终输出结果,是否为最简结果
        if self.content.isdigit() and self.times.isdigit():
            if gcd(int(self.content),int(self.times)) == 1: #等待gcd函数优化
                return 1#最简结果
            else:
                return 0#不是最简结果
        else: return -1#不应为分数类

    def to_latex(self):#latex输出函数
        return r'\frac{'+self.numerator+r'}{'+self.denominator+r'}'
    
    def to_AST(self):#AST输出函数
        return [r'\frac',self.numerator,self.denominator]
    
class numsqrt:#根式类
    def __init__(self,content: str,times: str) -> None:
        self.content = content
        self.times = times
        self.simplify()
        self.is_final_output()
        self.to_AST()
        self.to_latex()
    
    def simplify(self):#根式最简结果
        #根式最简结果
        pass#等待列表优化，不宜每次调用gcd函数判读

    def is_final_output(self):#判断是否为最终输出结果,是否为最简结果
        if self.content.isdigit() and self.times.isdigit():
            if gcd(int(self.content),int(self.times)) == 1: #等待gcd函数优化
                return 1#最简结果
            else:
                return 0#不是最简结果
        else: return -1#不应为根式类

    def to_latex(self):#latex输出函数
        if self.times == '2':#二次根式输出latex
            return r'\sqrt{'+self.content+r'}'
        else:#三次根式输出latex
            return r'\sqrt['+self.times+r']{'+self.content+r'}'
    
    def to_AST(self):#AST输出函数
        return [r'\sqrt',self.times,self.content]#根式输出AST

# class alphabet:#表达式类
#     def __init__(self,content: str) -> None:
#         self.content = content
#         self.simplify()
#         self.is_final_output()
#         self.to_AST()
#         self.to_latex()
    
#     def simplify(self):#表达式最简结果
#         #表达式最简结果
#         pass#等待列表优化，不宜每次调用gcd函数判读

#     def is_final_output(self):#判断是否为最终输出结果,是否为最简结果
#         pass#等待列表优化，不宜每次调用gcd函数判读

#     def to_latex(self):#latex输出函数
#         return self.content
    
#     def to_AST(self):#AST输出函数
#         return self.content
#endregion
"""
列表AST数规范
每层结构按照列表与最终元素构成，
其中最终元素仅包含：
1.空字符 2.数字（含科学计数法）完整数字类型为：+21.85E-5 3.运算符，参考operators和special_operators列表 4.希腊字母 5.单字母变量，允许下标，如 x_{i} 或 \alpha_{0}
列表之间可以嵌套，但是对于每个列表，其中的元素要么为列表，要么为最终元素。且经过有限层列表读取后可以得到全为最终元素的0级列表
"""
#region 主计算函数定义

SCIENTIFIC_NOTATION_REGEX = re.compile(
    r'^[+-]?(?:\d+\.?\d*|\.\d+)(?:[E][+-]?\d+)?$'  # 允许纯数字（如 123）和科学计数法
)
def cal_by_step(string: list,i:int = 0) -> str:#逐步计算设计的主计算函数，符合自然的数学计算逻辑，但时间和空间复杂度较高
    # #第一步，判断列表级数，即列表深度
    max_depth = 0#列表最大深度初始化值
    depth_list = []
    stack = [(string,0)]#初始化栈，存储当前列表和当前列表的深度
    while stack:
        current_list, current_depth = stack.pop()#取出栈顶元素
        max_depth = max(max_depth, current_depth)
        for element in current_list:#遍历当前列表中的元素
            if isinstance(element, list):#如果元素是列表，则将列表和深度入栈
                stack.append((element, current_depth + 1))
    #第二步，当一个列表深度为0，即列表中均为最终元素，进行列表计算，返回字符串

def cal_list(string: list,i:int = 0) -> str:#主计算函数，依据列表AST转为传递给各函数的值，最终结果值按照类的定义中最简结果
    #自定义的AST有一个优点是，可以之间从左到右直接读取元素，对于一个0级列表，从左到右就是运算顺序
    num = 1
    numcal,symbol = is_num_or_alpha(string)
    if numcal:#为纯数字运算
        while i < len(string):#遍历列表中的元素
            match string[i]:
                #数字类型，返回
                case _ if SCIENTIFIC_NOTATION_REGEX.match(string[i]):
                    if 'E' in string[i]:#判断是否为科学计数法,如果是，则浮点数运算
                        num = float(string[i])
                    else:#其他数字类型，传入分数类进行精确计算
                        num = numfrac(string[i])
                    if i == 0:#如果当前元素是第一个元素，则继续遍历，num传递
                        i+=1
                        continue
                    else:return num, i+1#如果当前元素不是第一个元素，则返回当前数字
                #运算符类型,递归
                case r'\times'|r'cdot':
                    cal_num,i = cal_list(string, i+1)#递归，传递下一个计算数字，和遍历起始位置和更替位置
                    num = num * cal_num#进行乘法运算
                    continue
                case r'\div':
                    cal_num,i = cal_list(string, i+1)#递归，传递下一个计算数字，和遍历起始位置和更替位置
                    num = num / cal_num#进行除法运算
                    continue
                case r'+':
                    cal_num,i = cal_list(string, i+1)#递归，传递下一个计算数字，和遍历起始位置和更替位置
                    num = num + cal_num#进行加法运算
                    continue
                case r'-':
                    cal_num,i = cal_list(string, i+1)
                    num = num - cal_num#进行减法运算
                    continue
                case r'^':
                    cal_num,i = cal_list(string, i+1)#递归，传递下一个计算数字，和遍历起始位置和更替位置
                    num = num ** cal_num#进行乘方运算
                    continue
                #第三类函数数字运算特殊类型，不用递归取数，直接传递并返回
                case r'\lim':#极限，调用sympy库，返回数字和传递位置
                    vars,appro,expr = string[i+1],string[i+2],string[i+3]
                    num = cal_alpha('\lim',vars,appro,expr)
                    return num, i+4
                case r'\int':#积分，调用sympy库
                    end,up,vars,expr = string[i+1],string[i+2],string[i+3],string[i+4]
                    num = cal_alpha('\int',end,up,vars,expr)
                    return num, i+5
                case r'\sum':#求和，调用sympy库
                    end,up,vars,expr = string[i+1],string[i+2],string[i+3],string[i+4]
                    num = cal_alpha('\sum',end,up,vars,expr)
                    return num, i+5
                case r'\prod':#累乘，调用sympy库
                    end,up,vars,expr = string[i+1],string[i+2],string[i+3],string[i+4]
                    num = cal_alpha('\prod',end,up,vars,expr)
                    return num, i+5
                #第一类函数，递归取数，并返回
                case r'\log':#对数，调用math库
                    end_num,ture_num = string[i+1],string[i+2]
                    if isinstance(end_num,list):#如果底数为列表，递归取数
                        end_num = cal_list(end_num)
                    if isinstance(ture_num,list):#如果真数为列表，递归取数
                        ture_num = cal_list(ture_num)
                    num = math.log(ture_num)/math.log(end_num)
                    return num, i+3
                case r'\ln':#自然底数对数，调用math库
                    ture_num = string[i+1]
                    if isinstance(ture_num,list):#如果真数为列表，递归取数
                        ture_num = cal_list(ture_num)
                    num = math.log(ture_num)
                    return num, i+2
                case r'\factorial':#阶乘，直接计算，直接返回
                    num = 1
                    try:
                        int_num = int(string[i+1])
                    except:raise ValueError('factorial must be a integer')
                    for i in range(1,int_num+1):
                        num *= i
                    return num, i+2
                case r'\max':#最大值，直接计算，直接返回
                    try:
                        num_list = float(string[i+1])
                    except:raise ValueError('max must be a list')
                    num = max(num_list)
                    return num, i+2
                case r'\min':#最小值，直接计算，直接返回
                    try:
                        num_list = float(string[i+1])
                    except:raise ValueError('min must be a list')
                    num = min(num_list)
                    return num, i+2
                case r'\sup':#上限，直接计算，直接返回
                    try:
                        num_list = float(string[i+1])
                    except:raise ValueError('sup must be a list')
                    num = max(num_list)
                    return num, i+2
                case r'\inf':#下限，直接计算，直接返回
                    try:
                        num_list = float(string[i+1])
                    except:return ValueError('inf must be a list')
                    num = min(num_list)
                    return num, i+2
                case r'\sqrt':#根号，调用类
                    times = string[i+1]
                    content = string[i+2]
                    if isinstance(times,list):#如果次数为列表，递归取数
                        times = cal_list(times)
                    if isinstance(content,list):#如果内容是列表，递归取数
                        content = cal_list(content)
                    num = numsqrt(content,times)
                    return num, i+3
                case r'\frac':#分数，调用类
                    numerator,denominator = string[i+1],string[i+2]
                    if isinstance(numerator,list):#如果分子为列表，递归取数
                        numerator = cal_list(numerator)
                    if isinstance(denominator,list):#如果分母为列表，递归取数
                        denominator = cal_list(denominator)
                    num = numfrac(numerator,denominator)
                    return num, i+3
                case r'\sin':#三角函数，调用math库
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = sin(degree)
                    return num, i+2
                case r'\cos':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = cos(degree)
                    return num, i+2
                case r'\tan':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = tan(degree)
                    return num, i+2
                case r'\cot':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = cot(degree)
                    return num, i+2
                case r'\sec':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = sec(degree)
                    return num, i+2
                case r'\csc':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = csc(degree)
                    return num, i+2
                case r'\arcsin':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = arcsin(degree)
                    return num, i+2
                case r'\arccos':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = arccos(degree)
                    return num, i+2
                case r'\arctan':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = arctan(degree)
                    return num, i+2
                case r'\arccot':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = arccot(degree)
                    return num, i+2
                case r'\arccsc':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = arccsc(degree)
                    return num, i+2
                case r'\arcsec':
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = arcsec(degree)
                    return num, i+2
                case r'\gcd':#最大公约数，调用gcd算法
                    num1,num2 = int(string[i+1],string[i+2])
                    try:
                        num = gcd(num1,num2)
                    except:raise ValueError('gcd must be two integer')
                    return num, i+3
                case r'\sinh':#双曲正弦函数，调用math库
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = sinh(degree)
                    return num, i+2
                case r'\cosh':#双曲余弦函数，调用math库
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = cosh(degree)
                    return num, i+2
                case r'\tanh':#双曲正切函数，调用math库
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = math.tanh(degree)
                    return num, i+2
                case r'\coth':#双曲余切函数，调用math库
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = math.coth(degree)
                    return num, i+2
                case r'\lg':#以10为底的对数，调用math库
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = math.log(degree)/math.log(10)
                    return num, i+2
                case r'arg':#角度函数，调用math库
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = arg(degree)
                    return num, i+2
                case r'\deg':#角度函数，调用math库
                    degree = string[i+1]
                    if isinstance(degree,list):#如果角度为列表，递归取数
                        degree = cal_list(degree)
                    num = deg(degree)
                    return num, i+2
                #特殊计算函数，特殊返回值
                case r'\FACT':#分解质因子，调用轮式因子分解函数
                    degree = string[i+1]
                    try:
                        num = int(degree)
                    except:raise ValueError('FACT must be a integer')
                    num = wheel_fact(num)
                    return num, i+2
                case _:
                    raise ValueError('invalid function')
    elif is_equation(string):#是方程，应当传参求解
        expr = AST_to_expr(string)
        num = cal_alpha(expr,symbol)
        return num, 0
    else:#多项式运算
        expr = AST_to_expr(string)
        return cal_alpha(expr,symbol),-1
    #第三步，递归处理每一个列表，当传入的主列表为0级，且已经满足最简条件判断，返回AST格式，仍为列表

def is_num_or_alpha(string: list) -> bool|str:#判断是数字计算还是多项式计算，数字计算返回True，多项式计算返回False
    if isinstance(string,list):
        i = 0
        while i < len(string):
            match string[i]:
                case _ if isinstance(string[i],list):#列表，递归判断
                    end,symbol = is_num_or_alpha(string[i])#传递变量
                    if end:
                        i+=1
                        continue
                    else:
                        return False,symbol
                case _ if string[i] in keep_operators:#数字运算符，返回仍是数字
                    i+=1
                    continue
                case _ if SCIENTIFIC_NOTATION_REGEX.match(string[i]):#纯数字或者科学计数法
                    i+=1
                    continue
                case 'e':#自然对数的底e
                    i+=1
                    continue
                case '\pi':#圆周率π
                    i+=1
                    continue
                case _ if string[i] in GH_letters:#希腊字母
                    return False,string[i]
                case _ if string[i].isalpha():#普通字母
                    return False,string[i]
                case _ if string[i] in jundge_operators:#特殊运算，判断是否为定值
                    if is_num_or_alpha(string[i+1])[0] and is_num_or_alpha(string[i+2])[0]:
                        pass
                    else:
                        return True,''
                    i+=5#跳过特殊运算
                    continue
                case _:
                    return False,string[i]
        return True,''
    elif isinstance(string,str):#当传入的列表为字符串，则进行字符串处理
        if string in keep_operators:#数字运算符，返回仍是数字
            return True,''
        elif SCIENTIFIC_NOTATION_REGEX.match(string):
            return True,''
        elif string == 'e':
            return True,''
        elif string == '\pi':
            return True,''
        else:
            return False,string

def cal_num(string: numfrac,figure: int) -> str:#数字计算，把最简结果也转换为浮点数
    #1.最简结果转换为浮点数以及精确位数 2.把只能数值计算的部分调用scipy 进行单独计算
    return string.float()

def cal_alpha(expr: str,symbol:str = 'x',type:int = 0) -> list:#多项式计算，计算为最简的表达式格式
    #分类：1.多项式计算 2.函数计算：求导，积分，求和，累乘 3.多项式赋值计算 4.函数赋值计算：定积分，定值求导，定值求和，定值累乘 5.方程计算：求解方程，图像绘制、图像显示
    x = sympy.Symbol(symbol)
    expr_sympy = sympy.eval(expr)
    if not type:
        equation = sympy.Eq(expr_sympy, 0)
        solution = sympy.solve(equation, x)
        return solution
    elif type == -1:
        return sympy.simplify(expr_sympy)

def is_equation(string: list) -> bool:#判断是否为方程
    # 1.判断数字计算结果是否为最终结果，2.多项式计算结果是否为最简结果
    if '=' in string: return True
    else: return False
#endregion
#region 各数学运算函数
def gcd(a: int, b: int) -> int:#求最大公约数
    if a > b: a, b = b, a
    while a != 0:
        a, b = b % a, a
    return b

def wheel_fact(n:int) -> str:#轮式因子分解质因子分解算法
    factors = []
    # 处理2和3这两个特殊情况
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    while n % 3 == 0:
        factors.append(3)
        n //= 3
    
    # 使用轮子 [2, 3, 5] 来减少不必要的除法
    wheel = [1, 2, 2, 4, 2, 4, 2, 4, 6, 2, 6]
    w_idx = 0
    p = 5
    while p * p <= n:
        if n % p == 0:
            factors.append(p)
            n //= p
        else:
            p += wheel[w_idx]
            w_idx = (w_idx + 1) % len(wheel)
    
    if n > 1:
        factors.append(n)
    
    return r'\times'.join(map(str, factors))

def sin(x: float) -> float:
    return math.sin(x)

def cos(x: float) -> float:
    return math.cos(x)

def tan(x: float) -> float:
    return math.tan(x)

def csc(x: float) -> float:
    return 1 / math.sin(x)

def sec(x: float) -> float:
    return 1 / math.cos(x)

def cot(x: float) -> float:
    return 1 / math.tan(x)

def arcsin(x: float) -> float:
    return math.asin(x)

def arccos(x: float) -> float:
    return math.acos(x)

def arctan(x: float) -> float:
    return math.atan(x)

def arccot(x: float) -> float:
    return math.atan(1 / x)

def arccsc(x: float) -> float:
    return math.asin(1 / x)

def arcsec(x: float) -> float:
    return math.acos(1 / x)

def sinh(x: float) -> float:
    return math.sinh(x)

def cosh(x: float) -> float:
    return math.cosh(x)

def tanh(x: float) -> float:
    return math.tanh(x)

def coth(x: float) -> float:
    return math.coth(x)

def arg(x: float) -> float:
    return math.arg(x)

def deg(x: float) -> float:
    return math.degrees(x)
#endregion


#region 格式转换函数
def AST_to_latex(operators: list) -> str:
    pass

def AST_to_expr(operators: list) -> str:
    pass
#endregion