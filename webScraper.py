# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 10:24:51 2020

@author: Aditya Agarwal
"""

import requests
from bs4 import BeautifulSoup


def my_function(link):
    """
    Function to get list of urls for data to scrap and creating their Response Objects 
    Link is passed to this function where we use requests.get() to create its Response Object
    Content of the response object parsed via Beautiful Soup LXML parser
    List of URLS is appended using the unique attribute of the web pages i.e. HREF
    """
    urls = []
    result=requests.get(link)
    src = result.content
    #print(src)
    soup = BeautifulSoup(src, 'lxml')
    for td_tag in soup.find_all("td"):
        a_tag = td_tag.find('a')
        if a_tag is not None and 'href' in a_tag.attrs:
            urls.append(a_tag.attrs['href']) 
    return urls

def get_processed_urls(urls):
    """
    From the given urls list segregate and seperate the mail links and the profile links
    A list of urls is passed and we seperate the links to profiles from the mail links and append in processed_urls
    """
    processed_urls = []
    length = len(urls)   
    for i  in range(length):
        if "mailto" in urls[i] :
            continue
        else :
            processed_urls.append(urls[i])
    return processed_urls

#list of relative links to check in the profile section 

vals = ["CurriculumVitae","SponsoredProjects","Courses",
         "Publications","ProfessionalWork","ResearchInterest","Seminars",
         "Memberships","ResearchPublications","VisitsAbroad","ProfessionalMemberships",
         "Awards","ResearchProjects","InstitutionalContribution","AwardsandRecognitions",
         "ResearchScholar","InstitutionalResponsibilities","InviteTalks",
         "ProfessionalActivities","Students","ProjectsandPublications"]

def make_text_file(vals, processed_urls):
    """
    To create text files for the data extracted from Profile section and realtive links of the processed urls 
    The list of urls for the profile section are analyzed and data is sccrapped off from these and stored in txt files
    Once text files are created for each unique name id relative links are checked
    The list of vals is traversed where these relative links are checked and written into the respective name id text file with UTF-8 encoding 
    """
    appends_list_length = len(vals)
    num_urls = len(processed_urls)

    for j in range(num_urls):
        a = processed_urls[j]
        print(a)
        k = 44
        n = 40
        b = ""
        alt_b = ""
        if "universe" in a:
            while a[k]!='/':
                b+=a[k]
                alt_b += a[k+1]
                k+=1
            if b == "":
                b = alt_b
            f = open(f"{b}.txt", "a",encoding="utf-8")
            res = requests.get(a)
            content_text = res.content
            soup = BeautifulSoup(content_text,'lxml')
            # print(soup.get_text())
            f.write(soup.get_text())
        
        elif "www" in a:
            while a[n]!='/':
                b+=a[n]
                alt_b += a[n+1]
                n+=1
            if b == "":
                b = alt_b
            f = open(f"{b}.txt", "a",encoding="utf-8")
            res = requests.get(a)
            content_text = res.content
            soup = BeautifulSoup(content_text,'lxml')
            # print(soup.get_text())
            f.write(soup.get_text())
            
        for h in range(appends_list_length):
            u = a.find("Profile")
            if(u==-1):
                u = a.find("profile")
            if(u==-1):
                continue
            x = 0
            z = ""
            while x!=u:
                z+=a[x]
                x+=1
            
            z+=vals[h]
            print(z)
            try:
                f = open(f"{b}.txt", "a",encoding="utf-8")
                res = requests.get(z)
                content_text = res.content
                soup = BeautifulSoup(content_text,'lxml')
                #print(soup.get_text())
                f.write(soup.get_text())
                print(f"wrote for {b} to {b}.txt\n")
                f.close()
            except Exception as e:
                print(f"Error with {b} - {e}\n")
                
            
        


def process_a_department(link):
    """
    To sequentially call the functions required to process the link and scrap data
    """
    urls = my_function(link)
    processed_urls = get_processed_urls(urls)
    make_text_file(vals,processed_urls)       
    
def main():
    """
    Consists of list of links for which data to be scrapped
    The following for loop traverses this list and passes each of the links to function process_a _department
    process_a_department calls the further necessary functions to process the link and create the output text file containing all the relevant information
    """
    
    data_links =['https://www.bits-pilani.ac.in/hyderabad/EEE/Faculty',
        'https://universe.bits-pilani.ac.in/hyderabad/computerscience/Faculty',
        'https://www.bits-pilani.ac.in/hyderabad/BPharmacy/Faculty',
        'https://www.bits-pilani.ac.in/hyderabad/BiologicalSciences/Faculty',
        'https://www.bits-pilani.ac.in/hyderabad/chemicalengineering/Faculty',
        'https://www.bits-pilani.ac.in/hyderabad/Chemistry/Faculty1',
        'https://www.bits-pilani.ac.in/hyderabad/civilengineering/Faculty',
        'https://www.bits-pilani.ac.in/hyderabad/Economics/Faculty1',
        'https://universe.bits-pilani.ac.in/hyderabad/Languages/Faculty',
        'https://www.bits-pilani.ac.in/hyderabad/Mathematics/Faculty',
        'https://www.bits-pilani.ac.in/hyderabad/mechanicalengineering/Faculty',
        'https://www.bits-pilani.ac.in/hyderabad/physics/Faculty']
    
    for link in data_links:
        try:
            process_a_department(link)
        except Exception as e:
            print(link, "not processed", e)
      #pass

main()