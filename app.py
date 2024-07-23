#version 2.0

import streamlit as st
import os
from utils import *
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
import concurrent
from dotenv import load_dotenv


# Function to save uploaded files
def save_uploadedfile(uploadedfile, save_folder):
    with open(os.path.join(save_folder, uploadedfile.name), "wb") as f:
        f.write(uploadedfile.getbuffer())

# Main function to run the Streamlit app

# Main function to run the Streamlit app
def main():
    st.title(" AI Resume Screener")

    # Create the directory if it doesn't exist
    save_folder = "input_file"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Read and inject custom CSS for sidebar and title
    with open('mystyle.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # File uploader widget
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

    # Sidebar elements
    with st.sidebar:
        # Toggle for Top K input
        top_k_toggle = st.checkbox("Enable Top K input", value=False)

        # Conditional slider input for Top K
        top_k = None
        if top_k_toggle:
            top_k = st.slider("Select Top K value", min_value=1, max_value=50, value=10)

        # Toggle for Percentage Criteria input
        percentage_toggle = st.checkbox("Enable Percentage Criteria input", value=False)

        # Conditional slider input for Percentage Criteria
        percentage_criteria = None
        if percentage_toggle:
            percentage_criteria = st.slider("Select Percentage Criteria value", min_value=10, max_value=100, value=50)

        # Filter button
        filter_button = st.button("Apply Filters")

    # Text area for job description
    job_description = st.text_area("Enter Job Description")

    # Upload button
    if st.button('Upload Resumes'):
        if uploaded_files and job_description:
            # Save uploaded files
            for uploaded_file in uploaded_files:
                save_uploadedfile(uploaded_file, save_folder)

            # Load resumes and extract text
            file_paths = [os.path.join(save_folder, uploaded_file.name) for uploaded_file in uploaded_files]
            resumes = load_resumes(file_paths)

        # Function to process a single resume
            def process_resume(file_path, text, job_description):
                score, analysis = new_llm_response(text, job_description)
                return file_path, score, analysis

            # Use ThreadPoolExecutor to process resumes in parallel
            similarity_scores = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_resume = {executor.submit(process_resume, file_path, text, job_description): file_path for file_path, text in resumes.items()}
                for future in concurrent.futures.as_completed(future_to_resume):
                    file_path = future_to_resume[future]
                    try:
                        file_path, score, analysis = future.result()
                        similarity_scores[file_path] = {"score": score, "analysis": analysis}
                    except Exception as exc:
                        print(f'{file_path} generated an exception: {exc}')
            
                # Sort similarity scores in descending order
                sorted_similarity_scores = dict(sorted(similarity_scores.items(), key=lambda item: item[1]['score'], reverse=True))


                # Prepare data for the table
                data = {
                    "Resume Name": [os.path.basename(file_path) for file_path in sorted_similarity_scores.keys()],
                    "Similarity Score": [details['score'] for details in sorted_similarity_scores.values()],
                    "Analysis": [details["analysis"] for details in sorted_similarity_scores.values()],
                    "File Path": list(sorted_similarity_scores.keys())
                }

                # Create DataFrame
                df = pd.DataFrame(data)


                # Store DataFrame in session state
                st.session_state['df'] = df

                # If Top K is enabled, display only the top K entries
                if top_k_toggle and top_k is not None:
                    df = df.head(top_k)


                # If Percentage Criteria is enabled, filter by percentage
                if percentage_toggle and percentage_criteria is not None:
                    print("percent toggle")
                    df = df[df["Similarity Score"] >= (percentage_criteria)]

                # Display similarity scores as a table
                st.write("Similarity Scores:")
                st.session_state['modifed_after_process'] = df
        
                md_df = df.drop(columns=['File Path'])
                md_df['Similarity Score'] = md_df['Similarity Score'].apply(lambda x: f"{x}%")
    
                st.table(md_df)

        else:
                st.warning("Please upload files and enter a job description")

    if filter_button and 'df' in st.session_state:
        df = st.session_state['df']

        # If Top K is enabled, display only the top K entries
        if top_k_toggle and top_k is not None:
            df = df.head(top_k)
        # If Percentage Criteria is enabled, filter by percentage
        if percentage_toggle and percentage_criteria is not None:
            df = df[df["Similarity Score"] >= (percentage_criteria)]

        st.session_state['modifed_after_process'] = df
        # Display the filtered table
        st.write("Filtered Similarity Scores:")
        md_df = df.drop(columns=['File Path'])
        md_df['Similarity Score'] = md_df['Similarity Score'].apply(lambda x: f"{x}%")
        st.table(md_df)


    if 'modifed_after_process' in st.session_state:
        df = st.session_state['modifed_after_process']
        for index, row in df.iterrows():
            if st.button(f"View {row['Resume Name']}", key=index):
                with open(row['File Path'], "rb") as f:
                    binary_data = f.read()
                pdf_viewer(input=binary_data, width=700)



if __name__ == "__main__":

    load_dotenv()
    main()



# import streamlit as st
# from dotenv import load_dotenv
# from utils import *
# import uuid

# #Creating session variables
# if 'unique_id' not in st.session_state:
#     st.session_state['unique_id'] =''


# def main():
#     load_dotenv()

#     st.set_page_config(page_title="Resume Screening Assistance", page_icon=":clipboard:")

#     # Add a background color and text alignment
#     st.markdown(
#         """
#         <style>
#         body {
#             background-color: #f5f5f5;
#             text-align: center;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

#     # Add a header with a stylish title
#     st.title("📋 HR - Resume Screening Assistant")
#     st.subheader("Let me help you streamline the resume screening process! 💼")

#     # Create a sidebar for additional options
#     st.sidebar.header("Settings")
#     document_count = st.sidebar.number_input("Number of Resumes to Return", value=5, min_value=1, max_value=20, key="2")

#     # Add a job description input with a label
#     st.write("\n")
#     st.header("Job Description")
#     job_description = st.text_area("Please paste the 'JOB DESCRIPTION' here...", key="1", height=200)



# # Create a folder to save the uploaded files
#     output_folder = "uploaded_files"
#     os.makedirs(output_folder, exist_ok=True)

#     # File upload widget for multiple PDF files
#     pdf_files = st.file_uploader("Upload resumes here, only PDF files allowed", type=["pdf"], accept_multiple_files=True)

#     if pdf_files:
#         for pdf in pdf_files:
#             # Display the uploaded file
#             #st.write("Uploaded File:", pdf.name)

#             # Save the uploaded file to the specified folder
#             file_path = os.path.join(output_folder, pdf.name)
#             with open(file_path, "wb") as f:
#                 f.write(pdf.read())

#         st.success(f"Uploading Done")

#     is_hard_reload = st.session_state.get("is_hard_reload", False)
#     if is_hard_reload:
#     # Delete uploaded files on hard reload
#         for root, _, files in os.walk(output_folder):
#             for file in files:
#                 os.remove(os.path.join(root, file))
#         st.session_state.is_hard_reload = False  # Reset the flag
    
#     if st.button("Clear Data"):
#         st.session_state.is_hard_reload = True
#         st.experimental_rerun()

#     if 'analysis_button_clicked' not in st.session_state:
#         st.session_state.analysis_button_clicked = False


#     # Help me with the analysis button
#     if st.button("Help me with the analysis"):
#         st.session_state.analysis_button_clicked = True

#     # Check if the "Help me with the analysis" button is clicked
#     if st.session_state.analysis_button_clicked:
    
#         with st.spinner('Wait for it...'):

#             #Creating a unique ID, so that we can use to query and get only the user uploaded documents from PINECONE vector store
#             st.session_state['unique_id']=uuid.uuid4().hex

#             #Create a documents list out of all the user uploaded pdf files
#             final_docs_list=create_docs(pdf_files,st.session_state['unique_id'])

#             #Displaying the count of resumes that have been uploaded
#             st.write("*Resumes uploaded* :"+str(len(final_docs_list)))

#             #Create embeddings instance
#             embeddings=create_embeddings_load_data()

#             #Push data to PINECONE
#             push_to_pinecone("03d95796-5a51-4b32-a07b-4feb019b9a98","asia-southeast1-gcp-free","res",embeddings,final_docs_list)

#             #Fecth relavant documents from PINECONE
#             relavant_docs=similar_docs(job_description,document_count,"03d95796-5a51-4b32-a07b-4feb019b9a98","asia-southeast1-gcp-free","res",embeddings,st.session_state['unique_id'])

#             # st.write(relavant_docs)

#             output_folder = "best_resumes"
#             os.makedirs(output_folder, exist_ok=True)
#             save_best_resumes(relavant_docs, output_folder)

#             #Introducing a line separator
#             st.write(":heavy_minus_sign:" * 30)

#             #For each item in relavant docs - we are displaying some info of it on the UI
#             for item in range(len(relavant_docs)):
                
#                 st.subheader("👉 "+str(item+1))

#                 #Displaying Filepath
#                 st.write("**File** : "+relavant_docs[item][0].metadata['name'])

#                 #Introducing Expander feature
#                 with st.expander('Show me 👀'): 
#                     st.info("**Match Score** : "+str(relavant_docs[item][1]))
        
#             submit1=st.button("Resumes for Extract Skills")
        
#             #print(submit1)
#             if submit1:
#                 with st.spinner('Extracting Skills...'):
#                     pdf=os.listdir("best_resumes")

#                     df=create_docs_dataFrame(pdf)

#                     st.write("\n")
#                     st.header("Extracted Skills from Filtered Resumes")

#                     st.write(df.head())

#                     data_as_csv= df.to_csv(index=False).encode("utf-8")
#                     st.download_button(
#                         "Download data as CSV", 
#                         data_as_csv, 
#                         "benchmark-tools.csv",
#                         "text/csv",
#                         key="download-tools-csv",
#                     )
#                 st.success("Skills extracted successfully.❤️")   



# #Invoking main function
# if __name__ == '__main__':
#     main()
