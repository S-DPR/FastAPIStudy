from request.config_structs import TestcaseConfig
from input_generator.base_generator import BaseGenerator, BaseConfig
from input_generator.line_generator import line_generator, LineConfig
from input_generator.matrix_generator import matrix_generator, MatrixConfig
from input_generator.query_generator import query_generator, QueryConfig
from input_generator.undirected_graph_generator import undirected_graph_generator, UndirectedGraphConfig

from request.parsing import create_variables
from request.expression import safe_eval

CONFIG_CLASS_REGISTRY = {
    "line": LineConfig,
    "undirected_graph": UndirectedGraphConfig,
    "matrix": MatrixConfig,
    "query": QueryConfig,
}

GENERATOR_INSTANCE_REGISTRY = {
    "line": line_generator,
    "undirected_graph": undirected_graph_generator,
    'matrix': matrix_generator,
    "query": query_generator,
}

def resolve_generator_config(type_name: str, variables: dict, config: dict) -> tuple[BaseGenerator, BaseConfig]:
    try:
        cfg_class = CONFIG_CLASS_REGISTRY[type_name]
        gen = GENERATOR_INSTANCE_REGISTRY[type_name]
        return gen, cfg_class(variables, config)
    except KeyError:
        raise ValueError(f"지원하지 않는 타입: {type_name}")

# $v는 이전에 지정한 변수
# 입력포맷 : [ variable, line ]
# 입력포맷의 variable은 초기init
# line : { variable: [ var.. ], repeat: $v, format: { ... }, type: (str) }
# line.type은 graph나 line..
# var: { name: (str), type: (str), range: [int, int] }
# format: 뭐 이런저런 옵션들... 뭐 separator나 sequence..

def process(testcaseConfig: TestcaseConfig):
    variable_format, lines = testcaseConfig.variable_format, testcaseConfig.lines
    result = []
    variables = create_variables({}, variable_format)
    for line in lines:
        config = line.config
        line_type = line.type

        # output = create_outputs(i.get('output', {}))
        output = line.output
        variable_format = line.variable

        repeat_count = safe_eval(line.repeat, variables)
        variables['_repeat'] = repeat_count
        current_line_data = []
        generator, gen_config = resolve_generator_config(line_type, variables, config)
        for _ in range(repeat_count):
            variables |= create_variables(variables, variable_format)
            current_line_data.extend(generator.generate(variables, output, gen_config))
        for line_data in current_line_data:
            result.append(output.separator.join(map(str, line_data)))
    return '\n'.join(result)

# print(process([
#         {'name': 'N', 'type': 'int', 'range': [[3, 3]]}
#     ], [
#     {
#         'variable': [
#             {'name': 'x', 'type': 'int', 'range': [[1, 5]]}
#         ],
#         'type': 'line',
#         'repeat': '$N',
#         'output': {
#             'sequence': ['$x']
#         }
#     }
# ]))
# print(process([], [
#     {
#         'variable': [
#             { 'name': 'n', 'type': 'int', 'range': [[10, 15]] },
#         ],
#         'output': { 'sequence': ['$n'] }
#     },
#     {
#         'type': 'undirected_graph',
#         'config': {
#             'node_count': '$n',
#             'is_cycle': False
#         },
#         'output': { 'sequence': ['$_s', '$_e'] }
#     }
# ]))
#
# print()
#
# print(process([], [
#     {
#         'variable': [
#             { 'name': 'n', 'type': 'int', 'range': [[2, 3], [8, 10]] },
#             { 'name': 'm', 'type': 'int', 'range': [['$n-1', '$n*($n-1)//2']] }
#         ],
#         'output': { 'sequence': ['$n', '$m'] }
#     },
#     {
#         'type': 'undirected_graph',
#         'config': {
#             'node_count': '$n',
#             'edge_count': '$m',
#             'weight_range': [1, 1000]
#         },
#         'output': { 'sequence': ['$_s', '$_e', '$_w'] }
#     }
# ]))
# print(process([], [
#     {
#         'variable': [
#             { 'name': 'n', 'type': 'int', 'range': [[5, 10]] }
#         ],
#         'type': 'matrix',
#         'output': {
#             'sequence': ['$_element'],
#             'separator': ',',
#         },
#         'config': {
#             'num_type': 'int',
#             'col_size': '$n',
#             'row_size': '$n',
#             'is_distinct': True,
#             'empty_value': 90,
#             'num_range': [[1, 10], [1, 30], [5, 48]]
#         }
#     }
# ]))

# print(process([], [
#     {
#         'variable': [
#             {'name': 'n', 'type': 'int', 'range': [[1, 10]]},
#             {'name': 'q', 'type': 'int', 'range': [[1, 10]]},
#         ],
#         'output': {
#             'sequence': ['$n', '$q']
#         }
#     },
#     {
#         'type': 'query',
#         'variable': [
#             { 'name': 'x', 'type': 'int', 'range': [[1, '$n']] },
#             { 'name': 'l', 'type': 'int', 'range': [[1, '$n']] },
#             { 'name': 'r', 'type': 'int', 'range': [['$l', '$n']] }
#         ],
#         'config': {
#             'outputs': [
#                 {
#                     'sequence': ['1', '$x']
#                 },
#                 {
#                     'sequence': ['2', '$l', '$r']
#                 }
#             ],
#             'distribution': [10, 10],
#             'min_count': [1, 1],
#             'max_count': [1000000, 1000000],
#         },
#         'repeat': '$q'
#     }
# ]))

# print(process([], [
#     {
#         'variable': [
#             { 'name': 'n', 'type': 'enum', 'range': [['a', 'b', 'c']] }
#         ],
#         'type': 'line',
#         'output': {
#             'sequence': ['$n']
#         }
#     }
# ]))


# print(process(TestcaseConfig([], [
#     TestcaseBlockConfig(
#         output=Output(['nn', '$n', '$m']),
#         repeat='100000',
#         type='line',
#         variable=[
#             Variable('n', [[1, 5]]),
#             Variable('m', [[5, 10]]),
#         ],
#         config={}
#     ),
#     TestcaseBlockConfig(
#         output=Output(['$_s', '$_e']),
#         repeat='1',
#         type='undirected_graph',
#         variable=[],
#         config={
#             'node_count': '$n'
#         }
#     )
# ])))