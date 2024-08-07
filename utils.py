#version 2.0
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
import numpy as np
import pymupdf
import json

client = OpenAI()
embeddings = OpenAIEmbeddings()



from string import Template
 
def new_llm_response(resume_text, job_description):
    prompt_template = Template("""
    You are an experienced HR professional with extensive experience in analyzing resumes based on Job Descriptions.
    Your task is to compare the following resume text against the given Job Description and provide a similarity score along with a brief analysis.
 
    ### Job Description:
    ${job_description}
 
    ### Resume:
    ${resume_text}
 
    ### Task:
    1. Compare the resume against the Job Description.
    2. Provide a similarity score for the resume (on a scale of 0-100%).
    3. Offer a brief analysis explaining the score.
 
    Format the output in JSON only:
    {
      Similarity Score: [Score] ,
      Analysis: [Details]
    }
 
    Note: Strongly follow the Output format.
    """)
 
    # Create the prompt by substituting the template with actual values
    prompt = prompt_template.substitute(
        resume_text=resume_text,
        job_description=job_description
    )
 
    # Generate the completion
    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt}
        ]
    )

    ans = completion.choices[0].message.content
    j_ans= json.loads(ans)
    score = int(j_ans['Similarity Score'])
    analysis = j_ans['Analysis']
    return score , analysis


def load_resumes(file_path):
  resume_dic = {}
  for i in file_path:
       doc = pymupdf.open(i) # open a supported document
       all_text = ""
       for page in doc:
        all_text += page.get_text() + chr(12)
        # resume_text = llm_response(all_text)
        resume_dic[i] = all_text
        
  return resume_dic







# import shutil
# from langchain.vectorstores import Pinecone
# from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
# from langchain.schema import Document
# import pinecone
# from pypdf import PdfReader
# import os
# import pandas as pd
# import nltk
# from nltk.corpus import stopwords
# nltk.download('stopwords')
# import spacy
# from pyresparser import ResumeParser


# #Extract Information from PDF file
# def get_pdf_text(pdf_doc):
#     text = ""
#     pdf_reader = PdfReader(pdf_doc)
#     for page in pdf_reader.pages:
#         text += page.extract_text()
#     return text



# # iterate over files in
# # that user uploaded PDF files, one by one
# def create_docs(user_pdf_list, unique_id):
#     docs=[]
#     for filename in user_pdf_list:
        
#         chunks=get_pdf_text(filename)

#         #Adding items to our list - Adding data & its metadata
#         docs.append(Document(
#             page_content=chunks,
#             metadata={"name": filename.name,"type=":filename.type,"size":filename.size,"unique_id":unique_id},
#         ))

#     return docs


# #Create embeddings instance
# def create_embeddings_load_data():
#     #embeddings = OpenAIEmbeddings()
#     embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
#     return embeddings


# #Function to push data to Vector Store - Pinecone here
# def push_to_pinecone(pinecone_apikey,pinecone_environment,pinecone_index_name,embeddings,docs):

#     pinecone.init(
#     api_key=pinecone_apikey,
#     environment=pinecone_environment
#     )
#     print("done......2")
#     Pinecone.from_documents(docs, embeddings, index_name=pinecone_index_name)
    


# #Function to pull infrmation from Vector Store - Pinecone here
# def pull_from_pinecone(pinecone_apikey,pinecone_environment,pinecone_index_name,embeddings):

#     pinecone.init(
#     api_key=pinecone_apikey,
#     environment=pinecone_environment
#     )

#     index_name = pinecone_index_name

#     index = Pinecone.from_existing_index(index_name, embeddings)
#     return index



# #Function to help us get relavant documents from vector store - based on user input
# def similar_docs(query,k,pinecone_apikey,pinecone_environment,pinecone_index_name,embeddings,unique_id):

#     pinecone.init(
#     api_key=pinecone_apikey,
#     environment=pinecone_environment
#     )

#     index_name = pinecone_index_name

#     index = pull_from_pinecone(pinecone_apikey,pinecone_environment,index_name,embeddings)
#     similar_docs = index.similarity_search_with_score(query, int(k),{"unique_id":unique_id})
#     #print(similar_docs)
#     return similar_docs




# # Function to save the best resumes to a folder

# def save_best_resumes(similar_docs, output_folder):
#     folder_path=os.path.abspath("uploaded_files")
#     #print(folder_path)
#     for i, doc in enumerate(similar_docs[:]):
#         document_name = doc[0].metadata.get("name", f"Unknown_Document_{i+1}")
#         file_path=os.path.join(folder_path,document_name)
#         des=os.path.abspath(output_folder)
#         # print(des)
#         # print("=================================")
        
#         shutil.copy(file_path,des)



# def extract_name_from_uploaded_file(uploaded_file_str):
#     # start_index = uploaded_file_str.find("name='") + len("name='")
#     # end_index = uploaded_file_str.find("'", start_index)
#     name = uploaded_file_str.split("\\")[-1]
#     #print(name)
#     return name


# def create_docs_dataFrame(user_pdf_list):
    
#     df = pd.DataFrame({'Name': [],
#                    'Skills': []
#                     }).reset_index(drop=True)
#     resume_folder_path=os.path.abspath("best_resumes")
    
#     for i in user_pdf_list:
#         file_path = os.path.join(resume_folder_path, i)
        
#         #Model in ResumeParser is `en_core_web_sm` with NER (Named Entity Recognition)

#         data = ResumeParser(file_path).get_extracted_data()
#         # print(data)

#         # df = df.append({'Name': extract_name_from_uploaded_file((str(pdf))), 'Skills': data["skills"]}, ignore_index=True)
#         df = pd.concat([df,pd.DataFrame([{'Name': extract_name_from_uploaded_file((str(file_path))), 'Skills': data["skills"]}])])


#     return df
