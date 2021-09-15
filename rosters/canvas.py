"""
Roster Fetcher that uses the Canvas API
"""

import logging
import os
import pathlib
import yaml 
import re
from canvasapi import Canvas


canvas_cfg_file = pathlib.Path(pathlib.Path(os.environ['HOME']) / '.canvasapi')
canvas_cfg = None
canvas = None
if canvas_cfg_file.exists():
    logging.info(f"Loading canvas config file: {canvas_cfg_file}")
    with open(canvas_cfg_file) as fh:
        canvas_cfg = yaml.load(fh, Loader=yaml.Loader)
    canvas = Canvas(canvas_cfg['API_URL'], canvas_cfg['API_KEY'])
else:
    logging.warn('No Canvas config file.')


def canvas_enabled():
    return canvas != None

def fetch():
    rosters = {}
    for course in canvas.get_courses(enrollment_state='active', enrollment_type='teacher', include=['term']):
        m = re.match(r'(Spring|Fall|Summer) 20(\d+)', course.term['name'])
        if m is not None:
            roster = []
            for enrollment in course.get_enrollments(type=['StudentEnrollment', 'ObserverEnrollment']):
                roster.append({
                    "fullname": enrollment.user['name'],
                    "id": enrollment.user['sis_user_id'],
                    "email": f"{enrollment.user['sis_user_id']}@student.cabrillo.edu",
                    "status": enrollment.type,
                })
            course_code = '-'.join(course.course_code.split('-')[0:3])
            course_key = f"{course_code}:{course.term['name']}"            
            rosters[course_key] = {
                'term': course.term['name'],
                'roster': roster,
            }
            print(rosters)
    return rosters
