from bs4 import BeautifulSoup
import requests
import urllib.parse
import json

class OsirisAPI:
    CatalogusLinkBase = "https://osiris.tue.nl/osiris_student_tueprd/OnderwijsCatalogusSelect.do?selectie=cursus&collegejaar=2017"
    CatalogusCourse = CatalogusLinkBase + "&cursus={code}"
    CatalogusListCourses = CatalogusLinkBase + "&faculteit={faculty}&cursustype={stage}"
    CatalogusListCoursesLevel = CatalogusListCourses + "&categorie={level}"
    CatalogusNextLink = "https://osiris.tue.nl/osiris_student_tueprd/OnderwijsCatalogusKiesCursus.do?event=goto&source=OnderwijsZoekCursus&value={index}&partialTargets=OnderwijsZoekCursus"

    Types = (
        ('BC', "Bachelor College"),
        ('GS', "Graduate School")
    )

    Types_dict = {
        'Graduate School' : 'GS',
        'Bachelor College' : 'BC',
    }

    Languages_dict = {
        'Engels' : 'EN',
        'Nederlands' : 'NL',
    }

    Faculties = (
        ("BMT", "Biomedical Engineering"),
        ("B", "the Built Environment"),
        ("EE", "Electrical Engineering"),
        ("ID", "Industrial Design"),
        ("IE&IS", "Industrial Engineering & Innovation Sciences"),
        ("ST", "Chemical Engineering and Chemistry"),
        ("TN", "Applied Physics"),
        ("W", "Mechanical Engineering"),
        ("W&I", "Mathematics and Computer Science")
    )

    def __init__(self):
        self.session = requests.session()
        try:
            with open('osiris/proxies.json', 'r') as stream:
                self.proxies = json.loads(stream.readlines()[0].strip('\n'))
        except:
            self.proxies = {}
        self.session.headers['User-Agent'] = 'Master Marketplace ELE Tue, master.ele.tue.nl'
        self.session.headers['From'] = 'mastermarketplace@tue.nl'

    def _extractCourseFromSoup(self, soup, code):
        #some elements are not onliners so are prepared here, onlines are put directly in the dictionary
        #same goes for elements that are prone to faillure due to the TU/e not being consistent with data
        try:
            responsiblestaffname = soup.find('tr', id='cursContactpersoon').find('a').text
        except:
            responsiblestaffname = soup.find('tr', id='cursContactpersoon').text
        try:
            quartiles = [int(soup.find('tr', id='cursAanvangsblok').find('span', class_='psbTekst').text[-1])]
            if soup.find('tr', id='cursAanvangsblok').find('a'):
                quartiles.append(int(soup.find('tr', id='cursAanvangsblok').find('a').text[-1]))
        except:
            quartiles = ['X']

        try:
            timeslots = [a[-1] for a in soup.find('tr', id='cursTimeslot').find('td', class_='psbTekst').text.split(':')[:-1]]
        except:
            timeslots = ['X']


        course = {
            'code' : code,
            'name' : soup.find('span', class_='psbGroteTekst').text,
            'type' : self.Types_dict.get(soup.find('tr', id='cursCursustype').find('span', class_='psbTekst').text, 'unknown'),
            'owner' : {
                'faculty' : soup.find('span', id='cursFaculteit').text.strip().strip(';'),
                'group' : soup.find('span', id='cursCoordinerendOnderdeel').text.replace(';', '').replace('Group', '').strip()
            },
            'responsiblestaff' : {
                'name' : responsiblestaffname,
                'email' : soup.find('tr', id='medeEMailAdres').find('a').text
            },
            'ECTS' : float(soup.find('tr', id='cursStudiepunten').find('span', class_='psbTekst').text.replace(',','.')),
            'language' : soup.find('tr', id='cursVoertaal').find('span', class_='psbTekst').text,
            'detaillink' : self.CatalogusCourse.format(code=code),
        }
        if course['type'] == 'BC':
            try:
                course['level'] = int(soup.find('tr', id='cursCategorie').find('span', class_='psbTekst').text[0])
            except:
                course['level'] = 'X'
        courses = []
        for timeslot in timeslots:
            for quartile in quartiles:
                c = course.copy()
                c['timeslot'] = timeslot
                c['quartile'] = quartile
                courses.append(c)

        return courses

    def getCourseInfo(self, code):
        code = urllib.parse.quote_plus(code)
        r = self.session.get(self.CatalogusCourse.format(code=code), proxies=self.proxies)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'lxml')
        if 'fout' in str(soup.title).lower():
            return None

        if len(soup.find_all('table', class_='OraTableContent')) == 1:
            results = []
            for tr in soup.find('table', class_='OraTableContent').find_all('tr'):
                try:
                    block = tr.find_all('td')[7]
                    slot = tr.find_all('td')[8]
                    r2 = self.session.get(self.CatalogusCourse.format(code=code) +
                                          '&timeslot=' + slot.find('span').text.split(',')[0] +
                                          '&aanvangsblok=' + block.find('span').text,
                                          proxies=self.proxies)
                except:
                    continue
                if r2.status_code != 200:
                    return None
                soup2 = BeautifulSoup(r2.text, 'lxml')
                if 'fout' in str(soup2.title).lower():
                    return None
                results += self._extractCourseFromSoup(soup2, code)
            return results
        else:

            return self._extractCourseFromSoup(soup, code)

    def getCourses(self, faculty="EE", stage="GS"):
        codes = set()
        faculty = urllib.parse.quote_plus(faculty)
        stage = urllib.parse.quote_plus(stage)
        r = self.session.get(self.CatalogusListCourses.format(faculty=faculty, stage=stage), proxies=self.proxies)
        if r.status_code != 200:
            return None
        soupinitial = BeautifulSoup(r.text, 'lxml')
        if 'fout' in str(soupinitial.title).lower():
            return None

        if len(soupinitial.find_all('option')) > 0:
            for page in soupinitial.find_all('option'):
                r = self.session.get(self.CatalogusNextLink.format(index=page['value']), proxies=self.proxies)
                if r.status_code != 200:
                    return None
                souppage = BeautifulSoup(r.text, 'lxml')
                cells = souppage.find_all('a', class_='psbLink')
                for cell in cells:
                    codes.add(cell.text)
        else:
            cells = soupinitial.find_all('a', class_='psbLink')
            for cell in cells:
                codes.add(cell.text)
        return list(codes)

    def getCoursesLevel(self, faculty="EE", level=3):
        codes = set()
        faculty = urllib.parse.quote_plus(faculty)
        stage = "BC"
        r = self.session.get(self.CatalogusListCoursesLevel.format(faculty=faculty, stage=stage, level=level), proxies=self.proxies)
        if r.status_code != 200:
            return None
        soupinitial = BeautifulSoup(r.text, 'lxml')
        if 'fout' in str(soupinitial.title).lower():
            return None

        if len(soupinitial.find_all('option')) > 0:
            for page in soupinitial.find_all('option'):
                r = self.session.get(self.CatalogusNextLink.format(index=page['value']), proxies=self.proxies)
                if r.status_code != 200:
                    return None
                souppage = BeautifulSoup(r.text, 'lxml')
                cells = souppage.find_all('a', class_='psbLink')
                for cell in cells:
                    codes.add(cell.text)
        else:
            cells = soupinitial.find_all('a', class_='psbLink')
            for cell in cells:
                codes.add(cell.text)

        return list(codes)