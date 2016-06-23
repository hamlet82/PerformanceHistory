# import modules
import codecs
import re
import string
import xml.etree.ElementTree as ET
import os
import os.path

# create xml element
os.chdir('i:/Archives Digitization Project/PerformanceHistoryRepo/PerformanceHistory/Programs')
files = [g for g in os.listdir('.') if os.path.isfile(g)]
for g in files:
    tree = ET.parse(g)
    root = tree.getroot()

    #create list of lines for new file (kludge to solve ampersand escaping
    lines = []

    # separate composer and work into two elements
    def separateComposerWork(composerAndWork):
        composer = re.sub(r'(.*?) /.*',r'\1',composerAndWork)
        work = re.sub(r'.*?/ (.*)',r'\1',composerAndWork)
        return composer, work

    # remove extra spaces at front of soloist info
    def fixSpaces(text):
        if re.match(r'  ',text):
            fixed_text = re.sub(r'  (\w.*)',r'\1',text)
        elif re.match(r' ',text):
            fixed_text = re.sub(r' (\w.*)',r'\1',text)
        else:
            fixed_text = text
        return fixed_text

    # separate soloist lists into separate individuals (and instruments and roles)
    def sortSoloistInfo(soloists,soloist_instruments,soloist_roles):
        if re.search(r';',soloists):
            try:
                soloists_list = str.split(soloists,";")
                soloist_instruments_list = str.split(soloist_instruments,";")
                soloist_roles_list = str.split(soloist_roles,";")
                for x in range(0,len(soloists_list)):
                    lines.append("<soloist>")
                    lines.append("<soloistName>%s</soloistName>"%fixSpaces(soloists_list[x]))
                    lines.append("<soloistInstrument>%s</soloistInstrument>"%fixSpaces(soloist_instruments_list[x]))
                    lines.append("<soloistRoles>%s</soloistRoles>"%fixSpaces(soloist_roles_list[x]))
                    lines.append("</soloist>")
            except:
                lines.append("<soloist>")
                lines.append("<soloistName>%s</soloistName>"%soloists)
                lines.append("<soloistInstrument>%s</soloistInstrument>"%soloist_instruments)
                lines.append("<soloistRoles>%s</soloistRoles>"%soloist_roles)
                lines.append("</soloist>")
        else:
            lines.append("<soloist>")
            lines.append("<soloistName>%s</soloistName>"%soloists)
            lines.append("<soloistInstrument>%s</soloistInstrument>"%soloist_instruments)
            lines.append("<soloistRoles>%s</soloistRoles>"%soloist_roles)
            lines.append("</soloist>")

    # reprint the unchanged entities
    def standardItems(p):
        lines.append("<id>%s</id>"%p.find('id').text)
        lines.append("<programID>%s</programID>"%p.find('programID').text)
        lines.append("<orchestra>%s</orchestra>"%p.find('orchestra').text)
        lines.append("<season>%s</season>"%p.find('season').text)

    # reprint unchanged concert info entities
    def concertInfo(c):
        lines.append("<eventType>%s</eventType>"%c.find('eventType').text)
        lines.append("<Location>%s</Location>"%c.find('Location').text)
        lines.append("<Venue>%s</Venue>"%c.find('Venue').text)
        lines.append("<Date>%s</Date>"%c.find('Date').text)
        lines.append("<Time>%s</Time>"%c.find('Time').text)

    # reorder worksInfo children into works, each with conductor, composer, title, and soloists (if applicable)
    def sortWorksInfo(works):
        conductors = works.findall('worksConductorName')
        composerAndWork = works.findall('worksComposerTitle')
        work_ids = works.findall('workID')
        movements = works.findall('worksMovement')
        #movement_ids = works.findall('movementID')
        soloists = works.findall('worksSoloistName')
        soloist_instruments = works.findall('worksSoloistInstrument')
        soloist_roles = works.findall('worksSoloistRole')
        for x in range(0,len(conductors)):
            composer_work_separated = separateComposerWork(composerAndWork[x].text)
            lines.append("<work ID=\"%s\">"%work_ids[x].text)
            if re.match(r'Intermission',composer_work_separated[0]):
                lines.append("<interval>%s</interval>"%composer_work_separated[0][:-1])
            else:
                if composer_work_separated[0]:
                    lines.append("<composerName>%s</composerName>"%composer_work_separated[0])
                if composer_work_separated[1]:
                    lines.append("<workTitle>%s</workTitle>"%composer_work_separated[1])
                if len(movements) > 0:
                    if movements[x].text:
                        lines.append("<movement>%s</movement>"%movements[x].text)
                if conductors[x].text:
                    lines.append("<conductorName>%s</conductorName>"%conductors[x].text)
                try:
                    if soloists[x].text:
                        lines.append("<soloists>")
                        sortSoloistInfo(soloists[x].text, soloist_instruments[x].text,soloist_roles[x].text)
                        lines.append("</soloists>")
                except:
                    pass
            lines.append("</work>")

    # parse xml file and write new output, per functions above
    programs = root.findall('doc')

    lines.append('<programs>')

    for p in programs:
        lines.append("<program>")
        standardItems(p)
        for c in p.findall('concertInfo'):
            lines.append("<concertInfo>")
            concertInfo(c)
            lines.append("</concertInfo>")
        lines.append("<worksInfo>")
        sortWorksInfo(p.find('worksInfo'))
        lines.append("</worksInfo>")
        lines.append("</program>")

    lines.append("</programs>")
    all_lines = []
    for l in lines:
        l = re.sub(r'&', r'&amp;', l)
        all_lines.append(l)
    text = ''.join(all_lines)
    text = re.sub(r'><','>\n<',text)
    text = re.sub(r'(<program>|</program>)',r'  \1',text)
    text = re.sub(r'(<id>|<programID>|<orchestra>|<season>|<concertInfo>|</concertInfo>|<worksInfo>|</worksInfo>)',r'    \1',text)
    text = re.sub(r'(<eventType>|<Location>|<Venue>|<Date>|<Time>|<work ID|</work>|<interval>)',r'      \1',text)
    text = re.sub(r'(<composerName>|<workTitle>|<movement>|<conductorName>|<soloists>|</soloists>)',r'        \1',text)
    text = re.sub(r'(<soloist>|</soloist>)',r'          \1',text)
    text = re.sub(r'(<soloistName>|<soloistInstrument>|<soloistRoles>)',r'            \1',text)

    # create new xml file
    f = codecs.open(g, 'w','utf-8')
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write(text)
    f.close()
