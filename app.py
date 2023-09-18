import streamlit as st
from dotenv import load_dotenv
from utils import *
import uuid

#Creating session variables
if 'unique_id' not in st.session_state:
    st.session_state['unique_id'] =''


def main():
    load_dotenv()

    st.set_page_config(page_title="Resume Screening Assistance", page_icon=":clipboard:")

    # Add a background color and text alignment
    st.markdown(
        """
        <style>
        body {
            background-color: #f5f5f5;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Add a header with a stylish title
    st.title("📋 HR - Resume Screening Assistant")
    st.subheader("Let me help you streamline the resume screening process! 💼")

    # Create a sidebar for additional options
    st.sidebar.header("Settings")
    document_count = st.sidebar.number_input("Number of Resumes to Return", value=5, min_value=1, max_value=20, key="2")

    # Add a job description input with a label
    st.write("\n")
    st.header("Job Description")
    job_description = st.text_area("Please paste the 'JOB DESCRIPTION' here...", key="1", height=200)



# Create a folder to save the uploaded files
    output_folder = "uploaded_files"
    os.makedirs(output_folder, exist_ok=True)

    # File upload widget for multiple PDF files
    pdf_files = st.file_uploader("Upload resumes here, only PDF files allowed", type=["pdf"], accept_multiple_files=True)

    if pdf_files:
        for pdf in pdf_files:
            # Display the uploaded file
            #st.write("Uploaded File:", pdf.name)

            # Save the uploaded file to the specified folder
            file_path = os.path.join(output_folder, pdf.name)
            with open(file_path, "wb") as f:
                f.write(pdf.read())

        st.success(f"Uploading Done")

    is_hard_reload = st.session_state.get("is_hard_reload", False)
    if is_hard_reload:
    # Delete uploaded files on hard reload
        for root, _, files in os.walk(output_folder):
            for file in files:
                os.remove(os.path.join(root, file))
        st.session_state.is_hard_reload = False  # Reset the flag
    
    if st.button("Clear Data"):
        st.session_state.is_hard_reload = True
        st.experimental_rerun()

    if 'analysis_button_clicked' not in st.session_state:
        st.session_state.analysis_button_clicked = False


    # Help me with the analysis button
    if st.button("Help me with the analysis"):
        st.session_state.analysis_button_clicked = True

    # Check if the "Help me with the analysis" button is clicked
    if st.session_state.analysis_button_clicked:
    
        with st.spinner('Wait for it...'):

            #Creating a unique ID, so that we can use to query and get only the user uploaded documents from PINECONE vector store
            st.session_state['unique_id']=uuid.uuid4().hex

            #Create a documents list out of all the user uploaded pdf files
            final_docs_list=create_docs(pdf_files,st.session_state['unique_id'])

            #Displaying the count of resumes that have been uploaded
            st.write("*Resumes uploaded* :"+str(len(final_docs_list)))

            #Create embeddings instance
            embeddings=create_embeddings_load_data()

            #Push data to PINECONE
            push_to_pinecone("03d95796-5a51-4b32-a07b-4feb019b9a98","asia-southeast1-gcp-free","res",embeddings,final_docs_list)

            #Fecth relavant documents from PINECONE
            relavant_docs=similar_docs(job_description,document_count,"03d95796-5a51-4b32-a07b-4feb019b9a98","asia-southeast1-gcp-free","res",embeddings,st.session_state['unique_id'])

            # st.write(relavant_docs)

            output_folder = "best_resumes"
            os.makedirs(output_folder, exist_ok=True)
            save_best_resumes(relavant_docs, output_folder)

            #Introducing a line separator
            st.write(":heavy_minus_sign:" * 30)

            #For each item in relavant docs - we are displaying some info of it on the UI
            for item in range(len(relavant_docs)):
                
                st.subheader("👉 "+str(item+1))

                #Displaying Filepath
                st.write("**File** : "+relavant_docs[item][0].metadata['name'])

                #Introducing Expander feature
                with st.expander('Show me 👀'): 
                    st.info("**Match Score** : "+str(relavant_docs[item][1]))
        
            submit1=st.button("Resumes for Extract Skills")
        
            #print(submit1)
            if submit1:
                with st.spinner('Extracting Skills...'):
                    pdf=os.listdir("best_resumes")

                    df=create_docs_dataFrame(pdf)

                    st.write("\n")
                    st.header("Extracted Skills from Filtered Resumes")

                    st.write(df.head())

                    data_as_csv= df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download data as CSV", 
                        data_as_csv, 
                        "benchmark-tools.csv",
                        "text/csv",
                        key="download-tools-csv",
                    )
                st.success("Skills extracted successfully.❤️")   



#Invoking main function
if __name__ == '__main__':
    main()
