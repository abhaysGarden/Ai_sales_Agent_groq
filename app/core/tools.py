import json
import os
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import faiss

KB_FILE = "data/kb.json"
CRM_FILE = "data/crm.json"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeAugmentationTool:
    def __init__(self):
        """
        Initializes the KnowledgeAugmentationTool instance.

        This constructor checks for the existence of required CRM and KB files and loads
        their contents into memory. If the files are missing or contain invalid JSON, 
        appropriate error messages are logged, and default empty structures are assigned 
        to instance variables. It also prepares document texts and initializes a model 
        using specified fallback options. The model is then used to encode document 
        texts and build a FAISS index for efficient similarity search. If any step fails,
        relevant warnings are logged, and the index is set to None.
        """

        if not os.path.exists(KB_FILE) or not os.path.exists(CRM_FILE):
            logger.error("KB or CRM file missing.")
            self.kb_docs = []
            self.crm_data = {}
            self.model = None
            return

        try:
            with open(CRM_FILE, "r") as f:
                self.crm_data = json.load(f)
            with open(KB_FILE, "r") as f:
                self.kb_docs = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing CRM/KB files: {e}")
            self.kb_docs = []
            self.crm_data = {}
            return

        self.doc_texts = [doc["text"] for doc in self.kb_docs]
        self.model = self._load_model_with_fallback(["all-MiniLM-L6-v2", "all-MiniLM-L12-v2"])

        if self.model:
            try:
                self.doc_embeddings = self.model.encode(self.doc_texts, convert_to_tensor=False)
                self.index = faiss.IndexFlatL2(len(self.doc_embeddings[0]))
                self.index.add(self.doc_embeddings)
            except Exception as e:
                logger.warning(f"FAISS indexing failed: {e}")
                self.index = None
        else:
            self.index = None

    def _load_model_with_fallback(self, model_names: List[str]) -> Optional[SentenceTransformer]:
        """
        Attempts to load a SentenceTransformer model from a list of model names.

        This method tries to load and return a SentenceTransformer model by iterating
        over the provided list of model names. If loading a model is successful, it
        returns the loaded model. If an exception occurs while trying to load a model,
        a warning is logged, and the next model in the list is attempted. If all model
        loading attempts fail, an error is logged, and the method returns None.

        Args:
            model_names (List[str]): A list of model names to attempt to load.

        Returns:
            Optional[SentenceTransformer]: The loaded SentenceTransformer model, or
            None if all attempts fail.
        """

        for name in model_names:
            try:
                logger.info(f"Trying to load model: {name}")
                return SentenceTransformer(name)
            except Exception as e:
                logger.warning(f"Failed to load model '{name}': {e}")
        logger.error("All embedding models failed to load.")
        return None

    def fetch_prospect_details(self, prospect_id: str) -> Dict:
        """
        Retrieves prospect details from the CRM data.

        Args:
            prospect_id (str): The ID of the prospect to retrieve.

        Returns:
            Dict: The prospect details, or a dictionary with an "error" key if the prospect ID is not found.
        """
        return self.crm_data.get(prospect_id, {
            "error": "Prospect ID not found"
        })

    def query_knowledge_base(self, query: str, filters: Optional[dict] = None) -> List[Dict]:
        """
        Queries the knowledge base for similar documents to the given query.

        If the SentenceTransformer model or the FAISS index is not available, a warning is logged, and a list with a single document containing an "error" field is returned.

        Args:
            query (str): The query to search for in the knowledge base.

        Returns:
            List[Dict]: A list of up to 3 documents from the knowledge base that are most similar to the query, or a list with a single document containing an "error" field if the query fails.
        """
        if not self.model or not self.index:
            logger.warning("Query skipped: embedding model or index not available.")
            return [{"text": "Knowledge base temporarily unavailable."}]

        try:
            query_embedding = self.model.encode([query])[0]
            scores, indices = self.index.search([query_embedding], k=3)
            return [self.kb_docs[i] for i in indices[0] if i < len(self.kb_docs)]
        except Exception as e:
            logger.error(f"Knowledge base query failed: {e}")
            return [{"text": f"Knowledge base query failed: {str(e)}"}]
