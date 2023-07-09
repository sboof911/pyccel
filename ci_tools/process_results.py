""" Script to process the output of numpydoc validator"
"""
import argparse
import json
import os
import sys

from annotation_helpers import print_to_string, get_code_file_and_lines

parser = argparse.ArgumentParser(description='Process the output of numpydoc validator')
parser.add_argument('report', metavar='report', type=str,
                        help='Report generated by numpydoc validator')
parser.add_argument('summary', metavar='summary', type=str,
                        help='Github step summary')
args = parser.parse_args()

error_codes = ['GL01', 'GL02', 'GL03', 'GL05', 'GL06', 'GL07', 'GL08', 'GL09',
               'GL10', 'SS01', 'SS02', 'SS03', 'SS04', 'SS05', 'SS06', 'ES01',
               'PR01', 'PR02', 'PR03', 'PR04', 'PR05', 'PR06', 'PR07', 'PR08',
               'PR09', 'PR10', 'RT01', 'RT02', 'RT03', 'RT04', 'RT05', 'YD01',
               'SA02', 'SA03', 'SA04']

warning_codes = ['EX01', 'SA01']

pyccel_folder = os.path.abspath('compare')

errors = {}
warnings = {}
parsing_errors = []
annotations = []
with open(args.report, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            file_name, code, msg = line.split(':', maxsplit=2)
        except ValueError:
            code = 'PARSING_ERROR'

        if code in error_codes:
            level = 'failure'
            if file_name not in errors:
                errors[file_name] = [msg]
            else:
                errors[file_name].append(msg)
            parsing_errors.append(line)
        elif code in warning_codes:
            level = 'warning'
            if file_name not in warnings:
                warnings[file_name] = [msg]
            else:
                warnings[file_name].append(msg)
        else:
            level = None
            parsing_errors.append(line)
        if level:
            file, start, end = get_code_file_and_lines(file_name, pyccel_folder = pyccel_folder)
            with open(file, 'r', encoding='utf-8') as code_file:
                lines = code_file.readlines()[start-1:end+2]
            lines = [l.strip() for l in lines]
            doc_openings = [i for i,l in enumerate(lines) if l.startswith('"""') or l.endswith('"""')]
            lines = lines[doc_openings[0]:doc_openings[1]+1]
            end = start + doc_openings[1]
            start = start + doc_openings[0]
            sections = [(l,i) for i,l in enumerate(lines[:-1]) if lines[i+1] != '' and all(c in ('-','=') for c in lines[i+1])]
            nsections = len(sections)
            if code.startswith('PR'):
                changed = False
                if msg.startswith('Parameter "'):
                    _, key, _ = msg.split('"', 3)
                    try:
                        start = start + next(i for i,l in enumerate(lines) if l.startswith(key))
                        end = start
                        changed = True
                    except StopIteration:
                        pass
                if not changed:
                    idx = next(i for i, (sec, l) in enumerate(sections) if sec == 'Parameters')
                    if idx < nsections:
                        end = start + sections[idx+1][1] - 1
                    start += sections[idx][1]
            if code.startswith('RT'):
                idx = next(i for i, (sec, l) in enumerate(sections) if sec == 'Returns')
                if idx < nsections:
                    end = start + sections[idx+1][1] - 1
                start += sections[idx][1]
            annotations.append({
                "annotation_level":level,
                "start_line":start,
                "end_line":end,
                "path":file,
                "message":msg
            })

fail = len(errors) > 0 or len(parsing_errors) > 0

summary = []

print_to_string('# Part 2 : Numpydoc Validation:', text=summary)
print_to_string(f'## {"FAILURE" if fail else "SUCCESS"}!', text=summary)
if fail:
    print_to_string('### ERRORS!', text=summary)
for file_name, errs in errors.items():
    print_to_string(f'#### {file_name}', text=summary)
    print_to_string(''.join(f'- {err}' for err in errs), text=summary)
if len(warnings) > 0:
    print_to_string('### WARNINGS!', text=summary)
for file_name, warns in warnings.items():
    print_to_string(f'#### {file_name}', text=summary)
    print_to_string(''.join(f'- {warn}' for warn in warns), text=summary)
if len(parsing_errors) > 0:
    print_to_string('### PARSING ERRORS!', text=summary)
    parsing_errors = ['\n' if 'warn(msg)' in err else err for err in parsing_errors]
    print_to_string(''.join(f'{add_warn}' for add_warn in parsing_errors), text=summary)

summary_text = '\n'.join(summary)

with open('test_json_result.json', mode='r', encoding="utf-8") as json_file:
    messages = json.load(json_file)

messages['summary'] += '\n\n'+summary_text
messages.setdefault('annotations', []).extend(annotations)

with open(args.summary, 'a', encoding='utf-8') as f:
    print(summary_text, file=f)

with open('test_json_result.json', mode='w', encoding="utf-8") as json_file:
    json.dump(messages, json_file)

sys.exit(fail)

