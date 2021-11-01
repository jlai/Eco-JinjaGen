from jinja2 import Environment, FileSystemLoader, select_autoescape, filters
import yaml
import shutil
import os
import os.path
import re

userCodePath = r"E:\Program Files\Steam\steamapps\common\Eco\Eco_Data\Server\Mods\UserCode"
leadingSpaces = re.compile('[ \t]+')
camelCaseWords = re.compile('[A-Z][a-z]+')

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

def camelCaseToWords(value):
    return ' '.join(camelCaseWords.findall(value))

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True
)

env.filters['escape'] = escapeQuotesFilter
env.filters['defaults'] = defaultsFilter
env.filters['matchindent'] = matchindentFilter
env.filters['camelCaseToWords'] = camelCaseToWords

def parseFile(filename):
    with open(filename) as f:
        fileDesc = yaml.safe_load(f)

        defaultTemplateName = fileDesc.get('template')
        defaultRelativeDir = fileDesc.get('directory')

        for itemDesc in fileDesc['items']:
            name = itemDesc['name']

            templateName = itemDesc.get('template') or defaultTemplateName
            if not templateName:
                raise Exception("no template or default template")

            template = env.get_template(templateName)

            output = template.render({"item": itemDesc})

            filename = f"{name}.override.cs" if itemDesc.get('override') else f"{name}.cs"
            relativeDir = itemDesc.get('directory') or defaultRelativeDir

            os.makedirs(f"out/{relativeDir}", exist_ok=True)
            with open(f"out/{relativeDir}/{filename}", 'w') as outputFile:
                outputFile.write(output)

            os.makedirs(f"{userCodePath}/{relativeDir}", exist_ok=True)
            shutil.copyfile(f"out/{relativeDir}/{filename}", f"{userCodePath}/{relativeDir}/{filename}")

with os.scandir('project') as scan:
    for entry in scan:
        parseFile(entry.path)
