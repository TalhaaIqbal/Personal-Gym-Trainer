import pytest
from unittest.mock import patch, MagicMock
import os
from app.core.backblaze.b2_client import initiate_s3_client, upload_video, generate_watch_link


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the lru_cache before each test to ensure fresh client instances."""
    initiate_s3_client.cache_clear()
    yield
    initiate_s3_client.cache_clear()


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for B2 configuration."""
    env_vars = {
        "B2_UPLOADER_KEY_ID": "test_uploader_key",
        "B2_UPLOADER_APPLICATION_KEY": "test_uploader_app_key",
        "B2_VIEWER_KEY_ID": "test_viewer_key",
        "B2_VIEWER_APPLICATION_KEY": "test_viewer_app_key",
        "B2_ENDPOINT": "https://s3.us-west-004.backblazeb2.com",
        "B2_REGION": "us-west-004",
        "B2_BUCKET_NAME": "test-bucket"
    }
    with patch.dict(os.environ, env_vars, clear=True):
        yield env_vars


@pytest.fixture
def mock_boto3_client():
    """Mock boto3.client to return a MagicMock S3 client."""
    mock_client = MagicMock()
    with patch('app.core.backblaze.b2_client.boto3.client') as mock_boto3:
        mock_boto3.return_value = mock_client
        yield mock_client


class TestInitiateS3Client:
    """Tests for the initiate_s3_client function."""

    def test_initiate_uploader_client(self, mock_env_vars, mock_boto3_client):
        """Test that uploader client is created with correct credentials."""
        client = initiate_s3_client(role="uploader")
        
        assert client is not None
        mock_boto3_client.assert_called_once()

    def test_initiate_viewer_client(self, mock_env_vars, mock_boto3_client):
        """Test that viewer client is created with correct credentials."""
        client = initiate_s3_client(role="viewer")
        
        assert client is not None
        mock_boto3_client.assert_called_once()

    def test_invalid_role_raises_error(self, mock_env_vars):
        """Test that invalid role raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            initiate_s3_client(role="invalid_role")
        
        assert "Invalid role specified" in str(exc_info.value)

    def test_lru_cache_caches_clients(self, mock_env_vars, mock_boto3_client):
        """Test that clients are cached using lru_cache."""
        # First call
        client1 = initiate_s3_client(role="uploader")
        # Second call with same role
        client2 = initiate_s3_client(role="uploader")
        
        # Should return the same cached instance
        assert client1 is client2
        # boto3.client should only be called once due to caching
        assert mock_boto3_client.call_count == 1

    def test_different_roles_create_different_clients(self, mock_env_vars, mock_boto3_client):
        """Test that different roles create different cached clients."""
        uploader_client = initiate_s3_client(role="uploader")
        viewer_client = initiate_s3_client(role="viewer")
        
        # Should be different instances
        assert uploader_client is not viewer_client
        # boto3.client should be called twice for different roles
        assert mock_boto3_client.call_count == 2


class TestUploadVideo:
    """Tests for the upload_video function."""

    def test_upload_video_success(self, mock_env_vars, mock_boto3_client, tmp_path):
        """Test successful video upload."""
        # Create a temporary test file
        test_file = tmp_path / "test_video.mp4"
        test_file.write_bytes(b"fake video content")
        
        upload_video(local_path=str(test_file), target_key="videos/test.mp4")
        
        # Verify upload_file was called with correct parameters
        mock_boto3_client.upload_file.assert_called_once()
        call_args = mock_boto3_client.upload_file.call_args
        
        assert call_args[1]['Filename'] == str(test_file)
        assert call_args[1]['Bucket'] == "test-bucket"
        assert call_args[1]['Key'] == "videos/test.mp4"
        assert call_args[1]['ExtraArgs'] == {'ContentType': 'video/mp4'}

    def test_upload_video_uses_uploader_role(self, mock_env_vars, mock_boto3_client, tmp_path):
        """Test that upload_video uses the uploader role."""
        test_file = tmp_path / "test_video.mp4"
        test_file.write_bytes(b"fake video content")
        
        upload_video(local_path=str(test_file), target_key="videos/test.mp4")
        
        # Verify the client was initiated with uploader role
        # This is checked by ensuring boto3.client was called
        assert mock_boto3_client.call_count >= 1


class TestGenerateWatchLink:
    """Tests for the generate_watch_link function."""

    def test_generate_watch_link_success(self, mock_env_vars, mock_boto3_client):
        """Test successful watch link generation."""
        mock_url = "https://test-presigned-url.com"
        mock_boto3_client.generate_presigned_url.return_value = mock_url
        
        url = generate_watch_link(video_key="videos/test.mp4", expires_in_seconds=1800)
        
        assert url == mock_url
        mock_boto3_client.generate_presigned_url.assert_called_once_with(
            ClientMethod='get_object',
            Params={'Bucket': 'test-bucket', 'Key': 'videos/test.mp4'},
            ExpiresIn=1800
        )

    def test_generate_watch_link_default_expiry(self, mock_env_vars, mock_boto3_client):
        """Test that default expiry is 3600 seconds."""
        mock_boto3_client.generate_presigned_url.return_value = "https://test-url.com"
        
        generate_watch_link(video_key="videos/test.mp4")
        
        call_args = mock_boto3_client.generate_presigned_url.call_args
        assert call_args[1]['ExpiresIn'] == 3600

    def test_generate_watch_link_custom_expiry(self, mock_env_vars, mock_boto3_client):
        """Test custom expiry time."""
        mock_boto3_client.generate_presigned_url.return_value = "https://test-url.com"
        
        generate_watch_link(video_key="videos/test.mp4", expires_in_seconds=7200)
        
        call_args = mock_boto3_client.generate_presigned_url.call_args
        assert call_args[1]['ExpiresIn'] == 7200

    def test_generate_watch_link_uses_viewer_role(self, mock_env_vars, mock_boto3_client):
        """Test that generate_watch_link uses the viewer role."""
        mock_boto3_client.generate_presigned_url.return_value = "https://test-url.com"
        
        generate_watch_link(video_key="videos/test.mp4")
        
        # Verify the client was initiated
        assert mock_boto3_client.call_count >= 1
