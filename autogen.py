from jinja2 import Environment, FileSystemLoader, select_autoescape, filters
import yaml
import shutil
import os
import os.path
import re

userCodePath = r"E:\Program Files\Steam\steamapps\common\Eco\Eco_Data\Server\Mods\UserCode"
leadingSpaces = re.compile('[ \t]+')

def escapeQuotesFilter(value):
    return value.replace('"', "\'") if value else ""

def defaultsFilter(d, **defaults):
    newDict = dict(defaults)
    newDict.update(d)
    return newDict

def matchindentFilter(value, codeToMatch):
    targetIndentMatch = leadingSpaces.match(codeToMatch)
    valueIndentMatch = leadingSpaces.match(value)

    targetIndent = len(targetIndentMatch.group(0)) if targetIndentMatch else 0
    valueIndent = len(valueIndentMatch.group(0)) if valueIndentMatch else 0

    if targetIndent > valueIndent:
        return filters.do_indent(value, targetIndent - valueIndent, first=True)
    else:
        # TODO unindent
        return value

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)

env.filters['escape'] = escapeQuotesFilter
env.filters['defaults'] = defaultsFilter
env.filters['matchindent'] = matchindentFilter

def parseFile(filename):
    with open(filename) as f:
        fileDesc = yaml.safe_load(f)

        templateName = fileDesc['template']
        destination = fileDesc['destination']

        defaultTemplate = env.get_template(templateName)

        for itemDesc in fileDesc['items']:
            name = itemDesc['name']

            template = env.get_template(itemDesc['template']) if 'template' in itemDesc else defaultTemplate

            output = template.render({"item": itemDesc})

            os.makedirs(f"out/{destination}", exist_ok=True)
            with open(f"out/{destination}/{name}.cs", 'w') as outputFile:
                outputFile.write(output)

            shutil.copyfile(f"out/{destination}/{name}.cs", f"{userCodePath}/{destination}/{name}.cs")

with os.scandir('project') as scan:
    for entry in scan:
        parseFile(entry.path)