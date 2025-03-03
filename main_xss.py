import random
from variable import load_variable_samples
from sanitizer import load_sanitizer_samples
from sink import load_sink_samples
from sequence import load_sequence_samples
from decorator import load_decorator_samples
from fragment import load_fragment_samples
import datetime
import os
import time

# start = time.time()
# 定义全局参数
### 包装器层数及概率
# decorator_level、decorator_weight、decorator_type、decorator_type_weight共同构成了包装器层数及概率的配置
# 通过调整这四个参数，可以实现测试用例集的圈复杂度分布与真实软件的圈复杂度分布的相似性
# decorator_level: 包装器层数列表
# decorator_weight: 包装器层数对应的概率列表
# decorator_type: 包装器类型列表，共有simple、function、class三种
# decorator_type_weight: 包装器类型对应的概率列表
decorator_level = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 13, 17, 20, 26, 30]
decorator_weight = [15, 19, 17, 16, 15, 11, 10, 10, 9, 9, 8, 8, 7, 7, 6]
decorator_type = ["simple", "function", "class"]
decorator_type_weight = [10, 5, 80]
### 片段数量及概率
# partition_num、partition_weight、partition_type、partition_type_weight共同构成了片段数量及概率的配置
# 通过调整这四个参数，与包装器层数及概率相配合，共同实现对真实软件的圈复杂度和耦合度的模拟
# partition_num: 片段数量列表
# partition_weight: 片段数量对应的概率列表
# partition_type: 片段类型列表，共有simple、function、class三种
# partition_type_weight: 片段类型对应的概率列表
fragment_num = [3, 4, 5, 6]
fragment_weight = [10, 20, 40, 30]
fragment_type = ["simple", "function", "class"]
fragment_type_weight = [10, 60, 5]
## 单个路径重复次数
repeat_num = 400

# 加载所有组件
## 变量
variables = load_variable_samples("xml/variable.xml")
controllable_variables = [x for x in variables if x.controllable]
uncontrollable_variables = [x for x in variables if not x.controllable]
print(f"controllable_variables: {len(controllable_variables)}")
print(f"uncontrollable_variables: {len(uncontrollable_variables)}")
## 安全机制
sanitizers = load_sanitizer_samples("xml/xss/sanitizer.xml")
print(f"sanitizers: {len(sanitizers)}")
## Sink点
sinks = load_sink_samples("xml/xss/sink.xml")
valid_sinks = [x for x in sinks if x.valid]
invalid_sinks = [x for x in sinks if not x.valid]
print(f"valid_sinks: {len(valid_sinks)}")
print(f"invalid_sinks: {len(invalid_sinks)}")
print(
    f"valid_sinks_sufficient_sanitizer: {sum(x.sufficient_sanitizers_count for x in valid_sinks)}"
)
print(
    f"valid_sinks_insufficient_sanitizer: {sum(x.insufficient_sanitizers_count for x in valid_sinks)}"
)
## 代码路径
sequences = load_sequence_samples("xml/sequence.xml")
## 包装器
decorators = load_decorator_samples("xml/decorator.xml")
## 片段
fragments = load_fragment_samples("xml/fragment.xml")

# 获取当前日期和时间，作为输出文件夹的名称
current_datetime = datetime.datetime.now()
## 将日期时间格式化为字符串，例如 '2023-04-01_15-30-45'
datetime_str = "output" + os.sep + current_datetime.strftime("XSS_%Y-%m-%d_%H-%M-%S")

# 创建输出文件夹
## 定义要创建的文件夹的完整路径（这里以当前脚本所在目录为例）
folder_path = os.path.join(os.getcwd(), datetime_str)
## 检查文件夹是否存在，如果不存在则创建
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    os.makedirs(folder_path + os.sep + "vuln")
    os.makedirs(folder_path + os.sep + "non-vuln")
    os.makedirs(folder_path + os.sep + "disc-civ-uiv")
    os.makedirs(folder_path + os.sep + "disc-civ-csv")
    os.makedirs(folder_path + os.sep + "disc-civ-cin")
    os.makedirs(folder_path + os.sep + "disc-cv-uv")
    os.makedirs(folder_path + os.sep + "disc-cv-cn")


# 渲染模板
def render_code(template, placeholder, code, max=-1):
    return template.replace(placeholder, code, max)


# 选择包装器，生成包装器列表
def choose_decorators(decorators_all, level):
    list_decorators = []
    # 判断包装层数是否大于0
    if level > 0:
        # 首先选择最顶层包装器
        # 这里只选择一个包装器，原因是有些包装器只能位于顶层
        # 顶层包装器共有类、函数、其他三种，这里按照一定的概率选择类和函数或者其他。
        type = random.choices(decorator_type, decorator_type_weight, k=1).pop()
        list_decorators = random.choices(
            [x for x in decorators_all if x.type == type], k=1
        )
        if level > 1:
            # 选择非顶层包装器，原因是有些包装器只能位于顶层
            list_decorators += random.choices(
                [x for x in decorators_all if x.istop == False], k=level - 1
            )
    # 返回选择的包装器列表
    return list_decorators


# 代码包装
def do_decorator(decorator_list, code):
    ## 先将包装器代码替换为{{ placeholder }}，此处需要反向遍历包装器列表
    for i in reversed(decorator_list):
        # 随机生成一个10位的随机字符串作为变量名，防止变量名冲突
        random_name = "".join(
            random.sample("zyxwvutsrqponmlkjihgfedcbaABCDEFGHIJKLMNOPQRSTUVWXYZ", 10)
        )
        decorator_code = i.code.replace(r"{{ random_name }}", random_name)
        # 通过替换占位符{{ placeholder }}，将包装器代码插入到代码中
        code = decorator_code.replace(r"{{ placeholder }}", code)
    # 返回经过包装的代码
    return code


# 选择代码片段，生成片段列表
def choose_fragments(fragments_all):
    # 随机选择代码片段数量，即sequence.xml中定义的代码片段占位符并不会全部使用，而是根据概率选择
    num = random.choices(fragment_num, fragment_weight, k=1).pop()
    list_fragments = []

    # 随机选择片段类型
    fragment_type_list = random.choices(fragment_type, fragment_type_weight, k=num)
    # 根据片段类型选择片段
    for i in fragment_type_list:
        list_fragments += random.sample([x for x in fragments_all if x.type == i], 1)
    # 返回选择的片段列表
    return list_fragments


# 替换代码片段
def do_fragment(fragments_list, code):
    for j in fragments_list:
        # 随机生成一个10位的随机字符串作为变量名，防止变量名冲突
        random_name = "".join(
            random.sample("zyxwvutsrqponmlkjihgfedcbaABCDEFGHIJKLMNOPQRSTUVWXYZ", 10)
        )
        fragment_code = j.code.replace(r"{{ random_name }}", random_name)
        # 通过替换占位符{{ fragment }}，将片段代码插入到代码中
        code = render_code(code, r"{{ fragment }}", fragment_code, 1)
    # 删除未使用的片段占位符
    code = code.replace(
        r"""            /***************** fragment begin ******************/
            {{ fragment }}
            /***************** fragment end *****************/""",
        "",
    )
    # 返回经过片段替换的代码
    return code


# 生成基本测试用例
def generate_basic_test_case(repeat=1):
    # 遍历路径
    for i in sequences:
        for r in range(repeat):
            test_case_file_name = f"{folder_path}{os.sep}{i.vulnerable()}{os.sep}XSS_test_case_{i.type}_{r}"
            cv = random.choice(controllable_variables)
            uv = random.choice(uncontrollable_variables)
            code = i.code

            if "VS" in i.type:
                vs = random.choice(valid_sinks)
                ss = random.choice([x for x in vs.sanitizers if x.sufficient])
                i_s = random.choice([x for x in vs.sanitizers if not x.sufficient])

                level_vs = random.choices(decorator_level, decorator_weight, k=1).pop()
                level_ss = random.choices(decorator_level, decorator_weight, k=1).pop()
                level_i_s = random.choices(decorator_level, decorator_weight, k=1).pop()

                code = render_code(
                    code,
                    r"{{ Valid_Sink }}",
                    do_decorator(choose_decorators(decorators, level_vs), vs.code),
                )
                code = render_code(
                    code,
                    r"{{ Insufficient_Sanitizer }}",
                    do_decorator(choose_decorators(decorators, level_ss), i_s.code),
                )
                code = render_code(
                    code,
                    r"{{ Sufficient_Sanitizer }}",
                    do_decorator(choose_decorators(decorators, level_i_s), ss.code),
                )

            else:
                ns = random.choice(invalid_sinks)
                ss = random.choice(sanitizers)
                i_s = random.choice(sanitizers)

                level_ns = random.choices(decorator_level, decorator_weight, k=1).pop()
                level_ss = random.choices(decorator_level, decorator_weight, k=1).pop()
                level_i_s = random.choices(decorator_level, decorator_weight, k=1).pop()

                code = render_code(
                    code,
                    r"{{ Invalid_Sink }}",
                    do_decorator(choose_decorators(decorators, level_ns), ns.code),
                )
                code = render_code(
                    code,
                    r"{{ Sufficient_Sanitizer }}",
                    do_decorator(choose_decorators(decorators, level_ss), ss.code),
                )
                code = render_code(
                    code,
                    r"{{ Insufficient_Sanitizer }}",
                    do_decorator(choose_decorators(decorators, level_i_s), i_s.code),
                )

            level_uv = random.choices(decorator_level, decorator_weight, k=1).pop()
            level_cv = random.choices(decorator_level, decorator_weight, k=1).pop()

            code = render_code(
                code,
                r"{{ Uncontrollable_Variable }}",
                do_decorator(choose_decorators(decorators, level_uv), uv.code),
            )
            code = render_code(
                code,
                r"{{ Controllable_Variable }}",
                do_decorator(choose_decorators(decorators, level_cv), cv.code),
            )

            fragment_list = choose_fragments(fragments)
            code = do_fragment(fragment_list, code)

            if "CV" in i.type:
                test_case_file_name += f"_cv{cv.id}.{level_cv}"

            if "UV" in i.type:
                test_case_file_name += f"_uv{uv.id}.{level_uv}"

            if "NS" in i.type:
                test_case_file_name += f"_ns{ns.id}.{level_ns}"

            if "VS" in i.type:
                test_case_file_name += f"_vs{vs.id}.{level_vs}"

            if "SS" in i.type:
                test_case_file_name += f"_ss{ss.id}.{level_ss}"

            if "IS" in i.type:
                test_case_file_name += f"_is{i_s.id}.{level_i_s}"

            test_case_file_name += ".php"
            with open(test_case_file_name, "w", encoding="utf-8") as file:
                file.write(code)
            # print(f"Test case saved to {test_case_file_name}")


# 生成辨别率测试用例
def genrate_discrimination_test_case(repeat=1):
    for x in sequences:
        if x.type == "CV.IS.VS":
            sequence_civ = x
        elif x.type == "UV.IS.VS":
            sequence_uiv = x
        elif x.type == "CV.SS.VS":
            sequence_csv = x
        elif x.type == "CV.IS.NS":
            sequence_cin = x
        elif x.type == "CV.VS":
            sequence_cv = x
        elif x.type == "UV.VS":
            sequence_uv = x
        elif x.type == "CV.NS":
            sequence_cn = x

    sequence_groups = [
        {
            "name": "disc-civ-uiv",
            "vulnerable_sequence": sequence_civ,
            "non_vulnerable_sequence": sequence_uiv,
        },
        {
            "name": "disc-civ-csv",
            "vulnerable_sequence": sequence_civ,
            "non_vulnerable_sequence": sequence_csv,
        },
        {
            "name": "disc-civ-cin",
            "vulnerable_sequence": sequence_civ,
            "non_vulnerable_sequence": sequence_cin,
        },
        {
            "name": "disc-cv-uv",
            "vulnerable_sequence": sequence_cv,
            "non_vulnerable_sequence": sequence_uv,
        },
        {
            "name": "disc-cv-cn",
            "vulnerable_sequence": sequence_cv,
            "non_vulnerable_sequence": sequence_cn,
        },
    ]

    for group in sequence_groups:
        vulnerable_sequence = group["vulnerable_sequence"]
        non_vulnerable_sequence = group["non_vulnerable_sequence"]
        for r in range(repeat):
            vulnerable_testcase_file_name = f"{folder_path}{os.sep}{group['name']}{os.sep}XSS_test_case_{r}_{vulnerable_sequence.type}.php"
            non_vulnerable_testcase_file_name = f"{folder_path}{os.sep}{group['name']}{os.sep}XSS_test_case_{r}_{non_vulnerable_sequence.type}.php"

            cv = random.choice(controllable_variables)
            uv = random.choice(uncontrollable_variables)
            vs = random.choice(valid_sinks)
            ns = random.choice(invalid_sinks)
            i_s = random.choice([x for x in vs.sanitizers if not x.sufficient])
            ss = random.choice([x for x in vs.sanitizers if x.sufficient])

            der_list = [
                choose_decorators(
                    decorators,
                    random.choices(decorator_level, decorator_weight, k=1).pop(),
                )
                for n in range(3)
            ]

            vul_code = vulnerable_sequence.code
            non_vul_code = non_vulnerable_sequence.code

            vul_code = render_code(
                vul_code,
                r"{{ Uncontrollable_Variable }}",
                do_decorator(der_list[2], uv.code),
            )
            vul_code = render_code(
                vul_code,
                r"{{ Controllable_Variable }}",
                do_decorator(der_list[2], cv.code),
            )
            non_vul_code = render_code(
                non_vul_code,
                r"{{ Uncontrollable_Variable }}",
                do_decorator(der_list[2], uv.code),
            )
            non_vul_code = render_code(
                non_vul_code,
                r"{{ Controllable_Variable }}",
                do_decorator(der_list[2], cv.code),
            )

            vul_code = render_code(
                vul_code,
                r"{{ Insufficient_Sanitizer }}",
                do_decorator(der_list[1], i_s.code),
            )
            vul_code = render_code(
                vul_code,
                r"{{ Sufficient_Sanitizer }}",
                do_decorator(der_list[1], ss.code),
            )
            non_vul_code = render_code(
                non_vul_code,
                r"{{ Insufficient_Sanitizer }}",
                do_decorator(der_list[1], i_s.code),
            )
            non_vul_code = render_code(
                non_vul_code,
                r"{{ Sufficient_Sanitizer }}",
                do_decorator(der_list[1], ss.code),
            )

            vul_code = render_code(
                vul_code, r"{{ Valid_Sink }}", do_decorator(der_list[0], vs.code)
            )
            non_vul_code = render_code(
                non_vul_code, r"{{ Valid_Sink }}", do_decorator(der_list[0], vs.code)
            )
            non_vul_code = render_code(
                non_vul_code, r"{{ Invalid_Sink }}", do_decorator(der_list[0], ns.code)
            )

            fragment_list = choose_fragments(fragments)
            vul_code = do_fragment(fragment_list, vul_code)
            non_vul_code = do_fragment(fragment_list, non_vul_code)

            with open(vulnerable_testcase_file_name, "w", encoding="utf-8") as file:
                file.write(vul_code)
            # print(f"Test case saved to {vulnerable_testcase_file_name}")

            with open(non_vulnerable_testcase_file_name, "w", encoding="utf-8") as file:
                file.write(non_vul_code)
            # print(f"Test case saved to {non_vulnerable_testcase_file_name}")


if __name__ == "__main__":
    generate_basic_test_case(repeat_num)
    genrate_discrimination_test_case(repeat_num)

    # 代码格式化
    os.system(f"php php-cs-fixer.phar fix --show-progress=bar {datetime_str}")
    # 代码分析
    # os.system(f"php phploc-7.0.2.phar {datetime_str}")

    # end = time.time()
    # print(end - start)
