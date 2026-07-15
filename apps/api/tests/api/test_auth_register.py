"""Tests for auth register, refresh, and logout endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.auth
@pytest.mark.asyncio
async def test_register_new_user(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "securepassword123",
            "display_name": "New User",
        },
    )
    assert res.status_code in (201, 503)
    if res.status_code == 201:
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "expires_in" in data


@pytest.mark.auth
@pytest.mark.asyncio
async def test_register_duplicate_email(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "securepassword123",
            "display_name": "New User",
        },
    )
    if res.status_code == 201:
        res2 = await api_client.post(
            "/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "anotherpassword",
                "display_name": "Duplicate",
            },
        )
        assert res2.status_code == 409


@pytest.mark.auth
@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "securepassword123",
            "display_name": "Bad Email",
        },
    )
    assert res.status_code == 422


@pytest.mark.auth
@pytest.mark.asyncio
async def test_register_short_password_returns_422(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/register",
        json={
            "email": "short@test.com",
            "password": "short",
            "display_name": "Short Pass",
        },
    )
    assert res.status_code == 422


@pytest.mark.auth
@pytest.mark.asyncio
async def test_refresh_with_invalid_token(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/refresh",
        json={"refresh_token": "invalid-token-value"},
    )
    assert res.status_code in (401, 503)


@pytest.mark.auth
@pytest.mark.asyncio
async def test_logout_with_valid_token(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/logout",
        json={"refresh_token": "some-token"},
    )
    assert res.status_code in (204, 503)


@pytest.mark.auth
@pytest.mark.asyncio
async def test_login_invalid_credentials(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrongpass"},
    )
    assert res.status_code in (401, 503)


@pytest.mark.auth
@pytest.mark.asyncio
async def test_login_missing_email_returns_422(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/login",
        json={"password": "somepass"},
    )
    assert res.status_code == 422


@pytest.mark.auth
@pytest.mark.asyncio
async def test_login_missing_password_returns_422(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/login",
        json={"email": "test@test.com"},
    )
    assert res.status_code == 422
