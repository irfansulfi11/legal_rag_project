import os
import dotenv
import asyncio
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class RAGEngine:
    def __init__(self):
        # Load environment variables
        dotenv.load_dotenv()
        
        if "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.PDF_PATH = "data/it_act_2000_updated.pdf"
        self.DB_PATH = "db"
        
        self.vector_store = None
        self.qa_chain = None
        self.llm = None
        self.embeddings = None
        
    def initialize(self):
        """
        Initialize the RAG system.
        This function is called from a thread, so we need to manage the asyncio event loop.
        """
        try:
            # Create and run a new event loop for this thread
            asyncio.run(self._initialize_async())
        except Exception as e:
            print(f"Error during async initialization: {e}")
            raise e

    async def _initialize_async(self):
        """Asynchronous part of the initialization."""
        print("Initializing RAG engine asynchronously...")
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Load or create vector store
        if os.path.exists(self.DB_PATH):
            print("Loading existing vector store...")
            self.vector_store = Chroma(
                persist_directory=self.DB_PATH, 
                embedding_function=self.embeddings
            )
        else:
            print("Creating new vector store...")
            self.vector_store = self._create_vector_store()
        
        # Initialize LLM and create RAG chain
        self.llm = GoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
        self.qa_chain = self._create_rag_chain()
        
        print("RAG engine initialized successfully!")
    
    def _create_vector_store(self):
        """Create vector store from PDF document"""
        if not os.path.exists(self.PDF_PATH):
            raise FileNotFoundError(f"PDF file not found: {self.PDF_PATH}")
        
        print("Loading PDF document...")
        loader = PyPDFLoader(self.PDF_PATH)
        documents = loader.load()
        
        print("Splitting document into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)
        
        print("Creating embeddings and storing in ChromaDB...")
        vector_store = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=self.DB_PATH
        )
        
        print("Vector store created successfully!")
        return vector_store
    
    def _create_rag_chain(self):
        """Create the RAG chain with custom prompt"""
        prompt_template_str = """
        You are a helpful legal assistant specializing in India's Information Technology Act, 2000.
        
        Instructions:
        1. Answer questions based ONLY on the provided context
        2. If the answer is in the context, provide a clear, comprehensive answer
        3. If the answer cannot be found in the context, respond with: "I cannot find the answer in the provided document."
        4. Always be precise and cite relevant sections when possible
        5. Use professional legal language but keep it accessible
        
        CONTEXT: {context}
        QUESTION: {question}
        
        ANSWER:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template_str, 
            input_variables=["context", "question"]
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        return qa_chain
    
    def get_response(self, question):
        """Get response to a question"""
        if not self.qa_chain:
            raise RuntimeError("RAG engine not initialized")
        
        try:
            response = self.qa_chain.invoke({"query": question})
            return response.get("result", "No response generated")
        except Exception as e:
            raise RuntimeError(f"Error generating response: {str(e)}")
    
    def get_streaming_response(self, question):
        """Get streaming response to a question"""
        if not self.qa_chain:
            raise RuntimeError("RAG engine not initialized")
        
        try:
            # Stream response chunks
            for chunk in self.qa_chain.stream({"query": question}):
                if 'result' in chunk:
                    yield chunk['result']
        except Exception as e:
            raise RuntimeError(f"Error generating streaming response: {str(e)}")
    
    def get_relevant_documents(self, question, k=3):
        """Get relevant documents for a question"""
        if not self.vector_store:
            raise RuntimeError("Vector store not initialized")
        
        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        docs = retriever.get_relevant_documents(question)
        
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    
    def is_ready(self):
        """Check if the RAG engine is ready"""
        return self.qa_chain is not None and self.vector_store is not None
