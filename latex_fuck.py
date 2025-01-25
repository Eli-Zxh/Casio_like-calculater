def extract_latex_commands(file_path):
    try:
        result = []
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().replace('\n', ' ')  # 将所有换行符转换为空格
            start = 0
            content_length = len(content)
            while (start := content.find('\\', start)) != -1:
                end = content.find(' ', start)
                if end == -1 or end >= content_length:
                    end = content_length  # 如果没有找到空格或空格在行末，则将end设为行末
                equ = content[start + 1:end]
                result.append(f"'\\{equ}'")
                start = end + 1
        print(', '.join(result))
    except FileNotFoundError:
        print(f"无法打开文件 {file_path}")

extract_latex_commands('./Casio_like-calculater/latex_fuck.txt')