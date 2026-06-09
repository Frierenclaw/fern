import aioboto3

from core.config import config


class S3Client:
    def __init__(self):
        self._session = aioboto3.Session(
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.S3_REGION_NAME
        )
        self.endpoint_url = config.S3_ENDPOINT_URL

    async def upload_object(
        self,
        object_name: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str:
        async with self._session.client(
            service_name='s3',
            endpoint_url=self.endpoint_url
        ) as s3:
            extra: dict = {
                'Bucket': config.BUCKET_NAME,
                'Key': object_name,
                'Body': data,
            }
            if content_type:
                extra['ContentType'] = content_type
            
            await s3.put_object(**extra)
        
        return f'{self.endpoint_url}/{config.BUCKET_NAME}/{object_name}'