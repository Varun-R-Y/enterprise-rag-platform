import uuid
from app.schemas.document import RetrieveResult
from app.services.prompt_builder import PromptBuilder


def test_prompt_builder_success():
    # Arrange
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    builder = PromptBuilder()

    context = [
        RetrieveResult(
            score=0.95,
            tenant_id=tenant_id,
            document_id=doc_id,
            title="Handbook",
            original_filename="NovaTech_Employee_Handbook.pdf",
            page=3,
            chunk_number=0,
            text="Employees receive 12 casual leave days annually.",
        ),
        RetrieveResult(
            score=0.88,
            tenant_id=tenant_id,
            document_id=doc_id,
            title="Handbook",
            original_filename="NovaTech_Employee_Handbook.pdf",
            page=4,
            chunk_number=1,
            text="Sick leave requires a medical certificate if exceeding 3 consecutive days.",
        ),
    ]
    question = "How many casual leave days do I get?"

    # Act
    prompt = builder.build_prompt(question, context)

    # Assert
    # 1. System instructions, versioning, and rules exist
    assert "Prompt Version: 1.0" in prompt
    assert "You are an Enterprise Knowledge Assistant." in prompt
    assert "Rules:" in prompt
    assert "1. Use ONLY the provided context." in prompt
    assert "2. Never use outside knowledge." in prompt
    assert "If the answer is not explicitly supported by the provided context, do not infer or guess." in prompt
    assert '"I could not find that information in the provided documents."' in prompt
    assert "4. Keep answers concise and professional." in prompt
    assert "5. At the end of the answer, include a Sources section listing every document and page used." in prompt

    # 2. Contains user question
    assert "Question" in prompt
    assert question in prompt

    # 3. Compact context format is respected for all documents
    expected_doc1 = (
        "Document: NovaTech_Employee_Handbook.pdf\n"
        "Page: 3\n\n"
        "Content:\n"
        "Employees receive 12 casual leave days annually."
    )
    expected_doc2 = (
        "Document: NovaTech_Employee_Handbook.pdf\n"
        "Page: 4\n\n"
        "Content:\n"
        "Sick leave requires a medical certificate if exceeding 3 consecutive days."
    )
    assert expected_doc1 in prompt
    assert expected_doc2 in prompt

    # 4. Separator is present
    assert "----------------------------------------" in prompt

    # 5. Ranking order of retrieve results is preserved
    idx_doc1 = prompt.index(expected_doc1)
    idx_doc2 = prompt.index(expected_doc2)
    assert idx_doc1 < idx_doc2


def test_prompt_builder_empty_context():
    # Arrange
    builder = PromptBuilder()
    context = []
    question = "Is remote work allowed?"

    # Act & Assert (Should not raise exception)
    prompt = builder.build_prompt(question, context)

    # Verify basic sections exist
    assert "Prompt Version: 1.0" in prompt
    assert "Context" in prompt
    assert "Question" in prompt
    assert question in prompt
    assert "Answer:" in prompt


def test_prompt_builder_preserves_formatting():
    # Arrange
    tenant_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    builder = PromptBuilder()

    multiline_text = (
        "Leave Policy\n\n"
        "• Casual Leave: 12 days\n"
        "\t• Sick Leave: 10 days\n"
        "Special chars: $ % & * @ #"
    )

    context = [
        RetrieveResult(
            score=0.90,
            tenant_id=tenant_id,
            document_id=doc_id,
            title="Handbook",
            original_filename="NovaTech_Employee_Handbook.pdf",
            page=2,
            chunk_number=0,
            text=multiline_text,
        )
    ]
    question = "Show leave types."

    # Act
    prompt = builder.build_prompt(question, context)

    # Assert formatting (newlines, tabs, bullets, special characters) is fully preserved
    assert multiline_text in prompt
