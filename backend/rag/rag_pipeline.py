from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_mistralai import ChatMistralAI

from backend.config import Config
from backend.rag.retriever import MaritimeRetriever


class MaritimeRAGPipeline:

    def __init__(self):

        self.retriever = MaritimeRetriever()

        self.llm = ChatMistralAI(
            api_key=Config.MISTRAL_API_KEY,
            model=Config.MISTRAL_MODEL,
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_template(
            """
You are an AI Maritime Risk Analysis Assistant.

You must answer ONLY using the retrieved context.

If the answer is not present in the context, reply exactly:

"I could not find enough information in the available reports."

----------------------------
Retrieved Context
----------------------------

{context}

----------------------------
User Question
----------------------------

{question}

----------------------------
Instructions
----------------------------

1. Answer clearly.
2. Use only the provided context.
3. Do not hallucinate.
4. Mention important facts.
5. If multiple reports contain relevant information,
   combine them into one answer.
"""
        )

        self.output_parser = StrOutputParser()

    def retrieve_context(self, question):

        documents = self.retriever.retrieve_documents(question)

        context = "\n\n".join(
            doc.page_content for doc in documents
        )

        return context, documents

    def ask(self, question):

        context, documents = self.retrieve_context(question)

        chain = (
            self.prompt
            | self.llm
            | self.output_parser
        )

        answer = chain.invoke(
            {
                "context": context,
                "question": question
            }
        )

        return answer, documents


if __name__ == "__main__":

    rag = MaritimeRAGPipeline()

    while True:

        question = input("\nAsk a question (type 'exit' to quit):\n> ")

        if question.lower() == "exit":
            break

        answer, docs = rag.ask(question)

        print("\n" + "=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(answer)

        print("\n" + "=" * 80)
        print("SOURCES")
        print("=" * 80)

        for i, doc in enumerate(docs, start=1):

            print(f"\nSource {i}")

            print(
                f"File : {doc.metadata.get('source')}"
            )

            print(
                f"Page : {doc.metadata.get('page')}"
            )