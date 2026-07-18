import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, AsyncMock

from main import app
from app.api.routes.chat import get_chat_service
from app.schemas.chat import Source, ChatResponse
from app.models.tenant import Tenant


@pytest.fixture
def auth_headers(client: TestClient, db_session: Session):
    """
    Creates a tenant and a user, logs them in, and returns headers containing the JWT token.
    """
    tenant_id = uuid.uuid4()
    tenant = Tenant(id=tenant_id, name="Test Tenant", slug="test-tenant")
    db_session.add(tenant)
    db_session.commit()

    user_data = {
        "email": "chat_user@example.com",
        "password": "strongpassword123",
        "full_name": "Chat User",
        "tenant_id": str(tenant_id)
    }
    client.post("/auth/register", json=user_data)

    login_data = {
        "username": "chat_user@example.com",
        "password": "strongpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    db_session.rollback()
    return {"Authorization": f"Bearer {token}"}, tenant_id


def test_chat_api_success(client: TestClient, auth_headers):
    headers, tenant_id = auth_headers
    
    # 1. Mock the ChatService
    mock_chat_service = MagicMock()
    expected_response = ChatResponse(
        answer="Employees receive 12 casual leave days annually.",
        sources=[
            Source(
                document="NovaTech_Employee_Handbook_v1.pdf",
                document_id=uuid.uuid4(),
                page=1,
                score=0.75
            )
        ]
    )
    mock_chat_service.chat = AsyncMock(return_value=expected_response)
    
    # Override dependency
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service

    try:
        # 2. Act: Make requests
        payload = {
            "question": "How many casual leave days do employees receive?",
            "top_k": 3,
            "score_threshold": 0.5
        }
        response = client.post("/chat", headers=headers, json=payload)
        
        # 3. Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["answer"] == "Employees receive 12 casual leave days annually."
        assert len(data["sources"]) == 1
        assert data["sources"][0]["document"] == "NovaTech_Employee_Handbook_v1.pdf"
        assert data["sources"][0]["page"] == 1
        assert data["sources"][0]["score"] == 0.75

        # Verify underlying service mock called correctly
        mock_chat_service.chat.assert_called_once_with(
            tenant_id=tenant_id,
            question="How many casual leave days do employees receive?",
            top_k=3,
            score_threshold=0.5
        )
    finally:
        # Cleanup dependency overrides
        app.dependency_overrides.clear()


def test_chat_api_unauthorized(client: TestClient):
    # Act: Request without authentication headers
    payload = {"question": "How many casual leave days do employees receive?"}
    response = client.post("/chat", json=payload)
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_chat_api_empty_question(client: TestClient, auth_headers):
    headers, _ = auth_headers

    # Act: Empty question string
    payload = {"question": "", "top_k": 5}
    response = client.post("/chat", headers=headers, json=payload)
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Question cannot be empty" in response.json()["detail"]

    # Act: Whitespace-only question string
    payload = {"question": "   ", "top_k": 5}
    response = client.post("/chat", headers=headers, json=payload)
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Question cannot be empty" in response.json()["detail"]


def test_chat_api_service_exception_500(client: TestClient, auth_headers):
    headers, _ = auth_headers

    # 1. Mock the ChatService to raise exception
    mock_chat_service = MagicMock()
    mock_chat_service.chat = AsyncMock(side_effect=RuntimeError("Ollama connection failed"))
    
    # Override dependency
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service

    try:
        # 2. Act
        payload = {"question": "How many casual leave days do employees receive?"}
        response = client.post("/chat", headers=headers, json=payload)
        
        # 3. Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "An unexpected error occurred" in data["detail"]
        assert "Ollama connection failed" not in data["detail"]  # Stack trace hidden
    finally:
        app.dependency_overrides.clear()
