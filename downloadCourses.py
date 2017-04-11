#Author: Dhawal Majithia dmmajithia@ucdavis.edu
#What this script does - Downloads all classes being offered in a specific term at UC Davis, into a text file '(termCode).txt'. An example text file with all Spring 2017 classes is included - 201703.txt
# Can I change the format of the text file? YES

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import re
import subjects
import pyrebase
#import sub2

SUBJECT_CODES_BY_NAME = subjects.SUBJECT_CODES_BY_NAME
SUBJECT_NAMES_BY_CODE = subjects.SUBJECT_NAMES_BY_CODE

courses = {}
#terms = {'06' : 'Summer Special', '07' : 'Summer Session 2', '09' : 'Fall Semester', '10' : 'Fall Quarter'}'08' : 'Summer Session 1', '01' : Winter Quarter. more term codes can be found on registrars website
terms = {'03' : 'Spring Quarter'}
count = 8551 # set total number of crns

driver = webdriver.PhantomJS(executable_path='path_to_PhantomJS_executable')
done = 0
print ("code1") #for debugging
for term in terms:
    courses = {}
    for code in sorted(SUBJECT_NAMES_BY_CODE):
        
        print (code)
        driver.get('https://registrar.ucdavis.edu/courses/search/index.cfm')
        print ("code2")
        el = driver.find_element_by_name('termCode')
        for option in el.find_elements_by_tag_name('option'):
            #print(option.value)
            if option.text == 'Spring Quarter 2017': #change text based on term
                option.click() # select() in earlier versions of webdriver
            break
    
        #Select(driver.find_element_by_id('termCode')).select_by_value(term)
        driver.find_element_by_xpath('//*[@id="termCode"]/select/option[6]').click() #chaange option based on term
        
        print (term)
        
        el = driver.find_element_by_name('course_number')
        el.send_keys(code)
        
        
        driver.find_element_by_name('search').click()
        time.sleep(10)
        
        crns = re.findall(r"\bcrn=[\w]*", driver.page_source)
        crns = list(set(crns))
        
        if len(crns) > 1:
            temp = []
            for crn in crns:
                crn = crn.replace('crn=', '')
                if crn != '' and crn.isdigit():
                    temp.append(crn)
        
            crns = temp
            print (crns)
            #print(driver.page_source)
            
            for crn in crns:
                driver.get('https://registrar.ucdavis.edu/courses/search/course.cfm?crn=' + crn + '&termcode=' + '2017' + term)
                course_name = driver.find_element_by_xpath('/html/body/div/table[1]/tbody/tr[1]/td/h1').text
                #print(course_name)
                names = [x.lstrip('0') for x in course_name.split(' ', 4)]
                course_number = names[1]
                section = names[2]
                if section[len(section)-1].isnumeric():
                    print (course_name)
                    course_name = names[4]
                    print (course_name)
                else:
                    print ('que paso?')
                    print (course_name)
                    course_name = names[3]
                    section = '-'
                
                instructor = driver.find_element_by_xpath('/html/body/div/table[1]/tbody/tr[5]/td').text
                instructor = instructor.replace('Instructor: ', '')
                times = []
                i = 2
                while i <= 4:
                    #print (len(driver.find_elements_by_xpath('/html/body/div/table[2]/tbody/tr['+str(i)+']/td[1]')))
                    if len(driver.find_elements_by_xpath('/html/body/div/table[2]/tbody/tr['+str(i)+']/td[1]')) > 0 :
                        days = driver.find_element_by_xpath('/html/body/div/table[2]/tbody/tr['+str(i)+']/td[1]').text
                        hours = driver.find_element_by_xpath('/html/body/div/table[2]/tbody/tr['+str(i)+']/td[2]').text
                        location = driver.find_element_by_xpath('/html/body/div/table[2]/tbody/tr['+str(i)+']/td[3]').text
                        timeV = {'days' : days, 'hours' : hours, 'location' : location}
                        if i == 2 :
                            times.append({'Lecture' : timeV})
                        elif i >= 3:
                            times.append({'D-L' : timeV})
                        print (i)
                    i += 1
                done += 1
                print (done*100/count)
                if code in courses:
                    subject = courses[code]
                    if course_number in subject:
                        if instructor in subject[course_number]:
                            #just add section
                            subject[course_number][instructor]['sections'].append({'sNumber' : section, 'times' : times})
                        else:
                            #add instructor and then section
                            subject[course_number][instructor] = {'sections' : [{'sNumber' : section, 'times' : times}]}
                    else:
                        subject[course_number] = { instructor : {'sections' : [{'sNumber' : section, 'times' : times}]}, 'course_name' : course_name}

                else:
                    courses[code] = {course_number : { instructor : {'sections' : [{'sNumber' : section, 'times' : times}]}, 'course_name' : course_name}}

    print ('\n\n\n\n')

    #print (courses)
    #You can change the format of the text file here.
    f = open('2017' + term + '.txt', 'w')
    for code in courses:
        for course_number in courses[code]:
            stR = 'Class: ' + code + ',' + course_number + ','+ courses[code][course_number]['course_name'] + '\n'
            
            for instructor in courses[code][course_number]:
                if instructor != 'course_name':
                    str1 = stR + 'Instructor: ' + instructor
                    for section in courses[code][course_number][instructor]['sections']:
                        str2 = str1 + '\nSection: ' + section['sNumber']
                        str3 = str2
                        i = 1
                        timeUpdate = {}
                        sectionID = course_number + instructor + section['sNumber']
                        
                        for timeLoc in section['times']:
                            for type in timeLoc:
                                t1 = timeLoc[type]
                                str3 += '\n' + type + ': ' + t1['days'] + ' ' + t1['hours'] + ' Location: ' + t1['location']
                                i += 1
                        f.write(str3 + '\n')
                        print (str3 + '\n')
