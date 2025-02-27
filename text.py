import tkinter as tk
# import time
"""
这是一个latex渲染器，用于将预处理为AST的latex表达式，渲染到canvas画布
其中AST的处理规范参照latextest.py
整体渲染的处理思路为：
1. 对AST进行遍历，对于每一个特殊函数渲染类型，进行判读渲染，如：\int,\frac，\sqrt,\sum,\lim,\fractional;
2. 对于嵌套类型，根据嵌套位置，给予适当的整体缩放比例，递归处理；
3. 对于每一个特殊字符如\int,\pi，给予对于的unicode字符渲染，并适当缩放；
4. 显而易见，渲染用的AST规范要宽于计算用的AST规范，对于空字符的处理，应使用方块先进行占位；
5. 括号显示问题：目前的AST规范里是不允许括号的出现的，考虑同样不允许括号的出现，需要括号位置给予自动渲染
2025/2/11
"""
#目前尚未实现，音标字节符号的的渲染
# """
# 音节类型：\’{o} 二声， \"{o} 两点，\^{o} 向量标记， \‘{o} 四声， \`{o} 上波浪线，\={o} 一声，
# \d s 降调，\.{o} 牛顿求导标记，\u{o} 上勾线， \H{o} 双上划线， \t{oo} 弧度标记, \c{o} 下尾线
# \d{o} 降调， \r s 上空心圆，\b{o} 下划线,\AA 上方加圈, \ss 音阶标记，\i 循环节标记， \j J调标记,
# \H s 双上划线， \o 空集∅ ,\t s 右上方加弧线，\v s 三声， \O 大写空集， \P 音符标号， \S 音符
# \ae 音标字母æ '\u00E6', \AE 大写音标字母Æ '\u00C6', \dag †, \ddag ‡, \copyright ©, \pounds £
# """

#region 渲染中特殊字符字典
GH_letter = {
    r'\alpha': '\u03B1',       # 小写alpha α
    r'\beta': '\u03B2',        # 小写beta β
    r'\gamma': '\u03B3',       # 小写gamma γ
    r'\delta': '\u03B4',       # 小写delta δ
    r'\epsilon': '\u03B5',     # 小写epsilon ε
    r'\zeta': '\u03B6',        # 小写zeta ζ
    r'\eta': '\u03B7',         # 小写eta η
    r'\theta': '\u03B8',       # 小写theta θ
    r'\iota': '\u03B9',        # 小写iota ι
    r'\kappa': '\u03BA',       # 小写kappa κ
    r'\lambda': '\u03BB',      # 小写lambda λ
    r'\mu': '\u03BC',          # 小写mu μ
    r'\nu': '\u03BD',          # 小写nu ν
    r'\xi': '\u03BE',          # 小写xi ξ
    r'\omicron': '\u03BF',     # 小写omicron ο
    r'\pi': '\u03C0',          # 小写pi π
    r'\rho': '\u03C1',         # 小写rho ρ
    r'\sigma': '\u03C3',       # 小写sigma σ
    r'\tau': '\u03C4',         # 小写tau τ
    r'\upsilon': '\u03C5',     # 小写upsilon υ
    r'\phi': '\u03C6',         # 小写phi φ
    r'\chi': '\u03C7',         # 小写chi χ
    r'\psi': '\u03C8',         # 小写psi ψ
    r'\omega': '\u03C9',       # 小写omega ω
    r'\Alpha': '\u0391',       # 大写Alpha Α
    r'\Beta': '\u0392',        # 大写Beta Β
    r'\Gamma': '\u0393',       # 大写Gamma Γ
    r'\Delta': '\u0394',       # 大写Delta Δ
    r'\Epsilon': '\u0395',     # 大写Epsilon Ε
    r'\Zeta': '\u0396',        # 大写Zeta Ζ
    r'\Eta': '\u0397',         # 大写Eta Η
    r'\Theta': '\u0398',       # 大写Theta Θ
    r'\Iota': '\u0399',        # 大写Iota Ι
    r'\Kappa': '\u039A',       # 大写Kappa Κ
    r'\Lambda': '\u039B',      # 大写Lambda Λ
    r'\Mu': '\u039C',          # 大写Mu Μ
    r'\Nu': '\u039D',          # 大写Nu Ν
    r'\Xi': '\u039E',          # 大写Xi Ξ
    r'\Omicron': '\u039F',     # 大写Omicron Ο
    r'\Pi': '\u03A0',          # 大写Pi Π
    r'\Rho': '\u03A1',         # 大写Rho Ρ
    r'\Sigma': '\u03A3',       # 大写Sigma Σ
    r'\Tau': '\u03A4',         # 大写Tau Τ
    r'\Upsilon': '\u03A5',     # 大写Upsilon Υ
    r'\Phi': '\u03A6',         # 大写Phi Φ
    r'\Chi': '\u03A7',         # 大写Chi Χ
    r'\Psi': '\u03A8',         # 大写Psi Ψ
    r'\Omega': '\u03A9',       # 大写Omega Ω
}

DELIMITERS = {
    r'\vert': '\u007C',       # 垂直线 |
    r'\|': '\u2016',          # 双垂线 ||
    r'\Vert': '\u2016',         # 双垂线 ||
    r'\{': '\u007B',           # 左花括号 {
    r'\}': '\u007D',           # 右花括号 }
    r'\langle': '\u27E8',       # 左尖括号 <
    r'\rangle': '\u27E9',       # 右尖括号 >
    r'\lfloor': '\u230A',       # 左下取整符号 ⌊
    r'\rfloor': '\u230B',       # 右下取整符号 ⌋
    r'\lceil': '\u2308',        # 左上取整符号 ⌈
    r'\rceil': '\u2309',        # 右上取整符号 ⌉
    r'\Uparrow': '\u21D1',      # 双上箭头 ⇑
    r'\Downarrow': '\u21D3',    # 双下箭头 ⇓
    r'\uparrow': '\u2191',      # 上箭头 ↑
    r'\downarrow': '\u2193',    # 下箭头 ↓
    r'\llcorner': '\u231E',     # 左下角 ⌜
    r'\lrcorner': '\u231F',     # 右下角 ⌝
    r'\ulcorner': '\u231C',     # 左上角 ⌜
    r'\urcorner': '\u231D',     # 右上角 ⌝
    r'\backslash': '\u005C',    # 反斜杠 \
}

Variable_sized_symbols = {
    r'\sum': '\u2211',         # 求和符号 ∑
    r'\int': '\u222B',         # 积分符号 ∫
    r'\biguplus': '\u228E',    # 大并集符号 ⊎
    r'\bigoplus': '\u2A01',    # 大加号在圆圈内 ⊕
    r'\bigvee': '\u22C1',      # 大逻辑或符号 ∨
    r'\prod': '\u220F',         # 求积符号 ∏
    r'\oint': '\u222E',        # 环路积分符号 ∮
    r'\bigcap': '\u22C2',      # 大交集符号 ∧
    r'\bigotimes': '\u2A02',   # 大乘号在圆圈内 ⊗
    r'\bigwedge': '\u22C0',    # 大逻辑与符号 ∧
    r'\coprod': '\u2210',      # 上下求积符号 ∐
    r'\iint': '\u222C',        # 二重积分符号 ∬
    r'\bigcup': '\u22C3',      # 大并集符号 ∪
    r'\bigodot': '\u2A00',     # 大点在圆圈内 ⊙
    r'\bigsqcup': '\u2294',    # 大方并集符号 ⊔
}

Binary_Operation = {
    r'+':'\u002B',            # 加号 +
    r'-':'\u2212',            # 减号 -
    r'=':'\u003D',            # 等号 =
    r'\ast': '\u2217',        # 星号 ∗
    r'\pm': '\u00B1',         # 加减号 ±
    r'\cap': '\u2229',        # 交集 ∩
    r'\lhd': '\u22B2',        # 正规子群符号 ⊲
    r'\star': '\u2606',       # 星形 ★
    r'\mp': '\u2213',         # 减加号 ∓
    r'\cup': '\u222A',        # 并集 ∪
    r'\rhd': '\u22B3',        # 正规商群符号 ⊳
    r'\cdot': '\u22C5',       # 中心点乘号 ·
    r'\amalg': '\u2210',      # 上下求积符号 ∐
    r'\uplus': '\u228E',      # 大并集符号 ⊎
    r'\triangleleft': '\u25C3', # 左三角 ⊲
    r'\circ': '\u2218',       # 圆圈 ∘
    r'\odot': '\u2299',       # 点在圆圈内 ⊙
    r'\sqcap': '\u2293',      # 方形交集符号 ⊓
    r'\triangleright': '\u25B9', # 右三角 ⊳
    r'\bullet': '\u2022',     # 实心圆点 •
    r'\ominus': '\u2296',     # 减号在圆圈内 ⊖
    r'\sqcup': '\u2294',      # 方形并集符号 ⊔
    r'\unlhd': '\u22B4',      # 正规子群符号 ⊴
    r'\bigcirc': '\u25CB',     # 大圆圈 ⊙
    r'\oplus': '\u2295',      # 加号在圆圈内 ⊕
    r'\wedge': '\u2227',      # 逻辑与 ∧
    r'\unrhd': '\u22B5',      # 正规商群符号 ⊵
    r'\diamond': '\u22C4',    # 菱形 ⊢
    r'\oslash': '\u2298',     # 除号在圆圈内 ⊘
    r'\vee': '\u2228',        # 逻辑或 ∨
    r'\bigtriangledown': '\u25BD', # 大下三角 ▽
    r'\times': '\u00D7',      # 乘号 ×
    r'\otimes': '\u2297',     # 乘号在圆圈内 ⊗
    r'\dagger': '\u2020',     # 单垂线星号 †
    r'\bigtriangleup': '\u25B3', # 大上三角 △
    r'\div': '\u00F7',        # 除号 ÷
    r'\wr': '\u2240',         # 卷积符号 ⊠
    r'\ddagger': '\u2021',    # 双垂线星号 ‡
    r'\setminus': '\u2216',   # 集合差 ∖
    r'\centerdot': '\u22C5',  # 中心点乘号 ·
    r'\Box': '\u25A1',        # 正方形 □
    r'\barwedge': '\u2305',   # 上方合取符号 ⋅
    r'\veebar': '\u22BB',     # 逻辑或带横线 ⋋
    r'\circledast': '\u229B', # 圆内星号 ⊙
    r'\boxplus': '\u229E',    # 方框加号 ⊞
    r'\curlywedge': '\u22CF', # 花括号交集符号 ⋏
    r'\curlyvee': '\u22CE',   # 花括号并集符号 ⋎
    r'\circledcirc': '\u229A', # 圆内圆圈 ⊚
    r'\boxminus': '\u229F',   # 方框减号 ⊟
    r'\Cap': '\u22D2',        # 大交集符号 ⋒
    r'\Cup': '\u22D3',        # 大并集符号 ⋓
    r'\circleddash': '\u229D', # 圆内减号 ⊝
    r'\boxtimes': '\u22A0',   # 方框乘号 ⊠
    r'\bot': '\u22A5',        # 垂直线 ⊥
    r'\top': '\u22A4',        # 顶点 ⊤
    r'\dotplus': '\u2214',     # 点加号 ∔
    r'\boxdot': '\u22A1',      # 方形点乘 ⊙
    r'\intercal': '\u22BA',    # 交差号 ⊺
    r'\rightthreetimes': '\u22C5', # 右三乘号 ⋅
    r'\divideontimes': '\u22C7', # 除号在圆圈内 ÷
    r'\square': '\u25A1',      # 方形 □
    r'\doublebarwedge': '\u2306', # 双上横线合取 ∧
    r'\leftthreetimes': '\u22CB', # 左三乘号 ⋋
    r'\equiv': '\u2261',       # 同余号 ≡
    r'\leq': '\u2264',         # 小于等于 ≤
    r'\geq': '\u2265',         # 大于等于 ≥
    r'\perp': '\u22A5',        # 垂直线 ⊥
    r'\cong': '\u2245',        # 同构号 ≅
    r'\prec': '\u227A',        # 小于号（严格） ≺
    r'\succ': '\u227B',        # 大于号（严格） 
    r'\mid': '\u2223',         # 整除号 |
    r'\neq': '\u2260',         # 不等于 ≠
    r'\preceq': '\u227C',      # 小于等于号（偏序） 
    r'\succeq': '\u227D',      # 大于等于号（偏序） 
    r'\parallel': '\u2225',    # 平行线 ∥
    r'\sim': '\u223C',         # 波浪线 ≈
    r'\ll': '\u226A',          # 远小于 ≪
    r'\gg': '\u226B',          # 远大于 
    r'\bowtie': '\u22C8',      # 钻石符号 ⊗
    r'\simeq': '\u2243',       # 同构号（波浪线） ≃
    r'\subset': '\u2282',      # 真子集 ⊂
    r'\supset': '\u2283',      # 真超集 ⊃
    r'\Join': '\u22C8',        # 连接符号 ∨
    r'\approx': '\u2248',      # 近似等于 ≈
    r'\subseteq': '\u2286',    # 子集 ⊆
    r'\supseteq': '\u2287',    # 超集 ⊇
    r'\ltimes': '\u22C9',      # 左作用符号 ⊲
    r'\asymp': '\u224D',       # 同构号（波浪线） ≍
    r'\sqsubset': '\u228F',    # 方形真子集 
    r'\sqsupset': '\u2290',    # 方形真超集 A
    r'\rtimes': '\u22CA',      # 右作用符号 ⊳
    r'\doteq': '\u2250',       # 点等于 .=
    r'\sqsubseteq': '\u2291',  # 方形子集 v
    r'\sqsupseteq': '\u2292',  # 方形超集 w
    r'\smile': '\u2323',       # 笑脸符号 ^
    r'\propto': '\u221D',      # 成比例 ∝
    r'\dashv': '\u22A3',       # 反证明 `
    r'\vdash': '\u22A2',       # 证明 _
    r'\frown': '\u2322',       # 哭脸符号
    r'\models': '\u22A8',      # 模型 |=
    r'\in': '\u2208',          # 属于 ∈
    r'\ni': '\u220B',          # 包含 3
    r'\notin': '\u2209',       # 不属于 ∈/
     r'u': '\u0075',            # 小写字母u u
    r'\approxeq': '\u224A',     # 近似等于 ≊
    r'\leqq': '\u2266',         # 小于等于（等于号加横线） ≤
    r'\geqq': '\u2267',         # 大于等于（等于号加横线） ≥
    r'\prec': '\u227A',         # 小于号（严格） ≺
    r'\succ': '\u227B',         # 大于号（严格） ≻
    r'\thicksim': '\u223D',     # 厚波浪线 ∼
    r'\leqslant': '\u2A7D',     # 小于等于（等于号加尖角） ≤
    r'\geqslant': '\u2A7E',     # 大于等于（等于号加尖角） ≥
    r'\lesseqgtr': '\u22DB',    # 小于等于大于符号 ≶
    r'\lessgtr': '\u2277',      # 小于大于符号 ≷
    r'\backsim': '\u223D',      # 反波浪线 ∼
    r'\thicksim': '\u223D',     # 厚波浪线 ∼
    r'\leqslant': '\u2A7D',     # 小于等于（等于号加尖角） ≤
    r'\geqslant': '\u2A7E',     # 大于等于（等于号加尖角） ≥
    r'\lesseqgtr': '\u22DB',    # 小于等于大于符号 ≶
    r'\lessgtr': '\u2277',      # 小于大于符号 ≷
    r'\backsimeq': '\u22CD',    # 反厚波浪线 ∽
    r'\lll': '\u22D8',          # 远小于（三个小于号） ≪
    r'\ggg': '\u22D9',          # 远大于（三个大于号） ≫
    r'\gtreqqless': '\u22DB',   # 大于等于小于符号 ≶
    r'\triangleq': '\u225C',    # 三角等于符号 ≅
    r'\circeq': '\u2257',       # 圆等于符号 ≗
    r'\bumpeq': '\u224F',       # 点等于符号 ≏
    r'\Bumpeq': '\u224E',       # 厚点等于符号 ≎
    r'\doteqdot': '\u2251',     # 点等于符号（圆点） ≑
    r'\thickapprox': '\u2248',  # 厚近似等于符号 ≈
    r'\Subset': '\u22D0',       # 真子集（双括号） ⊂
    r'\Supset': '\u22D1',       # 真超集（双括号） ⊃
    r'\shortmid': '\u2223',     # 整除号 |
    r'\fallingdotseq': '\u2252',# 下降点等于符号 ≒
    r'\subseteqq': '\u2AC5',    # 子集（等于号加尖角） ⊆
    r'\supseteqq': '\u2AC6',    # 超集（等于号加尖角） ⊇
    r'\smallfrown': '\u2322',   # 小哭脸符号 ∩
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\eqslantless': '\u2A95',  # 等于小于符号 ⋕
    r'\eqslantgtr': '\u2A96',  # 等于大于符号 ⋖
    r'\backepsilon': '\u03F6',  # 反属于符号 ϶
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\lessdot': '\u22D6',      # 小于号（圆点） ⋖
    r'\gtrdot': '\u22D7',       # 大于号（圆点） ⋗
    r'\gtreqless': '\u22DA',    # 大于等于小于符号 ≪
    r'\lesssim': '\u2272',      # 小于等于号（波浪线） ≲
    r'\gtrsim': '\u2273',       # 大于等于号（波浪线） ≳
    r'\gtrless': '\u22DA',      # 大于等于小于符号 ≪
    r'\gtrless': '\u22D4',      # 大于小于符号 ⋔
    r'\pitchfork': '\u22D4',    # 叉号 ⋔
    r'\Subset': '\u22D0',       # 真子集（双括号） ⊂
    r'\Supset': '\u22D1',       # 真超集（双括号） ⊃
    r'\shortmid': '\u2223',     # 整除号 |
    r'\precapprox': '\u2AB7',   # 小于等于号（波浪线） ⋷
    r'\succapprox': '\u2AB8',   # 大于等于号（波浪线） ⋸
    r'\pitchfork': '\u22D4',    # 叉号 ⋔
    r'\Subset': '\u22D0',       # 真子集（双括号） ⊂
    r'\Supset': '\u22D1',       # 真超集（双括号） ⊃
    r'\shortmid': '\u2223',     # 整除号 |
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\pitchfork': '\u22D4',    # 叉号 ⋔
    r'\Subset': '\u22D0',       # 真子集（双括号） ⊂
    r'\Supset': '\u22D1',       # 真超集（双括号） ⊃
    r'\shortmid': '\u2223',     # 整除号 |
    r'\precapprox': '\u2AB7',   # 小于等于号（波浪线） ⋷
    r'\succapprox': '\u2AB8',   # 大于等于号（波浪线） ⋸
    r'\pitchfork': '\u22D4',    # 叉号 ⋔
    r'\Subset': '\u22D0',       # 真子集（双括号） ⊂
    r'\Supset': '\u22D1',       # 真超集（双括号） ⊃
    r'\shortmid': '\u2223',     # 整除号 |
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\pitchfork': '\u22D4',    # 叉号 ⋔
    r'\Subset': '\u22D0',       # 真子集（双括号） ⊂
    r'\Supset': '\u22D1',       # 真超集（双括号） ⊃
    r'\shortmid': '\u2223',     # 整除号 |
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线） ≾
    r'\succsim': '\u227F',      # 大于等于号（波浪线） ≿
    r'\between': '\u226C',      # 在之间 ≬
    r'\precsim': '\u227E',      # 小于等于号（波浪线）
    r'\succsim': '\u227F',      # 大于等于（波浪线） ≽
    r'\between': '\u226C',       # 在...之间 ≬
    r'\doteqdot': '\u2251',     # 点等于（双点） ≑
    r'\precapprox': '\u2AB7',    # 小于等于（波浪线） ⪷
    r'\succapprox': '\u2AB8',    # 大于等于（波浪线） ⪸
    r'\pitchfork': '\u22D4',     # 十字架 ⊥
    r'\thickapprox': '\u2248',   # 近似等于（粗） ≈
    r'\Subset': '\u22D0',        # 真子集（粗） ⊂
    r'\Supset': '\u22D1',        # 真超集（粗） ⊃
    r'\shortmid': '\u2223',      # 整除号（短） |
    r'\fallingdotseq': '\u2252', # 向下点等于 ≒
    r'\subseteqq': '\u2AC5',    # 子集（双线） ⊆
    r'\supseteqq': '\u2AC6',    # 超集（双线） ⊇
    r'\smallfrown': '\u2322',    # 小哭脸符号 ⊹
    r'\risingdotseq': '\u2253',  # 向上点等于 ≓
    r'\sqsubset': '\u228F',      # 方形真子集 ⊏
    r'\sqsupset': '\u2290',      # 方形真超集 ⊐
    r'\smallsmile': '\u2323',    # 小笑脸符号 ⊺
    r'\varpropto': '\u221D',     # 成比例（变体） ∝
    r'\preccurlyeq': '\u227C',   # 小于等于（波浪线） ⪸
    r'\succcurlyeq': '\u227D',   # 大于等于（波浪线） ⪹
    r'\Vdash': '\u22A9',        # 双垂直线 ⊩
    r'\therefore': '\u2234',     # 因此 ∴
    r'\curlyeqprec': '\u22DE',   # 左卷曲等于 ⪻
    r'\curlyeqsucc': '\u22DF',   # 右卷曲等于 ⪼
    r'\vDash': '\u22A8',        # 垂直线 ⊩
    r'\because': '\u2235',       # 因为 ∵
    r'\blacktriangleleft': '\u25C3', # 左黑三角 ⊲
    r'\blacktriangleright': '\u25B9', # 右黑三角 ⊳
    r'\Vvdash': '\u22AA',        # 双垂直线（粗） ⊪
    r'\eqcirc': '\u2256',        # 圆等于 ≖
    r'\trianglelefteq': '\u22B4', # 左三角等于 ⪴
    r'\trianglerighteq': '\u22B5', # 右三角等于 ⪵
    r'\shortparallel': '\u2225', # 平行线（短） ∥
    r'\vartriangleleft': '\u22B2', # 左三角（变体） ⊲
    r'\vartriangleright': '\u22B3', # 右三角（变体） ⊳
    r'\nshortparallel': '\u2226', # 不平行 ∦
    r'\ncong': '\u2247',       # 不同于 ≅
    r'\nleq': '\u226E',        # 不小于等于 
    r'\ngeq': '\u226F',        # 不大于等于 
    r'\nsubseteq': '\u2288',   # 不是子集 *
    r'\nmid': '\u2224',        # 不整除 -
    r'\nleqq': '\u2270',       # 不小于等于 
    r'\ngeqq': '\u2271',       # 不大于等于 
    r'\nsupseteq': '\u2289',   # 不是超集 +
    r'\nparallel': '\u2226',   # 不平行 ∦
    r'\nleqslant': '\u2A7D',   # 不小于等于 
    r'\ngeqslant': '\u2A7E',   # 不大于等于 "
    r'\nsubseteqq': '\u2AC5',  # 不是子集 ⊆
    r'\nshortmid': '\u2224',   # 不整除 .
    r'\nless': '\u226E',       # 不小于 ≮
    r'\ngtr': '\u226F',        # 不大于 ≯
    r'\nsupseteqq': '\u2AC6',  # 不是超集 ⊇
    r'\nparallel': '\u2226',   # 不平行 ∥
    r'\nprec': '\u22E0',       # 不小于 ≺
    r'\nsucc': '\u22E1',       # 不大于 
    r'\subsetneq': '\u228A',   # 真子集 ⊂
    r'\nsim': '\u2241',        # 不同于 ∼
    r'\preceq': '\u227C',      # 小于等于（偏序） 
    r'\succeq': '\u227D',      # 大于等于（偏序） 
    r'\supsetneq': '\u228B',   # 真超集 ⊃
    r'\nVDash': '\u22AF',      # 不模型 
    r'\precnapprox': '\u2AB9', # 不小于约等 
    r'\succnapprox': '\u2ABA', # 不大于约等 $
    r'\subsetneqq': '\u228A',  # 真子集 ⊂
    r'\nvdash': '\u22AE',      # 不证明 
    r'\precnsim': '\u22E8',    # 不小于同构 
    r'\succnsim': '\u22E9',    # 不大于同构 )
    r'\supsetneqq': '\u228B',  # 真超集 ⊃
    r'\nvDash': '\u22AD',      # 不逻辑蕴含 
    r'\lnapprox': '\u2249',    # 不近似等于 
    r'\gnapprox': '\u2249',    # 不近似等于
    r'\varsubsetneq': '\u228A',# 真子集 ⊂
    r'\ntriangleleft': '\u22EA',# 不左三角 
    r'\lneq': '\u2A87',        # 小于（严格） <
    r'\gneq': '\u2A88',        # 大于（严格） >
    r'\varsupsetneq': '\u228B',# 真超集 ⊃
    r'\ntrianglelefteq': '\u22EC',# 不左三角等于 
    r'\lneqq': '\u2268',       # 小于等于（严格） ≤
    r'\gneqq': '\u2269',       # 大于等于（严格） ≥
    r'\varsubsetneqq': '\u228A',# 真子集 ⊂
    r'\ntriangleright': '\u22EB',# 不右三角 
    r'\lnsim': '\u2244',       # 不同于 ∼
    r'\gnsim': '\u2247',       # 不同于 ≅
    r'\varsupsetneqq': '\u228B',# 真超集 ⊃
    r'\ntrianglerighteq': '\u22ED',# 不右三角等于 
}

Arrow_symbols = {
    r'\leftarrow': '\u2190',     # 左箭头 ←
    r'\longleftarrow': '\u219A', # 长左箭头 ←−
    r'\uparrow': '\u2191',       # 上箭头 ↑
    r'\Leftarrow': '\u21D0',     # 左双箭头 ⇐
    r'\Longleftarrow': '\u21D4', # 长左双箭头 ⇐=
    r'\Uparrow': '\u21D1',       # 双上箭头 ⇑
    r'\rightarrow': '\u2192',    # 右箭头 →
    r'\longrightarrow': '\u219B',# 长右箭头 −→
    r'\downarrow': '\u2193',     # 下箭头 ↓
    r'\Rightarrow': '\u21D2',    # 右双箭头 ⇒
    r'\Longrightarrow': '\u21D5',# 长右双箭头 =⇒
    r'\Downarrow': '\u21D3',     # 双下箭头 ⇓
    r'\leftrightarrow': '\u2194',# 左右箭头 ↔
    r'\longleftrightarrow': '\u219C',# 长左右箭头 ←→
    r'\updownarrow': '\u2195',   # 上下箭头 l
    r'\Leftrightarrow': '\u21D4',# 左右双箭头 ⇔
    r'\Longleftrightarrow': '\u21D6',# 长左右双箭头 ⇐⇒
    r'\Updownarrow': '\u21D5',   # 双上下箭头 m
    r'\mapsto': '\u21A6',        # 映射箭头 7→
    r'\longmapsto': '\u27FC',    # 长映射箭头 7−→
    r'\nearrow': '\u2197',       # 右上箭头 %
    r'\hookleftarrow': '\u21A9', # 左钩箭头 ←-
    r'\hookrightarrow': '\u21AA',# 右钩箭头 →
    r'\searrow': '\u2198',       # 右下箭头 &
    r'\leftharpoonup': '\u21BC', # 左上鱼叉箭头 (
    r'\rightharpoonup': '\u21C0',# 右上鱼叉箭头 *
    r'\swarrow': '\u2199',       # 左下箭头 .
    r'\leftharpoondown': '\u21BD',# 左下鱼叉箭头 )
    r'\rightharpoondown': '\u21C1',# 右下鱼叉箭头 +
    r'\nwarrow': '\u2196',       # 左上箭头 -
    r'\rightleftharpoons': '\u21CC',# 左右鱼叉箭头
    r'\leadsto': '\u21D2',       # 导致箭头
    r'\dashrightarrow': '\u21A6', # 右虚线箭头
    r'\dashleftarrow': '\u21A4',  # 左虚线箭头
    r'\leftleftarrows': '\u21C7', # 左左箭头
    r'\Lleftarrow': '\u21DA',    # 左双虚线箭头
    r'\twoheadleftarrow': '\u219E',# 左双头箭头
    r'\leftarrowtail': '\u21A2',  # 左箭头尾
    r'\looparrowleft': '\u21AB',  # 左环箭头
    r'\leftrightharpoons': '\u21CB',# 左右鱼叉箭头
    r'\curvearrowleft': '\u21B6', # 左曲线箭头
    r'\circlearrowleft': '\u21BA',# 左环形箭头
    r'\Lsh': '\u21B0',            # 左转向箭头
    r'\upuparrows': '\u21C8',      # 上上箭头
    r'\upharpoonleft': '\u21BF',   # 左上鱼叉箭头
    r'\downharpoonleft': '\u21C3', # 左下鱼叉箭头
    r'\multimap': '\u22B8',        # 多重映射箭头
    r'\leftrightsquigarrow': '\u21AD',# 左右波浪箭头
    r'\rightrightarrows': '\u21C9',# 右右箭头
    r'\twoheadrightarrow': '\u21A0',# 右双头箭头
    r'\rightarrowtail': '\u21A3',  # 右箭头尾
    r'\looparrowright': '\u21AC',  # 右环箭头
    r'\curvearrowright': '\u21B7', # 右曲线箭头
    r'\circlearrowright': '\u21BB',# 右环形箭头
    r'\Rsh': '\u21B1',            # 右转向箭头
    r'\downdownarrows': '\u21CA',  # 下下箭头
    r'\upharpoonright': '\u21BE',  # 右上鱼叉箭头
    r'\downharpoonright': '\u21C2',# 右下鱼叉箭头
    r'\rightsquigarrow': '\u21DD', # 右波浪箭头
    r'\nleftarrow': '\u219A',      # 长左箭头
    r'\nrightarrow': '\u219B',     # 长右箭头
    r'\nLeftarrow': '\u21D0',      # 长左双箭头
    r'\nRightarrow': '\u21D2',     # 长右双箭头
    r'\nleftrightarrow': '\u21AE', # 长左右箭头
    r'\nLeftrightarrow': '\u21D4', # 长左右双箭头
}

Miscellaneous_symbols = {
    r'\infty': '\u221E',       # 无穷大符号 ∞
    r'\forall': '\u2200',      # 对所有 ∀
    r'\Bbbk': '\u0136',        # 黑体k k
    r'\wp': '\u2118',          # 脚本小写p ℘
    r'\nabla': '\u2207',       # 倒三角（梯度） ∇
    r'\exists': '\u2203',      # 存在 ∃
    r'\bigstar': '\u2605',     # 大星形 ★
    r'\angle': '\u2220',       # 角 ∠
    r'\partial': '\u2202',     # 偏导数符号 ∂
    r'\nexists': '\u2204',     # 不存在 ∄
    r'\diagdown': '\u2571',    # 斜线 /
    r'\measuredangle': '\u2221',# 测量角 ∡
    r'\eth': '\u00F0',          # 小写eth ð
    r'\emptyset': '\u2205',    # 空集 ∅
    r'\diagup': '\u2572',      # 斜线 \
    r'\sphericalangle': '\u2222',# 球面角 ∢
    r'\clubsuit': '\u2663',     # 梅花 ♣
    r'\varnothing': '\u2205',  # 空集 ∅
    r'\Diamond': '\u25C7',     # 菱形 ◇
    r'\complement': '\u2201',  # 补集 ∁
    r'\diamondsuit': '\u2666', # 方块 ♦
    r'\imath': '\u0131',        # 小写i i
    r'\Finv': '\u2132',        # 反转F Ⅎ
    r'\triangledown': '\u25BD',# 下三角 ▽
    r'\heartsuit': '\u2665',   # 红心 ♥
    r'\jmath': '\u0237',        # 小写j j
    r'\Game': '\u2141',        # 游戏符号 ℁
    r'\triangle': '\u25B3',    # 上三角 △
    r'\spadesuit': '\u2660',   # 黑桃 ♠
    r'\ell': '\u2113',         # 脚本小写l ℓ
    r'\hbar': '\u210F',        # 简化哈密顿算符 ℏ
    r'\vartriangle': '\u2206', # 三角形差 Δ
    r'\cdots': '\u22EF',       # 中心省略号 ⋯
    r'\iiiint': '\u222F',      # 四重积分符号 ⨌
    r'\hslash': '\u210F',      # 简化哈密顿算符 ℏ
    r'\blacklozenge': '\u29EB',# 黑色菱形 ⬛
    r'\vdots': '\u22EE',       # 垂直省略号 ⋮
    r'\iiint': '\u222D',       # 三重积分符号 ⨛
    r'\lozenge': '\u25CA',     # 菱形 ◊
    r'\blacksquare': '\u25A0', # 黑色正方形 ■
    r'\ldots': '\u2026',       # 水平省略号 …
    r'\iint': '\u222C',        # 二重积分符号 ⨌
    r'\mho': '\u2127',         # 倒置M ℧
    r'\blacktriangle': '\u25B4',# 黑色上三角 ▲
    r'\ddots': '\u22F1',       # 斜省略号 ⋱
    r'\sharp': '\u266F',       # 升号 ♯
    r'\prime': '\u2032',       # 素数符号 ′
    r'\blacktrinagledown': '\u25BE',# 黑色下三角 ▼
    r'\Im': '\u2111',          # 虚部 ℑ
    r'\flat': '\u266D',        # 降号 ♭
    r'\square': '\u25A1',      # 正方形 □
    r'\backprime': '\u2035',   # 反素数符号 ‵
    r'\Re': '\u211C',          # 实部 ℜ
    r'\natural': '\u266E',     # 自然符号 ♮
    r'\surd': '\u221A',        # 平方根符号 √
    r'\circledS': '\u24C8',    # 圆圈S ⊘
}
#endregion

#region 主渲染函数
#2.矩阵、括号等需要给予整体缩放比例
#3.上下标需要调整位置比例
def read_AST(operators:list, scale=1, x=10, y=10):#读取AST，传递参数给各显示函数，传入的位置为实际显示的左上角nw西北位置
    i=0#这个AST设计的好处是，可以直接从左到右读写，从左到右便是显示顺序和计算顺序
    current_x = x
    max_height = 0
    DOM_tree = []
    while i < len(operators) - 1:#对于渲染来说，可以分类为这几种：
        elem = operators[i]
        #0.如果是列表，递归处理,顺序阅读判读到的列表，不参与缩放问题，不添加缩放系数，但应该添加括号
        if isinstance(elem, list):
            TEXT = Render_brace('left',(current_x, y),1.5*scale)
            scale_memory = scale#暂存缩放大小
            current_x += int(7/scale)
            text, current_x = read_AST(elem, scale, current_x, y)[0:1]
            TEXT = TEXT + text
            current_x += int(7/scale)#移位
            scale = scale_memory#恢复缩放大小
            TEXT = TEXT + Render_brace('right',(current_x, y),1.5*scale)
            DOM_tree.append(TEXT)
            i += 1
            continue
        match elem:
            #1.分式、积分、求和、极限、累乘、根式等需要给予上下位置特殊处理
            case r'\frac':
                DOM_tree.append(Render_frac((count_len(operators[i+1]),count_len(operators[i+2])),(current_x, y),scale))#分数绘制
                if isinstance(operators[i+1], list):
                    TEXT = read_AST(operators[i+1], scale+1 if scale!=1 else scale, current_x, y+20/scale)[0]#分子递归渲染
                else:TEXT = Render_text(operators[i+1], scale, current_x, y+20/scale)
                DOM_tree.append(TEXT)
                if isinstance(operators[i+2], list):
                    TEXT = read_AST(operators[i+2], scale+1 if scale!=1 else scale, current_x, y-20/scale)#分母递归渲染
                else:TEXT = Render_text(operators[i+2], scale, current_x, y-20/scale)
                DOM_tree.append(TEXT)
                i += 3
            #根号处理（带自适应缩放）
            case r'\sqrt':
                if operators[i+1] == '2'|2:#二次根式
                    TEXT = Render_sqrt(count_len(operators[i+2]),(current_x, y),scale)#根号绘制2
                else:
                    TEXT = Render_text(operators[i+2],(current_x,y),1.5*scale) + Render_sqrt(count_len(operators[i+2]),(current_x, y),scale)#根号绘制
                    TEXT.type = 'sqrt'
                    current_x += int(7/scale)
                DOM_tree.append(TEXT)
                if isinstance(operators[i+2], list):
                    TEXT = read_AST(operators[i+2], scale+1 if scale!=1 else scale, current_x, y)[0]#根式递归渲染
                else:TEXT = Render_text(operators[i+2], scale, current_x, y)
                DOM_tree.append(TEXT)
                current_x += int(7/scale)
                i += 3
            # 积分/求和符号处理
            case r'\int':
                DOM_tree.append(Render_int((current_x, y),scale))
                if operators[i+1] and operators[i+2]:#存在上下限，不定积分、求和、累乘
                    pass
            case r'\sum':#求和符号
                DOM_tree.append(Render_sum((current_x, y),scale))
                if operators[i+1] and operators[i+2]:#存在上下限，不定积分、求和、累乘
                    pass
            case r'\prod':#累乘符号
                DOM_tree.append(Render_prod((current_x, y),scale))
                if isinstance(operators[i+1], list):
                    read_AST(operators[i+1], scale+1 if scale!=1 else scale, current_x, y)#下限递归渲染
                else:Render_text(operators[i+1], scale, current_x, y)
            case r'\lim':
                Render_lim((current_x, y),scale)
                if isinstance(operators[i+2], list):
                    read_AST(operators[i+2], scale+1 if scale!=1 else scale, current_x, y)#上限递归渲染
                else:Render_text(operators[i+2], scale, current_x, y)
             # 绝对值自动生成括号
            case r'\abs':
                pass
            # 普通字符处理
            case str() if not elem.startswith('\\'):
                pass
            #2.括号
            case r'':
                pass
            # 处理上下标
            case '_' | '^':
                pos_type = 'sub' if elem == '_' else 'sup'
                base_width = current_x - x
                content = operators[i+1]
                offset = 5*scale if pos_type == 'sub' else -5*scale
                read_AST(content, scale*0.6, x + base_width, y + offset)
                i += 2
            # 处理普通字符
            case str() if not elem.startswith('\\'):
                char_width = LaTeXRenderer.render_char(elem, current_x, y, scale)
                current_x += char_width
                i += 1
            # 自动生成括号
            case '(' | '[' | '{':
                bracket_width = LaTeXRenderer.render_bracket(elem, operators[i+1], current_x, y, scale)
                current_x += bracket_width
                i += 2  # 跳过括号内容（已作为子列表处理）
            case _:
                # 处理未识别符号
                i += 1
    return DOM_tree,current_x - x, max_height # 返回总宽度

#endregion

#region 函数
def count_len(operators: list[str]|str) -> int:#计算长度的工具函数，用于传参
    """计算latex表达式长度"""
    total_len = 0
    if isinstance(operators, str):
        return len(operators)
    for i in operators:
        match i:
            case r'\int'|r'\sum'|r'\prod':#积分、求和、累乘记为3个字符大小
                total_len += 3
            case r'\log'|r'\sin'|r'\cos'|r'\tan'|r'\sec'|r'\csc'|r'\cot'|r'\gcd'|r'\max'|r'\min':#函数记为3个字符大小
                total_len += 3
            case r'\lim':#极限记为5个字符大小
                total_len += 5
            case r'\abs'|r'\ln'|r'\lg':#绝对值、自然对数、对数记为2个字符大小
                total_len += 2
            case r'\div'|r'+'|r'-'|r'\times'|r'\cdot'|r'='|r'^':#运算符记为1个字符大小
                total_len += 1
            case str():
                total_len += len(i)#字符串记为字符串长度
            case list():
                total_len += count_len(i)#递归计算列表长度
            case _:raise TypeError(f'invalid type{i}')
    return total_len

#endregion

#region 类函数
class LaTeXRenderer:
    def __init__(self,type: str,segment_id: list[str]|None = None,canvas: tk.Canvas = None):
        if type in ['sqrt','frac','int','sum','prod','lim','text','symbol','operator','brace','mixed','space','needle']:
            self.type = type
        else:raise TypeError('invalid render type')
        self.segment_ids = segment_id# 存储线段/文字ID
        if self.segment_ids is None:raise ValueError('segment_id is None')
        self.canvas = canvas
        if not canvas:raise ValueError('canvas is empty')

    def __add__(self, other):
        """重载加号，用于合并两个LaTeXRenderer对象"""
        if isinstance(other, LaTeXRenderer):
            self.segment_ids.extend(other.segment_ids)
            self.type = 'mixed'
            return self
        else:
            raise TypeError('invalid type')

    def erase(self):
        """擦除所有已记录元素"""
        for segment_id in self.segment_ids:
            if segment_id is LaTeXRenderer:del(segment_id)# 考虑可能的递归结构，删除LaTeXRenderer对象
            else:self.canvas.delete(segment_id)
        self.segment_ids.clear()

    def __del__(self):
        """对象销毁时自动执行擦除"""
        try:
            if self.canvas and self.segment_ids: self.erase()
        except Exception as e: pass # 捕获tkinter对象已销毁的情况
#endregion

#region 渲染函数
#各个渲染函数统一传参位置为左上角nw位置，统一使用论文字体Times New Roman
def Render_sqrt(len: int = 20, location: tuple = (10,10), scale=1.0):# 渲染根号
    scaled_len = len * scale * 1.2  # 缩放后的长度
    x, y = location  # 根号左上角位置
    id1 = canvas.create_line(x, y, x + scaled_len, y, fill="black", width = max(1,round(scale*14*0.092)))  # 绘制根号水平线
    id2 = canvas.create_text(x, y, text="√", anchor="ne", fill="black", font=("Times New Roman", int(scale * 14)))#绘制根号符号
    return LaTeXRenderer('sqrt',[id1, id2],canvas = canvas)

def Render_frac(len: tuple = (20,20),location: tuple = (10,50),scale=1.0):#直接渲染分数线函数,传入分子分母长度以及分数线头端位置
    len_frac = 1.2*scale*max(len)#获取分母分子长度最大值，算出分数线长度
    id = canvas.create_line(location[0],location[1],location[0]+len_frac,location[1],fill="black",width=scale*2)#绘制分数线
    return LaTeXRenderer('frac',[id],canvas = canvas)

def Render_text(string: str,location: tuple = (10,50),scale=1.0):#直接渲染文本函数
    id = canvas.create_text(location,text=string,anchor = 'nw',fill="black",font=("Times New Roman",int(scale*10)))#绘制文本
    return LaTeXRenderer('text',[id],canvas = canvas)

def Render_int(location: tuple = (20,120), scale=1.0):
    """改进后的积分符号渲染函数"""
    id = canvas.create_text(location,text=Variable_sized_symbols[r'\int'],anchor = 'nw',font=("Times New Roman",int(scale*25)))
    return LaTeXRenderer('int', [id], canvas = canvas)

def Render_sum(location: tuple = (20,120), scale=1.0):
    """改进后的求和符号渲染函数"""
    id = canvas.create_text(location,text=Variable_sized_symbols[r'\sum'],anchor = 'nw',font=("Times New Roman", int(scale*20)))
    return LaTeXRenderer('sum', [id], canvas = canvas)

def Render_prod(location: tuple = (20,120), scale=1.0):
    """改进后的累乘符号渲染函数"""
    id= canvas.create_text(location,text=Variable_sized_symbols[r'\prod'],anchor = 'nw',font=("Times New Roman", int(scale*20)))
    return LaTeXRenderer('prod', [id], canvas = canvas)

def Render_lim(location: tuple = (20, 100), scale=1.0):
    """优化后的极限符号渲染函数
    参数：
        has_subscript - 是否包含下标（自动调整位置）
    """
    # 基础尺寸调整
    base_height = 18  # 比积分符号稍大
    font_size = int(base_height * scale)
    
    # 字体配置（优先使用数学正体字体）
    math_fonts = (
        "Cambria Math", 
        "Times New Roman",
        "DejaVu Serif",
        "STIXGeneral",
        "Symbol",
        "Arial",
    )
    
    # 创建文本对象（强制正体显示）
    lim_id = canvas.create_text(location,text="lim",anchor = 'nw',font=(math_fonts[1], font_size),angle=0,tags="math_text")# 创建文本对象
    return LaTeXRenderer('lim', [lim_id], canvas = canvas)

def Render_operators(string,location: tuple = (10,50),scale=1.0):#绘制运算符
    id = canvas.create_text(location,text=Binary_Operation[string],anchor = 'nw',fill="black",font=("Times New Roman",int(scale*20)))#绘制文本
    return LaTeXRenderer('operator',[id],canvas = canvas)

def Render_brace(type:str = 'left',location: tuple = (10,50),scale=1.0):#绘制括号
    if type == 'left':id = canvas.create_text(location,text="(",anchor = 'nw',fill="black",font=("Times New Roman",int(scale*20)))#绘制文本
    elif type == 'right':id = canvas.create_text(location,text=")",anchor = 'nw',fill="black",font=("Times New Roman",int(scale*20)))#绘制文本
    else:raise ValueError('invalid brace type')
    return LaTeXRenderer('brace',[id],canvas = canvas)

def Render_symbol(string: str,location: tuple = (10,50),scale=1.0):#绘制符号
    id = canvas.create_text(location,text=string,anchor = 'nw',fill="black",font=("Times New Roman",int(scale*20)))#绘制文本
    return LaTeXRenderer('symbol',[id],canvas = canvas)

def Render_space(location: tuple = (10,50),scale=1.0):#绘制空格
    id = canvas.create_text(location,text="□",anchor = 'nw',fill="black",font=("Times New Roman",int(scale*20)))#绘制文本
    return LaTeXRenderer('space',[id],canvas = canvas)

def Render_needle(location: tuple = (10,50),scale=1.0):#绘制指针
    id = canvas.create_text(location,text="|",anchor = 'nw',fill="black",font=("Times New Roman",int(scale*20)))#绘制文本
    return LaTeXRenderer('needle',[id],canvas = canvas)
#endregion

#region 显示框设置
WINDOW_SIZE = (400,150)#显示框大小
if __name__ == "__main__":
    root = tk.Tk()
    root.title("LaTeX Renderer")
    root.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
    # font = ("TkDefaultFont", 12)

    # 创建一个Canvas画布，宽度为800像素，高度为300像素
    canvas = tk.Canvas(root, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])
    canvas.pack()
    # # 在画布上添加参考线
    # for x in range(0, WINDOW_SIZE[0]+1, 50):
    #     canvas.create_line(x, 0, x, WINDOW_SIZE[1], fill='gray', dash=(4,2))  # 垂直参考线
    # for y in range(0, WINDOW_SIZE[1]+1, 50):
    #     canvas.create_line(0, y, WINDOW_SIZE[0], y, fill='gray', dash=(4,2))  # 水平参考线
    # # 测试渲染时应使用可见坐标
    # integal = Render_int(location=(200, 100), scale=1.0)  # 对齐到红色参考线

    # sqrt = Render_sqrt(len = 10,location=(100, 10), scale=1.0)
    # operator = Render_operators(r"\times", location=(50, 100), scale=1.0)

    # frac = Render_frac(len =(20,20),location=(100, 75), scale=1.5)
    # text = Render_text("Hello, World!", location=(50, 25), scale=1.0)
    # integal = Render_int(location=(200, 50), scale=1.0)
    # sum = Render_sum(location=(30, 10), scale=1.0)
    # prod = Render_prod(location=(250, 10), scale=1.0)
    # lim = Render_lim(location=(350, 25), scale=1.0)

    root.mainloop()
#endregion