# Birthday Flyer Generator

This project can now store uploaded photos and generated flyers in the cloud using **Amazon S3** (or any S3-compatible provider like Cloudflare R2, DigitalOcean Spaces, MinIO, etc.).

## Cloud upload setup (recommended: S3)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   ```bash
   export USE_S3_STORAGE=true
   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_STORAGE_BUCKET_NAME=your-bucket-name
   export AWS_S3_REGION_NAME=us-east-1
   ```
3. Optional variables:
   ```bash
   # needed for S3-compatible non-AWS providers
   export AWS_S3_ENDPOINT_URL=https://<your-provider-endpoint>

   # optional CDN/custom domain
   export AWS_S3_CUSTOM_DOMAIN=cdn.example.com
   ```

## Notes

- When `USE_S3_STORAGE=true`, all `ImageField` files (`uploaded_photo`, `generated_flyer`, branding logo) are stored in your configured cloud bucket.
- When `USE_S3_STORAGE` is not enabled, the app continues to use local `media/` storage.
- Flyer generation now streams files from storage and writes generated PNGs back through Django storage, so it works with both local and cloud backends.
