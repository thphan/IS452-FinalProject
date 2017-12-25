#NetID: thphan2 - 4 credit hours

# Project Overview:
# In the final project, I want to build a Python program which can provide different functionalities for a paper collection
# such as building the collection automatically add paper, update paper, delete paper and search for paper in the collection
# as well as extract data out of the collection.

import os
import re
import csv
import networkx as nx
import matplotlib.pyplot as plt


#function to process metadata .csv file
def process_csv(filename):
    reader=csv.reader(open(filename))
    keys_list = next(reader)
    keys_list = [key.strip("ï»¿") for key in keys_list]
    vals_list = next(reader)
    paper_dict = {}
    for key,val in zip(keys_list, vals_list):
        paper_dict[key] = val
    paper_dict["Publication Date"]=re.sub('=|"','',paper_dict["Publication Date"])
    paper_dict["ISSN"]=re.sub('=|"','',paper_dict["ISSN"])
    return paper_dict


#function to process data file of paper .txt
def process_txt(filename, paper_dict):
    infile = open(filename, "r")
    lines = infile.read()
    infile.close()
    #create synonym list to treat the title of similar parts in the paper similarly
    litreview_synonym = ["RELATED WORKS\n"]
    method_synonym = ["PROPOSED METHOD\n","METHODS\n","METHOD\n"]
    result_synonym = ["RESULTS AND DISCUSSION\n","PRELIMINARY RESULTS","EXPERIMENT AND RESULTS ANALYSIS\n","EXPERIMENT\n","RESULT\n"]
    conclusion_synonym = ["CONCLUSION\n","CONCLUSIONS\n","CONCLUSION AND FUTURE WORK\n"]
    lines=re.sub("|".join(litreview_synonym),"LITERATURE REVIEW\n",lines)
    lines=re.sub("|".join(method_synonym),"METHODOLOGY\n",lines)
    lines=re.sub("|".join(result_synonym),"RESULTS\n",lines)
    lines=re.sub("|".join(conclusion_synonym),"CONCLUSION\n",lines)

    #find the start and end position of different parts in a paper
    intro_start = lines.find("INTRODUCTION")
    if lines.find("LITERATURE REVIEW") >= 0:
        intro_end=lines.find("LITERATURE REVIEW")
    else:
        intro_end=lines.find("METHODOLOGY")
    method_start=lines.find("METHODOLOGY")
    result_start=lines.find("RESULTS")
    conclusion_start=lines.find("CONCLUSION")
    ref_start=lines.find("REFERENCES")
    ref_end=lines.find("Copyright of Proceedings of the Association")
    paper_dict["INTRODUCTION"]=lines[intro_start:intro_end]
    paper_dict["METHODOLOGY"]=lines[method_start:result_start]
    paper_dict["RESULTS"]=lines[result_start:conclusion_start]
    paper_dict["CONCLUSION"]=lines[conclusion_start:ref_start]
    paper_dict["REFERENCES"]=lines[ref_start:ref_end]


#function to check if the paper is already available in the collection using access number
def check_avail(access_number,paper_collection):
    access_num_list=[paper["Accession Number"] for paper in paper_collection]
    if access_number in access_num_list:
            return True
    else:
        return False


#function to add a new paper to collection (including the check whether the paper  already exists or not
def add_paper(csv_filename,txt_filename,paper_collection):
    paper_dict=process_csv(csv_filename)
    if check_avail(paper_dict["Accession Number"],paper_collection)==False:
        process_txt(txt_filename, paper_dict)
        paper_collection.append(paper_dict)
        print ("The paper - ", paper_dict["Article Title"], "is added into collection")
    else:
        print("The paper you keyed in is already available in the collection. Please enter different paper!")


#function to reset the whole collection, remove all the current papers and add all the papers within ./Datasets/csv and ./Datasets/txt folders
def update_allfiles(paper_collection):
    for file in os.listdir("./Datasets/csv"):
        #process metadata .csv file
        csv_filename="./Datasets/csv/"+file
        paper_dict=process_csv(csv_filename)
        #process corresponding .txt file
        txt_filename="./Datasets/txt/"+file.replace("csv","txt")
        process_txt(txt_filename, paper_dict)
        #add the paper dictionary into paper collection
        paper_collection.append(paper_dict)


#function to delete a paper (including the check if the paper already exists in the collection)
def delete_paper(access_number,paper_collection):
    if check_avail(access_number,paper_collection):
        paper_collection=[paper for paper in paper_collection if paper["Accession Number"] != access_number]
        print("The paper is deleted!")
    else:
        print("The paper with accession number",access_number,"is not available in the collection.")
    return paper_collection

#function to find a paper based on a key.
def find_paper(paper_collection, key, value):
    filtered_papers = [paper for paper in paper_collection if value.lower() in paper[key].lower()]
    return filtered_papers


#function to update a paper based on the access_number, which key to update, and which value the key should be updated.
def update_paper(access_number,update_item,update_val,paper_collection):
    if check_avail(access_number, paper_collection) and (update_item in paper_collection[0].keys()):
        print("The paper is available in collection")
        for i in range(0,len(paper_collection)):
            if paper_collection[i]["Accession Number"] == access_number:
                paper_collection[i][update_item] = update_val
                print("The paper is updated")
    else:
        print ("No papers with provided accession number '%s' or the update key '%s' is not available." %(access_number,update_item))


#function to search by author
def author_search(name,paper_collection):
    results = find_paper(paper_collection,"Author",name)
    if len(results)>0:
        print("Author name containing '%s' is found in below paper:\n------" %name)
        for paper in results:
            print ("Title: %s\nAuthor: %s\nPublication Year: %s\n------" %(paper["Article Title"],paper["Author"],paper["Publication Date"]))
    else:
        print("No authors with name containing '%s' are found in the paper collection" %name)


#function to search by paper title
def title_search(title,paper_collection):
    results = find_paper(paper_collection,"Article Title",title)
    if len(results)>0:
        print("Article Title containing '%s' is found in below paper:\n------" %title)
        for paper in results:
            print ("Title: %s\nAuthor: %s\nPublication Year: %s\n------" %(paper["Article Title"],paper["Author"],paper["Publication Date"]))
    else:
        print("No articles with title containing '%s' are found in the paper collection" %title)


#function to search by publication year
def year_search(year,paper_collection):
    results = find_paper(paper_collection,"Publication Date",year)
    if len(results)>0:
        print("Publication year '%s' is found in below paper:\n------" %year)
        for paper in results:
            print ("Title: %s\nAuthor: %s\nPublication Year: %s\n------" %(paper["Article Title"],paper["Author"],paper["Publication Date"]))
    else:
        print("No articles published in '%s' are found in the paper collection" %year)


#function to create the author network
def create_author_network(paper_collection):
    #convert author name to <LastName>, <Initial> format
    author_nodes=[]
    author_edges=[]
    for paper in paper_collection:
        #extract cited authors
        ref_texts = paper["REFERENCES"]
        a_pattern = re.compile("([A-Z][a-z]+, ([A-Z]\.\s?)+)")
        a_results = re.findall(a_pattern, ref_texts)
        cited_authors = [x.strip().replace("\n"," ") for x, y in a_results]
        #add cited authors into author_nodes
        for name in cited_authors:
            author_nodes.append(name)
        #get author names
        author_names = paper["Author"].split(";")
        #for each author, transfrom his/her name into format <Lastname>, <Initial>. <Initial>. <etc...>
        #then add him/her into the author_nodes
        #add the tuple of (author, cited_author) into author_edges
        for name in author_names:
            if name.find(",")>=0:
                upper_chars=re.findall(re.compile("[A-Z]"), name[name.find(",")+2:])
                name = name[0:name.find(",")+2] + ". ".join(upper_chars) + "."
            author_nodes.append(name.strip())
            for cited_name in cited_authors:
                author_edges.append((name,cited_name))
    #order the author_nodes by alphabetical order
    author_nodes=sorted(list(set(author_nodes)))
    count=0
    #print out the options for authors and their position in the author list.
    for i in range(0,len(author_nodes)):
        print("[%s] %s\t\t\t" %(i,author_nodes[i]),end="")
        count+=1
        if count>3:
            print()
            count=0
    #ask for the user to enter the position of the author he/she wants to view the author network
    selected_author = eval(input("\nSelect an author number:"))
    plot_network(author_nodes[selected_author],author_edges)


#function to plot the network graph for a selected author
def plot_network(author,all_edges):
    subset_edges=[(a,ca) for a,ca in all_edges if a==author or ca==author]
    subset_nodes=[]
    #create subset of the authors related to the selected author and himself
    for a,ca in subset_edges:
        subset_nodes.append(a)
        subset_nodes.append(ca)
    #initialize a directed graph
    G=nx.DiGraph()
    #add nodes and edges for the graph
    G.add_nodes_from(set(subset_nodes))
    G.add_edges_from(subset_edges)
    pos = nx.spring_layout(G)
    # draw graph
    nx.draw_networkx(G,pos,arrows=True,edge_color='orange',node_color='orange',font_size=10,font_color='black')
    plt.axis('off')
    # show graph
    plt.show()


#main function includes all the options available for user to select
def main():
    paper_collection=[]
    user_input=""
    while user_input.lower()!="q":
        print("Select one of the below options, press q/Q to exit:\
              \n\tPress 0. View the collection.\
              \n\tPress 1. Update full collection of papers. Please make sure txt and csv files are saved in ./Datasets/txt and ./Datasets/csv folders.\
              \n\tPress 2. Manually add a paper into collection.\
              \n\tPress 3. Update details of an existing paper.\
              \n\tPress 4. Delete a paper.\
              \n\tPress 5. Search paper by author name.\
              \n\tPress 6. Search paper by title.\
              \n\tPress 7. Search paper by publication year.\
              \n\tPress 8. View author network of the collection.")
        user_input=input("Enter an option: ")
        if user_input=="0":
            print("List of papers in the current collection\n------")
            if len(paper_collection)==0:
                print("No papers are available in the collection. Please add some!")
            else:
                for paper in paper_collection:
                    print("Article Title: %s\n Author: %s\nPublication Date: %s\nAccession Number: %s" %(paper["Article Title"],paper["Author"],paper["Publication Date"],paper["Accession Number"]))
                    print("------")
        elif user_input=="1":
            paper_collection=[]
            update_allfiles(paper_collection)
        elif user_input=="2":
            #add_paper("./Datasets/csv_temp/Chong2016.csv","./Datasets/temp/Chong2016.txt",paper_collection)
            #add_paper("./Datasets/csv_temp/You2013.csv","./Datasets/temp/You2013.txt",paper_collection)
            csv_filename=input("Enter full path for csv filename:")
            txt_filename=input("Enter full path for txt filename:")
            add_paper(csv_filename,txt_filename,paper_collection)
        elif user_input=="3":
            #update_paper("11530292","ISSN","test1234",paper_collection)
            access_number=input("Enter the Accession Number of the paper you want to update:")
            update_item,update_val=input("Which item you want to update and its value? (separate by comma)")
            update_paper(access_number,update_item,update_val)
        elif user_input=="4":
            access_number=input("Enter the Accession Number of the paper you want to delete:")
            paper_collection=delete_paper(access_number,paper_collection)
        elif user_input=="5":
            #author_search("cho",paper_collection)
            author_name=input("Enter a search term for Author Name:")
            author_search(author_name,paper_collection)
        elif user_input=="6":
            #title_search("measur",paper_collection)
            title=input("Enter a search term for Article Title:")
            title_search(title,paper_collection)
        elif user_input=="7":
            #year_search("2016",paper_collection)
            year=input("Enter the publication year of the papers you want to search for:")
            year_search(year,paper_collection)
        elif user_input=="8":
            create_author_network(paper_collection)
        elif user_input.lower()=="q":
            print("Program exiting...")
        else:
            print("Your keyed in option is invalid, please select another option!")


main()
