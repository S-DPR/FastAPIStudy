from grpc_internal.create_testcase import client as tc_client
from grpc_internal.code_runner import client as code_client
from grpc_internal.file_manager import client as file_client
import os
import uuid

def run(format_, code1, code2, time_limit, repeat_count):
    code_uuid = str(uuid.uuid4())
    code1_name = os.path.basename(file_client.file_save(code1, code_uuid + "_1")['filepath'])
    code2_name = os.path.basename(file_client.file_save(code2, code_uuid + "_2")['filepath'])
    result = []
    for kth in range(repeat_count):
        input_filename = f"{code_uuid}_{kth+1}"
        output_filename = f"{code_uuid}_{kth+1}"

        first_output_filename = output_filename + "_1.out"
        second_output_filename = output_filename + "_2.out"

        tc = tc_client.testcase_generate(format_)
        tc_path = file_client.file_save(tc['output'], input_filename, 'in')['filepath']
        code1_exitcode = code_client.execute_code(code1_name, "python", os.path.join("/script", input_filename + ".in"), os.path.join("/script", first_output_filename), time_limit)['exitcode']
        code2_exitcode = code_client.execute_code(code2_name, "python", os.path.join("/script", input_filename + ".in"), os.path.join("/script", second_output_filename), time_limit)['exitcode']
        if code1_exitcode != code2_exitcode:
            ret = "ERROR FAILED"
        elif code1_exitcode != 0:
            ret = "ERROR BUT EQUAL"
        else:
            ret = file_client.file_diff("/app/scripts", first_output_filename, second_output_filename)['result']
        result.append({ input_filename: ret })
    return result
