"""
Pre-process a syllabus (class schedule) file. 

"""
import arrow   # Dates and times
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)

base = arrow.now()   # Default, replaced if file has 'begin: ...'
current_date = arrow.now().format("MM/DD/YYYY")

def current_week(date):
    # Parse string date. Docs for 'get' method:
    #   http://arrow.readthedocs.io/en/latest/
    parsed_date = arrow.get(date, "MM/DD/YYYY")
    today = arrow.now().format("MM/DD/YYYY")
    parsed_today = arrow.get(today, "MM/DD/YYYY")

    ### Logging ###
    log.debug("Check: " + str(parsed_today))
    log.debug("From: " + str(parsed_date))

    # Shift days 6 to ensure we don't count beginning of next week
    week_from_date = parsed_date.shift(days=6)

    ### Logging ###
    log.debug("Up until: " + str(week_from_date) + "\n")

    date_range = []

    for day in arrow.Arrow.range('day', parsed_date, week_from_date):
        log.debug(str(day))
        date_range.append(day)
    
    if(parsed_today in date_range):
        return True
    
    return False


def process(raw):
    """
    Line by line processing of syllabus file.  Each line that needs
    processing is preceded by 'head: ' for some string 'head'.  Lines
    may be continued if they don't contain ':'.  If # is the first
    non-blank character on a line, it is a comment ad skipped. 
    """
    field = None
    entry = {}
    cooked = []
    # Define count of weeks past base week (defined in syllabus passed through)
    week_count = 0
    for line in raw:
        log.debug("Line: {}".format(line))
        line = line.strip()
        if len(line) == 0 or line[0] == "#":
            log.debug("Skipping")
            continue
        parts = line.split(':')
        if len(parts) == 1 and field:
            entry[field] = entry[field] + line + " "
            continue
        if len(parts) == 2:
            field = parts[0]
            content = parts[1]
        else:
            raise ValueError("Trouble with line: '{}'\n".format(line) +
                             "Split into |{}|".format("|".join(parts)))

        if field == "begin":
            try:
                base = arrow.get(content, "MM/DD/YYYY")
                # print("Base date {}".format(base.isoformat()))
            except:
                raise ValueError("Unable to parse date {}".format(content))

        elif field == "week":
            if entry:
                cooked.append(entry)
                entry = {}
            entry['topic'] = ""
            entry['project'] = ""
            # Shift the days to appropriate date for start date of week. Then,
            #  format appropriately.
            entry['date'] = base.shift(days = 7*week_count).format("MM/DD/YYYY")
            
            # Adds new entry for column that contains week number
            entry['week'] = content

            entry['currentweek'] = current_week(entry['date'])
            
            # Increment week counter so we can correctly display dates
            week_count += 1

        elif field == 'topic' or field == 'project':
            entry[field] = content

        else:
            raise ValueError("Syntax error in line: {}".format(line))

    if entry:
        cooked.append(entry)

    return cooked


def main():
    f = open("data/schedule.txt")
    parsed = process(f)
    print(parsed)


if __name__ == "__main__":
    main()
