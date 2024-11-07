import sys
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from urllib.parse import quote_plus
import click
import requests


MAX_WORKERS = 15

@dataclass
class RequestData:
    method: str
    url: str
    param: str
    proxies: dict

@dataclass
class FuzzTemplate:
    template: str
    canary: str


class InvalidTemplate(Exception):
    ...

def parse_template(template_file: str) -> FuzzTemplate:
    data = ""
    with open(template_file, "r") as f:
        data = f.read()
    template_section = "[template]"
    canary_section = "[canary]"
    template_index = data.find(template_section)
    canary_index = data.find(canary_section)
    if template_index == -1:
        raise InvalidTemplate("Missing template section")
    if canary_index == -1:
        raise InvalidTemplate("Missing canary section")
    if template_index < canary_index:
        template = data[template_index+len(template_section):canary_index]
        canary = data[canary_index+len(canary_section):]
    else:
        template = data[template_index:]
        canary = data[canary_index+len(canary_section):template_index]
    template = template.strip()
    canary = canary.strip()
    if not template:
        raise InvalidTemplate("Missing template contents")
    if not canary:
        raise InvalidTemplate("Missing canary contents")
    return FuzzTemplate(template, canary)


def generate_payloads(template: str) -> set[str]:
    CONTROL_CHARS = {
        "\u0000": "Null character (NUL)",
        "\u0001": "Start of Header (SOH)",
        "\u0002": "Start of Text (STX)",
        "\u0003": "End of Text (ETX)",
        "\u0004": "End of Transmission (EOT)",
        "\u0005": "Enquiry (ENQ)",
        "\u0006": "Acknowledge (ACK)",
        "\u0007": "Bell (BEL)",
        "\u0008": "Backspace (BS)",
        "\u0009": "Horizontal Tab (HT)",
        "\u000a": "Line Feed (LF)",
        "\u000b": "Vertical Tab (VT)",
        "\u000c": "Form Feed (FF)",
        "\u000d": "Carriage Return (CR)",
        "\u000e": "Shift Out (SO)",
        "\u000f": "Shift In (SI)",
        "\u0010": "Data Link Escape (DLE)",
        "\u0011": "Device Control 1 (DC1)",
        "\u0012": "Device Control 2 (DC2)",
        "\u0013": "Device Control 3 (DC3)",
        "\u0014": "Device Control 4 (DC4)",
        "\u0015": "Negative Acknowledge (NAK)",
        "\u0016": "Synchronous Idle (SYN)",
        "\u0017": "End of Transmission Block (ETB)",
        "\u0018": "Cancel (CAN)",
        "\u0019": "End of Medium (EM)",
        "\u001a": "Substitute (SUB)",
        "\u001b": "Escape (ESC)",
        "\u001c": "File Separator (FS)",
        "\u001d": "Group Separator (GS)",
        "\u001e": "Record Separator (RS)",
        "\u001f": "Unit Separator (US)",
        "\u007f": "Delete (DEL)",
        "": "Empty",
        " ": "Space",
    }
    generator_code = ""
    fuzz_count = 0
    payloads = set()
    while "_FUZZ_" in template:
        fuzz_count += 1
        template = template.replace("_FUZZ_", f"{{char_{fuzz_count}}}", 1)
    indent = "  "
    generator_code +="with click.progressbar(range(0, len(CONTROL_CHARS)**fuzz_count), label='Generating payloads') as bar:\n"
    for i in range(1, fuzz_count + 1):
        generator_code += indent * i + f"for char_{i} in CONTROL_CHARS:\n"
    generator_code += indent * (fuzz_count+1) + "payloads.add(template.format("
    for i in range(1, fuzz_count + 1):
        generator_code += f"char_{i}=char_{i},"
    generator_code += "))\n"
    generator_code += indent * (fuzz_count+1)+"bar.update(1)"
    exec(generator_code)
    click.secho(f"[SUCCESS] Generated {len(payloads)} payloads", fg="green")
    return payloads


def does_payload_execute(session: requests.Session, request_data: RequestData, payload: str, canary):
    params, data ={}, {}
    if request_data.method == "GET":
        params = {request_data.param: payload}
    else:
        data = {request_data.param: payload}
    try:
        response = session.request(request_data.method, request_data.url, params=params, data=data, proxies=request_data.proxies)
        if canary in response.text:
            print(
                f"Payload: {quote_plus(payload)}, response: {quote_plus(response.text)}"
            )
            return True
        elif response.status_code == 500:
            print(
                f"Caught exception for payload: {quote_plus(payload)}, exception: {response.text}"
            )
            return True
    except requests.RequestException:
        pass
    return False


def fuzz(requests_data: RequestData, payloads: set[str], canary: str):
    session = requests.Session()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for _ in range(0, len(payloads)):
            futures.append(
                executor.submit(does_payload_execute, session, requests_data, payloads.pop(), canary)
            )
        vulnerable = False
        with click.progressbar(futures, label="Fuzzing") as bar:
            for future in as_completed(futures):
                bar.update(1)
                if not future.result():
                   continue
                vulnerable = True
    if vulnerable:
        click.secho("[SUCCESS] Found one or more payloads that executed", fg="green")
    else:
        click.secho("[FAIL] No payloads executed", fg="red")

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-u", "--url", required=True, help="URL of the backend sanitizer"
    )
    arg_parser.add_argument(
        "-p",
        "--param",
        required=False,
        help=(
            "Parameter where payload should be injected. If the method used is POST, the "
            "parameter will be injected in the body"
        ),
        default="text",
    )
    arg_parser.add_argument(
        "-m",
        "--method",
        required=False,
        help="HTTP method to use (GET/POST).",
        default="GET",
    )
    arg_parser.add_argument(
        "-t",
        "--template",
        required=True,
        help=(
            "Fuzzing template used to generate the payloads."
            "The '_FUZZ_' inside the template will be replaced with a control character"
        ),
    )
    arg_parser.add_argument("--http-proxy", required=False, help="HTTP proxy to use", default="")
    arg_parser.add_argument("--https-proxy", required=False, help="HTTPS proxy to use", default="")
    args = arg_parser.parse_args(sys.argv[1:])
    proxies = {}
    if args.http_proxy:
        proxies["http"] = args.http_proxy
    if args.https_proxy:
        proxies["https"] = args.https_proxy
    request_data = RequestData(args.method, args.url, args.param, proxies)
    fuzz_template = parse_template(args.template)
    payloads = generate_payloads(fuzz_template.template)
    fuzz(request_data, payloads, fuzz_template.canary)

if __name__ == "__main__":
    main()
