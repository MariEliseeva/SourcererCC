import re
import zipfile
import difflib

def GetInfo(num):
    with open('tokenizers/block-level/blocks_tokens/files-tokens-0.tokens','r',encoding='utf8') as fin:
        for line in fin:
            x = line.split(',')
            x[1] = int(x[1])
            if x[1] == num:
                x[0] = int(x[0])
                with open('tokenizers/block-level/bookkeeping_projs/bookkeeping-proj-0.projs','r') as fin2:
                    for line2 in fin2:
                        y = line2.split(',')
                        y[0] = int(y[0])
                        if y[0] == x[0]:
                            project_full = "tokenizers/block-level/" + y[1][1:-1]
                            z = re.match(r'"(.*)/(.*).zip"',"\"tokenizers/block-level/" + y[1][1:]) 
                            project_short = z.group(2)
                x[2] = int(x[2])
                name = line.split(')')[0].split('(')[0].split(',')[4] + '(' + line.split(')')[0].split('(')[1] + ')'
                length = x[2]

    with open('tokenizers/block-level/file_block_stats/files-stats-0.stats','r') as fin:
        for line in fin:
            x = line.split(',')
            x[2] = int(x[2])
            if x[2] == num % 10000000:
                z = re.match(r'"NULL(.*)"',x[4])
                address_full = x[4][6:-1]
                address_short = z.group(1)
            if x[2] == num:
                number_of_lines = x[7] + '-' + x[8]
                starting_line = int(x[7])
                end_line = int(x[8])
                    
    block_code = ""
    with zipfile.ZipFile(project_full,'r') as zipin:
        with zipin.open(address_full,'r') as fin:
            lines = fin.readlines()
            for i in range(starting_line-1,end_line-1):
                block_code = block_code + lines[i].decode("utf-8")
    return([project_short,name,length,address_short,number_of_lines,block_code])


def expand_diff_line(line, diff):
    res = list(diff.replace("-", "^").replace("+", "^").replace("\t", " ") + " " * (len(line) - len(diff)))
    token_start = -1
    met_diff = False
    for i, char in enumerate(line):
        if not char.isalpha() and not char.isdigit():
            if met_diff:
                for j in range(token_start, i):
                    res[j] = '^'
            met_diff = False
            token_start = -1
        elif token_start == -1:
            token_start = i
        if res[i] == '^':
            for j in range(token_start, i):
                res[j] = '^'
            token_start = i
            met_diff = True
    return "".join(res)


def modified_diff(block1, block2):
    i = 0
    line_num = 0
    block1_lines = {}
    block2_lines = {}
    block1 = block1.split("\n")
    block2 = block2.split("\n")
    diff_lines = list(map(lambda x: x.rstrip("\n"), difflib.Differ().compare(block1, block2)))
    while i < len(diff_lines):
        line = diff_lines[i]
        if line[0] == '-':
            if i + 1 < len(diff_lines) and diff_lines[i + 1][0] == '?':
                block1_lines[line_num] = (line, expand_diff_line(line, diff_lines[i + 1]))
                i += 1
                if i + 1 < len(diff_lines) and diff_lines[i + 1][0] != '+':
                    block2_lines[line_num] = ("", "")
            else:
                block1_lines[line_num] = (line, "? ")
        elif line[0] == '+':
            if i - 2 >= 0 and diff_lines[i - 1][0] == '?' and diff_lines[i - 2][0] == '-' or i - 1 >= 0 and diff_lines[i - 1][0] == '-':
                line_num -= 1
            if i + 1 < len(diff_lines) and diff_lines[i + 1][0] == '?':
                block2_lines[line_num] = (line, expand_diff_line(line, diff_lines[i + 1]))
                i += 1
            else:
                block2_lines[line_num] = (line, "? ")
        else:
            block1_lines[line_num] = (line, "")
            block2_lines[line_num] = (line, "")
        line_num += 1
        i += 1
    return (block1_lines, block2_lines)


def html_format_diff_line(code_line, diff_line):
    if code_line == "":
        return ""
    modify_types = {"+": "add", "-": "rm"}
    modify_type = modify_types[code_line[0]] if code_line[0] in modify_types else ""
    res = code_line[2:]
    diff = diff_line[2:]
    k = 0
    i = 0
    while i < len(diff):
        if diff[i] == ' ':
            k += 1
            i += 1
        else:
            j = i
            while j < len(diff) and diff[j] == '^':
                j += 1
            res = f'{res[:k]}<span class="{modify_type}">{res[k:k + j - i].replace(" ", "&nbsp;")}</span>{res[k + j - i:]}'
            k += j - i + len(f'<span class="{modify_type}"></span>')
            i = j
    spaces = 0
    while spaces < len(res) and res[spaces] == ' ':
        spaces += 1
    res = "&nbsp;" * spaces + res[spaces:]
    if diff_line == "? ":
        res = f'<span class = "{modify_type}">{res}</span>'
    return res.replace("\t", "--->")


def html_format_code_row(shown_line_num, code_html_line):
    return f"""<td class="line_num">{shown_line_num}</td>
    <td style="text-align:left">{code_html_line}</td>"""


def html_format_header(title, info):
    info_table = "\n".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in info.items())
    return f"""<th colspan="2" class="header">
        {title}
        <table>
            {info_table}
        </table>
    </th>"""


def html_format_line(cur_line_num, diff_lines, line_num):
    code_line, diff_line, shown_line_num = "", "", ""
    if line_num in diff_lines:
        code_line, diff_line = diff_lines[line_num]
        shown_line_num = cur_line_num
        cur_line_num += 1
    return html_format_diff_line(code_line, diff_line), shown_line_num, cur_line_num


def html_format_one_file_lines(start_line, diff_lines):
    result = ""
    cur_line_num = start_line
    for line_num in range(max(diff_lines.keys()) + 1):
        code_html_line, shown_line_num, cur_line_num = html_format_line(cur_line_num, diff_lines, line_num)
        result += f"<tr>{html_format_code_row(shown_line_num, code_html_line)}</tr>"
    return result


def html_format_two_files_lines(start_line_1, diff_lines_1, start_line_2, diff_lines_2):
    result = ""
    cur_line_num_1 = start_line_1
    cur_line_num_2 = start_line_2
    for line_num in range(max(max(diff_lines_1.keys()), max(diff_lines_2.keys())) + 1):
        code_html_line_1, shown_line_num_1, cur_line_num_1 = html_format_line(cur_line_num_1, diff_lines_1, line_num)
        code_html_line_2, shown_line_num_2, cur_line_num_2 = html_format_line(cur_line_num_2, diff_lines_2, line_num)
        result += f"""<tr>
            {html_format_code_row(shown_line_num_1, code_html_line_1)}
            {html_format_code_row(shown_line_num_2, code_html_line_2)}
        </tr>"""
    return result


def make_table(diff_lines, title, info, start_line):
    table_rows = html_format_one_file_lines(start_line, diff_lines)
    result_table = f"""<table rules="groups">
        <colgroup></colgroup>
        <colgroup></colgroup>
        <thead>
            <tr>
                {html_format_header(title, info)}
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>"""
    return result_table


def make_diff_table(diff_lines_1, title_1, info_1, start_line_1, diff_lines_2, title_2, info_2, start_line_2):
    table_rows = html_format_two_files_lines(start_line_1, diff_lines_1, start_line_2, diff_lines_2)
    return f"""<table rules="groups">
        <colgroup></colgroup>
        <colgroup></colgroup>
        <colgroup></colgroup>
        <colgroup></colgroup>
        <thead>
            <tr>
                {html_format_header(title_1, info_1)}
                {html_format_header(title_2, info_2)}
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>"""


my_style = """<head>
    <style type="text/css">
        table {
            border: black;
        }
        .header {
            background-color: #e0e0e0;
            text-align: center;
            font-weight: bold;
        }
        .line_num {background-color: #c0c0c0}
        .add {background-color: #aaffaa}
        .rm {background-color: #ffff77}
        tr {
            text-align: left;
        }
        tr:nth-child(odd) {
            background: #f5f5f5;
        }
        tr:hover {
            background-color: #c4e3f3;
        }
    </style>
</head>"""

inp = input('Enter the pair of blocks with a comma: ')
inp = inp.split(',')
print ('Getting information...')
res1 = GetInfo(int(inp[0]))
print ('Completed for the first block...')
res2 = GetInfo(int(inp[1]))
print ('Completed for the second block. Creating an HTML file...')

info_a = {
    "project": res1[0],
    "name": res1[1],
    "length": res1[2],
    "address": res1[3],
    "lines": res1[4]
}

info_b = {
    "project": res2[0],
    "name": res2[1],
    "length": res2[2],
    "address": res2[3],
    "lines": res2[4]
}

a, b = modified_diff(res1[5], res2[5])
page = my_style + make_diff_table(a, str(inp[0]), info_a, int(res1[4].split("-")[0]), b, str(inp[1]), info_b, int(res2[4].split("-")[0]))
with open(f"{inp[0]}-{inp[1]}.html",'w', encoding="utf-8") as fout:
    fout.write(page)
print ('DONE')
print(f"Check {inp[0]}-{inp[1]}.html for results")
