import bs4 as bs
import requests
import MySQLdb
import datetime
keywords_search = []
interest_search = []


# Retrieve Keywords from Database
def retrieve_keywords():
    select_keywords_sql =  "SELECT job_category FROM `app_jobcategory`"
    select_interest_sql = "SELECT personal_interest_sector FROM `app_interestsector`"

    conn = MySQLdb.connect(host='localhost', user='root', password='', db='ecg_db')
    db = conn.cursor()

    conn.set_character_set('utf8')
    db.execute('SET NAMES utf8;')
    db.execute('SET CHARACTER SET utf8;')
    db.execute('SET character_set_connection=utf8;')

    try:
        # Retrieve Job Keywords
        db.execute(select_keywords_sql)
        rows = db.fetchall()
        for each_row in rows:
            keywords_search.append(each_row[0])

        # Retrieve Job Interest
        db.execute(select_interest_sql)
        rows = db.fetchall()
        for each_row in rows:
            interest_search.append(each_row[0])
    except:
        print("Error!")
    finally:
        conn.close()


# Database Properties
def connect_db(data):
    date = [str(datetime.date.today())]
    # DELETE FROM `job` WHERE `job_date` < '2017-07-13'
    delete_sql = "DELETE FROM `app_job` WHERE `job_date` < %s"
    insert_sql = "INSERT INTO `app_job` (job_id, job_url, job_position, job_company, job_category, job_description, job_date, job_keyword, job_interest) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    conn = MySQLdb.connect(host='localhost', user='root', password='', db='ecg_db')
    db = conn.cursor()

    conn.set_character_set('utf8')
    db.execute('SET NAMES utf8;')
    db.execute('SET CHARACTER SET utf8;')
    db.execute('SET character_set_connection=utf8;')

    # Clear Database
    print("Clearing database...")
    db.execute(delete_sql, date)
    conn.commit

    # Insert data
    print("Inserting data...")
    db.executemany(insert_sql, data)
    conn.commit()
    conn.close()
    # try:
    #     # Clear Database
    #     print("Clearing database...")
    #     db.execute(delete_sql, date)
    #     conn.commit
    #
    #     # Insert data
    #     print("Inserting data...")
    #     db.executemany(insert_sql, data)
    #     conn.commit()
    # except:
    #     print("Error!")
    # finally:
    #     conn.close()
    # select_sql = "SELECT * FROM `job`"
    # db.execute(select_sql)
    # rows = db.fetchall()
    # print(rows)
    # for each_row in rows:
    #     print(each_row)


# cg_scrape_keyword: Job Keyword Scraping from Careers@GOV
def cg_scrape_keyword():
    interest = ""
    data = []
    for keyword in keywords_search:
        keyword = keyword.strip()
        keyword_space_replace = keyword.replace(' ', '%20')
        keyword_no_space = keyword.replace(' ', '')
        keyword_no_space = keyword_no_space.replace('/', '')

        url = "http://careers.pageuppeople.com/688/cwlive/en/search/?=&search-keyword=" + keyword_space_replace
        html_contents = requests.get(url).text
        soup = bs.BeautifulSoup(html_contents, 'html5lib')

        table = soup.find('table')
        table_body = table.find('tbody', {'id': 'search-results-content'})

        if 'No jobs matched your search' not in table_body.text:
            counter = 0
            for row in table_body.find_all('tr'):
                if counter != 5:
                    counter += 1
                    counter_string = str(counter).rjust(3, '0')
                    job_id = "CG" + "-" + keyword_no_space.upper() + counter_string

                    href_link = row.find('a').get('href')
                    job_link = "http://careers.pageuppeople.com" + href_link

                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]

                    # Retrieve Job Descriptions
                    job_html_contents = requests.get(job_link).text
                    job_soup = bs.BeautifulSoup(job_html_contents, 'html5lib')
                    job_desc = job_soup.find('div', {'id': 'job-details'})

                    job_date = str(datetime.date.today())

                    # print("--------------------------------------")
                    # print("Job Keyword: " + keyword)
                    # print("Personal Interest: " + interest)
                    # print("Job ID:" + job_id)
                    # print("Job Link:" + job_link)
                    # print("Position:" + cols[0])
                    # print("Company:" + cols[1])
                    # print("Job Category:" + cols[2])
                    # print("Job Descriptions: " + job_desc.text)
                    # print("Date:" + job_date)
                    # print("--------------------------------------")

                    values = [job_id, job_link, cols[0], cols[1], cols[2], job_desc.text, job_date, keyword, interest]
                    data.append(values)
    connect_db(data)


# cg_scrape_interest: Job Interest Scraping from Careers@GOV
def cg_scrape_interest():
    keyword = ""
    data = []
    for interest in interest_search:
        interest = interest.strip()
        interest_space_replace = interest.replace(' ', '%20')
        interest_no_space = interest.replace(' ', '')
        interest_no_space = interest_no_space.replace('/', '')

        url = "http://careers.pageuppeople.com/688/cwlive/en/search/?=&search-keyword=" + interest_space_replace
        html_contents = requests.get(url).text
        soup = bs.BeautifulSoup(html_contents, 'html5lib')

        table = soup.find('table')
        table_body = table.find('tbody', {'id': 'search-results-content'})

        if 'No jobs matched your search' not in table_body.text:
            counter = 0
            for row in table_body.find_all('tr'):
                if counter != 5:
                    counter += 1
                    counter_string = str(counter).rjust(3, '0')
                    job_id = "CG" + "-" + interest_no_space.upper() + counter_string

                    href_link = row.find('a').get('href')
                    job_link = "http://careers.pageuppeople.com" + href_link

                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]

                    # Retrieve Job Descriptions
                    job_html_contents = requests.get(job_link).text
                    job_soup = bs.BeautifulSoup(job_html_contents, 'html5lib')
                    job_desc = job_soup.find('div', {'id': 'job-details'})

                    job_date = str(datetime.date.today())

                    # print("--------------------------------------")
                    # print("Job Keyword: " + keyword)
                    # print("Personal Interest: " + interest)
                    # print("Job ID:" + job_id)
                    # print("Job Link:" + job_link)
                    # print("Position:" + cols[0])
                    # print("Company:" + cols[1])
                    # print("Job Category:" + cols[2])
                    # print("Job Descriptions: " + job_desc.text)
                    # print("Date:" + job_date)
                    # print("--------------------------------------")

                    values = [job_id, job_link, cols[0], cols[1], cols[2], job_desc.text, job_date, keyword, interest]
                    data.append(values)
    connect_db(data)


# js_scrape_keyword: Job Keyword Scraping from JobStreet
def js_scrape_keyword():
    interest = ""
    data = []
    for keyword in keywords_search:
        keyword = keyword.strip()
        keyword_space_replace = keyword.replace(' ', '%20')
        keyword_no_space = keyword.replace(' ', '')
        url = "https://www.jobstreet.com.sg/en/job-search/job-vacancy.php?ojs=10&key=" + keyword_space_replace
        html_contents = requests.get(url).text
        soup = bs.BeautifulSoup(html_contents, 'html5lib')

        containers = soup.find_all('div', {'class': 'panel-body'})

        counter = 0
        for con in containers:
            if counter != 5:
                job_position = con.find('a', {'class': 'position-title-link'})

                if job_position is not None:
                    counter += 1
                    counter_string = str(counter).rjust(3, '0')
                    job_id = "JS" + "-" + keyword_no_space.upper() + counter_string

                    job_link = job_position.get('href')

                    job_company = con.find('a', {'class': 'company-name'})
                    if job_company is not None:
                        job_company = job_company.text
                    else:
                        job_company = ""

                    job_category = con.find('a', {'id': 'job_industry_desc'})
                    if job_category is not None:
                        job_category = job_category.text
                    else:
                        job_category = ""

                    # Retrieve Job Descriptions
                    job_html_contents = requests.get(job_link).text
                    job_soup = bs.BeautifulSoup(job_html_contents, 'html5lib')
                    job_desc = job_soup.find('div', {'class': 'unselectable wrap-text'})
                    if job_desc is not None:
                        job_desc = job_desc.text
                    else:
                        job_desc = ""

                    job_date = str(datetime.date.today())

                    # print("--------------------------------------")
                    # print("Job Keyword: " + keyword)
                    # print("Personal Interest: " + interest)
                    # print("Job ID: " + job_id)
                    # print("Job Link:" + job_link)
                    # print("Position: " + job_position.text)
                    # print("Company: " + job_company)
                    # print("Category: " + job_category)
                    # print("Job Description:" + job_desc)
                    # print("Date:" + job_date)
                    # print("--------------------------------------")

                    values = [job_id, job_link, job_position.text, job_company, job_category, job_desc, job_date, keyword, interest]
                    data.append(values)
    connect_db(data)


# js_scrape_keyword: Job Interest Scraping from JobStreet
def js_scrape_interest():
    keyword = ""
    data = []
    for interest in interest_search:
        interest = interest.strip()
        interest_space_replace = interest.replace(' ', '%20')
        interest_no_space = interest.replace(' ', '')
        url = "https://www.jobstreet.com.sg/en/job-search/job-vacancy.php?ojs=10&key=" + interest_space_replace
        html_contents = requests.get(url).text
        soup = bs.BeautifulSoup(html_contents, 'html5lib')

        containers = soup.find_all('div', {'class': 'panel-body'})

        counter = 0
        for con in containers:
            if counter != 5:
                job_position = con.find('a', {'class': 'position-title-link'})

                if job_position is not None:
                    counter += 1
                    counter_string = str(counter).rjust(3, '0')
                    job_id = "JS" + "-" + interest_no_space.upper() + counter_string

                    job_link = job_position.get('href')

                    job_company = con.find('a', {'class': 'company-name'})
                    if job_company is not None:
                        job_company = job_company.text
                    else:
                        job_company = ""

                    job_category = con.find('a', {'id': 'job_industry_desc'})
                    if job_category is not None:
                        job_category = job_category.text
                    else:
                        job_category = ""

                    # Retrieve Job Descriptions
                    job_html_contents = requests.get(job_link).text
                    job_soup = bs.BeautifulSoup(job_html_contents, 'html5lib')
                    job_desc = job_soup.find('div', {'class': 'unselectable wrap-text'})
                    if job_desc is not None:
                        job_desc = job_desc.text
                    else:
                        job_desc = ""

                    job_date = str(datetime.date.today())

                    # print("--------------------------------------")
                    # print("Job Keyword: " + keyword)
                    # print("Personal Interest: " + interest)
                    # print("Job ID: " + job_id)
                    # print("Job Link:" + job_link)
                    # print("Position: " + job_position.text)
                    # print("Company: " + job_company)
                    # print("Category: " + job_category)
                    # print("Job Description:" + job_desc)
                    # print("Date:" + job_date)
                    # print("--------------------------------------")

                    values = [job_id, job_link, job_position.text, job_company, job_category, job_desc, job_date, keyword, interest]
                    data.append(values)
    connect_db(data)


# jd_scrape: Job Scraping from JobsDB
def jd_scrape():
    data = []
    url = "http://sg.jobsdb.com/SG/EN/Search/FindJobs?KeyOpt=COMPLEX&JSRV=1&RLRSF=1&JobCat=1&SearchFields=Positions,Companies&Key=software%20engineer&JSSRC=HPSS"
    html_contents = requests.get(url).text
    soup = bs.BeautifulSoup(html_contents, 'html5lib')

    result_list = soup.find_all('div', {'class': 'result-sherlock-cell'})

    counter = 0
    for result in result_list:
        if counter != 10:
            job_position = result.find('a', {'class': 'posLink'})

            if job_position is not None:
                counter += 1
                counter_string = str(counter).rjust(8, '0')
                job_id = "JD" + counter_string

                job_link = job_position.get('href')

                job_company = result.find('a', {'class': 'coLink CompanyAction'})
                if job_company is not None:
                    job_company = job_company.text

                # Retrieve Job Category & Descriptions
                job_html_contents = requests.get(job_link).text
                job_soup = bs.BeautifulSoup(job_html_contents, 'html5lib')

                job_category = job_soup.find('div', {'class': 'primary-meta-box row meta-industry'})
                job_category = job_category.text.replace('Industry  ', '')
                job_category = job_category.strip()

                job_desc = job_soup.find('div', {'class': 'jobad-primary-details'})
                if job_desc is not None:
                    job_desc = job_desc.text
                else:
                    job_desc = 'None'

                job_date = str(datetime.date.today())

                # print("Job ID: " + job_id)
                # print("Job Link:" + job_link)
                # print("Position: " + job_position.text)
                # print("Company: " + job_company)
                # print("Category: " + job_category)
                # print("Job Description:" + job_desc)
                # print("Date:" + job_date)
                # print("--------------------------------------")

                values = [job_id, job_link, job_position.text, job_company, job_category, job_desc, job_date]
                data.append(values)
    connect_db(data)


def run():
    print("Running: Retrieving keywords for Jobs & Personal Interests")
    retrieve_keywords()

    print("Running: Job Keyword Scraping from Careers@GOV")
    cg_scrape_keyword()
    print("Running: Job Interest Scraping from Careers@GOV")
    cg_scrape_interest()

    print("Running: Job Keyword Scraping from JobStreet")
    js_scrape_keyword()
    print("Running: Job Interest Scraping from JobStreet")
    js_scrape_interest()

    print("------------------- Job Scraping End -------------------")

run()
