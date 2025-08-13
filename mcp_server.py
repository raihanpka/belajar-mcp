from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# Tool to read a doc
@mcp.tool(
    name="read_doc_content",
    description="Read the content of a document and return it as a string.",
)
def read_document(doc_id: str = Field(description="ID of the document to read")):
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found")
    return docs[doc_id]

# Tool to edit a doc
@mcp.tool(
    name="edit_doc_content",
    description="Edit a document by replacing a string in the documents content with another string.",
)
def edit_document(
    doc_id: str = Field(description="ID of the document to edit"), 
    old_str: str = Field(description="The text to replace. Must match exactly including whitespace and case."),
    new_str: str = Field(description="The new text to insert in place of the old text."),
):
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return "Document edited successfully"

# Resource to return all doc id's
@mcp.resource(
    uri="mem://docs",
    name="list_docs_ids",
    description="Return all document IDs.",
)
def list_docs_ids():
    if not docs:
        raise ValueError("No documents found")
    return docs.keys()

# Resource to return the contents of a particular doc
@mcp.resource(
    uri="mem://docs/{doc_id}",
    name="return_doc_content",
    description="Return the contents of a particular document.",
)
def return_doc_content(doc_id: str):
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found")
    return docs[doc_id]

# Prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="rewrite_doc",
    description="Rewrite a document in markdown format.",
)
def rewrite_doc(doc_id: str):
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found")
    return f"Rewrite the document with ID {doc_id} in markdown format."

# Prompt to summarize a doc
@mcp.prompt(    
    name="summarize_doc",
    description="Summarize a document.",
)
def summarize_doc(doc_id: str):
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found")
    return f"Summarize the document with ID {doc_id}."

if __name__ == "__main__":
    mcp.run(transport="stdio")
